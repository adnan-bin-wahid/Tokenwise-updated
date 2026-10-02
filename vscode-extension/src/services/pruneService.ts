import * as vscode from "vscode";
import { CarbonEstimateResponse, PruneResultViewModel } from "../types";
import { TokenWiseApiClient } from "./apiClient";
import { getTokenWiseConfig } from "./config";
import { countTokens } from "./tokenCounter";

export class PruneService {
  private sessionCo2GramsSaved = 0;

  private mapRemoteEstimate(response: CarbonEstimateResponse) {
    return {
      prefillJoules: response.prefill_joules,
      decodeJoules: response.decode_joules,
      totalJoules: response.total_joules,
      co2Grams: response.co2_grams,
      carbonIntensityGPerKwh: response.carbon_intensity_g_per_kwh,
      modelFamily: response.model_name,
      prefillRoute: response.prefill_route,
      decodeRoute: response.decode_route,
      featuresSource: response.features_source,
    } as const;
  }

  public async checkHealth(): Promise<string> {
    const client = new TokenWiseApiClient(getTokenWiseConfig());
    const health = await client.health();
    return [
      `Status: ${health.status}`,
      `Pruner: ${health.model_loaded ? "loaded" : "missing"}`,
      `Carbon models: ${health.carbon_models_loaded ? "loaded" : "missing"}`,
      `Device: ${health.device ?? "n/a"}`,
    ].join(" | ");
  }

  public async prune(query: string, code: string, threshold: number): Promise<PruneResultViewModel> {
    const cfg = getTokenWiseConfig();
    const client = new TokenWiseApiClient(cfg);
    const response = await client.prune({ query, code, threshold });

    if (response.error_msg) {
      throw new Error(response.error_msg);
    }

    const reductionPercent = response.origin_token_cnt > 0
      ? ((response.origin_token_cnt - response.left_token_cnt) / response.origin_token_cnt) * 100
      : 0;

    const result: PruneResultViewModel = {
      query,
      score: response.score,
      originalCode: code,
      prunedCode: response.pruned_code,
      originTokenCount: response.origin_token_cnt,
      prunedTokenCount: response.left_token_cnt,
      modelInputTokenCount: response.model_input_token_cnt,
      reductionPercent,
      keptFrags: response.kept_frags,
    };

    if (!cfg.enableCarbonEstimation) {
      return result;
    }

    const originalInputTokens = Math.max(1, countTokens(code));
    const prunedInputTokens = Math.max(1, countTokens(response.pruned_code));
    const common = {
      output_tokens: cfg.expectedOutputTokens,
      model_name: cfg.targetModelName,
      model_size_b: cfg.targetModelSizeB,
      gpu_type: cfg.targetGpuType,
      latency_per_input_token_ms: cfg.latencyPerInputTokenMs,
      latency_per_output_token_ms: cfg.latencyPerOutputTokenMs,
      mmlu_pro_score: cfg.targetMmluProScore,
      bbh_score: cfg.targetBbhScore,
      carbon_intensity_g_per_kwh: cfg.carbonIntensityGPerKwh,
    };

    try {
      const [beforeRemote, afterRemote] = await Promise.all([
        client.estimateCarbon({ ...common, input_tokens: originalInputTokens }),
        client.estimateCarbon({ ...common, input_tokens: prunedInputTokens }),
      ]);
      const carbonBefore = this.mapRemoteEstimate(beforeRemote);
      const carbonAfter = this.mapRemoteEstimate(afterRemote);
      result.carbonBefore = carbonBefore;
      result.carbonAfter = carbonAfter;
      result.carbonSavings = {
        prefillJoulesSaved: Math.max(0, carbonBefore.prefillJoules - carbonAfter.prefillJoules),
        decodeJoulesSaved: Math.max(0, carbonBefore.decodeJoules - carbonAfter.decodeJoules),
        totalJoulesSaved: Math.max(0, carbonBefore.totalJoules - carbonAfter.totalJoules),
        co2GramsSaved: Math.max(0, carbonBefore.co2Grams - carbonAfter.co2Grams),
      };
      this.sessionCo2GramsSaved += result.carbonSavings.co2GramsSaved;
    } catch (error) {
      void vscode.window.showWarningMessage(
        `TokenWise: pruning succeeded, but trained carbon estimation was unavailable (${String(error)}).`,
      );
    }

    return result;
  }

  public getSessionCo2GramsSaved(): number {
    return this.sessionCo2GramsSaved;
  }
}
