import * as vscode from "vscode";
import { PruneService } from "../services/pruneService";
import { getTokenWiseConfig } from "../services/config";
import { askQuery, askThreshold, getSelectedOrFullCode } from "../utils/editor";
import { ResultPanel } from "../ui/resultPanel";

export function createPruneSelectedCommand(
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

    const { code, isSelection } = getSelectedOrFullCode(editor);
    if (!isSelection) {
      void vscode.window.showWarningMessage(
        "TokenWise: select code first, or use Prune Current File.",
      );
      return;
    }

    const query = await askQuery();
    if (!query) {
      return;
    }

    const cfg = getTokenWiseConfig();
    const threshold = await askThreshold(cfg.defaultThreshold);
    if (threshold === undefined) {
      return;
    }

    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "TokenWise: pruning selected code",
      },
      async () => {
        try {
          const result = await service.prune(query, code, threshold);
          if (cfg.autoOpenResultPanel) {
            panel.show(result, extensionUri);
          }
          onSuccess?.();
          void vscode.window.showInformationMessage(
            `TokenWise: done. Token reduction ${result.reductionPercent.toFixed(2)}%.`,
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
