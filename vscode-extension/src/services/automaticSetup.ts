import { createHash, randomBytes } from "node:crypto";
import * as fs from "node:fs/promises";
import * as path from "node:path";
import { rememberWorkspace } from "./cleanupRegistry";

export interface BackendRegistration {
  schema_version: 1;
  project_root: string;
  python_path: string;
  runtime_dir: string;
}

export interface RegisteredBackend {
  registrationPath: string;
  registration: BackendRegistration;
}

export interface AutomaticSetupResult {
  workspaceRoot: string;
  rulePath: string;
  changedFiles: string[];
}

type JsonObject = Record<string, unknown>;
interface PendingWrite { target: string; previous?: Buffer; content: Buffer }

const DEFAULT_SETTINGS = {
  enabled: true, token_budget: 4096, threshold: 0.45, max_candidates: 6,
  response_guidance: true,
  backend_port: 8000, auto_start_backend: true,
  startup_timeout_seconds: 40, request_timeout_seconds: 90,
};
const WINDOWS_HOOK_COMMAND = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise/tokenwise-hook.ps1";
const PORTABLE_HOOK_COMMAND = "python3 .agents/tokenwise/tokenwise-launcher.py --hook";
const LEGACY_HOOK_COMMAND = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise-hook.ps1";
const LEGACY_RULE_HASH = "65e962fc19c85a5306dd0ec303710941985e3892d7c5e7758fdfa7f2347c6d53";

function object(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function digest(content: Buffer): string {
  return createHash("sha256").update(content).digest("hex");
}

async function readOptional(filename: string): Promise<Buffer | undefined> {
  try {
    return await fs.readFile(filename);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      return undefined;
    }
    throw error;
  }
}

function parseObject(content: Buffer | undefined, filename: string): JsonObject {
  if (!content) {
    return {};
  }
  try {
    const result: unknown = JSON.parse(content.toString("utf8").replace(/^\uFEFF/, ""));
    if (object(result)) {
      return result;
    }
  } catch {
    // Do not replace unreadable user configuration with defaults.
  }
  throw new Error(`${filename} must contain a valid JSON object. No workspace files were changed.`);
}

