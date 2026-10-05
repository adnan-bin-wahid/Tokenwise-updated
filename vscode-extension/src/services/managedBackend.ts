import { execFile, spawn } from "node:child_process";
import * as fs from "node:fs/promises";
import * as path from "node:path";

export interface PythonCommand { executable: string; args: string[] }
export interface SetupProgress { stage: string; message: string; current?: number; total?: number; step?: number; total_steps?: number; installation_root?: string }
export class SetupError extends Error {
  public constructor(message: string, public readonly stage?: string, public readonly hint?: string, public readonly cancelled = false, public readonly step?: number) {
    super(message); this.name = "SetupError";
  }
}

export function parseSetupError(output: string): SetupError | undefined {
  for (const line of output.split(/\r?\n/).reverse()) {
    if (!line.startsWith("TOKENWISE_SETUP_ERROR ")) { continue; }
    try {
      const value = JSON.parse(line.slice("TOKENWISE_SETUP_ERROR ".length));
      if (typeof value.stage === "string" && typeof value.message === "string" && typeof value.hint === "string") {
        return new SetupError(value.message.slice(0, 2000), value.stage, value.hint.slice(0, 1000), false,
          Number.isInteger(value.step) && value.step >= 1 && value.step <= 7 ? value.step : undefined);
      }
    } catch { /* Keep ordinary errors readable if the installer record is incomplete. */ }
  }
  return undefined;
}

export function setupProgressMessage(item: SetupProgress): string {
  const numbered = Number.isInteger(item.step) && Number.isInteger(item.total_steps)
    && item.step! > 0 && item.step! <= item.total_steps! && item.total_steps! <= 20;
  const percent = Number.isFinite(item.current) && Number.isFinite(item.total) && item.current! >= 0 && item.total! > 0
    ? ` (${Math.min(100, Math.floor(item.current! / item.total! * 100))}%)` : "";
  return `${numbered ? `Step ${item.step}/${item.total_steps}: ` : ""}${item.message}${percent}`;
}
export interface ProcessOptions {
  log: (line: string) => void;
  progress?: (item: SetupProgress) => void;
  signal?: AbortSignal;
  env?: NodeJS.ProcessEnv;
  onSpawn?: (pid: number) => void;
}

export function parseSetupProgress(line: string): SetupProgress | undefined {
  if (!line.startsWith("TOKENWISE_PROGRESS ")) { return undefined; }
  try {
    const value = JSON.parse(line.slice("TOKENWISE_PROGRESS ".length)) as SetupProgress;
    if (typeof value.stage === "string" && typeof value.message === "string") { return value; }
  } catch { /* Ordinary pip output is not a progress record. */ }
  return undefined;
}

function inspectPython(command: PythonCommand, signal?: AbortSignal): Promise<PythonCommand | undefined> {
  return new Promise((resolve) => execFile(command.executable, [...command.args, "-c", "import sys,struct,json; print(json.dumps({'version':list(sys.version_info[:2]),'bits':struct.calcsize('P')*8,'executable':sys.executable}))"],
    { windowsHide: true, timeout: 10000, encoding: "utf8", maxBuffer: 16384, signal },
    (error, stdout) => {
      if (!error) {
        try {
          const value = JSON.parse(stdout.trim());
          if (value.version?.[0] === 3 && value.version?.[1] === 12 && value.bits === 64
            && typeof value.executable === "string" && path.isAbsolute(value.executable)) {
            // Spawn Python directly, so the owned process PID also owns install.lock.
            resolve({ executable: value.executable, args: [] });
            return;
          }
        } catch { /* Ignore unsupported interpreters and launcher diagnostics. */ }
      }
      resolve(undefined);
    }));
}

