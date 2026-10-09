const assert = require("node:assert/strict");
const { test, beforeEach } = require("node:test");
const Module = require("node:module");
const path = require("node:path");
const os = require("node:os");
const fs = require("node:fs/promises");
const { SetupError, setupProgressMessage } = require("../dist/services/managedBackend.js");
const storageRoot = path.resolve(os.tmpdir(), "TokenWise Storage");
const managedRoot = path.resolve(os.tmpdir(), "TokenWise Managed");
const extensionRoot = path.resolve(os.tmpdir(), "TokenWise Extension");
const uri = (fsPath, scheme = "file") => ({ fsPath, scheme, authority: "", with: () => uri(fsPath), toString: () => `${scheme}:${fsPath}` });
let calls, messages, settings, registered, approval, pythonError, offline, welcomed, errors, information, state, cleanupProfiles;
const context = {
  globalStorageUri: uri(storageRoot, "vscode-userdata"), extensionUri: uri(extensionRoot),
  extension: { packageJSON: { version: "0.4.0" } },
  globalState: { get: key => key === "welcomeShown" ? welcomed : state.get(key), update: async (key, value) => { if (key === "welcomeShown") { welcomed = value; } else { state.set(key, value); } } },
};
const vscode = {
  env: { remoteName: undefined, openExternal: async (value) => calls.push(["external", value]) },
  Uri: { parse: (value) => value, joinPath: (root, ...parts) => uri([root.fsPath, ...parts].join("/")) },
  ConfigurationTarget: { Global: 1 }, ProgressLocation: { Notification: 15 },
  workspace: { isTrusted: true, workspaceFolders: [], getConfiguration: () => ({
    get: (key, fallback) => settings[key] ?? fallback,
    update: async (key, value, target) => { settings[key] = value; calls.push(["setting", key, value, target]); },
  }) },
  commands: { executeCommand: async (...args) => calls.push(["command", ...args]) },
  window: {
    createOutputChannel: () => ({ appendLine: (line) => calls.push(["log", line]), show() {}, dispose() {} }),
    showInformationMessage: async (message, options) => { messages.push(message); return options?.modal ? approval : information.shift(); },
    showWarningMessage: async (message) => { messages.push(message); },
    showErrorMessage: async (message) => { messages.push(message); return errors.shift(); },
    withProgress: async (_, action) => action({ report() {} }, { onCancellationRequested: () => ({ dispose() {} }) }),
  },
};
const automatic = {
  discoverRegisteredBackend: async () => registered,
  validateBackendInstallation: async (root) => root,
  registerBackend: async (root, storage) => {
    calls.push(["register", root, storage]);
    return { registration: { project_root: root, python_path: path.join(managedRoot, ".venv/Scripts/python.exe"), runtime_dir: path.join(storageRoot, "backend/runtime") } };
  },
};
const managed = {
  SetupError, setupProgressMessage,
  findPython312: async () => { if (pythonError) { throw new Error("64-bit Python 3.12 was not found"); } return { executable: "python", args: [] }; },
  installManagedBackend: async (...args) => { calls.push(["install", ...args]); return managedRoot; },
  runSetupProcess: async (_, args, options) => {
    calls.push(["process", args, options.env]);
    if (offline && !args.includes("--start")) { throw new Error("backend offline"); }
    return JSON.stringify({ backend_url: "http://127.0.0.1:8005", health: { service: "tokenwise", model_loaded: true, device: "cpu" } });
  },
};
const load = Module._load;
Module._load = function (request, ...args) {
  if (request === "vscode") { return vscode; }
  if (request === "./automaticSetup") { return automatic; }
  if (request === "./managedBackend") { return managed; }
  if (request === "./cleanupRegistry") { return { buildCleanupPlan: async () => ({ profiles: cleanupProfiles }) }; }
  if (request === "./cleanupProcesses") { return { stopOwnedProcesses: async profile => calls.push(["stop-owned", profile]) }; }
  return load.call(this, request, ...args);
};
const { BackendManager } = require("../dist/services/backendManager.js");
Module._load = load;
beforeEach(() => {
  calls = []; messages = []; settings = {}; registered = undefined; approval = "Install Backend";
  pythonError = false; offline = false; welcomed = false;
  errors = []; information = []; state = new Map(); cleanupProfiles = [];
  vscode.workspace.isTrusted = true; vscode.env.remoteName = undefined;
});

test("setup requires trusted local execution", async () => {
  const manager = new BackendManager(context);
  vscode.workspace.isTrusted = false;
  assert.equal(await manager.setup(), undefined);
  assert.ok(!calls.some((call) => call[0] === "install"));
  vscode.workspace.isTrusted = true;
  vscode.env.remoteName = "ssh-remote";
  await manager.start();
  assert.ok(!calls.some((call) => call[0] === "process"));
  manager.dispose();
});

test("declining download consent starts no installer", async () => {
  const manager = new BackendManager(context);
  approval = undefined;
  assert.equal(await manager.setup(), undefined);
  assert.deepEqual(calls, []);
  manager.dispose();
});

