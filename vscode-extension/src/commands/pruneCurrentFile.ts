import * as vscode from "vscode";
import { PruneService } from "../services/pruneService";
import { getTokenWiseConfig } from "../services/config";
import { askQuery, askThreshold } from "../utils/editor";
import { ResultPanel } from "../ui/resultPanel";

export function createPruneCurrentFileCommand(
  service: PruneService,
  panel: ResultPanel,
  extensionUri: vscode.Uri,
  onSuccess?: () => void,
) {
  return async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      void vscode.window.showWarningMessage("TokenWise: no active editor.");
      return;
    }

    const code = editor.document.getText();
    const resource = editor.document.uri;
    const query = await askQuery();
    if (!query) {
      return;
    }

    const cfg = getTokenWiseConfig(resource);
    const threshold = await askThreshold(cfg.defaultThreshold);
    if (threshold === undefined) {
      return;
    }

    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "TokenWise: pruning current file",
      },
      async () => {
        try {
          const result = await service.prune(query, code, threshold, { resource, mode: "selected_file", firstLine: 1 });
          if (cfg.autoOpenResultPanel) {
            panel.show(result, extensionUri);
          }
          onSuccess?.();
          void vscode.window.showInformationMessage(
            `TokenWise: done. Source ${result.reductionPercent < 0 ? "increase" : "reduction"} ${Math.abs(result.reductionPercent).toFixed(2)}%.`,
          );
        } catch (error) {
          void vscode.window.showErrorMessage(
            `TokenWise prune failed: ${String(error)}`,
          );
        }
      },
    );
  };
}
