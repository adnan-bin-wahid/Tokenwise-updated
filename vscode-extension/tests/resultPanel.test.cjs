const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");
const load = Module._load;
const panels = [];
const copied = [];
const written = [];
const warnings = [];
let saveDestination;
let writeFails = false;
Module._load = function (name, ...args) {
  if (name === "vscode") {
    return {
      ViewColumn: { Beside: 2 },
      env: { clipboard: { writeText: async value => copied.push(value) } },
      workspace: { fs: { writeFile: async (uri, data) => {
        if (writeFails) { throw new Error("permission denied"); }
        written.push({ uri, result: JSON.parse(data.toString()) });
      } } },
      window: {
        showSaveDialog: async () => saveDestination,
        showInformationMessage() {},
        showWarningMessage: async value => warnings.push(value),
        createWebviewPanel: () => {
          const panel = { webview: { html: "", onDidReceiveMessage(callback) { panel.receive = callback; } }, onDidDispose() {}, reveal() {} };
          panels.push(panel); return panel;
        },
      },
    };
  }
  return load.call(this, name, ...args);
};
const { ResultPanel } = require("../dist/ui/resultPanel.js");
Module._load = load;
const reportedResult = {
  structured_goal: { task_type: "generic_task", identifiers: [] },
  original_tokens: 17, pruned_tokens: 117, unified_prompt: "[TokenWise automatic context]",
  files: [{ file_path: "src/demo1/__init__.py", relation: "prompt-selected file", tier: 1,
    original_tokens: 17, pruned_tokens: 17, score: .0044 }],
};
const estimate = grams => ({ prefillJoules: 1, decodeJoules: 2, totalJoules: 3,
  co2Grams: grams, modelFamily: "Llama", prefillRoute: "xgboost_interpolation",
  decodeRoute: "xgboost_interpolation", featuresSource: "registry", carbonIntensityGPerKwh: 475 });

test("17 source tokens in a 117-token bundle shows zero source reduction and 100-token overhead", () => {
  const html = new ResultPanel().getWorkspaceHtml(reportedResult);
  assert.match(html, /Source reduction/);
  assert.match(html, /0\.00%/);
  assert.match(html, /100 tokens/);
  assert.doesNotMatch(html, /-588|NaN|Infinity/);
});

test("actual source expansion has a positive increase label, not a negative reduction", () => {
  const html = new ResultPanel().getWorkspaceHtml({ ...reportedResult, retained_source_tokens: 34 });
  assert.match(html, /Source increase/);
  assert.match(html, /100\.00%/);
  assert.doesNotMatch(html, /-100\.00%/);
});

test("manual pruning also labels an actual token expansion honestly", () => {
  const html = new ResultPanel().getHtml({
    query: "Explain version metadata", score: .1, originalCode: "version = 1", prunedCode: "version = 1",
    originTokenCount: 17, prunedTokenCount: 34, reductionPercent: -100,
    modelInputTokenCount: 34, keptFrags: [], carbonStatus: "disabled",
  });
  assert.match(html, /Source increase/);
  assert.match(html, /100\.00%/);
  assert.doesNotMatch(html, /-100\.00%/);
});

test("carbon view includes before, after, phase energies and signed increases", () => {
  const html = new ResultPanel().getWorkspaceHtml({
    ...reportedResult, carbonStatus: "ready", carbonBefore: estimate(.001), carbonAfter: estimate(.002),
    carbonBaseline: "formatted-context",
    carbonSavings: { totalJoulesSaved: -1, prefillJoulesSaved: -1, decodeJoulesSaved: 0, co2GramsSaved: -.001 },
  });
  assert.match(html, /CO2 before/);
  assert.match(html, /CO2 after/);
  assert.match(html, /CO2 increase/);
  assert.match(html, /Energy increase/);
  assert.match(html, /0\.002000 g/);
  assert.match(html, /Same files and formatting/);
  assert.match(html, /not measured emissions/);
});

test("carbon unavailable, pending and disabled states remain visible", () => {
  const panel = new ResultPanel();
  assert.match(panel.getWorkspaceHtml({ ...reportedResult, carbonStatus: "pending" }), /Estimating carbon/);
  assert.match(panel.getWorkspaceHtml({ ...reportedResult, carbonStatus: "disabled" }), /Carbon estimation is disabled/);
  const html = panel.getWorkspaceHtml({ ...reportedResult, carbonStatus: "unavailable", carbonError: "<invalid>" });
  assert.match(html, /Carbon estimate unavailable/);
  assert.match(html, /&lt;invalid&gt;/);
  assert.doesNotMatch(html, /<invalid>/);
});

