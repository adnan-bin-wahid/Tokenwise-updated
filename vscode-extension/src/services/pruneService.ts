import * as vscode from "vscode";
import { PruneResultViewModel, PruningInputTrace } from "../types";
import { TokenWiseApiClient } from "./apiClient";
import { getTokenWiseConfig } from "./config";
import { estimateCarbonComparison } from "./carbonComparison";

export class PruneService {
  private sessionCo2GramsSaved = 0;

  public constructor(private readonly backendUrl?: (start: boolean) => Promise<string | undefined>) {}

  private async client(resource?: vscode.Uri, start = true) {
    if (!vscode.workspace.isTrusted || vscode.env.remoteName) {
      throw new Error("Pruning requires a trusted local workspace.");
    }
    const cfg = getTokenWiseConfig(resource);
    if (this.backendUrl) {
      const url = await this.backendUrl(start);
      if (!url) { throw new Error("Run TokenWise: Set Up Backend, then retry pruning."); }
      cfg.apiUrl = url;
    }
    return { cfg, client: new TokenWiseApiClient(cfg) };
  }

  public async checkHealth(): Promise<string> {
    const { client } = await this.client(undefined, false);
    const health = await client.health();
    return [
      `Status: ${health.status}`,
      `Pruner: ${health.model_loaded ? "loaded" : "missing"}`,
      `Carbon models: ${health.carbon_models_loaded ? "loaded" : "missing"}`,
      `Device: ${health.device ?? "n/a"}`,
    ].join(" | ");
  }

  public async prune(query: string, code: string, threshold: number, input?: {
    resource: vscode.Uri; mode: "selected_file" | "selected_excerpt"; firstLine: number;
  }): Promise<PruneResultViewModel> {
    const { cfg, client } = await this.client(input?.resource);
    const response = await client.prune({ query, code, threshold });

    if (response.error_msg) {
      throw new Error(response.error_msg);
    }
    for (const value of [response.origin_token_cnt, response.left_token_cnt, response.model_input_token_cnt]) {
      if (!Number.isInteger(value) || value < 0) { throw new Error("Invalid pruning token counts returned by backend."); }
    }
    if (response.line_scores && Object.entries(response.line_scores).some(([line, score]) =>
      !/^[1-9][0-9]*$/.test(line) || !Number.isFinite(score) || score < 0 || score > 1)) {
      throw new Error("Invalid line relevance scores returned by backend.");
    }
    if (!Number.isFinite(response.score) || response.score < 0 || response.score > 1
      || typeof response.pruned_code !== "string" || !Array.isArray(response.kept_frags)
      || response.kept_frags.some(line => !Number.isInteger(line) || line < 1 || line > code.split(/\r\n|\r|\n/).length)) {
      throw new Error("Invalid pruning result returned by backend.");
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
      lineScores: response.line_scores,
      input_trace: input ? {
        mode: input.mode, current_query: query, effective_query: query,
        scope: input.resource.fsPath, first_line: input.firstLine, threshold,
        history_text: "", history_source: "none",
      } satisfies PruningInputTrace : undefined,
    };

    if (!cfg.enableCarbonEstimation) {
      result.carbonStatus = "disabled";
      return result;
    }

    if (!response.origin_token_cnt || !response.left_token_cnt) {
      result.carbonStatus = "unavailable";
      result.carbonError = "No retained source tokens; a source-only carbon comparison is not available.";
      return result;
    }
    try {
      Object.assign(result, await estimateCarbonComparison(client, cfg, response.origin_token_cnt, response.left_token_cnt));
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
