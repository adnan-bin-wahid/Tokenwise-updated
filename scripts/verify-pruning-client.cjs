const Module = require("node:module");
const fs = require("node:fs");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const load = Module._load;
Module._load = function (name, ...args) {
  if (name === "vscode") { return { workspace: { isTrusted: true }, env: {}, window: { showWarningMessage: value => process.stderr.write(`${value}\n`) } }; }
  if (name === "./config") { return { getTokenWiseConfig: () => ({ apiUrl: "http://127.0.0.1:9", timeoutMs: 120000,
    enableCarbonEstimation: true, expectedOutputTokens: 256, targetModelName: "meta-llama-3-8b-instruct", carbonIntensityGPerKwh: 475,
    ...(input.zero_overrides ? { targetModelSizeB: 0, latencyPerInputTokenMs: 0,
      latencyPerOutputTokenMs: 0, targetGpuType: "" } : {}) }) }; }
  return load.call(this, name, ...args);
};
const { PruneService } = require("../vscode-extension/dist/services/pruneService.js");
Module._load = load;
new PruneService(async () => input.base).prune(input.query, input.code, input.threshold,
  { resource: { fsPath: input.file_path }, mode: input.mode, firstLine: input.first_line })
  .then(result => process.stdout.write(JSON.stringify(result)))
  .catch(error => { process.stderr.write(String(error)); process.exitCode = 1; });
