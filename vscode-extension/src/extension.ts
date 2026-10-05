import * as vscode from "vscode";
import { PruneService } from "./services/pruneService";
import { ResultPanel } from "./ui/resultPanel";
import { createPruneSelectedCommand } from "./commands/pruneSelected";
import { createPruneCurrentFileCommand } from "./commands/pruneCurrentFile";
import { createCheckHealthCommand } from "./commands/checkHealth";
import { createBuildRepositoryContextCommand } from "./commands/buildRepositoryContext";
import { AutomaticContextMonitor } from "./services/automaticContext";
import { createEnableAutomaticContextCommand } from "./commands/enableAutomaticContext";
import { BackendManager } from "./services/backendManager";
import { UninstallTracker } from "./services/uninstallTracker";
import { RepositoryIndexSync } from "./services/repositoryIndexSync";
import { createCompareContextStrategiesCommand } from "./commands/compareContextStrategies";
import { createDemonstratePruningCommand } from "./commands/demonstratePruning";

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  const tracker = new UninstallTracker(context);
  try { await tracker.prepare(); }
  catch (error) { await vscode.window.showErrorMessage(`TokenWise cannot register uninstall cleanup: ${String(error)}`); return; }
  const service = new PruneService((start) => backend.backgroundUrl(start));
  const panel = new ResultPanel();
  const backend: BackendManager = new BackendManager(context, () => tracker.prepare(), () => indexSync.backendChanged());
  const indexSync = new RepositoryIndexSync(context, (start) => backend.backgroundUrl(start));

  const statusItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100,
  );
  statusItem.text = "$(filter) TokenWise";
  statusItem.tooltip = "Enable automatic repository context or inspect the TokenWise backend";
  statusItem.command = "tokenwise.enableAutomaticContext";
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

  const automaticMonitor = new AutomaticContextMonitor(statusItem, panel, context.extensionUri);
  context.subscriptions.push(
    statusItem,
    backend,
    automaticMonitor,
    indexSync,
    vscode.commands.registerCommand(
      "tokenwise.enableAutomaticContext",
      createEnableAutomaticContextCommand(context, (folder) => {
        automaticMonitor.configured(folder);
        indexSync.configured(folder);
      }, () => backend.setup()),
    ),
    vscode.commands.registerCommand("tokenwise.setUpBackend", () => backend.setup()),
    vscode.commands.registerCommand("tokenwise.startBackend", () => backend.start()),
    vscode.commands.registerCommand("tokenwise.showDiagnostics", () => backend.diagnostics()),
    vscode.commands.registerCommand("tokenwise.openSetupGuide", () => backend.guide()),
    vscode.commands.registerCommand("tokenwise.compareContextStrategies",
      createCompareContextStrategiesCommand(panel, context.extensionUri, () => backend.backgroundUrl(true))),
    vscode.commands.registerCommand("tokenwise.demonstratePruning",
      createDemonstratePruningCommand(service, panel, context.extensionUri, () => backend.backgroundUrl(true))),
    vscode.commands.registerCommand("tokenwise.removeAllLocalData", () => tracker.removeAll(async () => {
      indexSync.pause(); await backend.cancelSetup();
    })),
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
  void backend.welcome().catch(() => undefined);
}

export function deactivate(): void {
  // no-op
}
