import * as fs from "node:fs/promises";
import * as path from "node:path";
import { atomicWrite, EXTENSION_ID, hash, parseObject, readOptional, safeChild, safeRoot } from "./cleanupFiles";

export interface CleanupProfile {
  storageRoot: string;
  settingsRoot: string;
  workspaceRoots: string[];
  backend?: { installation: string; managed: boolean; pid?: number; port?: number; installerPid?: number };
}
export interface CleanupPlan {
  schema_version: 1;
  extension_id: string;
  registryRoot: string;
  profiles: CleanupProfile[];
}

export async function registryLocation(extensionRoot: string): Promise<string> {
  const parent = await fs.realpath(path.dirname(extensionRoot));
  return safeChild(parent, `.tokenwise-cleanup/${EXTENSION_ID}`);
}

export async function registerLifecycle(storageRoot: string, extensionRoot: string): Promise<void> {
  if (path.basename(storageRoot).toLowerCase() !== EXTENSION_ID || path.basename(path.dirname(storageRoot)).toLowerCase() !== "globalstorage") { throw new Error("Unexpected TokenWise user storage path."); }
  await fs.mkdir(storageRoot, { recursive: true });
  const storage = await safeRoot(storageRoot);
  const registry = await registryLocation(extensionRoot);
  await fs.mkdir(registry, { recursive: true });
  const markerPath = await safeChild(registry, "owner.json");
  const previous = await readOptional(markerPath);
  if (previous && parseObject(previous).extension_id !== EXTENSION_ID) { throw new Error("Uninstall registry ownership is invalid."); }
  if (!previous) { await atomicWrite(markerPath, JSON.stringify({ schema_version: 1, extension_id: EXTENSION_ID })); }
  const profilePath = await safeChild(registry, `profile-${hash(storage)}.json`);
  const priorProfile = await readOptional(profilePath);
  const workspaceRoots = priorProfile ? parseObject(priorProfile).workspaceRoots ?? [] : [];
  await atomicWrite(profilePath, JSON.stringify({
    schema_version: 1, extension_id: EXTENSION_ID, storageRoot: storage, settingsRoot: path.dirname(path.dirname(storage)),
    workspaceRoots,
  }));
}

export async function rememberWorkspace(storageRoot: string, workspaceRoot: string): Promise<void> {
  const storage = await fs.realpath(storageRoot);
  const workspace = await fs.realpath(workspaceRoot);
  const filename = await safeChild(storage, `backend/workspaces/${hash(workspace)}.json`);
  await atomicWrite(filename, JSON.stringify({ schema_version: 1, workspaceRoot: workspace }));
}

