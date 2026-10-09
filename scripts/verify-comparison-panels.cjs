const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const Module = require("node:module");

async function main() {
  const playwright = require(path.resolve(process.argv[2]));
  const directory = path.resolve(process.argv[3] ?? "tmp/release-0.6.8-ui");
  await fs.mkdir(directory, { recursive: true });
  let webview;
  const load = Module._load;
  let ResultPanel;
  try {
    Module._load = function (name, ...args) {
      if (name !== "vscode") { return load.call(this, name, ...args); }
      return { ViewColumn: { Beside: 2 }, window: { createWebviewPanel() {
        const panel = { webview: { html: "", onDidReceiveMessage() {} }, onDidDispose() {}, reveal() {} };
        webview = panel.webview;
        return panel;
      } } };
    };
    ({ ResultPanel } = require("../vscode-extension/dist/ui/resultPanel.js"));
  } finally { Module._load = load; }

  // Synthetic fixtures verify rendering and controls, not research outcomes.
  const result = { structured_goal: { task_type: "generic_task", identifiers: [] },
    original_tokens: 100, retained_source_tokens: 40, pruned_tokens: 80,
    unified_prompt: "Synthetic reference packet: explain account lockout.", files: [],
    carbonStatus: "disabled" };
  const comparison = { query: "Explain account lockout", selection_scope: "none",
    notes: ["Synthetic UI fixture. Not a measured agent experiment."],
    methods: [["all_python", 200], ["tokenwise", 80]].map(([id, tokens]) => ({
      id, title: id === "all_python" ? "All Python code" : "TokenWise context", input_tokens: tokens,
      prompt_tokens: tokens + 5, source_tokens: tokens - 20,
      files: ["security/auth_service.py"], context: `${id} synthetic packet`,
    })) };
  const panel = new ResultPanel();
  const run = { conversationId: "synthetic-without", model: "synthetic-model",
    durationSeconds: 2, usage: { input_tokens: 200, output_tokens: 20, total_tokens: 220 },
    answer: "Synthetic answer <reference>", tools: [], toolTraceAvailable: false };
  panel.showAgentUsageComparison({ measurement_scope: "imported_antigravity_cli_usage", importedAt: "UI verification",
    without: run, with: { ...run, conversationId: "synthetic-with",
      usage: { input_tokens: 80, output_tokens: 20, total_tokens: 100 } },
    notes: ["Synthetic fixture only. Actual logs are supplied by the user."] });
  const views = {
    memory: panel.getWorkspaceHtml({ ...result, input_trace: {
      mode: "conversation", current_query: "Explain account lockout boundary tests", effective_query: "Lockout evidence and earlier requirements",
      scope: "Repository discovery", threshold: .45, history_text: "Explain account lockout. Do not modify any files.\n\nUse bullet points.",
      history_source: "agent_supplied_user_turns", memory: {
        version: "1", enabled: true, selection: "Synthetic memory UI fixture", summary: "Explain account lockout.",
        requirements: ["Do not modify any files.", "Use bullet points."], considered_messages: 4, omitted_messages: 2,
        characters: 78, truncated: false, messages: [
          { position: 1, text: "Explain account lockout. Do not modify any files.", reason: "topic anchor" },
          { position: 3, text: "Use bullet points.", reason: "earlier requirement" }],
        packet: { status: "applied", tokens: 50, text: "Synthetic reference block. Latest user request takes precedence." } } } }),
    automatic: panel.getWorkspaceHtml({ ...result, comparison }),
    pending: panel.getWorkspaceHtml({ ...result, comparisonStatus: "pending" }),
    unavailable: panel.getWorkspaceHtml({ ...result, comparisonStatus: "unavailable", comparisonError: "Saved repository changed; send a fresh prompt." }),
    cli_usage: webview.html,
  };
  const checks = [];
  const browser = await playwright.chromium.launch({ headless: true });
  try {
    for (const [name, html] of Object.entries(views)) {
      for (const [layout, width, height] of [["desktop", 1280, 1000], ["narrow", 390, 844]]) {
        const page = await browser.newPage({ viewport: { width, height } });
        const errors = [];
        page.on("pageerror", error => errors.push(error.message));
        await page.evaluate(() => {
          window.messages = [];
          window.acquireVsCodeApi = () => ({ postMessage: message => window.messages.push(message) });
        });
        await page.setContent(html);
        await page.addStyleTag({ content: `:root {
          --vscode-editor-background: #1e1e1e; --vscode-editor-foreground: #d4d4d4;
          --vscode-descriptionForeground: #aaa; --vscode-panel-border: #454545;
          --vscode-button-background: #007acc; --vscode-button-foreground: #fff;
          --vscode-button-hoverBackground: #1687cf; --vscode-testing-iconPassedColor: #73c991;
          --vscode-textCodeBlock-background: #181818; --vscode-font-family: Arial, sans-serif;
        }` });
        if (name === "automatic") {
          assert.equal(await page.getByRole("button", { name: "Copy Selected Code", exact: true }).count(), 0);
          await page.getByText(/60.00% reduction; 120 tokens saved/).first().waitFor();
          for (const [label, method] of [["Copy All Python Code", "all_python"], ["Copy TokenWise Context", "tokenwise"]]) {
            await page.getByRole("button", { name: label, exact: true }).click();
            assert.deepEqual(await page.evaluate(() => window.messages.at(-1)), { command: "copyComparison", method });
          }
          await page.getByRole("button", { name: "Export Comparison", exact: true }).click();
          assert.deepEqual(await page.evaluate(() => window.messages.at(-1)), { command: "exportComparison" });
        } else if (name === "memory") {
          await page.getByText(/Conversation memory: 2 selected \/ 4 considered/).waitFor();
          await page.getByText(/Omitted: 2/).waitFor();
          await page.getByRole("button", { name: "Export Pruning Run", exact: true }).click();
          assert.deepEqual(await page.evaluate(() => window.messages.at(-1)), { command: "exportPruningRun" });
        } else if (name === "cli_usage") {
          await page.getByRole("columnheader", { name: "Reported counter", exact: true }).waitFor();
          await page.getByRole("button", { name: "Export Reported Usage Comparison", exact: true }).click();
          assert.deepEqual(await page.evaluate(() => window.messages.at(-1)), { command: "exportAgentComparison" });
        } else {
          await page.getByText(name === "pending" ? /Preparing automatic packet comparison/ : /Saved repository changed/).waitFor();
          await page.getByText("Unified context", { exact: true }).waitFor();
        }
        const bounds = await page.evaluate(() => ({
          horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
          overflowingStats: [...document.querySelectorAll(".stat")].filter(element => element.scrollWidth > element.clientWidth).length,
          overlappingStats: [...document.querySelectorAll(".stats")].some(group => {
            const boxes = [...group.children].map(element => element.getBoundingClientRect());
            return boxes.some((box, index) => boxes.slice(index + 1).some(other =>
              box.left < other.right && box.right > other.left && box.top < other.bottom && box.bottom > other.top));
          }),
        }));
        assert.deepEqual(bounds, { horizontalOverflow: false, overflowingStats: 0, overlappingStats: false });
        assert.deepEqual(errors, []);
        await page.screenshot({ path: path.join(directory, `${name}-${layout}.png`), fullPage: true });
        checks.push({ name, layout, ...bounds, pageErrors: 0, fixture: "synthetic UI only" });
        await page.close();
      }
    }
  } finally { await browser.close(); }
  await fs.writeFile(path.join(directory, "checks.json"), JSON.stringify(checks, null, 2));
  console.log(JSON.stringify(checks, null, 2));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
