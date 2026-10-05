const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const Module = require("node:module");

async function main() {
  const reportPath = path.resolve(process.argv[2] ?? "tmp/context-results.json");
  const playwright = require(process.argv[3] ?? "playwright");
  const results = JSON.parse(await fs.readFile(reportPath, "utf8"));
  const load = Module._load;
  let ResultPanel;
  try {
    Module._load = function (name, ...args) {
      return name === "vscode" ? {} : load.call(this, name, ...args);
    };
    ({ ResultPanel } = require("../vscode-extension/dist/ui/resultPanel.js"));
  } finally {
    Module._load = load;
  }
  const panel = new ResultPanel();
  const directory = path.join(path.dirname(reportPath), "result-panel");
  await fs.mkdir(directory, { recursive: true });
  const browser = await playwright.chromium.launch({ headless: true });
  const checks = [];
  try {
    const inputReport = typeof results.selected_file?.originalCode === "string";
    const views = inputReport ? Object.fromEntries(["repository", "selected_file", "selected_high_threshold", "selected_excerpt", "conversation", "new_chat"]
      .filter(name => results[name])
      .map(name => [name, results[name]])) : results.comparison ? { comparison: results } : { overview: results.overview, scaffold: results.scaffold };
    for (const [name, result] of Object.entries(views)) {
      for (const [layout, width, height] of [["desktop", 1280, 1000], ["narrow", 390, 844]]) {
        const page = await browser.newPage({ viewport: { width, height } });
        const errors = [];
        page.on("pageerror", error => errors.push(error.message));
        await page.evaluate(() => {
          window.messages = [];
          window.acquireVsCodeApi = () => ({ postMessage: message => window.messages.push(message) });
        });
        const selected = name.startsWith("selected_");
        await page.setContent(selected ? panel.getHtml(result) : panel.getWorkspaceHtml({
          ...result, ...(name === "comparison" || inputReport ? {} : { automatic_context: {
            event_id: name, query: "GIVE ME THE FULL OVERVIEW OF MY PROJECT",
            timestamp: "verification", elapsed_ms: 5720,
          } }),
        }));
        await page.addStyleTag({ content: `:root {
          --vscode-editor-background: #1e1e1e; --vscode-editor-foreground: #d4d4d4;
          --vscode-descriptionForeground: #aaa; --vscode-panel-border: #454545;
          --vscode-button-background: #007acc; --vscode-button-foreground: #fff;
          --vscode-button-hoverBackground: #1687cf; --vscode-testing-iconPassedColor: #73c991;
          --vscode-textCodeBlock-background: #181818; --vscode-font-family: Arial, sans-serif;
        }` });
        if (inputReport) {
          await page.getByRole("heading", { name: "Pruning inputs", exact: true }).waitFor();
          assert.equal(await page.getByText("Current task", { exact: true }).locator("+ strong").innerText(), result.input_trace.current_query);
          await page.locator("summary").filter({ hasText: "Inference objective" }).click();
          assert.equal(await page.locator("details").filter({ has: page.locator("summary").filter({ hasText: "Inference objective" }) })
            .locator("pre").innerText(), result.input_trace.effective_query);
          if (selected) {
            await page.getByRole("heading", { name: "Line decisions", exact: true }).waitFor();
            const number = Number(Object.keys(result.lineScores)[0]);
            const row = page.locator("section").filter({ has: page.getByRole("heading", { name: "Line decisions", exact: true }) })
              .locator("tbody tr").nth(number - 1);
            assert.equal(await row.locator("td").nth(0).innerText(), String(result.input_trace.first_line + number - 1));
            assert.equal(await row.locator("td").nth(1).innerText(), result.lineScores[String(number)].toFixed(4));
            await page.getByText("CO2 before", { exact: true }).waitFor();
          }
          if (name === "conversation") {
            await page.getByText("Native hook: current-chat user turns", { exact: true }).waitFor();
            await page.getByText(result.input_trace.history_text, { exact: true }).waitFor();
          }
          if (name === "new_chat") {
            assert.equal(result.context_hint_used, false);
            assert.equal(result.structured_goal.clarification_required, true);
            assert.equal(await page.getByText("History source", { exact: true }).locator("+ strong").innerText(), "None");
          }
        } else if (name === "comparison") {
          await page.getByRole("columnheader", { name: "Estimated CO2", exact: true }).waitFor();
          assert.equal(await page.locator("section tbody tr").count(), 3);
        } else {
          await page.getByText("CO2 before", { exact: true }).waitFor();
          await page.getByText("CO2 after", { exact: true }).waitFor();
          assert.equal(await page.getByText("Identifiers", { exact: true }).locator("+ strong").innerText(), "none");
        }
        if (name === "scaffold") {
          assert.equal(await page.getByText("Source reduction", { exact: true }).locator("+ div").innerText(), "0.00%");
          await page.getByText(/Only Python package initializers/).waitFor();
        }
        const bounds = await page.evaluate(() => ({
          horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
          overflowingStats: [...document.querySelectorAll(".stat")]
            .filter(element => element.scrollWidth > element.clientWidth).length,
          overlappingStats: [...document.querySelectorAll(".stats")].some(group => {
            const boxes = [...group.children].map(element => element.getBoundingClientRect());
            return boxes.some((box, index) => boxes.slice(index + 1).some(other =>
              box.left < other.right && box.right > other.left && box.top < other.bottom && box.bottom > other.top));
          }),
        }));
        assert.deepEqual(bounds, { horizontalOverflow: false, overflowingStats: 0, overlappingStats: false });
        await page.getByRole("button", { name: selected ? "Copy Pruned Context" : "Copy Unified Context" }).click();
        assert.deepEqual(await page.evaluate(() => window.messages), [{ command: selected ? "copyPruned" : "copyWorkspace" }]);
        if (inputReport) {
          await page.getByRole("button", { name: "Export Pruning Run", exact: true }).click();
          assert.deepEqual(await page.evaluate(() => window.messages.at(-1)), { command: "exportPruningRun" });
        }
        if (name === "comparison") {
          for (const [label, method] of [["Copy All Python Code", "all_python"], ["Copy Selected Code", "selected"], ["Copy TokenWise Context", "tokenwise"]]) {
            await page.getByRole("button", { name: label, exact: true }).click();
            assert.deepEqual(await page.evaluate(() => window.messages.at(-1)), { command: "copyComparison", method });
          }
          await page.getByRole("button", { name: "Export Comparison", exact: true }).click();
          assert.deepEqual(await page.evaluate(() => window.messages.at(-1)), { command: "exportComparison" });
        }
        assert.deepEqual(errors, []);
        await page.screenshot({ path: path.join(directory, `${name}-${layout}.png`), fullPage: true });
        checks.push({ name, layout, width, height, ...bounds, copyButton: true, pageErrors: 0 });
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }
  await fs.writeFile(path.join(directory, "checks.json"), JSON.stringify(checks, null, 2));
  console.log(JSON.stringify(checks, null, 2));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