export async function buildCleanupPlan(extensionRoot: string): Promise<CleanupPlan> {
  const registry = await registryLocation(extensionRoot);
  const result: CleanupPlan = { schema_version: 1, extension_id: EXTENSION_ID, registryRoot: registry, profiles: [] };
  const owner = await readOptional(await safeChild(path.dirname(path.dirname(registry)), `.tokenwise-cleanup/${EXTENSION_ID}/owner.json`));
  if (!owner) { return result; }
  if (parseObject(owner).extension_id !== EXTENSION_ID) { throw new Error("Invalid cleanup registry owner."); }
  for (const filename of await fs.readdir(registry)) {
    if (!/^profile-[a-f0-9]{64}\.json$/.test(filename)) { continue; }
    const entry = parseObject((await readOptional(await safeChild(registry, filename)))!);
    if (entry.extension_id !== EXTENSION_ID || typeof entry.storageRoot !== "string" || !path.isAbsolute(entry.storageRoot)
      || path.basename(entry.storageRoot).toLowerCase() !== EXTENSION_ID || path.basename(path.dirname(entry.storageRoot)).toLowerCase() !== "globalstorage"
      || entry.settingsRoot !== path.dirname(path.dirname(entry.storageRoot))) { throw new Error("Invalid registered cleanup profile."); }
    const profile: CleanupProfile = { storageRoot: entry.storageRoot, settingsRoot: entry.settingsRoot,
      workspaceRoots: Array.isArray(entry.workspaceRoots) ? entry.workspaceRoots.filter((root: unknown) => typeof root === "string" && path.isAbsolute(root)) : [] };
    const storageExists = await fs.lstat(profile.storageRoot).catch((error: NodeJS.ErrnoException) => { if (error.code !== "ENOENT") { throw error; } return undefined; });
    if (storageExists) {
      await safeRoot(profile.storageRoot);
      const inventory = await safeChild(profile.storageRoot, "backend/workspaces");
      for (const name of await fs.readdir(inventory).catch((error: NodeJS.ErrnoException) => { if (error.code !== "ENOENT") { throw error; } return [] as string[]; })) {
        if (!/^[a-f0-9]{64}\.json$/.test(name)) { continue; }
        const item = parseObject((await readOptional(await safeChild(profile.storageRoot, `backend/workspaces/${name}`)))!);
        if (item.schema_version === 1 && typeof item.workspaceRoot === "string" && path.isAbsolute(item.workspaceRoot)) { profile.workspaceRoots.push(item.workspaceRoot); }
      }
      const registrationBytes = await readOptional(await safeChild(profile.storageRoot, "backend/installation.json"));
      if (registrationBytes) {
        const registration = parseObject(registrationBytes);
        if (registration.schema_version === 1 && typeof registration.project_root === "string" && path.isAbsolute(registration.project_root)) {
          const inside = path.relative(path.join(profile.storageRoot, "backend/managed"), registration.project_root);
          const marker = inside && !inside.startsWith("..") && !path.isAbsolute(inside)
            ? await readOptional(await safeChild(profile.storageRoot, `backend/managed/${inside}/managed-install.json`)) : undefined;
          profile.backend = { installation: registration.project_root, managed: !!marker && parseObject(marker).schema_version === 1 };
          const runtime = await readOptional(await safeChild(profile.storageRoot, "backend/runtime/backend.json"));
          if (runtime) {
            const process = parseObject(runtime);
            if (process.project_root === registration.project_root && Number.isSafeInteger(process.pid) && process.pid > 0 && Number.isSafeInteger(process.port) && process.port >= 1024 && process.port <= 65535) {
              profile.backend.pid = process.pid; profile.backend.port = process.port;
            }
          }
        }
      }
      const lock = await readOptional(await safeChild(profile.storageRoot, "backend/install.lock"));
      const installerPid = lock && /^\d+$/.test(lock.toString()) ? Number(lock.toString()) : undefined;
      if (installerPid && Number.isSafeInteger(installerPid)) {
        profile.backend ??= { installation: "", managed: false };
        profile.backend.installerPid = installerPid;
      }
    }
    profile.workspaceRoots = [...new Set(profile.workspaceRoots)];
    await preserveInventory(registry, profile);
    result.profiles.push(profile);
  }
  return result;
}

export async function preserveInventory(registryRoot: string, profile: CleanupProfile): Promise<void> {
  const owner = await readOptional(await safeChild(registryRoot, "owner.json"));
  if (!owner || parseObject(owner).extension_id !== EXTENSION_ID) { throw new Error("Cleanup inventory has no valid owner."); }
  await atomicWrite(await safeChild(registryRoot, `profile-${hash(profile.storageRoot)}.json`), JSON.stringify({
    schema_version: 1, extension_id: EXTENSION_ID, storageRoot: profile.storageRoot, settingsRoot: profile.settingsRoot,
    workspaceRoots: [...new Set(profile.workspaceRoots)],
  }));
}

export async function adoptOpenWorkspace(storage: string, workspace: string): Promise<void> {
  try {
    const root = await fs.realpath(workspace);
    const bytes = await readOptional(await safeChild(root, ".tokenwise/backend-link.json"));
    if (bytes && parseObject(bytes).registration_path === path.join(await fs.realpath(storage), "backend/installation.json")) { await rememberWorkspace(storage, root); }
  } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") { throw error; } }
}
