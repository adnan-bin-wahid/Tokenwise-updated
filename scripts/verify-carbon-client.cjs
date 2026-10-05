const fs = require("node:fs");
const { TokenWiseApiClient } = require("../vscode-extension/dist/services/apiClient.js");
const { estimateCarbonComparison } = require("../vscode-extension/dist/services/carbonComparison.js");

async function main() {
  const input = JSON.parse(fs.readFileSync(0, "utf8"));
  const cfg = {
    apiUrl: input.base, timeoutMs: 10000, enableCarbonEstimation: true,
    expectedOutputTokens: 256, targetModelName: "meta-llama-3-8b-instruct", carbonIntensityGPerKwh: 475,
  };
  const result = await estimateCarbonComparison(
    new TokenWiseApiClient(cfg), cfg, input.before, input.after, "formatted-context",
  );
  process.stdout.write(JSON.stringify(result));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
