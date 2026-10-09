const fs = require("node:fs/promises");
const path = require("node:path");

async function main() {
  const root = path.resolve(__dirname, "..");
  const playwright = require(path.resolve(process.argv[2]));
  const report = JSON.parse(await fs.readFile(path.join(root, "evaluation/comparative-study/results.json"), "utf8"));
  if (report.failures.length || report.results.length !== 20) { throw new Error("Complete results required."); }
  const directory = path.join(root, "evaluation/comparative-study/figures");
  await fs.mkdir(directory, { recursive: true });
  const browser = await playwright.chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 900 }, deviceScaleFactor: 1 });
    await page.setContent('<!doctype html><html><body style="margin:0;background:white"><canvas width="1500" height="900"></canvas></body></html>');
    for (const kind of ["context-size", "matched-pruning", "memory-coverage"]) {
      const rendered = await page.evaluate(({ cases, kind }) => {
        const ctx = document.querySelector("canvas").getContext("2d", { willReadFrequently: true });
        ctx.fillStyle = "white"; ctx.fillRect(0, 0, 1500, 900);
        const titles = {
          "context-size": ["Context size: all indexed Python vs retrieval-only ablation", "Log scale. Retrieval condition disables neural pruning; this is not a full automatic-pipeline benchmark."],
          "matched-pruning": ["Real neural pruning: matched selected excerpts", "Signed packet reduction at threshold 0.45. A negative value means the packet grew. No answer-quality score is measured."],
          "memory-coverage": ["Conversation memory: required-file candidate coverage", "Retrieval-only ablation, same follow-up question. Files are counted before packet packing, not as retained code bodies."],
        };
        ctx.fillStyle = "#18242b"; ctx.font = "bold 25px Arial"; ctx.fillText(titles[kind][0], 36, 42);
        ctx.fillStyle = "#44525d"; ctx.font = "15px Arial"; ctx.fillText(titles[kind][1], 36, 73);
        const left = 310, right = 1370, top = 154, step = 31;
        const minimum = kind === "matched-pruning" ? -5 : kind === "context-size" ? 1000 : 0;
        const maximum = kind === "matched-pruning" ? 35 : kind === "context-size" ? 300000 : 100;
        const x = value => left + (kind === "context-size" ? (Math.log10(value)-Math.log10(minimum))/(Math.log10(maximum)-Math.log10(minimum)) : (value-minimum)/(maximum-minimum))*(right-left);
        const ticks = kind === "matched-pruning" ? [-5, 0, 5, 10, 15, 20, 25, 30, 35] : kind === "context-size" ? [1000, 4096, 10000, 30000, 100000, 300000] : [0, 20, 40, 60, 80, 100];
        ctx.font = "13px Arial";
        for (const tick of ticks) {
          ctx.strokeStyle = "#e2e7e9"; ctx.beginPath(); ctx.moveTo(x(tick), top-16); ctx.lineTo(x(tick), top+cases.length*step); ctx.stroke();
          ctx.fillStyle = "#44525d"; ctx.textAlign = "center";
          ctx.fillText(kind === "context-size" ? tick.toLocaleString("en-US") : `${tick}%`, x(tick), top-25);
        }
        ctx.textAlign = "left"; ctx.font = "14px Arial";
        cases.forEach((entry, index) => {
          const values = Object.fromEntries(entry.rows.map(row => [row.strategy, row]));
          const y = top + index*step;
          ctx.fillStyle = "#18242b"; ctx.fillText(entry.repository, 36, y+11);
          if (kind === "matched-pruning") {
            const value = 100*(values.selected_excerpt.input_tokens-values.neural_excerpt.input_tokens)/values.selected_excerpt.input_tokens;
            ctx.fillStyle = value < 0 ? "#a23d4a" : "#167d61";
            ctx.fillRect(Math.min(x(0),x(value)), y, Math.abs(x(value)-x(0)), 16);
            ctx.fillStyle = "#18242b"; ctx.fillText(`${value.toFixed(2)}%`, Math.max(x(0),x(value))+10, y+13);
          } else {
            const pair = kind === "context-size" ? [values.all_python.input_tokens, values.retrieval_only.input_tokens] : [values.history_off, values.history_on].map(row => 100*row.required_files_retrieved/row.required_files_total);
            pair.forEach((value, i) => {
              ctx.fillStyle = i === 0 ? "#61798a" : "#167d61";
              ctx.fillRect(left, y+i*11, x(value)-left, 9);
            });
          }
        });
        ctx.font = "15px Arial"; ctx.fillStyle = "#44525d";
        ctx.fillText("TokenWise 0.6.8 | 20 pinned repositories | Local measurements on October 9, 2026 | No Antigravity cloud calls", 36, 854);
        if (kind !== "matched-pruning") {
          ctx.fillStyle = "#61798a"; ctx.fillRect(36, 102, 18, 10); ctx.fillStyle = "#18242b";
          ctx.fillText(kind === "context-size" ? "All Python" : "Memory off", 62, 112);
          ctx.fillStyle = "#167d61"; ctx.fillRect(205, 102, 18, 10); ctx.fillStyle = "#18242b";
          ctx.fillText(kind === "context-size" ? "Retrieval-only" : "Memory on", 231, 112);
        }
        const labeledRows = cases.map((_, index) => {
          const pixels = ctx.getImageData(36, top+index*step, 270, 18).data;
          let ink = 0;
          for (let i = 0; i < pixels.length; i += 4) { if (pixels[i] < 220 && pixels[i+1] < 220 && pixels[i+2] < 220) { ink++; } }
          return ink > 40;
        });
        return { image: ctx.canvas.toDataURL("image/png"), labeledRows };
      }, { cases: report.results, kind });
      if (rendered.labeledRows.some(value => !value)) { throw new Error(`Missing repository label in ${kind}.`); }
      await fs.writeFile(path.join(directory, `${kind}.png`), Buffer.from(rendered.image.split(",")[1], "base64"));
    }
  } finally { await browser.close(); }
  console.log("Three figures generated from measured data; no synthetic outcome values.");
}
main().catch(error => { console.error(error); process.exitCode = 1; });
