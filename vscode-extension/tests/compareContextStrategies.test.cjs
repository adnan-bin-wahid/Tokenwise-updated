const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");

function fixture(options = {}) {
  const calls = { requests: [], shown: [], errors: [], warnings: [], carbon: 0 };
  const editor = { document: { languageId: "python", uri: { fsPath: "/demo/auth.py" },
    version: 1, isDirty: false, getText: () => options.excerpt ?? "" }, selection: {} };
  const response = { comparison: { methods: [{ id: "all_python", input_tokens: 800 },
    { id: "selected", input_tokens: 100 }, { id: "tokenwise", input_tokens: 300 }], notes: [] } };
  const vscode = { env: {}, workspace: { isTrusted: options.trusted !== false,
    getWorkspaceFolder: () => ({ uri: { scheme: "file", fsPath: "/demo" } }) },
    ProgressLocation: { Notification: 1 }, window: { activeTextEditor: editor,
      showWarningMessage: async value => calls.warnings.push(value),
      showErrorMessage: async value => calls.errors.push(value),
      showInputBox: async () => options.cancel ? undefined : " Explain lockout ",
      withProgress: async (_, action) => action() } };
  const load = Module._load;
  const filename = require.resolve("../dist/commands/compareContextStrategies.js");
  delete require.cache[filename];
  Module._load = function (name, ...args) {
    if (name === "vscode") { return vscode; }
    if (name === "../services/config") { return { getTokenWiseConfig: () => ({
      enableCarbonEstimation: options.carbon !== false, repositoryTokenBudget: 4096,
      defaultThreshold: .45, expectedOutputTokens: 256 }) }; }
    if (name === "../services/apiClient") { return { TokenWiseApiClient: class {
      async compareWorkspace(request) { calls.requests.push(request); return response; }
    } }; }
    if (name === "../services/carbonComparison") { return { estimateCarbonForInputs: async (_, __, inputs) => {
      calls.carbon++;
      assert.deepEqual(inputs, [800, 100, 300]);
      if (options.carbonFails) { throw new Error("estimator unavailable"); }
      return inputs.map(() => ({ modelFamily: "Llama", carbonIntensityGPerKwh: 475 }));
    } }; }
    return load.call(this, name, ...args);
  };
  let create;
  try { ({ createCompareContextStrategiesCommand: create } = require(filename)); }
  finally { Module._load = load; }
  return { editor, calls, response, run: create({ showWorkspaceResult: value => calls.shown.push(value) }, "extension",
    async () => { if (options.changeDuringSetup) { editor.document.version++; } return options.offline ? undefined : "http://127.0.0.1:8010"; }) };
}

test("manual baseline does not bias automatic retrieval with active-file editor hints", async () => {
  const f = fixture({ excerpt: "def authenticate(): pass" }); await f.run();
  const request = f.calls.requests[0];
  assert.equal(request.query, "Explain lockout");
  assert.equal(request.selection_file, "/demo/auth.py");
  assert.equal(request.selection_text, "def authenticate(): pass");
  assert.equal(request.active_file, undefined);
  assert.equal(request.selected_code, undefined);
  assert.deepEqual(request.diagnostics, []);
  assert.equal(f.response.comparison.carbonStatus, "ready");
  assert.equal(f.calls.shown.length, 1);
});

test("cancelled, untrusted, dirty and changed-file requests perform no retrieval", async () => {
  for (const options of [{ cancel: true }, { trusted: false }, { changeDuringSetup: true }, { dirty: true }]) {
    const f = fixture(options); f.editor.document.isDirty = Boolean(options.dirty); await f.run();
    assert.equal(f.calls.requests.length, 0);
  }
});

test("missing backend is retryable and carbon failure does not hide the packets", async () => {
  const offline = fixture({ offline: true }); await offline.run();
  assert.match(offline.calls.errors[0], /Set Up Backend/);
  const failed = fixture({ carbonFails: true }); await failed.run();
  assert.equal(failed.calls.shown.length, 1);
  assert.equal(failed.response.comparison.carbonStatus, "unavailable");
  assert.match(failed.response.comparison.carbonError, /estimator unavailable/);
  const disabled = fixture({ carbon: false }); await disabled.run();
  assert.equal(disabled.calls.carbon, 0);
  assert.equal(disabled.response.comparison.carbonStatus, "disabled");
});
