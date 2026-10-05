import * as vscode from "vscode";
import { TokenWiseApiClient } from "../services/apiClient";
import { getTokenWiseConfig } from "../services/config";
import { ResultPanel } from "../ui/resultPanel";
import { estimateCarbonComparison } from "../services/carbonComparison";

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

          if (cfg.enableCarbonEstimation) {
            try {
              Object.assign(response, await estimateCarbonComparison(client, cfg,
                response.raw_context_tokens ?? response.original_tokens, response.pruned_tokens,
                response.raw_context_tokens ? "formatted-context" : "source-only"));
            } catch (carbonError) {
              response.carbonStatus = "unavailable";
              response.carbonError = String(carbonError);
              void vscode.window.showWarningMessage(
                `TokenWise: repository context built, but carbon estimation was unavailable (${String(carbonError)}).`,
              );
            }
          } else {
            response.carbonStatus = "disabled";
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
