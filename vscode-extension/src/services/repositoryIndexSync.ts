import { randomUUID } from "node:crypto";
import * as fs from "node:fs/promises";
import * as path from "node:path";
import * as vscode from "vscode";
import { localStoragePath } from "./extensionPaths";

const excluded = new Set([".git", ".venv", "venv", "node_modules", "__pycache__", ".vscode", ".idea", "build", "dist", "carbon_artifacts", ".pytest_cache", ".mypy_cache", ".agents", ".agent", ".tokenwise"]);
const pythonPattern = "**/*.[pP][yY]";
type Action = "start" | "update" | "reconcile" | "stop";
interface State {
  folder: vscode.WorkspaceFolder;
  watcherId: string;
  subscriptions: vscode.Disposable[];
  source?: vscode.FileSystemWatcher;
  sourceSubscriptions: vscode.Disposable[];
  pending: Map<string, number>;
  revision: number;
  refreshRevision: number;
  sequence: number;
  enabled: boolean;
  closed: boolean;
  started: boolean;
  autoStart: boolean;
  url?: string;
  timer?: ReturnType<typeof setTimeout>;
  flight?: Promise<void>;
  controller?: AbortController;
  fingerprint?: string;
  error?: string;
}

export class RepositoryIndexSync implements vscode.Disposable {
  private readonly output = vscode.window.createOutputChannel("TokenWise Index");
  private readonly states = new Map<string, State>();
  private readonly subscriptions: vscode.Disposable[] = [];
  private readonly heartbeat: ReturnType<typeof setInterval>;
  private paused = false;
  private disposed = false;

  public constructor(private readonly context: vscode.ExtensionContext,
    private readonly endpoint: (start: boolean) => Promise<string | undefined>,
    private readonly debounceMs = 150, heartbeatMs = 30000) {
    this.subscriptions.push(vscode.workspace.onDidChangeWorkspaceFolders(event => {
      for (const folder of event.removed) { this.remove(folder); }
      for (const folder of event.added) { this.add(folder); }
    }), vscode.workspace.onDidGrantWorkspaceTrust(() => {
      for (const folder of vscode.workspace.workspaceFolders ?? []) { this.add(folder); }
      for (const state of this.states.values()) { void this.refresh(state); }
    }), vscode.workspace.onDidRenameFiles(event => {
      for (const item of event.files) { this.changed(item.oldUri, true); this.changed(item.newUri, true); }
    }), vscode.workspace.onDidDeleteFiles(event => {
      for (const uri of event.files) { this.changed(uri, true); }
    }));
    for (const folder of vscode.workspace.workspaceFolders ?? []) { this.add(folder); }
    this.heartbeat = setInterval(() => {
      for (const state of this.states.values()) {
        void this.refresh(state).then(() => this.flush(state)).catch(error => this.report(state, error));
      }
    }, heartbeatMs);
    this.heartbeat.unref();
  }

  private allowed(folder: vscode.WorkspaceFolder): boolean {
    return !this.disposed && !this.paused && vscode.workspace.isTrusted && !vscode.env.remoteName && folder.uri.scheme === "file";
  }

