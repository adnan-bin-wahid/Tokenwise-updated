import { execFile } from "node:child_process";
import * as path from "node:path";
import { promisify } from "node:util";
import { CleanupProfile } from "./cleanupRegistry";

const execute = promisify(execFile);
export interface ProcessIdentity { pid: number; executable: string; command: string; parent?: { executable: string; command: string } }
export interface ProcessControl {
  platform: NodeJS.Platform;
  probe(pid: number): Promise<ProcessIdentity | undefined>;
  stop(pid: number): Promise<void>;
}
const samePath = (a: string, b: string): boolean => typeof a === "string" && typeof b === "string" && (process.platform === "win32"
  ? path.resolve(a).toLowerCase() === path.resolve(b).toLowerCase() : path.resolve(a) === path.resolve(b));

export function ownsBackend(identity: ProcessIdentity, profile: CleanupProfile, platform: NodeJS.Platform): boolean {
  const backend = profile.backend;
  if (!backend?.managed || !backend.port || identity.pid !== backend.pid) { return false; }
  const inside = path.relative(path.join(profile.storageRoot, "backend/managed"), backend.installation);
  if (!inside || inside.startsWith("..") || path.isAbsolute(inside)) { return false; }
  const argsMatch = (command: string) => /(?:^|\s)-m\s+uvicorn\s+swe_pruner\.online_serving:app(?:\s|$)/.test(command)
    && new RegExp(`--port(?:\\s+|=)${backend.port}(?:\\s|$)`).test(command);
  if (!argsMatch(identity.command)) { return false; }
  const python = path.join(backend.installation, platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python");
  if (platform === "win32") {
    return samePath(identity.executable, python) || !!identity.parent && samePath(identity.parent.executable, python) && argsMatch(identity.parent.command);
  }
  return identity.command.includes(python) && /python(?:3(?:\.\d+)?)?$/.test(identity.executable);
}

export function ownsInstaller(identity: ProcessIdentity, profile: CleanupProfile): boolean {
  if (identity.pid !== profile.backend?.installerPid || !/python(?:w|3(?:\.\d+)?)?(?:\.exe)?$/i.test(identity.executable)
    || !/(?:[\/\\])install_backend\.py(?:"|\s|$)/.test(identity.command)) { return false; }
  const storage = /--storage(?:\s+|=)(?:"([^"]+)"|'([^']+)'|(\S+))/.exec(identity.command);
  return !!storage && samePath(storage[1] ?? storage[2] ?? storage[3], profile.storageRoot);
}

export const nativeProcessControl: ProcessControl = {
  platform: process.platform,
  async probe(pid) {
    if (!Number.isSafeInteger(pid) || pid <= 0) { throw new Error("Invalid cleanup process ID."); }
    if (process.platform === "win32") {
      const script = `$p = Get-CimInstance Win32_Process -Filter 'ProcessId = ${pid}'; if ($p) { $q = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $p.ParentProcessId); @{ pid = $p.ProcessId; executable = $p.ExecutablePath; command = $p.CommandLine; parent = @{ executable = $q.ExecutablePath; command = $q.CommandLine } } | ConvertTo-Json -Compress }`;
      const { stdout } = await execute("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", script], { windowsHide: true, timeout: 15000, maxBuffer: 65536 });
      return stdout.trim() ? JSON.parse(stdout) as ProcessIdentity : undefined;
    }
    try {
      const { stdout } = await execute("ps", ["-p", String(pid), "-o", "comm=", "-o", "args="], { timeout: 5000, maxBuffer: 65536 });
      const parts = stdout.trim().match(/^(\S+)\s+(.+)$/);
      return parts ? { pid, executable: parts[1], command: parts[2] } : undefined;
    } catch (error) { if ((error as { code?: number }).code === 1) { return undefined; } throw error; }
  },
  async stop(pid) {
    if (process.platform === "win32") {
      await execute("taskkill.exe", ["/PID", String(pid), "/T", "/F"], { windowsHide: true, timeout: 15000 });
    } else { process.kill(pid, "SIGTERM"); }
  },
};

export async function stopOwnedProcesses(profile: CleanupProfile, control: ProcessControl = nativeProcessControl): Promise<void> {
  for (const kind of ["installer", "backend"] as const) {
    const pid = kind === "installer" ? profile.backend?.installerPid : profile.backend?.managed ? profile.backend.pid : undefined;
    if (!pid) { continue; }
    const identity = await control.probe(pid);
    if (!identity) { continue; }
    const owns = (candidate: ProcessIdentity) => kind === "installer" ? ownsInstaller(candidate, profile) : ownsBackend(candidate, profile, control.platform);
    if (!owns(identity)) { throw new Error(`Refusing to stop an unverified ${kind} process ${pid}; preserving its storage.`); }
    // Recheck immediately before signalling to reduce PID-reuse risk.
    const current = await control.probe(pid);
    if (!current) { continue; }
    if (!owns(current)) { throw new Error(`Process ${pid} changed identity; preserving its storage.`); }
    try { await control.stop(pid); }
    catch (error) { if (await control.probe(pid)) { throw error; } }
    for (let attempt = 0; attempt < 30; attempt++) {
      if (!await control.probe(pid)) { break; }
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    if (await control.probe(pid)) { throw new Error(`Owned ${kind} process ${pid} has not exited; preserving its storage.`); }
  }
}
