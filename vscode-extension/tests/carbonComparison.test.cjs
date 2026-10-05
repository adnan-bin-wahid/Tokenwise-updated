const assert = require("node:assert/strict");
const { test } = require("node:test");
const { estimateCarbonComparison, estimateCarbonForInputs } = require("../dist/services/carbonComparison.js");

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

test("zero positive overrides and blank GPU use registry features in every scenario", async () => {
  const calls = [];
  const result = await estimateCarbonComparison({ estimateCarbon: async request => {
    calls.push(JSON.parse(JSON.stringify(request))); return response(request.input_tokens);
  } }, { ...config, targetModelSizeB: 0, latencyPerInputTokenMs: 0,
    latencyPerOutputTokenMs: 0, targetGpuType: "  " }, 701, 300);
  assert.equal(result.carbonStatus, "ready");
  for (const request of calls) {
    for (const key of ["model_size_b", "latency_per_input_token_ms", "latency_per_output_token_ms", "gpu_type"]) {
      assert.equal(Object.hasOwn(request, key), false);
    }
  }
});

test("positive overrides are preserved, including valid zero benchmark scores", async () => {
  const calls = [];
  await estimateCarbonForInputs({ estimateCarbon: async request => {
    calls.push(JSON.parse(JSON.stringify(request))); return response(request.input_tokens);
  } }, { ...config, targetModelSizeB: 8, latencyPerInputTokenMs: .8,
    latencyPerOutputTokenMs: 2.2, targetGpuType: " A100 ", targetMmluProScore: 0, targetBbhScore: 0 }, [100, 50, 70]);
  for (const request of calls) {
    assert.equal(request.model_size_b, 8);
    assert.equal(request.latency_per_input_token_ms, .8);
    assert.equal(request.latency_per_output_token_ms, 2.2);
    assert.equal(request.gpu_type, "A100");
    assert.equal(request.mmlu_pro_score, 0);
    assert.equal(request.bbh_score, 0);
  }
});

test("invalid feature overrides fail with the setting name before making requests", async () => {
  for (const key of ["targetModelSizeB", "latencyPerInputTokenMs", "latencyPerOutputTokenMs"]) {
    for (const value of [-1, NaN, Infinity]) {
      await assert.rejects(estimateCarbonForInputs({ estimateCarbon: async () => assert.fail("Unexpected request") },
        { ...config, [key]: value }, [100, 50]), new RegExp(`tokenWise\\.${key}`));
    }
  }
  for (const key of ["targetMmluProScore", "targetBbhScore"]) {
    for (const value of [-1, 1.1, NaN, Infinity]) {
      await assert.rejects(estimateCarbonForInputs({ estimateCarbon: async () => assert.fail("Unexpected request") },
        { ...config, [key]: value }, [100, 50]), new RegExp(`tokenWise\\.${key}`));
    }
  }
});

test("invalid required scenario settings produce actionable errors", async () => {
  for (const [key, values] of [["expectedOutputTokens", [0, -1, 1.5, NaN]], ["carbonIntensityGPerKwh", [0, -1, Infinity]]]) {
    for (const value of values) {
      await assert.rejects(estimateCarbonComparison({ estimateCarbon: async () => assert.fail("Unexpected request") },
        { ...config, [key]: value }, 100, 50), new RegExp(`tokenWise\\.${key}`));
    }
  }
});

test("all three strategies use identical carbon assumptions and preserve input ordering", async () => {
  const calls = [];
  const estimates = await estimateCarbonForInputs({ estimateCarbon: async request => {
    calls.push(request); return response(request.input_tokens);
  } }, config, [700, 100, 300]);
  assert.deepEqual(estimates.map(item => item.co2Grams), [.7, .1, .3]);
  assert.deepEqual(calls.map(({ input_tokens, ...scenario }) => scenario), [calls[0], calls[0], calls[0]].map(({ input_tokens, ...scenario }) => scenario));
});