test("overview coverage warnings are escaped and priorities are not labeled neural scores", () => {
  const html = new ResultPanel().getWorkspaceHtml({ ...reportedResult, context_mode: "repository_overview",
    indexed_files: 1, warnings: ["Only initializers <found>"] });
  assert.match(html, /Repository overview/);
  assert.match(html, /Priority/);
  assert.match(html, /Only initializers &lt;found&gt;/);
});

test("guidance version, profile, budget state and overhead are visible and escaped", () => {
  const panel = new ResultPanel();
  assert.match(panel.getWorkspaceHtml(reportedResult), /Response guidance.*not reported/s);
  for (const status of ["applied", "disabled", "omitted_budget"]) {
    const html = panel.getWorkspaceHtml({ ...reportedResult, response_guidance: {
      version: "1", profile: "generic_task <source>", enabled: status !== "disabled", status,
      format: status === "applied" ? "full" : null, tokens: status === "applied" ? 80 : 0, text: "Grounded instructions" } });
    assert.match(html, /Response guidance/);
    assert.match(html, /v1: generic_task &lt;source&gt;/);
    assert.ok(html.includes(status));
    assert.doesNotMatch(html, /<source>/);
  }
});

test("explicit exclusions and scope-filter methods are visible and escaped", () => {
  const html = new ResultPanel().getWorkspaceHtml({ ...reportedResult,
    structured_goal: { ...reportedResult.structured_goal, excluded_topics: ["invoice <pricing>"] },
    files: [{ ...reportedResult.files[0], pruning_method: "scope_filter+neural_lines" }] });
  assert.match(html, /Excluded topics/);
  assert.match(html, /invoice &lt;pricing&gt;/);
  assert.match(html, /scope_filter\+neural_lines/);
  assert.doesNotMatch(html, /<pricing>/);
});

test("background carbon refresh does not overwrite another automatic or manual result", () => {
  const panel = new ResultPanel();
  const first = { ...reportedResult, automatic_context: { event_id: "first", query: "Overview", timestamp: "now", elapsed_ms: 100 } };
  panel.showWorkspaceResult(first, "extension");
  assert.equal(panel.updateWorkspaceResult({ ...first, carbonStatus: "disabled" }), true);
  panel.showWorkspaceResult({ ...first, automatic_context: { ...first.automatic_context, event_id: "second" } }, "extension");
  const secondHtml = panels.at(-1).webview.html;
  assert.equal(panel.updateWorkspaceResult({ ...first, carbonStatus: "disabled" }), false);
  assert.equal(panels.at(-1).webview.html, secondHtml);
  panel.showWorkspaceResult(reportedResult, "extension");
  assert.equal(panel.updateWorkspaceResult(first), false);
});

const comparison = { query: "Explain <lockout>", selection_scope: "entire selected file", notes: ["Not measured <emissions>"],
  methods: ["all_python", "selected", "tokenwise"].map((id, index) => ({ id, title: id,
    input_tokens: [100, 20, 120][index], source_tokens: [80, 10, 60][index], files: ["auth.py"], context: `${id} exact packet` })) };

test("comparison rendering escapes data and labels expansion honestly", () => {
  const html = new ResultPanel().getWorkspaceHtml({ ...reportedResult, comparison });
  assert.match(html, /Explain &lt;lockout&gt;/);
  assert.match(html, /Not measured &lt;emissions&gt;/);
  assert.match(html, /20\.00% increase/);
  assert.match(html, /Copy Selected Code/);
  assert.match(html, /Export Comparison/);
});

test("automatic two-packet comparison discloses the baseline, lists files and omits selected controls", () => {
  const automatic = { ...comparison, methods: comparison.methods.filter(method => method.id !== "selected") };
  const html = new ResultPanel().getWorkspaceHtml({ ...reportedResult, comparison: automatic });
  assert.match(html, /not actual Antigravity IDE consumption/);
  assert.match(html, /All-Python baseline/);
  assert.match(html, /20 tokens added/);
  assert.match(html, /auth\.py/);
  assert.doesNotMatch(html, /Copy Selected Code/);
  const zero = { ...automatic, methods: automatic.methods.map(item => item.id === "all_python" ? { ...item, input_tokens: 0 } : item) };
  assert.match(new ResultPanel().getWorkspaceHtml({ ...reportedResult, comparison: zero }), /zero baseline/);
});