test("concurrent setup confirmations cannot start duplicate installers", async t => {
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  const original = managed.installManagedBackend;
  let installers = 0;
  t.mock.method(managed, "installManagedBackend", async (...args) => { installers++; await gate; return original(...args); });
  const manager = new BackendManager(context);
  t.after(() => { release(); manager.dispose(); });
  const first = manager.setup(), second = manager.setup();
  for (let tick = 0; tick < 10 && !installers; tick++) { await Promise.resolve(); }
  assert.equal(installers, 1);
  assert.equal(await second, undefined);
  release();
  assert.equal(await first, managedRoot);
});

test("managed setup registers a completed backend and saves application settings", async () => {
  const manager = new BackendManager(context);
  assert.equal(await manager.setup(), managedRoot);
  assert.equal(calls.find((call) => call[0] === "install")[4], "0.4.0");
  assert.deepEqual(calls.find((call) => call[0] === "setting"), ["setting", "backendInstallationPath", managedRoot, 1]);
  manager.dispose();
});

test("missing Python is visible and never claims successful installation", async () => {
  const manager = new BackendManager(context);
  pythonError = true;
  assert.equal(await manager.setup(), undefined);
  assert.match(messages.at(-1), /Python 3.12/);
  assert.ok(!calls.some((call) => call[0] === "register"));
  manager.dispose();
});

test("a failed setup step can be retried within the same consented setup", async t => {
  let attempts = 0, installed = 0;
  const original = managed.installManagedBackend;
  t.mock.method(managed, "installManagedBackend", async (...args) => {
    attempts++;
    if (attempts === 1) { throw new SetupError("Network disconnected", "model", "Reconnect and retry", false, 5); }
    return original(...args);
  });
  errors = ["Retry Failed Step"];
  const manager = new BackendManager(context, undefined, () => { installed++; });
  assert.equal(await manager.setup(), managedRoot);
  assert.equal(attempts, 2); assert.equal(installed, 1);
  assert.equal(messages.filter(text => text === "Install the TokenWise backend on this computer?").length, 1);
  assert.ok(messages.some(text => text.includes("step 5/7") && text.includes("Reconnect and retry")));
  manager.dispose();
});

test("a failed download leaves the previous backend running and registered", async t => {
  cleanupProfiles = [{ storageRoot, backend: { managed: true, pid: 42 } }];
  t.mock.method(managed, "installManagedBackend", async () => { throw new SetupError("offline", "model", "Retry later"); });
  const manager = new BackendManager(context);
  assert.equal(await manager.setup(), undefined);
  assert.ok(!calls.some(call => ["stop-owned", "register", "setting"].includes(call[0])));
  manager.dispose();
});

test("successful upgrades stop only this profile's verified managed backend before registering the replacement", async () => {
  cleanupProfiles = [
    { storageRoot, backend: { installation: "old", managed: true, pid: 42, port: 8001 } },
    { storageRoot: storageRoot + "-other", backend: { installation: "other", managed: true, pid: 43 } },
  ];
  const manager = new BackendManager(context);
  assert.equal(await manager.setup(), managedRoot);
  const stops = calls.filter(call => call[0] === "stop-owned");
  assert.equal(stops.length, 1); assert.equal(stops[0][1].backend.pid, 42);
  assert.ok(calls.findIndex(call => call[0] === "stop-owned") < calls.findIndex(call => call[0] === "register"));
  manager.dispose();
});

test("setup does not stop an existing checkout backend", async () => {
  cleanupProfiles = [{ storageRoot, backend: { installation: managedRoot, managed: false, pid: 42, port: 8001 } }];
  const manager = new BackendManager(context);
  assert.equal(await manager.setup(), managedRoot);
  assert.ok(!calls.some(call => call[0] === "stop-owned"));
  manager.dispose();
});

test("an older managed backend prompts for an update once per extension version", async t => {
  registered = managedRoot; welcomed = true;
  t.mock.method(fs, "readFile", async () => JSON.stringify({ schema_version: 1, version: "0.3.0" }));
  const manager = new BackendManager(context);
  await manager.welcome(); await manager.welcome();
  assert.equal(messages.filter(text => text.includes("Update the backend")).length, 1);
  assert.ok(!calls.some(call => call[0] === "install"));
  manager.dispose();
});

test("a newer managed backend is not offered a downgrade", async t => {
  registered = managedRoot;
  t.mock.method(fs, "readFile", async () => JSON.stringify({ schema_version: 1, version: "9.0.0" }));
  const manager = new BackendManager(context);
  await manager.welcome();
  assert.equal(messages.length, 0);
  manager.dispose();
});

test("start uses the shared runtime and actual server port rather than port 8000", async () => {
  const manager = new BackendManager(context);
  registered = managedRoot;
  await manager.start();
  const processCall = calls.find((call) => call[0] === "process");
  assert.ok(processCall[1].includes("--start"));
  assert.equal(processCall[2].TOKENWISE_RUNTIME_DIR, path.join(storageRoot, "backend/runtime"));
  assert.equal(settings.apiUrl, "http://127.0.0.1:8005");
  manager.dispose();
});

