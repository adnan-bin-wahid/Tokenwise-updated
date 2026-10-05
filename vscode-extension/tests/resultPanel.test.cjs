const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");
const load = Module._load;
const panels = [];
Module._load = function (name, ...args) {
  if (name === "vscode") {
    return {
      ViewColumn: { Beside: 2 },
      window: {
        createWebviewPanel: () => {
          const panel = { webview: { html: "", onDidReceiveMessage() {} }, onDidDispose() {}, reveal() {} };
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
