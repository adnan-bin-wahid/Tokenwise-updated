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
    for (const [name, result] of Object.entries({ overview: results.overview, scaffold: results.scaffold })) {
      for (const [layout, width, height] of [["desktop", 1280, 1000], ["narrow", 390, 844]]) {
        const page = await browser.newPage({ viewport: { width, height } });
        const errors = [];
        page.on("pageerror", error => errors.push(error.message));
        await page.evaluate(() => {
          window.messages = [];
          window.acquireVsCodeApi = () => ({ postMessage: message => window.messages.push(message) });
        });
        await page.setContent(panel.getWorkspaceHtml({
          ...result, automatic_context: {
            event_id: name, query: "GIVE ME THE FULL OVERVIEW OF MY PROJECT",
            timestamp: "verification", elapsed_ms: 5720,
          },
        }));
        await page.addStyleTag({ content: `:root {
          --vscode-editor-background: #1e1e1e; --vscode-editor-foreground: #d4d4d4;
          --vscode-descriptionForeground: #aaa; --vscode-panel-border: #454545;
          --vscode-button-background: #007acc; --vscode-button-foreground: #fff;
          --vscode-button-hoverBackground: #1687cf; --vscode-testing-iconPassedColor: #73c991;
          --vscode-textCodeBlock-background: #181818; --vscode-font-family: Arial, sans-serif;
        }` });
        await page.getByText("CO2 before", { exact: true }).waitFor();
        await page.getByText("CO2 after", { exact: true }).waitFor();
        assert.equal(await page.getByText("Identifiers", { exact: true }).locator("+ strong").innerText(), "none");
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
        await page.getByRole("button", { name: "Copy Unified Context" }).click();
        assert.deepEqual(await page.evaluate(() => window.messages), [{ command: "copyWorkspace" }]);
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
