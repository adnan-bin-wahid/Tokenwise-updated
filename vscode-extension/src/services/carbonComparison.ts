import { CarbonEstimateResponse, CarbonEstimateViewModel, CarbonImpactViewModel } from "../types";
import { TokenWiseApiClient } from "./apiClient";
import { TokenWiseConfig } from "./config";

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
  const common = {
    output_tokens: cfg.expectedOutputTokens, model_name: cfg.targetModelName,
    model_size_b: cfg.targetModelSizeB, gpu_type: cfg.targetGpuType,
    latency_per_input_token_ms: cfg.latencyPerInputTokenMs,
    latency_per_output_token_ms: cfg.latencyPerOutputTokenMs,
    mmlu_pro_score: cfg.targetMmluProScore, bbh_score: cfg.targetBbhScore,
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
