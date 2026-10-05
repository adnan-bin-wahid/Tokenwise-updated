import * as vscode from "vscode";
import { PruneResultViewModel } from "../types";
import { TokenWiseApiClient } from "./apiClient";
import { getTokenWiseConfig } from "./config";
import { countTokens } from "./tokenCounter";
import { estimateCarbonComparison } from "./carbonComparison";

export class PruneService {
  private sessionCo2GramsSaved = 0;

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
      result.carbonStatus = "disabled";
      return result;
    }

    const originalInputTokens = Math.max(1, countTokens(code));
    const prunedInputTokens = Math.max(1, countTokens(response.pruned_code));
    try {
      Object.assign(result, await estimateCarbonComparison(client, cfg, originalInputTokens, prunedInputTokens));
      this.sessionCo2GramsSaved += Math.max(0, result.carbonSavings?.co2GramsSaved ?? 0);
    } catch (error) {
      result.carbonStatus = "unavailable";
      result.carbonError = String(error);
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
