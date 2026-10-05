import * as vscode from "vscode";
import { TokenWiseApiClient } from "../services/apiClient";
import { getTokenWiseConfig } from "../services/config";
import { estimateCarbonForInputs } from "../services/carbonComparison";
import { ResultPanel } from "../ui/resultPanel";

export function createCompareContextStrategiesCommand(
  panel: ResultPanel, extensionUri: vscode.Uri, backendUrl: () => Promise<string | undefined>,
) {
  return async () => {
    const editor = vscode.window.activeTextEditor;
    if (!vscode.workspace.isTrusted || vscode.env.remoteName) {
      await vscode.window.showWarningMessage("Use a trusted local Python repository for comparison."); return;
    }
    const folder = editor && vscode.workspace.getWorkspaceFolder(editor.document.uri);
    if (!editor || !folder || folder.uri.scheme !== "file" || editor.document.languageId !== "python") {
      await vscode.window.showWarningMessage("Open a saved Python file inside the repository to choose the manual baseline."); return;
    }
    if (editor.document.isDirty) {
      await vscode.window.showWarningMessage("Save the Python file before comparing the same repository snapshot."); return;
    }
    const selected = editor.document.getText(editor.selection).trim();
    const version = editor.document.version;
    const query = (await vscode.window.showInputBox({
      prompt: "Enter the same task for all three context strategies",
      placeHolder: "Explain account lockout and the tests covering expiry and reset.",
    }))?.trim();
    if (!query) { return; }
    await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification,
      title: "TokenWise: comparing context strategies", cancellable: false }, async () => {
      try {
        const cfg = getTokenWiseConfig(folder.uri);
        const url = await backendUrl();
        if (!url) { throw new Error("Run TokenWise: Set Up Backend, then retry this command."); }
        if (editor.document.isDirty || editor.document.version !== version) {
          throw new Error("The selected file changed. Save it and retry the comparison.");
        }
        const client = new TokenWiseApiClient({ ...cfg, apiUrl: url });
        const response = await client.compareWorkspace({
          query, workspace_root: folder.uri.fsPath, selection_file: editor.document.uri.fsPath,
          selection_text: selected || undefined, language: "python", diagnostics: [],
          threshold: cfg.defaultThreshold, token_budget: cfg.repositoryTokenBudget, max_candidates: 8,
        });
        const comparison = response.comparison;
        if (!comparison?.methods?.length) { throw new Error("The backend returned no comparison packets."); }
        comparison.carbonStatus = cfg.enableCarbonEstimation ? "unavailable" : "disabled";
        if (cfg.enableCarbonEstimation) {
          try {
            const estimates = await estimateCarbonForInputs(client, cfg, comparison.methods.map(item => item.input_tokens));
            comparison.methods.forEach((item, index) => { item.carbon = estimates[index]; });
            comparison.carbonStatus = "ready";
            comparison.notes.push(`Carbon scenario: ${estimates[0].modelFamily}; ${cfg.expectedOutputTokens} expected output tokens; ${estimates[0].carbonIntensityGPerKwh} gCO2/kWh. This is not the agent's detected hardware.`);
          } catch (error) { comparison.carbonError = String(error); }
        }
        panel.showWorkspaceResult(response, extensionUri);
      } catch (error) { await vscode.window.showErrorMessage(`TokenWise: ${String(error)}`); }
    });
  };
}
