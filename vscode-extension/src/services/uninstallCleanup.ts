import * as fs from "node:fs/promises";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { CleanupPlan, CleanupProfile, preserveInventory } from "./cleanupRegistry";
import { emptyDirectory, editJSON, EXTENSION_ID, hash, isObject, parseObject, readOptional, removeOwnedTree, replaceUnchanged, safeChild, safeRoot } from "./cleanupFiles";
import { ProcessControl, stopOwnedProcesses } from "./cleanupProcesses";

export interface CleanupResult { removed: string[]; preserved: string[]; warnings: string[] }
const HOOKS = new Set([
  "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise/tokenwise-hook.ps1",
  "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise-hook.ps1",
  "python3 .agents/tokenwise/tokenwise-launcher.py --hook",
]);
const ownedFilename = (name: string): boolean => /^\.agents\/tokenwise\/tokenwise-(?:runtime\.ps1|context\.ps1|hook\.ps1|launcher\.py)$/.test(name)
  || /^\.agents\/rules\/tokenwise(?:-automatic-context(?:-\d+)?)?\.md$/.test(name);

export async function cleanupWorkspace(workspace: string, storage: string, result: CleanupResult): Promise<boolean> {
  const root = await safeRoot(workspace);
  const linkPath = await safeChild(root, ".tokenwise/backend-link.json");
  const link = await readOptional(linkPath);
  if (!link || parseObject(link).registration_path !== path.join(storage, "backend/installation.json")) { return false; }
  const manifestPath = await safeChild(root, ".agents/tokenwise/setup.json");
  const manifestBytes = await readOptional(manifestPath);
  if (!manifestBytes) { result.warnings.push(`No ownership manifest; preserving workspace integration: ${root}`); return false; }
  const manifest = parseObject(manifestBytes);
  if (manifest.schema_version !== 1 || !isObject(manifest.files)) { throw new Error(`Invalid ownership manifest: ${manifestPath}`); }
  const cleanup = isObject(manifest.cleanup) ? manifest.cleanup : {};

  for (const [relative, expected] of Object.entries(manifest.files)) {
    if (!ownedFilename(relative) || typeof expected !== "string" || !/^[a-f0-9]{64}$/.test(expected)) { result.warnings.push(`Ignoring invalid owned path: ${relative}`); continue; }
    const filename = await safeChild(root, relative);
    const current = await readOptional(filename);
    if (!current) { continue; }
    if (hash(current) !== expected && hash(current.toString("utf8").replace(/\r\n/g, "\n")) !== expected) { result.preserved.push(filename); continue; }
    await replaceUnchanged(filename, current); result.removed.push(filename);
  }
  const hooksPath = await safeChild(root, ".agents/hooks.json");
  const hooksBytes = await readOptional(hooksPath);
  if (hooksBytes) {
    const hooks = parseObject(hooksBytes);
    const hook = hooks["tokenwise-automatic-context"];
    if (isObject(hook) && Array.isArray(hook.PreInvocation)) {
      const retained = hook.PreInvocation.filter((handler: unknown) => !isObject(handler) || !HOOKS.has(handler.command));
      let next = hooksBytes.toString("utf8");
      const ownOnly = Object.keys(hook).every((name) => ["enabled", "PreInvocation"].includes(name));
      if (!retained.length && ownOnly) { next = editJSON(next, ["tokenwise-automatic-context"], undefined); }
      else { next = editJSON(next, ["tokenwise-automatic-context", "PreInvocation"], retained); }
      const empty = !Object.keys(parseObject(next)).length;
      const created = cleanup.hooks_created === true && cleanup.hooks_hash === hash(hooksBytes);
      const legacyOnly = !manifest.cleanup && Object.keys(hooks).length === 1 && ownOnly && !retained.length;
      await replaceUnchanged(hooksPath, hooksBytes, empty && (created || legacyOnly) ? undefined : Buffer.from(next));
      result.removed.push(`${hooksPath}: TokenWise handlers`);
    }
  }
  const settingsPath = await safeChild(root, ".agents/tokenwise.json");
  const settings = await readOptional(settingsPath);
  if (settings) { parseObject(settings); await replaceUnchanged(settingsPath, settings); result.removed.push(settingsPath); }
  const ignorePath = await safeChild(root, ".gitignore");
  const ignore = await readOptional(ignorePath);
  if (ignore) {
    if (isObject(cleanup.ignore) && cleanup.ignore.written_hash === hash(ignore)
      && (cleanup.ignore.previous === null || typeof cleanup.ignore.previous === "string")) {
      await replaceUnchanged(ignorePath, ignore, cleanup.ignore.previous === null ? undefined : Buffer.from(cleanup.ignore.previous, "base64"));
    } else {
      const text = ignore.toString("utf8");
      const next = text.replace(/(^|\r?\n)# TokenWise local context and backend link\r?\n\/\.tokenwise\/(?:\r?\n|$)/g, "$1");
      if (next !== text) { await replaceUnchanged(ignorePath, ignore, next.trim() ? Buffer.from(next) : undefined); }
    }
  }
  const latestPath = await safeChild(root, ".tokenwise/latest.json");
  const latest = await readOptional(latestPath);
  if (latest) {
    const event = parseObject(latest);
    if (typeof event.event_id === "string" && (typeof event.query === "string" || ["antigravity-hook", "antigravity-agent-command"].includes(event.transport))) { await replaceUnchanged(latestPath, latest); result.removed.push(latestPath); }
    else { result.preserved.push(latestPath); }
  }
  const conversations = await safeChild(root, ".tokenwise/conversations");
  for (const name of await fs.readdir(conversations).catch((error: NodeJS.ErrnoException) => { if (error.code !== "ENOENT") { throw error; } return [] as string[]; })) {
    if (!/^[a-f0-9]{64}\.(?:json|lock)$/.test(name)) { continue; }
    const filename = await safeChild(root, `.tokenwise/conversations/${name}`);
    const bytes = await readOptional(filename);
    if (bytes) {
      if (name.endsWith(".json")) {
        const state = parseObject(bytes);
        if (typeof state.prompt_id !== "string" || typeof state.event_id !== "string") { result.preserved.push(filename); continue; }
      }
      await replaceUnchanged(filename, bytes); result.removed.push(filename);
    }
  }
  await replaceUnchanged(linkPath, link); result.removed.push(linkPath);
  await replaceUnchanged(manifestPath, manifestBytes); result.removed.push(manifestPath);
  for (const relative of [".tokenwise/conversations", ".tokenwise", ".agents/tokenwise", ".agents/rules", ".agents"]) { await emptyDirectory(root, relative); }
  for (const relative of [".tokenwise", ".agents/tokenwise"]) {
    const directory = await safeChild(root, relative);
    const retained = await fs.readdir(directory).catch((error: NodeJS.ErrnoException) => { if (error.code !== "ENOENT") { throw error; } return [] as string[]; });
    for (const name of retained) { const filename = path.join(directory, name); if (!result.preserved.includes(filename)) { result.preserved.push(filename); } }
  }
  return true;
}

export async function cleanupSettings(filename: string, result: CleanupResult): Promise<void> {
  const parent = await safeRoot(path.dirname(filename));
  const target = await safeChild(parent, path.basename(filename));
  const bytes = await readOptional(target);
  if (!bytes) { return; }
  const settings = parseObject(bytes);
  let next = bytes.toString("utf8");
  for (const key of Object.keys(settings)) {
    if (/^tokenWise\./i.test(key)) { next = editJSON(next, [key], undefined); }
    else if (/^\[.+\]$/.test(key) && isObject(settings[key])) {
      for (const name of Object.keys(settings[key])) {
        if (/^tokenWise\./i.test(name)) { next = editJSON(next, [key, name], undefined); }
      }
    }
  }
  if (next !== bytes.toString("utf8")) { await replaceUnchanged(target, bytes, Buffer.from(next)); result.removed.push(`${target}: TokenWise preferences`); }
}

async function recordedWorkspaces(profile: CleanupProfile, result: CleanupResult): Promise<string[]> {
  const roots = new Set(profile.workspaceRoots);
  let directory: string;
  try { directory = await safeChild(profile.settingsRoot, "workspaceStorage"); }
  catch (error) { if ((error as NodeJS.ErrnoException).code === "ENOENT") { return [...roots]; } throw error; }
  for (const name of await fs.readdir(directory).catch((error: NodeJS.ErrnoException) => { if (error.code !== "ENOENT") { throw error; } return [] as string[]; })) {
    if (!/^[a-zA-Z0-9_-]+$/.test(name)) { continue; }
    const bytes = await readOptional(await safeChild(profile.settingsRoot, `workspaceStorage/${name}/workspace.json`));
    if (!bytes) { continue; }
    let record: Record<string, any>;
    try { record = parseObject(bytes); }
    catch { result.warnings.push(`Unusable IDE workspace history record: ${name}`); continue; }
    if (typeof record.folder === "string" && record.folder.startsWith("file:")) { roots.add(fileURLToPath(record.folder)); }
    if (typeof record.workspace === "string" && record.workspace.startsWith("file:")) {
      const configuration = fileURLToPath(record.workspace);
      try {
        await safeRoot(path.dirname(configuration));
        const file = await readOptional(await safeChild(path.dirname(configuration), path.basename(configuration)));
        if (!file) { continue; }
        const workspace = parseObject(file);
        for (const folder of Array.isArray(workspace.folders) ? workspace.folders : []) {
          if (isObject(folder) && typeof folder.path === "string") { roots.add(path.resolve(path.dirname(configuration), folder.path)); }
          else if (isObject(folder) && typeof folder.uri === "string" && folder.uri.startsWith("file:")) { roots.add(fileURLToPath(folder.uri)); }
        }
      } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") { result.warnings.push(`Unusable IDE workspace configuration: ${configuration}: ${String(error)}`); } }
    }
  }
  return [...roots];
}

export async function runCleanup(plan: CleanupPlan, control?: ProcessControl): Promise<CleanupResult> {
  if (plan.schema_version !== 1 || plan.extension_id !== EXTENSION_ID || !Array.isArray(plan.profiles)
    || path.basename(plan.registryRoot) !== EXTENSION_ID || path.basename(path.dirname(plan.registryRoot)) !== ".tokenwise-cleanup") { throw new Error("Invalid TokenWise cleanup plan."); }
  const result: CleanupResult = { removed: [], preserved: [], warnings: [] };
  const attempt = async (action: () => Promise<void>) => {
    try { await action(); } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") { result.warnings.push(String(error)); } }
  };
  for (const profile of plan.profiles) {
    if (!path.isAbsolute(profile.storageRoot) || path.basename(profile.storageRoot).toLowerCase() !== EXTENSION_ID
      || path.basename(path.dirname(profile.storageRoot)).toLowerCase() !== "globalstorage"
      || profile.settingsRoot !== path.dirname(path.dirname(profile.storageRoot))) { result.warnings.push("Rejected invalid cleanup profile."); continue; }
    let processesStopped = true;
    try { await stopOwnedProcesses(profile, control); }
    catch (error) { processesStopped = false; result.warnings.push(String(error)); }
    await attempt(async () => {
      profile.workspaceRoots = await recordedWorkspaces(profile, result);
      await preserveInventory(plan.registryRoot, profile);
      for (const root of profile.workspaceRoots) {
        await attempt(async () => {
          if (await cleanupWorkspace(root, profile.storageRoot, result)) { await cleanupSettings(await safeChild(root, ".vscode/settings.json"), result); }
        });
      }
    });
    await attempt(() => cleanupSettings(path.join(profile.settingsRoot, "settings.json"), result));
    if (!processesStopped) { continue; }
    await attempt(async () => {
      await removeOwnedTree(path.dirname(profile.storageRoot), path.basename(profile.storageRoot));
      result.removed.push(profile.storageRoot);
    });
  }
  if (!result.warnings.length && !result.preserved.length) {
    await attempt(async () => {
      const owner = await readOptional(await safeChild(plan.registryRoot, "owner.json"));
      if (owner && parseObject(owner).extension_id === EXTENSION_ID) {
        await removeOwnedTree(path.dirname(plan.registryRoot), path.basename(plan.registryRoot));
        await emptyDirectory(path.dirname(path.dirname(plan.registryRoot)), ".tokenwise-cleanup");
      }
    });
  }
  return result;
}
