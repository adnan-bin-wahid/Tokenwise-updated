const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");

function fixture(options = {}) {
  const calls = { requests: [], carbon: [], shown: [], errors: [], resources: [] };
  const uri = { fsPath: "/demo/mixed.py", scheme: "file" };
  const editor = { document: { uri, languageId: "python", getText: selection => selection ? "excerpt" : "whole file" },
    selection: { isEmpty: false, start: { line: 7 } } };
  const vscode = { env: {}, ProgressLocation: { Notification: 1 },
    workspace: { isTrusted: options.trusted !== false, workspaceFolders: [{ uri: { fsPath: "/demo", scheme: "file" } }] },
    window: { activeTextEditor: options.noEditor ? undefined : editor, showQuickPick: async () => ({ mode: options.mode ?? "repository" }),
      showInputBox: async () => "Earlier account lockout task", withProgress: async (_, action) => action(),
      showErrorMessage: async text => calls.errors.push(text), showWarningMessage: async text => calls.errors.push(text), showInformationMessage() {} } };
  const config = { apiUrl: "http://127.0.0.1:9", enableCarbonEstimation: options.carbon !== false,
    autoOpenResultPanel: true, enableResponseGuidance: options.guidance !== false, repositoryTokenBudget: 4096, defaultThreshold: .45 };
  const api = { TokenWiseApiClient: class {
    constructor(cfg) { assert.equal(cfg.apiUrl, "http://127.0.0.1:8017"); }
    async prune(request) { calls.requests.push(request); return { score: .8, pruned_code: "useful=2", token_scores: [],
      kept_frags: [request.code.includes("\n") ? 2 : 1], origin_token_cnt: 20, left_token_cnt: options.empty ? 0 : 10, model_input_token_cnt: 50,
      line_scores: options.badScores ? { 1: Infinity } : request.code.includes("\n") ? { 1: .2, 2: .9 } : { 1: .9 }, error_msg: null }; }
    async pruneWorkspace(request) { calls.requests.push(request); return { context_hint_used: Boolean(request.context_hint),
      raw_context_tokens: 500, pruned_tokens: 300, input_trace: { history_source: "supplied_user_context" } }; }
  } };
  const load = Module._load;
  Module._load = function (name, ...args) {
    if (name === "vscode") { return vscode; }
    if (name === "./config" || name === "../services/config") { return { getTokenWiseConfig: resource => {
      calls.resources.push(resource); return { ...config }; } }; }
    if (name === "./apiClient" || name === "../services/apiClient") { return api; }
    if (name === "./carbonComparison" || name === "../services/carbonComparison") { return { estimateCarbonComparison: async (_, cfg, ...counts) => {
      calls.carbon.push(counts); return { carbonStatus: cfg.enableCarbonEstimation ? "ready" : "disabled" }; } }; }
    if (name === "../utils/editor") { return { askQuery: async () => options.mode === "conversation" ? "Which tests cover that behavior?" : "Explain useful code", askThreshold: async () => .45,
      getSelectedOrFullCode: () => ({ code: "excerpt", isSelection: true }) }; }
    return load.call(this, name, ...args);
  };
  let service, current, selected, demo;
  try {
    for (const name of ["services/pruneService", "commands/pruneCurrentFile", "commands/pruneSelected", "commands/demonstratePruning"]) {
      delete require.cache[require.resolve(`../dist/${name}.js`)];
    }
    const { PruneService } = require("../dist/services/pruneService.js");
    service = new PruneService(async () => options.offline ? undefined : "http://127.0.0.1:8017");
    ({ createPruneCurrentFileCommand: current } = require("../dist/commands/pruneCurrentFile.js"));
    ({ createPruneSelectedCommand: selected } = require("../dist/commands/pruneSelected.js"));
    ({ createDemonstratePruningCommand: demo } = require("../dist/commands/demonstratePruning.js"));
  } finally { Module._load = load; }
  const panel = { show: result => calls.shown.push(result), showWorkspaceResult: result => calls.shown.push(result) };
  return { calls, uri, service, runCurrent: current(service, panel, "extension"), runSelected: selected(service, panel, "extension"),
    runDemo: demo(service, panel, "extension", async () => "http://127.0.0.1:8017") };
}

test("current-file pruning ignores a highlight and selection-only pruning sends only the excerpt", async () => {
  const current = fixture(); await current.runCurrent();
  assert.equal(current.calls.requests[0].code, "whole file");
  assert.equal(current.calls.shown[0].input_trace.mode, "selected_file");
  const selected = fixture(); await selected.runSelected();
  assert.equal(selected.calls.requests[0].code, "excerpt");
  assert.equal(selected.calls.shown[0].input_trace.first_line, 8);
  assert.equal(selected.calls.shown[0].input_trace.mode, "selected_excerpt");
});

test("manual pruning uses managed URL, scoped config, native counts and real line scores", async () => {
  const f = fixture();
  const result = await f.service.prune("Explain useful code", "noise=1\nuseful=2", .45,
    { resource: f.uri, mode: "selected_excerpt", firstLine: 8 });
  assert.equal(f.calls.resources[0], f.uri);
  assert.deepEqual(f.calls.carbon[0], [20, 10]);
  assert.deepEqual(result.lineScores, { 1: .2, 2: .9 });
  assert.equal(result.input_trace.history_source, "none");
});

test("bad scores, offline backend, untrusted workspace and empty output are handled explicitly", async () => {
  for (const [options, message] of [[{ badScores: true }, /Invalid line/], [{ offline: true }, /Set Up Backend/], [{ trusted: false }, /trusted local/]]) {
    const f = fixture(options); await assert.rejects(f.service.prune("task", "noise\nuseful", .45), message);
  }
  const f = fixture({ empty: true });
  const result = await f.service.prune("task", "noise\nuseful", 1);
  assert.equal(result.carbonStatus, "unavailable");
  assert.equal(f.calls.carbon.length, 0);
});

test("repository demonstration sends no hidden selection hints; history replay is explicitly labeled", async () => {
  const repository = fixture({ noEditor: true, carbon: false }); await repository.runDemo();
  assert.equal(repository.calls.requests[0].active_file, undefined);
  assert.equal(repository.calls.requests[0].selected_code, undefined);
  assert.equal(repository.calls.requests[0].context_hint, undefined);
  assert.equal(repository.calls.requests[0].response_guidance, true);
  const history = fixture({ mode: "conversation" }); await history.runDemo();
  assert.equal(history.calls.requests[0].context_hint, "Earlier account lockout task");
  assert.equal(history.calls.shown[0].input_trace.history_source, "supplied_replay");
});

test("repository and conversation demonstrations honor the guidance toggle", async () => {
  for (const mode of ["repository", "conversation"]) {
    const f = fixture({ mode, guidance: false }); await f.runDemo();
    assert.equal(f.calls.requests[0].response_guidance, false);
  }
});
