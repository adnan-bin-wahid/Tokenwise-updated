import * as fs from "node:fs/promises";
import * as path from "node:path";
import * as vscode from "vscode";
import { discoverRegisteredBackend, registerBackend, RegisteredBackend, validateBackendInstallation } from "./automaticSetup";
import { localStoragePath } from "./extensionPaths";
import { findPython312, installManagedBackend, runSetupProcess, SetupError, setupProgressMessage } from "./managedBackend";
import { buildCleanupPlan } from "./cleanupRegistry";
import { stopOwnedProcesses } from "./cleanupProcesses";

export class BackendManager implements vscode.Disposable {
  private readonly output = vscode.window.createOutputChannel("TokenWise Setup");
  private installing = false;
  private activeSetup: AbortController | undefined;
  private backgroundStart: Promise<string> | undefined;
  private backgroundAbort: AbortController | undefined;
  private backgroundRevision = 0;
  private disposed = false;

  public constructor(private readonly context: vscode.ExtensionContext, private readonly prepareCleanup?: () => Promise<void>, private readonly onInstalled?: () => void) {}

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
      modal: true, detail: "Requires 64-bit Python 3.12 and about 10 GB of free disk space. Setup creates a private environment and downloads CPU dependencies plus a verified 1.35 GB model. Completed steps and downloads can be reused on retry. When upgrading, the verified managed backend is stopped after installation; finish active prompts first. Existing checkout processes are not stopped. No repository code is uploaded. No Git, Node.js, administrator access, or API key is needed.",
    }, "Install Backend");
    if (approval !== "Install Backend") { return undefined; }
    if (this.installing) { await vscode.window.showInformationMessage("TokenWise backend setup is already running. See Output > TokenWise Setup."); return undefined; }
    this.installing = true;
    let installed = false;
    try {
      for (let attempt = 1; ; attempt++) {
        let phase = "prerequisites";
        try {
          if (this.disposed || !vscode.workspace.isTrusted || vscode.env.remoteName) { throw new Error("Setup requires an active, trusted local window."); }
          await this.prepareCleanup?.();
          const storage = localStoragePath(this.context);
          this.output.appendLine(`TokenWise user storage: ${storage}; setup attempt ${attempt}`);
          const preferred = vscode.workspace.getConfiguration("tokenWise").get<string>("pythonPath", "").trim();
          const result = await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: `TokenWise backend setup${attempt > 1 ? ` (retry ${attempt - 1})` : ""}`, cancellable: true }, async (progress, cancellation) => {
            const abort = new AbortController();
            this.activeSetup = abort;
            const subscription = cancellation.onCancellationRequested(() => abort.abort());
            if (cancellation.isCancellationRequested) { abort.abort(); }
            try {
              progress.report({ message: "Step 1/7: Finding 64-bit Python 3.12" });
              const python = await findPython312(preferred, abort.signal);
              abort.signal.throwIfAborted();
              return await installManagedBackend(python, path.join(this.context.extensionUri.fsPath, "resources", "backend-bundle"), storage,
                String(this.context.extension.packageJSON.version), {
                  signal: abort.signal, log: (line) => this.output.appendLine(line),
                  progress: (item) => progress.report({ message: setupProgressMessage(item) }),
                });
            } finally { subscription.dispose(); this.activeSetup = undefined; }
          });
          phase = "registration";
          await this.cancelSetup();
          // Reuse uninstall's strict identity checks, but remove no files during an upgrade.
          const plan = await buildCleanupPlan(this.context.extensionUri.fsPath);
          for (const profile of plan.profiles) {
            const root = path.resolve(profile.storageRoot), current = path.resolve(storage);
            const matches = process.platform === "win32" ? root.toLowerCase() === current.toLowerCase() : root === current;
            if (matches && profile.backend?.managed) {
              await stopOwnedProcesses({ ...profile, backend: { ...profile.backend, installerPid: undefined } });
            }
          }
          await registerBackend(result, storage);
          await vscode.workspace.getConfiguration("tokenWise").update("backendInstallationPath", result, vscode.ConfigurationTarget.Global);
          installed = true;
          void vscode.window.showInformationMessage("TokenWise backend installation complete.");
          return result;
        } catch (error) {
          this.output.show(true);
          const message = error instanceof Error ? error.message : String(error);
          this.output.appendLine(message);
          const reason = message.split(/\r?\n/).filter(Boolean).at(-1) ?? message;
          const cancelled = (error instanceof SetupError && error.cancelled) || (error instanceof Error && error.name === "AbortError");
          const detail = error instanceof SetupError && error.hint ? ` ${error.hint}` : " Completed steps and downloads are retained; fix the cause and retry.";
          const failedStage = error instanceof SetupError && error.stage ? error.stage : phase;
          const failedStep = error instanceof SetupError && error.step ? error.step : phase === "registration" ? 7 : undefined;
          const stage = ` (${failedStage}${failedStep ? `, step ${failedStep}/7` : ""})`;
          const text = cancelled ? "TokenWise setup cancelled. Completed steps and downloads are retained."
            : `TokenWise setup failed${stage}: ${reason.slice(0, 250)}. ${detail.trim()}`;
          const choices = ["Retry Failed Step", "Read Setup Guide", ...(message.includes("Python 3.12") ? ["Install Python"] : [])];
          const choice = cancelled ? await vscode.window.showInformationMessage(text, ...choices)
            : await vscode.window.showErrorMessage(text, ...choices);
          if (choice === "Retry Failed Step") { continue; }
          if (choice === "Read Setup Guide") { await this.guide(); }
          if (choice === "Install Python") { await vscode.env.openExternal(vscode.Uri.parse("https://www.python.org/downloads/")); }
          return undefined;
        }
      }
    } finally { this.installing = false; if (installed) { this.onInstalled?.(); } }
  }

  private async registration(signal?: AbortSignal): Promise<RegisteredBackend> {
    signal?.throwIfAborted();
    await this.prepareCleanup?.();
    signal?.throwIfAborted();
    const installation = await this.installation();
    signal?.throwIfAborted();
    if (!installation) { throw new Error("No complete backend is registered. Run TokenWise: Set Up Backend first."); }
    return registerBackend(installation, localStoragePath(this.context));
  }

  private async health(start: boolean, updateSetting = start, signal?: AbortSignal): Promise<string> {
    const backend = await this.registration(signal);
    signal?.throwIfAborted();
    const output = await runSetupProcess(backend.registration.python_path, [path.join(backend.registration.project_root, "scripts", "backend_control.py"), ...(start ? ["--start"] : [])], {
      log: (line) => this.output.appendLine(line), env: { TOKENWISE_RUNTIME_DIR: backend.registration.runtime_dir }, signal,
    });
    signal?.throwIfAborted();
    const result = JSON.parse(output.trim());
    if (!result.health?.model_loaded || result.health.service !== "tokenwise") { throw new Error("The backend model is not ready. See TokenWise Setup output."); }
    if (updateSetting) { await vscode.workspace.getConfiguration("tokenWise").update("apiUrl", result.backend_url, vscode.ConfigurationTarget.Global); }
    this.output.appendLine(`Installation: ${backend.registration.project_root}\nRuntime and backend log: ${backend.registration.runtime_dir}\nBackend: ${result.backend_url}\nDevice: ${result.health.device}`);
    return result.backend_url;
  }

  public async backgroundUrl(start: boolean): Promise<string | undefined> {
    if (this.disposed || this.installing || !vscode.workspace.isTrusted || vscode.env.remoteName) { return undefined; }
    const revision = this.backgroundRevision;
    const installation = await this.installation();
    if (!installation || revision !== this.backgroundRevision || this.disposed || this.installing || !vscode.workspace.isTrusted || vscode.env.remoteName) { return undefined; }
    if (!this.backgroundStart) {
      const abort = new AbortController();
      this.backgroundAbort = abort;
      this.backgroundStart = this.health(start, false, abort.signal).finally(() => {
        this.backgroundStart = undefined;
        this.backgroundAbort = undefined;
      });
    }
    return this.backgroundStart;
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
    if (!vscode.workspace.isTrusted || vscode.env.remoteName) { return; }
    const installation = await this.installation();
    if (installation) {
      try {
        const marker = JSON.parse(await fs.readFile(path.join(installation, "managed-install.json"), "utf8"));
        const version = String(this.context.extension.packageJSON.version);
        const previous = typeof marker.version === "string" && /^\d+\.\d+\.\d+$/.test(marker.version) ? marker.version.split(".").map(Number) : [];
        const current = version.split(".").map(Number);
        const older = previous.length === 3 && previous.some((part: number, index: number) => part < current[index] && previous.slice(0, index).every((value: number, offset: number) => value === current[offset]));
        if (marker.schema_version === 1 && older && this.context.globalState.get("backendUpdatePromptVersion") !== version) {
          await this.context.globalState.update("backendUpdatePromptVersion", version);
          const choice = await vscode.window.showInformationMessage(`TokenWise ${version} is installed, but its managed backend is ${marker.version}. Update the backend to enable the new features.`, "Update Backend", "Read Setup Guide");
          if (choice === "Update Backend" && await this.setup()) {
            void vscode.window.showInformationMessage("TokenWise backend updated. Background indexing reconnects automatically.");
          } else if (choice === "Read Setup Guide") { await this.guide(); }
        }
      } catch { /* Existing checkout backends and older markers need no automatic migration. */ }
      return;
    }
    if (this.context.globalState.get("welcomeShown")) { return; }
    await this.context.globalState.update("welcomeShown", true);
    const choice = await vscode.window.showInformationMessage("TokenWise's local backend is not configured.", "Enable Automatic Context", "Read Setup Guide");
    if (choice === "Enable Automatic Context") { await vscode.commands.executeCommand("tokenwise.enableAutomaticContext"); }
    if (choice === "Read Setup Guide") { await this.guide(); }
  }

  public async cancelSetup(): Promise<void> {
    this.backgroundRevision++;
    this.activeSetup?.abort(); this.backgroundAbort?.abort();
    await this.backgroundStart?.catch(() => undefined);
  }
  public dispose(): void { this.disposed = true; void this.cancelSetup(); this.output.dispose(); }
}
