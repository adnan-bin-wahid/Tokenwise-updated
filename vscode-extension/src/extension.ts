import * as vscode from "vscode";
import { PruneService } from "./services/pruneService";
import { ResultPanel } from "./ui/resultPanel";
import { createPruneSelectedCommand } from "./commands/pruneSelected";
import { createPruneCurrentFileCommand } from "./commands/pruneCurrentFile";
import { createCheckHealthCommand } from "./commands/checkHealth";
import { createBuildRepositoryContextCommand } from "./commands/buildRepositoryContext";

export function activate(context: vscode.ExtensionContext): void {
  const service = new PruneService();
  const panel = new ResultPanel();

  const statusItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100,
  );
  statusItem.text = "$(filter) TokenWise";
  statusItem.tooltip = "TokenWise is ready";
  statusItem.command = "tokenwise.checkHealth";
  statusItem.show();

  const refreshStatus = () => {
    const co2Saved = service.getSessionCo2GramsSaved();
    if (co2Saved > 0) {
      statusItem.text = `$(leaf) TokenWise ${co2Saved.toFixed(6)}g saved`;
      statusItem.tooltip = "TokenWise session carbon savings";
      return;
    }

    statusItem.text = "$(filter) TokenWise";
    statusItem.tooltip = "TokenWise is ready";
  };

  context.subscriptions.push(
    statusItem,
    vscode.commands.registerCommand(
      "tokenwise.pruneSelected",
      createPruneSelectedCommand(
        service,
        panel,
        context.extensionUri,
        refreshStatus,
      ),
    ),
    vscode.commands.registerCommand(
      "tokenwise.pruneCurrentFile",
      createPruneCurrentFileCommand(
        service,
        panel,
        context.extensionUri,
        refreshStatus,
      ),
    ),
    vscode.commands.registerCommand(
      "tokenwise.checkHealth",
      createCheckHealthCommand(service),
    ),
    vscode.commands.registerCommand(
      "tokenwise.buildRepositoryContext",
      createBuildRepositoryContextCommand(panel, context.extensionUri),
    ),
  );
}

export function deactivate(): void {
  // no-op
}
