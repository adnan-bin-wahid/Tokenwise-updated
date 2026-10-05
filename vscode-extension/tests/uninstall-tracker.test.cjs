const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");

function harness(options = {}) {
  const calls = [];
  const context = { extensionUri: { fsPath: "extension" }, subscriptions: [] };
  const plan = { marker: "plan" };
  const result = options.result ?? { removed: [], preserved: [], warnings: [] };
  const api = {
    env: { remoteName: options.remote },
    workspace: { isTrusted: options.trusted ?? true, workspaceFolders: options.folders },
    ProgressLocation: { Notification: 15 },
    window: {
      showWarningMessage: async (...args) => { calls.push(["warning", ...args]); return options.approval; },
      showInformationMessage: async text => calls.push(["info", text]),
      showErrorMessage: async text => calls.push(["error", text]),
      withProgress: async (settings, work) => { calls.push(["progress", settings]); return work(); },
      createOutputChannel: name => ({
        appendLine: text => calls.push(["report", name, text]),
        show: preserveFocus => calls.push(["show", preserveFocus]),
      }),
    },
  };
  const mocks = {
    vscode: api,
    "./extensionPaths": { localStoragePath: () => "storage" },
    "./cleanupRegistry": {
      registerLifecycle: async (...args) => calls.push(["register", ...args]),
      adoptOpenWorkspace: async (...args) => calls.push(["adopt", ...args]),
      buildCleanupPlan: async root => { calls.push(["plan", root]); return plan; },
    },
    "./uninstallCleanup": {
      runCleanup: async value => {
        assert.equal(value, plan);
        calls.push(["cleanup"]);
        if (options.failure) { throw new Error(options.failure); }
        return result;
      },
    },
  };
  const filename = require.resolve("../dist/services/uninstallTracker");
  delete require.cache[filename];
  const load = Module._load;
  Module._load = function (request, ...args) { return mocks[request] ?? load.call(this, request, ...args); };
  let tracker;
  try { tracker = new (require(filename).UninstallTracker)(context); }
  finally { Module._load = load; delete require.cache[filename]; }
  return { calls, context, tracker, cancel: () => calls.push(["cancel"]) };
}

test("cleanup tracking and removal never operate in untrusted or remote windows", async () => {
  for (const options of [{ trusted: false }, { remote: "ssh-remote" }]) {
    const f = harness(options);
    await f.tracker.prepare();
    assert.deepEqual(f.calls, []);
    await f.tracker.removeAll(f.cancel);
    assert.equal(f.calls.length, 1);
    assert.equal(f.calls[0][0], "warning");
  }
});

test("tracking registers storage and adopts only local open repositories", async () => {
  const f = harness({ folders: [
    { uri: { scheme: "file", fsPath: "local-repository" } },
    { uri: { scheme: "vscode-remote", fsPath: "remote-repository" } },
  ] });
  await f.tracker.prepare();
  assert.deepEqual(f.calls, [["register", "storage", "extension"], ["adopt", "storage", "local-repository"]]);
});

test("closing the cleanup confirmation does not cancel setup or remove data", async () => {
  const f = harness();
  await f.tracker.removeAll(f.cancel);
  assert.equal(f.calls.length, 1);
  assert.equal(f.calls[0][2].modal, true);
});

test("cleanup requires the explicit destructive confirmation action", async () => {
  const f = harness({ approval: "Cancel" });
  await f.tracker.removeAll(f.cancel);
  assert.equal(f.calls.length, 1);
});

test("confirmed cleanup cancels setup, reports progress and announces success", async () => {
  const f = harness({ approval: "Remove Data" });
  await f.tracker.removeAll(f.cancel);
  assert.deepEqual(f.calls.map(call => call[0]), ["warning", "cancel", "progress", "plan", "cleanup", "info"]);
  assert.equal(f.calls[2][1].cancellable, false);
  assert.ok(f.calls.at(-1)[1].includes("local data removed"));
});

test("partial cleanup exposes the preserved-file report without a false success message", async () => {
  const result = { removed: [], preserved: ["customized-rule"], warnings: ["unavailable-drive"] };
  const f = harness({ approval: "Remove Data", result });
  await f.tracker.removeAll(f.cancel);
  const report = f.calls.find(call => call[0] === "report");
  assert.equal(report[1], "TokenWise Cleanup");
  assert.deepEqual(JSON.parse(report[2]), result);
  assert.equal(f.context.subscriptions.length, 1);
  assert.ok(!f.calls.some(call => call[0] === "info"));
  assert.deepEqual(f.calls.find(call => call[0] === "show"), ["show", true]);
});

test("cleanup failure is reported as an error without claiming success", async () => {
  const f = harness({ approval: "Remove Data", failure: "fixture failure" });
  await f.tracker.removeAll(f.cancel);
  assert.ok(f.calls.at(-1)[1].includes("fixture failure"));
  assert.equal(f.calls.at(-1)[0], "error");
  assert.ok(!f.calls.some(call => call[0] === "info"));
});
