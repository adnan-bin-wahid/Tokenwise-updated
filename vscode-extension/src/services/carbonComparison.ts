import { CarbonEstimateResponse, CarbonEstimateViewModel, CarbonImpactViewModel } from "../types";
import { TokenWiseApiClient } from "./apiClient";
import { TokenWiseConfig } from "./config";

function optionalPositive(value: number | undefined, setting: string): number | undefined {
  // Some editors save an unset numeric override as zero. Use the registry instead.
  if (value === undefined || value === 0) { return undefined; }
  if (!Number.isFinite(value) || value < 0) {
    throw new Error(`tokenWise.${setting} must be positive, or zero for automatic model features.`);
  }
  return value;
}

function optionalBenchmark(value: number | undefined, setting: string): number | undefined {
  if (value !== undefined && (!Number.isFinite(value) || value < 0 || value > 1)) {
    throw new Error(`tokenWise.${setting} must be between 0 and 1, or unset.`);
  }
  return value;
}

function mapEstimate(item: CarbonEstimateResponse) {
  const values = [item.prefill_joules, item.decode_joules, item.total_joules,
    item.co2_grams, item.carbon_intensity_g_per_kwh];
  const routes = new Set(["xgboost_interpolation", "ridge_extrapolation"]);
  if (values.some(value => typeof value !== "number" || !Number.isFinite(value) || value < 0)
    || item.carbon_intensity_g_per_kwh <= 0 || typeof item.model_name !== "string"
    || typeof item.features_source !== "string" || !routes.has(item.prefill_route) || !routes.has(item.decode_route)) {
    throw new Error("The backend returned an invalid carbon estimate.");
  }
  return {
    prefillJoules: item.prefill_joules, decodeJoules: item.decode_joules,
    totalJoules: item.total_joules, co2Grams: item.co2_grams,
    carbonIntensityGPerKwh: item.carbon_intensity_g_per_kwh,
    modelFamily: item.model_name, prefillRoute: item.prefill_route,
    decodeRoute: item.decode_route, featuresSource: item.features_source,
  };
}

export async function estimateCarbonForInputs(
  client: Pick<TokenWiseApiClient, "estimateCarbon">, cfg: TokenWiseConfig, inputs: number[],
): Promise<CarbonEstimateViewModel[]> {
  if (!inputs.every(value => Number.isInteger(value) && value > 0)) {
    throw new Error("Carbon comparison requires positive token counts for all contexts.");
  }
  if (!Number.isInteger(cfg.expectedOutputTokens) || cfg.expectedOutputTokens <= 0) {
    throw new Error("tokenWise.expectedOutputTokens must be a positive integer (default: 256).");
  }
  if (!Number.isFinite(cfg.carbonIntensityGPerKwh) || cfg.carbonIntensityGPerKwh <= 0) {
    throw new Error("tokenWise.carbonIntensityGPerKwh must be positive (default: 475).");
  }
  const common = {
    output_tokens: cfg.expectedOutputTokens, model_name: cfg.targetModelName,
    model_size_b: optionalPositive(cfg.targetModelSizeB, "targetModelSizeB"),
    gpu_type: cfg.targetGpuType?.trim() || undefined,
    latency_per_input_token_ms: optionalPositive(cfg.latencyPerInputTokenMs, "latencyPerInputTokenMs"),
    latency_per_output_token_ms: optionalPositive(cfg.latencyPerOutputTokenMs, "latencyPerOutputTokenMs"),
    mmlu_pro_score: optionalBenchmark(cfg.targetMmluProScore, "targetMmluProScore"),
    bbh_score: optionalBenchmark(cfg.targetBbhScore, "targetBbhScore"),
    carbon_intensity_g_per_kwh: cfg.carbonIntensityGPerKwh,
  };
  return Promise.all(inputs.map(async input_tokens => mapEstimate(await client.estimateCarbon({ ...common, input_tokens }))));
}

export async function estimateCarbonComparison(
  client: Pick<TokenWiseApiClient, "estimateCarbon">, cfg: TokenWiseConfig,
  beforeTokens: number, afterTokens: number,
  baseline: "formatted-context" | "source-only" = "source-only",
): Promise<CarbonImpactViewModel> {
  if (!cfg.enableCarbonEstimation) { return { carbonStatus: "disabled" }; }
  const [carbonBefore, carbonAfter] = await estimateCarbonForInputs(client, cfg, [beforeTokens, afterTokens]);
  return {
    carbonBefore, carbonAfter, carbonStatus: "ready", carbonBaseline: baseline,
    carbonSavings: {
      prefillJoulesSaved: carbonBefore.prefillJoules - carbonAfter.prefillJoules,
      decodeJoulesSaved: carbonBefore.decodeJoules - carbonAfter.decodeJoules,
      totalJoulesSaved: carbonBefore.totalJoules - carbonAfter.totalJoules,
      co2GramsSaved: carbonBefore.co2Grams - carbonAfter.co2Grams,
    },
  };
}
