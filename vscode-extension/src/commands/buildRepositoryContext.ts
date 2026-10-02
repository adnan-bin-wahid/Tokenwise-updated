import * as vscode from "vscode";
import { TokenWiseApiClient } from "../services/apiClient";
import { getTokenWiseConfig } from "../services/config";
import { ResultPanel } from "../ui/resultPanel";

export function createBuildRepositoryContextCommand(
  panel: ResultPanel,
  extensionUri: vscode.Uri,
) {
  return async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      void vscode.window.showWarningMessage("TokenWise: no active editor.");
      return;
    }

    const document = editor.document;
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
    if (!workspaceFolder) {
      void vscode.window.showWarningMessage("TokenWise: the active file is not inside an open workspace.");
      return;
    }
    if (document.languageId !== "python") {
      void vscode.window.showWarningMessage(
        "TokenWise repository-context mode currently supports Python workspaces only.",
      );
      return;
    }

    const rawQuery = await vscode.window.showInputBox({
      prompt: "Describe the repository task or information you need",
      placeHolder: "e.g. Trace account lockout and successful authentication logic",
    });
    const query = rawQuery?.trim();
    if (!query) {
      return;
    }

    const cfg = getTokenWiseConfig();
    const selection = editor.selection;
    const selectedCode = document.getText(selection).trim() || undefined;
    let currentSymbol: string | undefined;
    if (!selectedCode) {
      const wordRange = document.getWordRangeAtPosition(selection.active);
      if (wordRange) {
        currentSymbol = document.getText(wordRange);
      }
    }

    const diagnostics = vscode.languages
      .getDiagnostics(document.uri)
      .filter(
        (item) =>
          item.severity === vscode.DiagnosticSeverity.Error ||
          item.severity === vscode.DiagnosticSeverity.Warning,
      )
      .map((item) => item.message);

    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "TokenWise: building bounded repository context...",
        cancellable: false,
      },
      async () => {
        try {
          const client = new TokenWiseApiClient(cfg);
          const response = await client.pruneWorkspace({
            query,
            workspace_root: workspaceFolder.uri.fsPath,
            active_file: document.uri.fsPath,
            language: document.languageId,
            current_symbol: currentSymbol,
            selected_code: selectedCode,
            diagnostics,
            threshold: cfg.defaultThreshold,
            local_llm_url: cfg.enableLocalGoalModel ? cfg.localLlmUrl : undefined,
            local_llm_model: cfg.enableLocalGoalModel ? cfg.localLlmModelName : undefined,
            token_budget: cfg.repositoryTokenBudget,
          });

          if (cfg.enableCarbonEstimation && response.original_tokens > 0 && response.pruned_tokens > 0) {
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
              const [before, after] = await Promise.all([
                client.estimateCarbon({ ...common, input_tokens: response.original_tokens }),
                client.estimateCarbon({ ...common, input_tokens: response.pruned_tokens }),
              ]);
              const mapEstimate = (item: typeof before) => ({
                prefillJoules: item.prefill_joules,
                decodeJoules: item.decode_joules,
                totalJoules: item.total_joules,
                co2Grams: item.co2_grams,
                carbonIntensityGPerKwh: item.carbon_intensity_g_per_kwh,
                modelFamily: item.model_name,
                prefillRoute: item.prefill_route,
                decodeRoute: item.decode_route,
                featuresSource: item.features_source,
              });
              response.carbonBefore = mapEstimate(before);
              response.carbonAfter = mapEstimate(after);
              response.carbonSavings = {
                prefillJoulesSaved: Math.max(0, before.prefill_joules - after.prefill_joules),
                decodeJoulesSaved: Math.max(0, before.decode_joules - after.decode_joules),
                totalJoulesSaved: Math.max(0, before.total_joules - after.total_joules),
                co2GramsSaved: Math.max(0, before.co2_grams - after.co2_grams),
              };
            } catch (carbonError) {
              void vscode.window.showWarningMessage(
                `TokenWise: repository context built, but carbon estimation was unavailable (${String(carbonError)}).`,
              );
            }
          }

          panel.showWorkspaceResult(response, extensionUri);
          void vscode.window.showInformationMessage(
            `TokenWise: repository context built (${response.pruned_tokens} packed tokens).`,
          );
        } catch (error) {
          void vscode.window.showErrorMessage(`TokenWise workspace prune failed: ${String(error)}`);
        }
      },
    );
  };
}
