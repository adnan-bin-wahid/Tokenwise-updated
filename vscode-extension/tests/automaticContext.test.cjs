const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");

const originalLoad = Module._load;
const watcherCallbacks = [];
let currentActivity;
const outputLines = [];
const vscodeStub = {
  window: { createOutputChannel: () => ({ appendLine: (line) => outputLines.push(line), show() {}, dispose() {} }) },
  commands: { registerCommand: () => ({ dispose() {} }) },
  Uri: { joinPath: (...parts) => parts.join("/") },
  RelativePattern: class {},
  workspace: {
    workspaceFolders: [],
    onDidChangeWorkspaceFolders: () => ({ dispose() {} }),
    fs: { readFile: async () => Buffer.from(JSON.stringify(currentActivity)), stat: async () => ({}) },
    getConfiguration: () => ({ get: () => true }),
    createFileSystemWatcher: () => ({
      onDidCreate: (handler) => { watcherCallbacks.push(handler); return { dispose() {} }; },
      onDidChange: (handler) => { watcherCallbacks.push(handler); return { dispose() {} }; },
      dispose() {},
    }),
  },
};
Module._load = function (request, ...args) {
  return request === "vscode" ? vscodeStub : originalLoad.call(this, request, ...args);
};
const { parseAutomaticActivity, AutomaticContextMonitor } = require("../dist/services/automaticContext.js");
Module._load = originalLoad;

const ready = {
  event_id: "new-prompt", timestamp: "2026-10-02T00:00:00Z", status: "ready",
  result: {
    structured_goal: {}, unified_prompt: "[TokenWise automatic context]", pruned_tokens: 100, original_tokens: 500,
    files: [{ file_path: "services/payment_service.py", relation: "prompt-selected file", tier: 1, score: 0.5, original_tokens: 500, pruned_tokens: 100 }],
  },
};

test("accepts a complete hook activity record", () => {
  assert.equal(parseAutomaticActivity(ready).result.files[0].file_path, "services/payment_service.py");
});

test("rejects incomplete activity instead of crashing the result view", () => {
  assert.equal(parseAutomaticActivity({ ...ready, result: {} }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, pruned_tokens: "100" } }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, files: [{ file_path: "payment.py" }] } }), undefined);
  assert.equal(parseAutomaticActivity(null), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, files: [null] } }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, verification: "true" }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, transport: 42 }), undefined);
});

test("accepts failure records so startup problems remain visible", () => {
  assert.equal(parseAutomaticActivity({ ...ready, status: "error", result: undefined, error: "offline" }).error, "offline");
});

test("a new hook result updates the status and opens the panel without stealing focus", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "demo" } }];
  currentActivity = { ...ready, status: "retrieving", result: undefined };
  const status = {};
  const panels = [];
  const monitor = new AutomaticContextMonitor(status, { showWorkspaceResult: (...args) => panels.push(args) }, "extension");
  await new Promise((resolve) => setImmediate(resolve));
  assert.match(status.text, /awaiting prompt/);
  currentActivity = { ...ready, query: "Explain payment retries", elapsed_ms: 5400 };
  watcherCallbacks.at(-1)();
  await new Promise((resolve) => setTimeout(resolve, 180));
  assert.match(status.text, /1 files, 100 tokens/);
  assert.equal(panels.length, 1);
  assert.equal(panels[0][0].automatic_context.query, currentActivity.query);
  assert.equal(panels[0][2], true);
  assert.ok(outputLines.some((line) => line.includes("services/payment_service.py")));
  monitor.dispose();
});

test("loading an old result does not present it as fresh agent activity", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "demo" } }];
  currentActivity = ready;
  const status = {};
  const panels = [];
  const monitor = new AutomaticContextMonitor(status, { showWorkspaceResult: (...args) => panels.push(args) }, "extension");
  await new Promise((resolve) => setImmediate(resolve));
  assert.match(status.text, /last result/);
  assert.match(status.tooltip, /Previous context/);
  assert.equal(panels.length, 0);
  monitor.dispose();
});

test("verification reports are labeled as tests and never open a live result panel", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "demo" } }];
  currentActivity = { ...ready, event_id: "old-result" };
  const status = {};
  const panels = [];
  const monitor = new AutomaticContextMonitor(status, { showWorkspaceResult: (...args) => panels.push(args) }, "extension");
  await new Promise((resolve) => setImmediate(resolve));
  currentActivity = { ...ready, verification: true };
  watcherCallbacks.at(-1)();
  await new Promise((resolve) => setTimeout(resolve, 180));
  assert.match(status.text, /TokenWise test/);
  assert.match(status.tooltip, /not a real Antigravity/);
  assert.equal(panels.length, 0);
  monitor.dispose();
});

test("a fresh agent-command result shows its transport and opens the panel", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "demo" } }];
  currentActivity = { ...ready, event_id: "old-result" };
  const status = {};
  const panels = [];
  const monitor = new AutomaticContextMonitor(status, { showWorkspaceResult: (...args) => panels.push(args) }, "extension");
  await new Promise((resolve) => setImmediate(resolve));
  currentActivity = { ...ready, transport: "antigravity-agent-command", query: "Explain account lockout" };
  watcherCallbacks.at(-1)();
  await new Promise((resolve) => setTimeout(resolve, 180));
  assert.match(status.text, /TokenWise Auto/);
  assert.match(status.tooltip, /agent command/);
  assert.equal(panels.length, 1);
  monitor.dispose();
});