test("automatic comparison failures and pending state remain visible without hiding the packet", () => {
  const panel = new ResultPanel();
  assert.match(panel.getWorkspaceHtml({ ...reportedResult, comparisonStatus: "pending" }), /Preparing automatic packet comparison/);
  const html = panel.getWorkspaceHtml({ ...reportedResult, comparisonStatus: "unavailable", comparisonError: "Snapshot <changed>" });
  assert.match(html, /Snapshot &lt;changed&gt;/);
  assert.match(html, /Unified context/);
});

test("reported CLI usage is separate from local counts, preserved in exports and escaped", async () => {
  const panel = new ResultPanel();
  const run = { conversationId: "first", durationSeconds: 2, answer: "Answer <unsafe>",
    usage: { input_tokens: 100, output_tokens: 10, total_tokens: 110 }, tools: [], toolTraceAvailable: false };
  const actual = { measurement_scope: "imported_antigravity_cli_usage", importedAt: "now", notes: ["CLI, not IDE"],
    without: run, with: { ...run, conversationId: "second", usage: { input_tokens: 120, output_tokens: 10, total_tokens: 130 } } };
  panel.showAgentUsageComparison(actual);
  const webview = panels.at(-1);
  assert.match(webview.webview.html, /20\.00% increase/);
  assert.match(webview.webview.html, /Answer &lt;unsafe&gt;/);
  assert.match(webview.webview.html, /trace unavailable/);
  assert.match(webview.webview.html, /not reported/);
  saveDestination = "actual.json";
  await webview.receive({ command: "exportAgentComparison" });
  assert.deepEqual(written.at(-1).result, actual);
  saveDestination = undefined;
});

test("copy controls use exact matching packets; export cancellation and failure are handled", async () => {
  const panel = new ResultPanel(); panel.showWorkspaceResult({ ...reportedResult, comparison }, "extension");
  const webview = panels.at(-1);
  for (const method of comparison.methods) {
    await webview.receive({ command: "copyComparison", method: method.id });
    assert.equal(copied.at(-1), method.context);
  }
  const count = copied.length;
  await webview.receive({ command: "copyComparison", method: "unknown" });
  assert.equal(copied.length, count);
  const writes = written.length;
  saveDestination = undefined;
  await webview.receive({ command: "exportComparison" });
  assert.equal(written.length, writes);
  saveDestination = "chosen.json";
  await webview.receive({ command: "exportComparison" });
  assert.deepEqual(written.at(-1).result.comparison, comparison);
  writeFails = true;
  await webview.receive({ command: "exportComparison" });
  assert.match(warnings.at(-1), /export failed.*permission denied/);
  writeFails = false;
});

test("pruning inputs and actual line masks distinguish threshold decisions from scope/history", async () => {
  const result = { query: "Task <source>", score: .8, originalCode: "noise=1\nuseful=2", prunedCode: "useful=2",
    originTokenCount: 20, prunedTokenCount: 10, modelInputTokenCount: 50, reductionPercent: 50, keptFrags: [2],
    lineScores: { 1: .2, 2: .9 }, input_trace: { mode: "selected_excerpt", current_query: "Task <source>",
      effective_query: "Task <source>", scope: "mixed.py", first_line: 8, threshold: .45, history_text: "", history_source: "none" } };
  const panel = new ResultPanel();
  const html = panel.getHtml(result);
  assert.match(html, /Selected excerpt/);
  assert.match(html, /Task &lt;source&gt;/);
  assert.match(html, /0\.2000/);
  assert.match(html, /0\.9000/);
  assert.match(html, /Not selected by mask/);
  assert.match(html, /Keep: threshold/);
  panel.show(result, "extension");
  saveDestination = "pruning.json";
  await panels.at(-1).receive({ command: "exportPruningRun" });
  assert.deepEqual(written.at(-1).result, result);
});

test("comparison export preserves the exact response-guidance trace", async () => {
  const guidance = { version: "1", profile: "generic_task", enabled: true, status: "applied",
    format: "full", tokens: 80, text: "Ground answers in the supplied source." };
  const panel = new ResultPanel();
  panel.showWorkspaceResult({ ...reportedResult, comparison, response_guidance: guidance }, "extension");
  saveDestination = "guided-comparison.json";
  await panels.at(-1).receive({ command: "exportComparison" });
  assert.deepEqual(written.at(-1).result.response_guidance, guidance);
});
