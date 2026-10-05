const assert = require("node:assert/strict");
const { test } = require("node:test");
const { estimateCarbonComparison } = require("../dist/services/carbonComparison.js");

const config = {
  enableCarbonEstimation: true, expectedOutputTokens: 256, targetModelName: "meta-llama-3-8b-instruct",
  carbonIntensityGPerKwh: 475,
};
const response = input => ({
  prefill_joules: input, decode_joules: 10, total_joules: input + 10, co2_grams: input / 1000,
  carbon_intensity_g_per_kwh: 475, model_name: "meta-llama-3-8b-instruct", features_source: "registry",
  prefill_route: "xgboost_interpolation", decode_route: "xgboost_interpolation",
});

test("carbon comparison keeps both estimates and a matched output/model scenario", async () => {
  const calls = [];
  const result = await estimateCarbonComparison({ estimateCarbon: async request => {
    calls.push(request); return response(request.input_tokens);
  } }, config, 700, 300, "formatted-context");
  assert.equal(result.carbonBefore.co2Grams, .7);
  assert.equal(result.carbonAfter.co2Grams, .3);
  assert.equal(result.carbonSavings.totalJoulesSaved, 400);
  assert.equal(result.carbonSavings.decodeJoulesSaved, 0);
  assert.equal(result.carbonStatus, "ready");
  assert.equal(result.carbonBaseline, "formatted-context");
  const [{ input_tokens: beforeTokens, ...beforeScenario }, { input_tokens: afterTokens, ...afterScenario }] = calls;
  assert.deepEqual(beforeScenario, afterScenario);
  assert.equal(beforeTokens, 700);
  assert.equal(afterTokens, 300);
});

test("increased context is reported as an increase, never clamped into a saving", async () => {
  const result = await estimateCarbonComparison({ estimateCarbon: async request => response(request.input_tokens) }, config, 17, 117);
  assert.equal(result.carbonSavings.totalJoulesSaved, -100);
  assert.ok(result.carbonSavings.co2GramsSaved < 0);
});

test("disabled carbon does not call the backend", async () => {
  const result = await estimateCarbonComparison({ estimateCarbon: async () => assert.fail("Unexpected request") },
    { ...config, enableCarbonEstimation: false }, 17, 117);
  assert.deepEqual(result, { carbonStatus: "disabled" });
});

test("invalid token counts are rejected without backend calls", async () => {
  for (const value of [0, -1, Infinity, NaN, 1.5]) {
    await assert.rejects(estimateCarbonComparison({ estimateCarbon: async () => assert.fail("Unexpected request") },
      config, value, 100), /positive token counts/);
  }
});

test("nonfinite, negative, and unsupported remote estimate values are rejected", async () => {
  for (const patch of [{ co2_grams: NaN }, { prefill_joules: -10 }, { model_name: 42 }, { prefill_route: "invented" }]) {
    await assert.rejects(estimateCarbonComparison({ estimateCarbon: async () => ({ ...response(100), ...patch }) },
      config, 100, 50), /invalid carbon estimate/);
  }
});

test("backend failure remains a failure, not a fabricated estimate", async () => {
  await assert.rejects(estimateCarbonComparison({ estimateCarbon: async () => { throw new Error("503 missing models"); } },
    config, 100, 50), /503 missing models/);
});
