import * as vscode from "vscode";
import { localStoragePath } from "./extensionPaths";
import { adoptOpenWorkspace, buildCleanupPlan, registerLifecycle } from "./cleanupRegistry";
import { runCleanup } from "./uninstallCleanup";

export class UninstallTracker {
  public constructor(private readonly context: vscode.ExtensionContext) {}

  public async prepare(): Promise<void> {
    if (vscode.env.remoteName || !vscode.workspace.isTrusted) { return; }
    const storage = localStoragePath(this.context);
    await registerLifecycle(storage, this.context.extensionUri.fsPath);
    for (const folder of vscode.workspace.workspaceFolders ?? []) {
      if (folder.uri.scheme === "file") { await adoptOpenWorkspace(storage, folder.uri.fsPath); }
    }
  }

  public async removeAll(cancelSetup: () => void): Promise<void> {
    if (!vscode.workspace.isTrusted || vscode.env.remoteName) { await vscode.window.showWarningMessage("Clean up TokenWise in a trusted local window."); return; }
    const approval = await vscode.window.showWarningMessage("Remove all local TokenWise data?", {
      modal: true,
      detail: "Removes managed environments/model downloads, tracked repository integration, context records, and TokenWise preferences. Existing backend checkouts, Python itself, unrelated files, and customized rules/launchers are preserved. Finish active agent commands first. A future setup must download its backend again.",
    }, "Remove Data");
    if (approval !== "Remove Data") { return; }
    try {
      cancelSetup();
      const result = await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: "Removing TokenWise data", cancellable: false },
        async () => runCleanup(await buildCleanupPlan(this.context.extensionUri.fsPath)));
      if (result.warnings.length || result.preserved.length) {
        const output = vscode.window.createOutputChannel("TokenWise Cleanup");
        this.context.subscriptions.push(output); output.appendLine(JSON.stringify(result, null, 2)); output.show(true);
        await vscode.window.showWarningMessage("TokenWise cleanup preserved customized/unavailable files. See Output > TokenWise Cleanup. Fix the listed issues and retry before uninstalling.");
      } else { await vscode.window.showInformationMessage("TokenWise local data removed. You can uninstall the extension or set it up again."); }
    } catch (error) { await vscode.window.showErrorMessage(`TokenWise cleanup failed: ${String(error)}`); }
  }
}