test("offline diagnostics report the problem without silently spawning a server", async () => {
  const manager = new BackendManager(context);
  registered = managedRoot; offline = true;
  await manager.diagnostics();
  assert.match(messages.at(-1), /backend offline/);
  assert.ok(!calls.find((call) => call[0] === "process")[1].includes("--start"));
  assert.ok(calls.some((call) => call[0] === "log" && call[1].includes("TokenWise user storage")));
  manager.dispose();
});

test("setup guide opens the bundled markdown instead of relying on a checkout", async () => {
  const manager = new BackendManager(context);
  await manager.guide();
  const call = calls.find((item) => item[0] === "command");
  assert.equal(call[1], "markdown.showPreview");
  assert.match(call[2].fsPath, /resources\/user-guide.md$/);
  manager.dispose();
});

test("demonstration guide opens the bundled teacher walkthrough without a checkout", async () => {
  const manager = new BackendManager(context);
  await manager.demonstrationGuide();
  const call = calls.find((item) => item[0] === "command");
  assert.equal(call[1], "markdown.showPreview");
  assert.match(call[2].fsPath, /resources\/demonstation.md$/);
  assert.ok(!calls.some((item) => ["install", "process", "setting"].includes(item[0])));
  manager.dispose();
});

test("background indexing never installs missing backends or changes user settings", async () => {
  const manager = new BackendManager(context);
  assert.equal(await manager.backgroundUrl(true), undefined);
  assert.equal(calls.length, 0);
  registered = managedRoot;
  assert.equal(await manager.backgroundUrl(true), "http://127.0.0.1:8005");
  assert.ok(calls.find(call => call[0] === "process")[1].includes("--start"));
  assert.ok(!calls.some(call => ["install", "setting"].includes(call[0])));
  assert.equal(messages.length, 0);
  manager.dispose();
});

test("validation guide opens the bundled comparison protocol without setup or a checkout", async () => {
  const manager = new BackendManager(context);
  await manager.validationGuide();
  const call = calls.find(item => item[0] === "command");
  assert.equal(call[1], "markdown.showPreview");
  assert.match(call[2].fsPath, /resources\/validation.md$/);
  assert.ok(!calls.some(item => ["install", "process", "setting"].includes(item[0])));
  manager.dispose();
});

test("background indexing honors disabled automatic startup", async () => {
  const manager = new BackendManager(context);
  registered = managedRoot;
  assert.equal(await manager.backgroundUrl(false), "http://127.0.0.1:8005");
  assert.ok(!calls.find(call => call[0] === "process")[1].includes("--start"));
  manager.dispose();
});

test("multiple workspace warmups share an in-flight backend startup", async () => {
  const manager = new BackendManager(context);
  registered = managedRoot;
  const urls = await Promise.all([manager.backgroundUrl(true), manager.backgroundUrl(true)]);
  assert.deepEqual(urls, ["http://127.0.0.1:8005", "http://127.0.0.1:8005"]);
  assert.equal(calls.filter(call => call[0] === "process").length, 1);
  manager.dispose();
});

test("background warmup is disabled for untrusted, remote, and disposed managers", async () => {
  const manager = new BackendManager(context);
  registered = managedRoot;
  vscode.workspace.isTrusted = false;
  assert.equal(await manager.backgroundUrl(true), undefined);
  vscode.workspace.isTrusted = true;
  vscode.env.remoteName = "ssh-remote";
  assert.equal(await manager.backgroundUrl(true), undefined);
  vscode.env.remoteName = undefined;
  manager.dispose();
  assert.equal(await manager.backgroundUrl(true), undefined);
  assert.equal(calls.length, 0);
});

test("cleanup cancellation prevents a warmup delayed during backend discovery", async t => {
  const original = automatic.discoverRegisteredBackend;
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  automatic.discoverRegisteredBackend = async () => { await gate; return managedRoot; };
  const manager = new BackendManager(context);
  t.after(() => { release(); automatic.discoverRegisteredBackend = original; manager.dispose(); });
  const warming = manager.backgroundUrl(true);
  await manager.cancelSetup();
  release();
  assert.equal(await warming, undefined);
  assert.equal(calls.length, 0);
});

test("cleanup waits for in-flight registration and aborts before spawning a backend", async t => {
  const original = automatic.registerBackend;
  let entered, release;
  const started = new Promise(resolve => { entered = resolve; });
  const gate = new Promise(resolve => { release = resolve; });
  automatic.registerBackend = async (...args) => { entered(); await gate; return original(...args); };
  registered = managedRoot;
  const manager = new BackendManager(context);
  t.after(() => { release(); automatic.registerBackend = original; manager.dispose(); });
  const warming = manager.backgroundUrl(true).catch(error => error);
  await started;
  let cancelled = false;
  const stopping = manager.cancelSetup().then(() => { cancelled = true; });
  await Promise.resolve();
  assert.equal(cancelled, false);
  release();
  await stopping;
  assert.equal((await warming).name, "AbortError");
  assert.ok(!calls.some(call => call[0] === "process"));
});
