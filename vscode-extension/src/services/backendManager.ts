import * as fs from "node:fs/promises";
import * as path from "node:path";
import * as vscode from "vscode";
import { discoverRegisteredBackend, registerBackend, RegisteredBackend, validateBackendInstallation } from "./automaticSetup";
import { localStoragePath } from "./extensionPaths";
import { findPython312, installManagedBackend, runSetupProcess } from "./managedBackend";

export class BackendManager implements vscode.Disposable {
  private readonly output = vscode.window.createOutputChannel("TokenWise Setup");
  private installing = false;
  private activeSetup: AbortController | undefined;

  public constructor(private readonly context: vscode.ExtensionContext) {}

  public async installation(): Promise<string | undefined> {
    const configured = vscode.workspace.getConfiguration("tokenWise").get<string>("backendInstallationPath", "").trim();
    if (configured) { try { return await validateBackendInstallation(configured); } catch { /* Allow repairing a moved installation. */ } }
    return discoverRegisteredBackend(localStoragePath(this.context));
  }

  public async setup(): Promise<string | undefined> {
    if (!vscode.workspace.isTrusted || vscode.env.remoteName) {
      await vscode.window.showWarningMessage("Set up TokenWise in a trusted local window, not a remote workspace.");
      return undefined;
    }
    if (this.installing) { await vscode.window.showInformationMessage("TokenWise backend setup is already running. See Output > TokenWise Setup."); return undefined; }
    const approval = await vscode.window.showInformationMessage("Install the TokenWise backend on this computer?", {
      modal: true, detail: "Requires 64-bit Python 3.12 and about 10 GB of free disk space. Setup creates a private environment in extension user storage and downloads CPU dependencies plus a verified 1.35 GB model from PyTorch, PyPI, and Hugging Face. It does not upload repository code. No Git, Node.js, administrator access, or API key is needed.",
    }, "Install Backend");
    if (approval !== "Install Backend") { return undefined; }
    this.installing = true;
    try {
      const storage = localStoragePath(this.context);
      this.output.appendLine(`TokenWise user storage: ${storage}`);
      const preferred = vscode.workspace.getConfiguration("tokenWise").get<string>("pythonPath", "").trim();
      const python = await findPython312(preferred);
      const result = await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: "TokenWise backend setup", cancellable: true }, async (progress, cancellation) => {
        const abort = new AbortController();
        this.activeSetup = abort;
        const subscription = cancellation.onCancellationRequested(() => abort.abort());
        if (cancellation.isCancellationRequested) { abort.abort(); }
        try {
          return await installManagedBackend(python, path.join(this.context.extensionUri.fsPath, "resources", "backend-bundle"), storage,
            String(this.context.extension.packageJSON.version), {
              signal: abort.signal, log: (line) => this.output.appendLine(line),
              progress: (item) => progress.report({ message: item.total ? `${item.message}: ${Math.floor((item.current ?? 0) / item.total * 100)}%` : item.message }),
            });
        } finally { subscription.dispose(); this.activeSetup = undefined; }
      });
      await registerBackend(result, storage);
      await vscode.workspace.getConfiguration("tokenWise").update("backendInstallationPath", result, vscode.ConfigurationTarget.Global);
      await vscode.window.showInformationMessage("TokenWise backend installation complete.");
      return result;
    } catch (error) {
      this.output.show(true);
      const message = error instanceof Error ? error.message : String(error);
      this.output.appendLine(message);
      const reason = message.split(/\r?\n/).filter(Boolean).at(-1) ?? message;
      const choice = await vscode.window.showErrorMessage(`TokenWise setup did not complete: ${reason.slice(0, 300)}`, "Read Setup Guide", ...(message.includes("Python 3.12") ? ["Install Python"] : []));
      if (choice === "Read Setup Guide") { await this.guide(); }
      if (choice === "Install Python") { await vscode.env.openExternal(vscode.Uri.parse("https://www.python.org/downloads/")); }
      return undefined;
    } finally { this.installing = false; }
  }

  private async registration(): Promise<RegisteredBackend> {
    const installation = await this.installation();
    if (!installation) { throw new Error("No complete backend is registered. Run TokenWise: Set Up Backend first."); }
    return registerBackend(installation, localStoragePath(this.context));
  }

  private async health(start: boolean): Promise<void> {
    const backend = await this.registration();
    const output = await runSetupProcess(backend.registration.python_path, [path.join(backend.registration.project_root, "scripts", "backend_control.py"), ...(start ? ["--start"] : [])], {
      log: (line) => this.output.appendLine(line), env: { TOKENWISE_RUNTIME_DIR: backend.registration.runtime_dir },
    });
    const result = JSON.parse(output.trim());
    if (!result.health?.model_loaded || result.health.service !== "tokenwise") { throw new Error("The backend model is not ready. See TokenWise Setup output."); }
    if (start) { await vscode.workspace.getConfiguration("tokenWise").update("apiUrl", result.backend_url, vscode.ConfigurationTarget.Global); }
    this.output.appendLine(`Installation: ${backend.registration.project_root}\nRuntime and backend log: ${backend.registration.runtime_dir}\nBackend: ${result.backend_url}\nDevice: ${result.health.device}`);
  }

  public async start(): Promise<void> {
    if (!vscode.workspace.isTrusted || vscode.env.remoteName) {
      await vscode.window.showWarningMessage("Start TokenWise in a trusted local window.");
      return;
    }
    try {
      await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: "Starting TokenWise backend", cancellable: false }, () => this.health(true));
      await vscode.window.showInformationMessage("TokenWise backend is ready. You can send your repository prompt.");
    } catch (error) { this.output.show(true); await vscode.window.showErrorMessage(String(error)); }
  }

  public async diagnostics(): Promise<void> {
    this.output.show(true);
    this.output.appendLine(`TokenWise ${this.context.extension.packageJSON.version}; platform ${process.platform}; trusted ${vscode.workspace.isTrusted}; remote ${vscode.env.remoteName ?? "none"}`);
    try {
      if (!vscode.workspace.isTrusted || vscode.env.remoteName) { throw new Error("Use a trusted local workspace."); }
      this.output.appendLine(`TokenWise user storage: ${localStoragePath(this.context)}`);
      await this.health(false);
      for (const folder of vscode.workspace.workspaceFolders ?? []) {
        if (folder.uri.scheme !== "file") { continue; }
        try {
          const link = JSON.parse(await fs.readFile(path.join(folder.uri.fsPath, ".tokenwise/backend-link.json"), "utf8"));
          this.output.appendLine(`${folder.name}: ${link.registration_path === path.join(localStoragePath(this.context), "backend/installation.json") ? "linked to this IDE profile" : "different registration; re-run Enable Automatic Context"}`);
        } catch { this.output.appendLine(`${folder.name}: not enabled; run Enable Automatic Context`); }
      }
      await vscode.window.showInformationMessage("TokenWise backend is healthy. Diagnostics are in Output > TokenWise Setup.");
    } catch (error) {
      this.output.appendLine(String(error));
      const choice = await vscode.window.showWarningMessage(`TokenWise: ${String(error)}`, "Start Backend", "Set Up Backend", "Read Setup Guide");
      if (choice === "Start Backend") { await this.start(); }
      if (choice === "Set Up Backend") { await this.setup(); }
      if (choice === "Read Setup Guide") { await this.guide(); }
    }
  }

  public async guide(): Promise<void> {
    await vscode.commands.executeCommand("markdown.showPreview", vscode.Uri.joinPath(this.context.extensionUri, "resources", "user-guide.md"));
  }

  public async welcome(): Promise<void> {
    if (this.context.globalState.get("welcomeShown") || !vscode.workspace.isTrusted || vscode.env.remoteName) { return; }
    await this.context.globalState.update("welcomeShown", true);
    if (await this.installation()) { return; }
    const choice = await vscode.window.showInformationMessage("TokenWise's local backend is not configured.", "Enable Automatic Context", "Read Setup Guide");
    if (choice === "Enable Automatic Context") { await vscode.commands.executeCommand("tokenwise.enableAutomaticContext"); }
    if (choice === "Read Setup Guide") { await this.guide(); }
  }

  public dispose(): void { this.activeSetup?.abort(); this.output.dispose(); }
}