  private add(folder: vscode.WorkspaceFolder): void {
    if (!this.allowed(folder) || this.states.has(folder.uri.toString())) { return; }
    const state: State = { folder, watcherId: randomUUID(), subscriptions: [], sourceSubscriptions: [],
      pending: new Map(), revision: 0, refreshRevision: 0, sequence: 0,
      enabled: false, closed: false, started: false, autoStart: true };
    this.states.set(folder.uri.toString(), state);
    for (const filename of [".tokenwise/backend-link.json", ".agents/tokenwise.json"]) {
      const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(folder, filename));
      const refresh = () => { void this.refresh(state); };
      state.subscriptions.push(watcher, watcher.onDidCreate(refresh), watcher.onDidChange(refresh), watcher.onDidDelete(refresh));
    }
    void this.refresh(state);
  }

  private async refresh(state: State): Promise<void> {
    const revision = ++state.refreshRevision;
    if (!this.allowed(state.folder) || state.closed) { this.deactivate(state); return; }
    try {
      const root = state.folder.uri.fsPath;
      const link = JSON.parse((await fs.readFile(path.join(root, ".tokenwise/backend-link.json"), "utf8")).replace(/^\uFEFF/, ""));
      const expected = path.join(localStoragePath(this.context), "backend/installation.json");
      const samePath = (a: string, b: string) => process.platform === "win32"
        ? path.resolve(a).toLowerCase() === path.resolve(b).toLowerCase() : path.resolve(a) === path.resolve(b);
      if (revision !== state.refreshRevision) { return; }
      if (link.schema_version !== 1 || typeof link.registration_path !== "string" || !path.isAbsolute(link.registration_path)
        || !samePath(link.registration_path, expected)) {
        this.deactivate(state); return;
      }
      const bytes = await fs.readFile(path.join(root, ".agents/tokenwise.json"), "utf8").catch((error: NodeJS.ErrnoException) => {
        if (error.code !== "ENOENT") { throw error; } return "{}";
      });
      const settings = JSON.parse(bytes.replace(/^\uFEFF/, ""));
      if (!settings || typeof settings !== "object" || Array.isArray(settings)
        || (settings.enabled !== undefined && typeof settings.enabled !== "boolean")
        || (settings.auto_start_backend !== undefined && typeof settings.auto_start_backend !== "boolean")) { throw new Error("Invalid TokenWise workspace configuration."); }
      if (revision !== state.refreshRevision) { return; }
      if (!this.allowed(state.folder) || state.closed || settings.enabled === false) { this.deactivate(state); return; }
      state.autoStart = settings.auto_start_backend !== false;
      state.enabled = true;
      if (!state.source) {
        state.source = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(state.folder, pythonPattern));
        const changed = (uri: vscode.Uri) => this.changed(uri);
        state.sourceSubscriptions.push(state.source.onDidCreate(changed), state.source.onDidChange(changed), state.source.onDidDelete(changed));
      }
      if (!state.started) { this.schedule(state); }
    } catch (error) {
      if (revision !== state.refreshRevision) { return; }
      this.deactivate(state);
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") { this.report(state, error); }
    }
  }

  private changed(uri: vscode.Uri, directory = false): void {
    if (uri.scheme !== "file") { return; }
    for (const state of this.states.values()) {
      if (!state.enabled || !this.allowed(state.folder) || state.closed) { continue; }
      const relative = path.relative(state.folder.uri.fsPath, uri.fsPath);
      if (!relative || path.isAbsolute(relative) || relative === ".." || relative.startsWith(`..${path.sep}`)) { continue; }
      const parts = relative.split(path.sep);
      if (parts.some(part => excluded.has(part)) || (!directory && path.extname(relative).toLowerCase() !== ".py")) { continue; }
      state.pending.set(parts.join("/"), ++state.revision);
      this.schedule(state);
    }
  }

  private schedule(state: State): void {
    if (state.timer) { clearTimeout(state.timer); }
    state.timer = setTimeout(() => {
      state.timer = undefined;
      void this.flush(state).catch(error => this.report(state, error));
    }, this.debounceMs);
    state.timer.unref();
  }

  private report(state: State, error: unknown): void {
    const text = String(error);
    if (!this.disposed && !state.closed && state.error !== text) {
      this.output.appendLine(`${state.folder.name}: ${text}`);
      state.error = text;
    }
  }

  private async post(state: State, action: Action, paths: string[] = []): Promise<void> {
    if (!state.url) { return; }
    const controller = new AbortController();
    state.controller = controller;
    const timer = setTimeout(() => controller.abort(), 30000);
    try {
      const response = await fetch(`${state.url}/index-workspace`, { method: "POST", signal: controller.signal,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace_root: state.folder.uri.fsPath, watcher_id: state.watcherId, sequence: ++state.sequence, action, paths }) });
      if (!response.ok) {
        throw new Error(response.status === 404 ? "Backend lacks background indexing; update the backend and restart it. Context retrieval can still continue."
          : `Index synchronization failed (${response.status}).`);
      }
      const result = await response.json() as { indexed_files: number; repository_fingerprint: string };
      if (!Number.isInteger(result.indexed_files) || result.indexed_files < 0
        || typeof result.repository_fingerprint !== "string" || (action !== "stop" && !/^[a-f0-9]{64}$/.test(result.repository_fingerprint))) {
        throw new Error("Invalid backend index response.");
      }
      if (action !== "stop" && !this.disposed && !state.closed && state.fingerprint !== result.repository_fingerprint) {
        this.output.appendLine(`${state.folder.name}: ${result.indexed_files} Python files indexed (${result.repository_fingerprint.slice(0, 12)}).`);
        state.fingerprint = result.repository_fingerprint;
      }
    } finally { clearTimeout(timer); if (state.controller === controller) { state.controller = undefined; } }
  }

  private flush(state: State): Promise<void> {
    if (!state.enabled || !this.allowed(state.folder) || state.closed) { return Promise.resolve(); }
    if (state.flight) { return state.flight; }
    let succeeded = false;
    state.flight = (async () => {
      if (!state.url) {
        const endpoint = await this.endpoint(state.autoStart);
        if (!endpoint || !state.enabled || !this.allowed(state.folder) || state.closed) { return; }
        const url = new URL(endpoint);
        if (url.protocol !== "http:" || !["127.0.0.1", "localhost", "[::1]"].includes(url.hostname)
          || url.username || url.password || url.pathname !== "/" || url.search || url.hash) { throw new Error("Index synchronization requires the registered local backend."); }
        state.url = url.origin;
      }
      const batch = state.started ? [...state.pending].slice(0, 512) : [];
      const paths = batch.map(([name]) => name);
      await this.post(state, !state.started ? "start" : paths.length ? "update" : "reconcile", paths);
      state.started = true;
      for (const [name, revision] of batch) { if (state.pending.get(name) === revision) { state.pending.delete(name); } }
      state.error = undefined;
      succeeded = true;
    })().catch(error => {
      this.release(state); state.started = false;
      throw error;
    }).finally(() => {
      state.flight = undefined;
      if (!state.enabled || state.closed || !this.allowed(state.folder)) { this.release(state); }
      else if (succeeded && state.pending.size) { this.schedule(state); }
    });
    return state.flight;
  }

  private release(state: State): void {
    if (state.url) {
      const url = state.url;
      state.url = undefined;
      const release = { ...state, url };
      // Reserve the release sequence before a retry can begin a newer session.
      state.sequence++;
      void this.post(release, "stop").catch(() => undefined);
    }
  }

  private deactivate(state: State): void {
    state.enabled = false; state.started = false;
    if (state.timer) { clearTimeout(state.timer); state.timer = undefined; }
    state.controller?.abort();
    state.pending.clear();
    state.source?.dispose(); state.source = undefined;
    for (const subscription of state.sourceSubscriptions.splice(0)) { subscription.dispose(); }
    if (!state.flight) { this.release(state); }
  }

  private remove(folder: vscode.WorkspaceFolder): void {
    const state = this.states.get(folder.uri.toString());
    if (!state) { return; }
    state.closed = true;
    this.deactivate(state);
    for (const subscription of state.subscriptions) { subscription.dispose(); }
    this.states.delete(folder.uri.toString());
  }

  public configured(folder: vscode.WorkspaceFolder): void {
    this.paused = false;
    this.add(folder);
    const state = this.states.get(folder.uri.toString());
    if (state) { void this.refresh(state); }
  }

  public pause(): void {
    this.paused = true;
    for (const state of this.states.values()) { this.deactivate(state); }
  }

  public backendChanged(): void {
    for (const state of this.states.values()) {
      const flight = state.flight;
      this.deactivate(state);
      state.fingerprint = undefined;
      void Promise.resolve(flight).catch(() => undefined).then(() => this.refresh(state));
    }
  }

  public dispose(): void {
    this.disposed = true;
    clearInterval(this.heartbeat);
    for (const state of [...this.states.values()]) { this.remove(state.folder); }
    for (const subscription of this.subscriptions) { subscription.dispose(); }
    this.output.dispose();
  }
}
