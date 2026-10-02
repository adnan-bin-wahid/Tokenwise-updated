const assert = require("node:assert/strict");
const { test, beforeEach } = require("node:test");
const Module = require("node:module");

const uri = (fsPath, scheme = "file", authority = "") => ({
  fsPath, scheme, authority, toString: () => `${scheme}:${fsPath}`,
  with: (changes) => uri(fsPath, changes.scheme ?? scheme, changes.authority ?? authority),
});
const folder = (name) => ({ name, uri: uri(`C:\\Repositories\\${name}`) });
const context = { extensionUri: uri("C:\\Extensions\\tokenwise-vscode"), globalStorageUri: uri("C:\\Storage\\TokenWise") };
let messages, calls, saved, configured, selectedFolder, approval, pickBackend, registered;
const setupStub = {
  validateBackendInstallation: async (root) => {
    if (root === "C:\\Backend") { return root; }
    throw new Error("missing model");
  },
  discoverRegisteredBackend: async () => registered,
  registerBackend: async (...args) => { calls.push(["register", ...args]); return { registrationPath: "registration.json" }; },
  configureAutomaticContext: async (...args) => { calls.push(["configure", ...args]); },
};
const vscode = {
  env: { remoteName: undefined },
  ConfigurationTarget: { Global: 1 }, ProgressLocation: { Notification: 15 },
  workspace: {
    isTrusted: true, workspaceFolders: [],
    getConfiguration: () => ({
      get: () => saved,
      update: async (...args) => calls.push(["setting", ...args]),
    }),
  },
  window: {
    showWarningMessage: async (text) => { messages.push(text); },
    showErrorMessage: async (text) => { messages.push(text); },
    showInformationMessage: async (text, options) => { messages.push(text); return options?.modal ? approval : undefined; },
    showQuickPick: async (items) => selectedFolder === undefined ? undefined : items[selectedFolder],
    showOpenDialog: async () => pickBackend ? [uri(pickBackend)] : undefined,
    withProgress: async (_, action) => action(),
  },
};
const originalLoad = Module._load;
Module._load = function (request, ...args) {
  if (request === "vscode") { return vscode; }
  if (request === "../services/automaticSetup") { return setupStub; }
  return originalLoad.call(this, request, ...args);
};
const { createEnableAutomaticContextCommand } = require("../dist/commands/enableAutomaticContext.js");
Module._load = originalLoad;
const run = () => createEnableAutomaticContextCommand(context, (item) => configured.push(item))();
const windowsTest = (name, action) => test(name, { skip: process.platform !== "win32" }, action);

beforeEach(() => {
  messages = []; calls = []; configured = []; saved = ""; registered = undefined;
  approval = "Enable"; pickBackend = "C:\\Backend"; selectedFolder = undefined;
  vscode.workspace.isTrusted = true; vscode.workspace.workspaceFolders = [folder("Python App")];
  vscode.env.remoteName = undefined;
  context.globalStorageUri = uri("C:\\Storage\\TokenWise");
});

test("untrusted workspaces never install scripts or register a backend", async () => {
  vscode.workspace.isTrusted = false;
  await run();
  assert.match(messages[0], /Trust this workspace/);
  assert.deepEqual(calls, []);
});

windowsTest("asks for a folder when no repository is open", async () => {
  vscode.workspace.workspaceFolders = [];
  await run();
  assert.match(messages[0], /Open a Python repository/);
  assert.deepEqual(calls, []);
});

windowsTest("remote workspaces are rejected before configuration", async () => {
  vscode.workspace.workspaceFolders[0].uri.scheme = "vscode-remote";
  await run();
  assert.match(messages[0], /local folders only/);
  assert.deepEqual(calls, []);
});

windowsTest("local vscode-userdata storage is accepted in Antigravity development hosts", async () => {
  context.globalStorageUri = uri("C:\\Storage\\TokenWise", "vscode-userdata");
  await run();
  assert.equal(calls[0][0], "register");
  assert.equal(calls[0][2], "C:\\Storage\\TokenWise");
  assert.equal(configured.length, 1);
  assert.ok(!messages.some((message) => message.includes("remote or virtual")));
});

windowsTest("a remote extension host is rejected even with a file workspace URI", async () => {
  vscode.env.remoteName = "ssh-remote";
  await run();
  assert.match(messages[0], /remote: ssh-remote/);
  assert.deepEqual(calls, []);
});

windowsTest("unknown or remote user-storage providers are not treated as native paths", async () => {
  for (const storage of [uri("C:\\Storage\\TokenWise", "memfs"), uri("C:\\Storage\\TokenWise", "vscode-userdata", "ssh-host")]) {
    context.globalStorageUri = storage;
    await run();
    assert.match(messages.at(-1), /Unsupported extension storage URI/);
    assert.deepEqual(calls, []);
  }
});

windowsTest("cancelling backend selection or confirmation writes nothing", async () => {
  pickBackend = undefined;
  await run();
  assert.deepEqual(calls, []);
  pickBackend = "C:\\Backend";
  approval = undefined;
  await run();
  assert.deepEqual(calls, []);
});

windowsTest("incomplete installations fail before workspace writes", async () => {
  pickBackend = "C:\\Incomplete";
  await run();
  assert.match(messages.at(-1), /setup failed: missing model/);
  assert.deepEqual(calls, []);
});

windowsTest("multi-root setup targets the selected repository and saves a user setting", async () => {
  vscode.workspace.workspaceFolders = [folder("First"), folder("Second")];
  selectedFolder = 1;
  await run();
  assert.equal(calls[0][0], "register");
  assert.equal(calls[0][2], context.globalStorageUri.fsPath);
  assert.equal(calls[1][1], vscode.workspace.workspaceFolders[1].uri.fsPath);
  assert.deepEqual(calls[2], ["setting", "backendInstallationPath", "C:\\Backend", 1]);
  assert.deepEqual(configured, [vscode.workspace.workspaceFolders[1]]);
  assert.match(messages.at(-1), /new Antigravity chat/);
});

windowsTest("valid shared registration works without another backend picker", async () => {
  registered = "C:\\Backend";
  pickBackend = undefined;
  await run();
  assert.equal(calls[0][1], "C:\\Backend");
  assert.equal(configured.length, 1);
});

windowsTest("invalid saved backend can be replaced without touching repository settings", async () => {
  saved = "C:\\Moved";
  await run();
  assert.match(messages[0], /saved TokenWise backend is unavailable/);
  assert.equal(calls[0][1], "C:\\Backend");
  assert.equal(calls.at(-1).at(-1), vscode.ConfigurationTarget.Global);
});
