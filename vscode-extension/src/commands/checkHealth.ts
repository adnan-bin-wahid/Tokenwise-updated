import * as vscode from "vscode";
import { PruneService } from "../services/pruneService";

export function createCheckHealthCommand(service: PruneService) {
  return async () => {
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "TokenWise: checking backend health",
      },
      async () => {
        try {
          const status = await service.checkHealth();
          void vscode.window.showInformationMessage(
            `TokenWise backend healthy. ${status}`,
          );
        } catch (error) {
          void vscode.window.showErrorMessage(
            `TokenWise health check failed: ${String(error)}`,
          );
        }
      },
    );
  };
}