export async function findPython312(preferred = "", signal?: AbortSignal): Promise<PythonCommand> {
  const candidates: PythonCommand[] = preferred ? [{ executable: preferred, args: [] }] : [
    ...(process.platform === "win32" ? [{ executable: "py", args: ["-3.12"] }] : []),
    ...["python3.12", "python3", "python"].map((executable) => ({ executable, args: [] })),
  ];
  for (const candidate of candidates) {
    if (signal?.aborted) { throw new SetupError("Python detection was cancelled.", "prerequisites", undefined, true); }
    const python = await inspectPython(candidate, signal);
    if (signal?.aborted) { throw new SetupError("Python detection was cancelled.", "prerequisites", undefined, true); }
    if (python) { return python; }
  }
  throw new Error("64-bit Python 3.12 was not found. Install Python 3.12, restart the IDE, or set TokenWise's Python Path user setting to its executable.");
}

export function runSetupProcess(command: string, args: string[], options: ProcessOptions): Promise<string> {
  return new Promise((resolve, reject) => {
    if (options.signal?.aborted) { reject(new SetupError("TokenWise setup was cancelled. Run setup again to resume.", undefined, undefined, true)); return; }
    const child = spawn(command, args, { shell: false, windowsHide: true, detached: process.platform !== "win32", stdio: ["ignore", "pipe", "pipe"], env: { ...process.env, PYTHONUTF8: "1", PYTHONUNBUFFERED: "1", ...options.env } });
    child.once("spawn", () => { if (child.pid) { options.onSpawn?.(child.pid); } });
    let tail = "", stdout = "", stderr = "", cancelled = false;
    const deliver = (line: string) => {
      const progress = parseSetupProgress(line);
      if (progress) { options.progress?.(progress); }
      options.log(line);
    };
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (text: string) => {
      stdout = (stdout + text).slice(-1024 * 1024);
      const lines = (tail + text).split(/\r?\n/);
      tail = lines.pop() ?? "";
      lines.forEach(deliver);
    });
    child.stderr.on("data", (text: string) => {
      stderr = (stderr + text).slice(-8192);
      options.log(text.trimEnd());
    });
    const cancel = () => {
      cancelled = true;
      if (child.exitCode !== null || child.signalCode !== null) { return; }
      if (process.platform === "win32" && child.pid) {
        execFile("taskkill.exe", ["/PID", String(child.pid), "/T", "/F"], { windowsHide: true }, () => undefined);
      } else if (child.pid) { try { process.kill(-child.pid, "SIGTERM"); } catch { child.kill("SIGTERM"); } }
    };
    options.signal?.addEventListener("abort", cancel, { once: true });
    child.once("error", (error) => { options.signal?.removeEventListener("abort", cancel); reject(error); });
    child.once("close", (code) => {
      options.signal?.removeEventListener("abort", cancel);
      if (tail) { deliver(tail); }
      if (cancelled) { reject(new SetupError("TokenWise setup was cancelled. Completed steps and partial downloads are retained.", undefined, undefined, true)); }
      else if (code !== 0) { reject(parseSetupError(stderr) ?? new SetupError((stderr.trim() || `Backend setup exited with code ${code}.`).slice(-2000))); }
      else { resolve(stdout); }
    });
  });
}

export async function installManagedBackend(
  python: PythonCommand, bundle: string, storage: string, version: string, options: ProcessOptions,
): Promise<string> {
  let installation: string | undefined;
  let installerPid: number | undefined;
  const progress = options.progress;
  try {
    await runSetupProcess(python.executable, [...python.args, path.join(bundle, "scripts", "install_backend.py"),
      "--bundle", bundle, "--storage", storage, "--version", version], {
      ...options, onSpawn: (pid) => { installerPid = pid; options.onSpawn?.(pid); },
      progress: (item) => { progress?.(item); if (item.stage === "complete") { installation = item.installation_root; } },
    });
  } finally {
    const lock = path.join(storage, "backend", "install.lock");
    try {
      if (installerPid && (await fs.readFile(lock, "utf8")) === String(installerPid)) { await fs.unlink(lock); }
    } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") { options.log(`Could not clean up the setup lock: ${String(error)}`); } }
  }
  if (!installation || !path.isAbsolute(installation)) { throw new Error("The backend installer did not report a completed installation."); }
  const managed = path.resolve(storage, "backend", "managed");
  const relative = path.relative(managed, installation);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) { throw new Error("The installer returned a path outside managed user storage."); }
  await fs.access(path.join(installation, "managed-install.json"));
  return installation;
}
