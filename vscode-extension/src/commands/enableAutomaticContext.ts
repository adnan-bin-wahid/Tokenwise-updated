import * as path from "node:path";
import * as vscode from "vscode";
import {
  configureAutomaticContext, discoverRegisteredBackend, registerBackend, validateBackendInstallation,
} from "../services/automaticSetup";

function localStoragePath(context: vscode.ExtensionContext): string {
  const storage = context.globalStorageUri;
  // Desktop Antigravity maps vscode-userdata to the local file provider.
  if (!["file", "vscode-userdata"].includes(storage.scheme)
    || (storage.scheme === "vscode-userdata" && storage.authority)) {
    throw new Error(`Unsupported extension storage URI (${storage.scheme}). Local file-backed storage is required.`);
  }
  const nativePath = storage.with({ scheme: "file" }).fsPath;
  if (!path.isAbsolute(nativePath)) {
    throw new Error("The extension storage directory must have an absolute local path.");
  }
  return nativePath;
}

export function createEnableAutomaticContextCommand(
  context: vscode.ExtensionContext,
  onConfigured: (folder: vscode.WorkspaceFolder) => void,
): () => Promise<void> {
  return async () => {
    if (!vscode.workspace.isTrusted) {
      await vscode.window.showWarningMessage("Trust this workspace before enabling TokenWise scripts and agent rules.");
      return;
    }
    if (process.platform !== "win32") {
      await vscode.window.showErrorMessage("Automatic Antigravity setup currently requires a local Windows workspace.");
      return;
    }
    const folders = vscode.workspace.workspaceFolders ?? [];
    if (!folders.length) {
      await vscode.window.showInformationMessage("Open a Python repository folder before enabling TokenWise automatic context.");
      return;
    }
    const selected = folders.length === 1 ? { folder: folders[0] } : await vscode.window.showQuickPick(
      folders.map((folder) => ({ label: folder.name, description: folder.uri.fsPath, folder })),
      { title: "Enable TokenWise for a workspace", placeHolder: "Select the Python repository" },
    );
    if (!selected) { return; }
    const folder = selected.folder;
    if (folder.uri.scheme !== "file" || vscode.env.remoteName) {
      await vscode.window.showErrorMessage(`Automatic context setup supports local folders only, not remote or virtual workspaces. Workspace scheme: ${folder.uri.scheme}; remote: ${vscode.env.remoteName ?? "none"}.`);
      return;
    }
    try {
      const storagePath = localStoragePath(context);
      const config = vscode.workspace.getConfiguration("tokenWise");
      const configured = config.get<string>("backendInstallationPath", "").trim();
      let installation: string | undefined;
      if (configured) {
        try { installation = await validateBackendInstallation(configured); }
        catch { await vscode.window.showWarningMessage("The saved TokenWise backend is unavailable. Select a complete installation below."); }
      }
      installation ??= await discoverRegisteredBackend(storagePath);
      if (!installation && context.extensionUri.scheme === "file") {
        try { installation = await validateBackendInstallation(path.dirname(context.extensionUri.fsPath)); }
        catch { /* A packaged extension is separate from its backend installation. */ }
      }
      if (!installation) {
        const chosen = await vscode.window.showOpenDialog({
          title: "Select the TokenWise backend installation (contains .venv, scripts, and swe-pruner)",
          canSelectFolders: true, canSelectFiles: false, canSelectMany: false,
          openLabel: "Use TokenWise Backend",
        });
        if (!chosen?.length) { return; }
        if (chosen[0].scheme !== "file") { throw new Error("Choose a local TokenWise backend folder."); }
        installation = await validateBackendInstallation(chosen[0].fsPath);
      }
      const approval = await vscode.window.showInformationMessage(
        `Enable automatic context in ${folder.name}?`,
        { modal: true, detail: `Backend: ${installation}\n\nTokenWise will add workspace launchers and an always-on agent rule, merge its hook and settings, and ignore local context files. Other rules and hook handlers are preserved. All configured workspaces share this backend installation.` },
        "Enable",
      );
      if (approval !== "Enable") { return; }
      if (!vscode.workspace.isTrusted || !vscode.workspace.workspaceFolders?.some((item) => item.uri.toString() === folder.uri.toString())) {
        throw new Error("The workspace changed or is no longer trusted. Run the command again.");
      }
      await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification, title: "Enabling TokenWise automatic context", cancellable: false,
      }, async () => {
        const backend = await registerBackend(installation!, storagePath);
        await configureAutomaticContext(folder.uri.fsPath, backend, path.join(context.extensionUri.fsPath, "resources", "automatic-context"));
      });
      try {
        await config.update("backendInstallationPath", installation, vscode.ConfigurationTarget.Global);
      } catch {
        await vscode.window.showWarningMessage("TokenWise is enabled. The backend registration was saved, but the user setting could not be updated.");
      }
      onConfigured(folder);
      await vscode.window.showInformationMessage(`TokenWise is enabled for ${folder.name}. Start a new Antigravity chat and enter your repository prompt.`);
    } catch (error) {
      await vscode.window.showErrorMessage(`TokenWise setup failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  };
}
