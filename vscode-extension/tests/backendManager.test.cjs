const assert = require("node:assert/strict");
const { test, beforeEach } = require("node:test");
const Module = require("node:module");
const path = require("node:path");
const os = require("node:os");
const storageRoot = path.resolve(os.tmpdir(), "TokenWise Storage");
const managedRoot = path.resolve(os.tmpdir(), "TokenWise Managed");
const extensionRoot = path.resolve(os.tmpdir(), "TokenWise Extension");
const uri = (fsPath, scheme = "file") => ({ fsPath, scheme, authority: "", with: () => uri(fsPath), toString: () => `${scheme}:${fsPath}` });
let calls, messages, settings, registered, approval, pythonError, offline, welcomed;
const context = {
  globalStorageUri: uri(storageRoot, "vscode-userdata"), extensionUri: uri(extensionRoot),
  extension: { packageJSON: { version: "0.4.0" } },
  globalState: { get: () => welcomed, update: async (_, value) => { welcomed = value; } },
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
    showInformationMessage: async (message, options) => { messages.push(message); return options?.modal ? approval : undefined; },
    showWarningMessage: async (message) => { messages.push(message); },
    showErrorMessage: async (message) => { messages.push(message); },
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
  return load.call(this, request, ...args);
};
const { BackendManager } = require("../dist/services/backendManager.js");
Module._load = load;
beforeEach(() => {
  calls = []; messages = []; settings = {}; registered = undefined; approval = "Install Backend";
  pythonError = false; offline = false; welcomed = false;
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