function jsonContent(value: unknown): Buffer {
  return Buffer.from(`${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function safeTarget(root: string, relative: string): Promise<string> {
  const target = path.resolve(root, relative);
  const inside = path.relative(root, target);
  if (!inside || inside.startsWith(`..${path.sep}`) || inside === ".." || path.isAbsolute(inside)) {
    throw new Error("TokenWise setup paths must stay inside their designated directory.");
  }
  let current = root;
  for (const segment of inside.split(path.sep)) {
    current = path.join(current, segment);
    try {
      const stat = await fs.lstat(current);
      if (stat.isSymbolicLink()) {
        throw new Error(`Refusing to configure a symbolic link or junction: ${current}`);
      }
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === "ENOENT") {
        break;
      }
      throw error;
    }
  }
  return target;
}

async function atomicWrite(filename: string, content: Buffer): Promise<void> {
  await fs.mkdir(path.dirname(filename), { recursive: true });
  const temporary = `${filename}.${randomBytes(8).toString("hex")}.tmp`;
  try {
    await fs.writeFile(temporary, content, { flag: "wx" });
    await fs.rename(temporary, filename);
  } finally {
    await fs.unlink(temporary).catch((error: NodeJS.ErrnoException) => {
      if (error.code !== "ENOENT") { throw error; }
    });
  }
}

async function applyWrites(writes: PendingWrite[]): Promise<string[]> {
  const changed = writes.filter((write) => !write.previous?.equals(write.content));
  for (const write of changed) {
    const current = await readOptional(write.target);
    if (current?.equals(write.previous ?? Buffer.alloc(0)) !== true && (current || write.previous)) {
      throw new Error(`A file changed during setup: ${write.target}. Run the command again.`);
    }
  }
  const completed: PendingWrite[] = [];
  try {
    for (const write of changed) {
      await atomicWrite(write.target, write.content);
      completed.push(write);
    }
  } catch (error) {
    // Restore only bytes still owned by this attempt, never a concurrent user edit.
    for (const write of completed.reverse()) {
      const current = await readOptional(write.target);
      if (current?.equals(write.content)) {
        if (write.previous) {
          await atomicWrite(write.target, write.previous);
        } else {
          await fs.unlink(write.target);
        }
      }
    }
    throw error;
  }
  return changed.map((write) => write.target);
}

export async function validateBackendInstallation(installationRoot: string): Promise<string> {
  const root = await fs.realpath(path.resolve(installationRoot));
  const required = [
    process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python",
    "scripts/antigravity_context.py", "scripts/antigravity_hook.py",
    "swe-pruner/swe-pruner/src/swe_pruner/online_serving.py",
    "swe-pruner/swe-pruner/model/model.safetensors",
    "swe-pruner/swe-pruner/model/tokenizer.json",
    "swe-pruner/swe-pruner/model/config.json",
    "swe-pruner/swe-pruner/model/tokenizer_config.json",
    "swe-pruner/swe-pruner/model/backbone/config.json",
  ];
  for (const relative of required) {
    try {
      const stat = await fs.stat(path.join(root, relative));
      if (!stat.isFile() || stat.size === 0) { throw new Error("missing file"); }
    } catch {
      throw new Error(`The backend installation is missing ${relative}. Complete TokenWise backend setup first.`);
    }
  }
  return root;
}

export async function registerBackend(installationRoot: string, storageRoot: string): Promise<RegisteredBackend> {
  const root = await validateBackendInstallation(installationRoot);
  await fs.mkdir(storageRoot, { recursive: true });
  const storage = await fs.realpath(storageRoot);
  const registrationPath = await safeTarget(storage, "backend/installation.json");
  const runtime = await safeTarget(storage, "backend/runtime");
  const registration: BackendRegistration = {
    schema_version: 1, project_root: root,
    python_path: path.join(root, process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python"),
    runtime_dir: runtime,
  };
  const previous = await readOptional(registrationPath);
  const content = jsonContent(registration);
  if (!previous?.equals(content)) {
    await atomicWrite(registrationPath, content);
  }
  return { registrationPath, registration };
}

export async function discoverRegisteredBackend(storageRoot: string): Promise<string | undefined> {
  const filename = path.join(storageRoot, "backend/installation.json");
  try {
    const registration = parseObject(await readOptional(filename), filename);
    if (registration.schema_version === 1 && typeof registration.project_root === "string") {
      return await validateBackendInstallation(registration.project_root);
    }
  } catch {
    // An installation may have moved; the setup command can select its new location.
  }
  return undefined;
}

function validateSettings(settings: JsonObject): void {
  for (const name of ["enabled", "auto_start_backend", "response_guidance"]) {
    if (typeof settings[name] !== "boolean") { throw new Error(`TokenWise setting ${name} must be a boolean.`); }
  }
  const ranges: Record<string, [number, number]> = {
    token_budget: [256, 32768], threshold: [0, 1], max_candidates: [1, 32],
    backend_port: [1024, 65525], startup_timeout_seconds: [1, 60], request_timeout_seconds: [1, 120],
  };
  for (const [name, [minimum, maximum]] of Object.entries(ranges)) {
    const value = settings[name];
    if (typeof value !== "number" || !Number.isFinite(value) || value < minimum || value > maximum
      || (!["threshold", "startup_timeout_seconds", "request_timeout_seconds"].includes(name) && !Number.isInteger(value))) {
      throw new Error(`Invalid TokenWise setting: ${name}. No workspace files were changed.`);
    }
  }
}

export async function configureAutomaticContext(
  workspaceRoot: string, backend: RegisteredBackend, templatesRoot: string,
  platform: NodeJS.Platform = process.platform,
): Promise<AutomaticSetupResult> {
  const hookCommand = platform === "win32" ? WINDOWS_HOOK_COMMAND : PORTABLE_HOOK_COMMAND;
  const launchers = platform === "win32"
    ? ["tokenwise-runtime.ps1", "tokenwise-context.ps1", "tokenwise-hook.ps1"] : ["tokenwise-launcher.py"];
  const root = await fs.realpath(workspaceRoot);
  const writes: PendingWrite[] = [];
  const snapshots = new Map<string, Buffer | undefined>();
  const read = async (relative: string) => {
    const target = await safeTarget(root, relative);
    if (!snapshots.has(target)) { snapshots.set(target, await readOptional(target)); }
    return snapshots.get(target);
  };
  const plan = async (relative: string, content: Buffer) => {
    const previous = await read(relative);
    writes.push({ target: await safeTarget(root, relative), previous, content });
  };

  const settingsPath = ".agents/tokenwise.json";
  const settings = { ...DEFAULT_SETTINGS, ...parseObject(await read(settingsPath), settingsPath), enabled: true };
  validateSettings(settings);
  const hooksPath = ".agents/hooks.json";
  const hooks = parseObject(await read(hooksPath), hooksPath);
  const existingHook = hooks["tokenwise-automatic-context"];
  if (existingHook !== undefined && !object(existingHook)) {
    throw new Error("The tokenwise-automatic-context hook must be a JSON object. No workspace files were changed.");
  }
  const hook: JsonObject = { ...(existingHook as JsonObject | undefined), enabled: true };
  const handlers = hook.PreInvocation ?? [];
  if (!Array.isArray(handlers) || handlers.some((handler) => !object(handler))) {
    throw new Error("TokenWise PreInvocation handlers must be JSON objects. No workspace files were changed.");
  }
  const retained = handlers.filter((handler: JsonObject) => handler.command !== LEGACY_HOOK_COMMAND
    && handler.command !== (platform === "win32" ? PORTABLE_HOOK_COMMAND : WINDOWS_HOOK_COMMAND));
  if (!retained.some((handler: JsonObject) => handler.command === hookCommand)) {
    retained.push({ type: "command", command: hookCommand,
      timeout: Math.ceil(settings.startup_timeout_seconds + settings.request_timeout_seconds + 20) });
  }
  hook.PreInvocation = retained;
  hooks["tokenwise-automatic-context"] = hook;

  const manifestPath = ".agents/tokenwise/setup.json";
  const manifest = parseObject(await read(manifestPath), manifestPath);
  const owned = manifest.schema_version === 1 && object(manifest.files) ? manifest.files : {};
  const newOwned: JsonObject = { ...owned };
  for (const filename of launchers) {
    const relative = `.agents/tokenwise/${filename}`;
    const content = await fs.readFile(path.join(templatesRoot, filename));
    const previous = await read(relative);
    if (previous && !previous.equals(content) && owned[relative] !== digest(previous)) {
      throw new Error(`Preserving an existing or customized file: ${relative}. Move it or choose a different workspace before enabling TokenWise.`);
    }
    await plan(relative, content);
    newOwned[relative] = digest(content);
  }

  const rule = await fs.readFile(path.join(templatesRoot, platform === "win32" ? "tokenwise.md" : "tokenwise-python.md"));
  const priorRulePath = typeof manifest.rule_path === "string" && /^\.agents\/rules\/tokenwise(?:-automatic-context(?:-\d+)?)?\.md$/.test(manifest.rule_path)
    ? manifest.rule_path : undefined;
  const candidates = [...new Set([
    ...(priorRulePath ? [priorRulePath] : []), ".agents/rules/tokenwise.md",
    ".agents/rules/tokenwise-automatic-context.md",
    ...Array.from({ length: 98 }, (_, index) => `.agents/rules/tokenwise-automatic-context-${index + 2}.md`),
  ])];
  let rulePath: string | undefined;
  for (const candidate of candidates) {
    const previous = await read(candidate);
    const normalizedHash = previous ? digest(Buffer.from(previous.toString("utf8").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n"))) : "";
    if (!previous || previous.equals(rule) || owned[candidate] === digest(previous)
      || (candidate === ".agents/rules/tokenwise.md" && normalizedHash === LEGACY_RULE_HASH)) {
      rulePath = candidate;
      await plan(candidate, rule);
      newOwned[candidate] = digest(rule);
      break;
    }
  }
  if (!rulePath) { throw new Error("No unused TokenWise rule filename is available. No workspace files were changed."); }

  const ignorePath = ".gitignore";
  const ignore = await read(ignorePath);
  const ignoreText = ignore?.toString("utf8") ?? "";
  const cleanup = object(manifest.cleanup) ? { ...manifest.cleanup } : {};
  if (!ignoreText.split(/\r?\n/).some((line) => [".tokenwise/", "/.tokenwise/"].includes(line.trim()))) {
    const newline = ignoreText.includes("\r\n") ? "\r\n" : "\n";
    const content = Buffer.from(`${ignoreText}${ignoreText && !ignoreText.endsWith("\n") ? newline : ""}# TokenWise local context and backend link${newline}/.tokenwise/${newline}`);
    cleanup.ignore = { previous: ignore?.toString("base64") ?? null, written_hash: digest(content) };
    await plan(ignorePath, content);
  }
  cleanup.hooks_created ??= !(await read(hooksPath));
  cleanup.hooks_hash = digest(jsonContent(hooks));
  await plan(settingsPath, jsonContent(settings));
  await plan(hooksPath, jsonContent(hooks));
  await plan(".tokenwise/backend-link.json", jsonContent({ schema_version: 1, registration_path: backend.registrationPath }));
  await plan(manifestPath, jsonContent({ schema_version: 1, rule_path: rulePath, files: newOwned, cleanup }));
  await rememberWorkspace(path.dirname(path.dirname(backend.registrationPath)), root);
  const changedFiles = await applyWrites(writes);
  return { workspaceRoot: root, rulePath, changedFiles };
}
