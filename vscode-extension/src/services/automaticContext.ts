import * as vscode from "vscode";
import { WorkspacePruneResponse } from "../types";
import { ResultPanel } from "../ui/resultPanel";
import { TokenWiseApiClient } from "./apiClient";
import { getTokenWiseConfig } from "./config";
import { estimateCarbonComparison } from "./carbonComparison";

interface AutomaticActivity {
  event_id: string;
  status: "retrieving" | "ready" | "error";
  timestamp: string;
  transport?: string;
  verification?: boolean;
  query?: string;
  elapsed_ms?: number;
  error?: string;
  result?: WorkspacePruneResponse;
  backend_url?: string;
}

export function parseAutomaticActivity(value: unknown): AutomaticActivity | undefined {
  if (!value || typeof value !== "object") {
    return undefined;
  }
  const item = value as Partial<AutomaticActivity>;
  if (typeof item.event_id !== "string" || typeof item.timestamp !== "string"
    || !["retrieving", "ready", "error"].includes(String(item.status))
    || (item.query !== undefined && typeof item.query !== "string")
    || (item.transport !== undefined && typeof item.transport !== "string")
    || (item.verification !== undefined && typeof item.verification !== "boolean")
    || (item.error !== undefined && typeof item.error !== "string")
    || (item.backend_url !== undefined && typeof item.backend_url !== "string")
    || (item.elapsed_ms !== undefined && !Number.isFinite(item.elapsed_ms))) {
    return undefined;
  }
  if (item.status === "ready") {
    const result = item.result;
    if (!result || typeof result.unified_prompt !== "string" || !result.structured_goal
      || typeof result.structured_goal !== "object" || Array.isArray(result.structured_goal)
      || ![result.pruned_tokens, result.original_tokens].every(count => Number.isInteger(count) && count >= 0)
      || !Array.isArray(result.files) || !result.files.length || result.files.some((file) =>
        !file || typeof file.file_path !== "string" || typeof file.relation !== "string"
        || ![1, 2, 3].includes(file.tier) || !Number.isFinite(file.score) || file.score < 0 || file.score > 1
        || ![file.original_tokens, file.pruned_tokens].every(count => Number.isInteger(count) && count >= 0))) {
      return undefined;
    }
    const goal = result.structured_goal;
    if ((goal.objective !== undefined && typeof goal.objective !== "string")
      || (goal.task_type !== undefined && typeof goal.task_type !== "string")
      || [goal.identifiers, goal.observed_errors].some(list => list !== undefined
        && (!Array.isArray(list) || list.some(item => typeof item !== "string")))) { return undefined; }
    if (result.context_mode !== undefined && !["focused", "repository_overview"].includes(result.context_mode)) {
      return undefined;
    }
    for (const name of ["raw_context_tokens", "retained_source_tokens", "context_overhead_tokens", "indexed_files"] as const) {
      const count = result[name];
      if (count !== undefined && (!Number.isInteger(count) || count < 0)) { return undefined; }
    }
    if (result.warnings !== undefined && (!Array.isArray(result.warnings)
      || result.warnings.some(warning => typeof warning !== "string"))) { return undefined; }
  }
  return item as AutomaticActivity;
}

export class AutomaticContextMonitor implements vscode.Disposable {
  private readonly output = vscode.window.createOutputChannel("TokenWise");
  private readonly watchers = new Map<string, vscode.Disposable[]>();
  private readonly seen = new Map<string, string>();
  private readonly timers = new Map<string, ReturnType<typeof setTimeout>>();
  private latest: AutomaticActivity | undefined;
  private latestFolder: vscode.WorkspaceFolder | undefined;
  private disposed = false;
  private readonly foldersListener: vscode.Disposable;
  private readonly command: vscode.Disposable;

  public constructor(
    private readonly status: vscode.StatusBarItem,
    private readonly panel: ResultPanel,
    private readonly extensionUri: vscode.Uri,
  ) {
    this.command = vscode.commands.registerCommand("tokenwise.showAutomaticContext", () => {
      if (this.latest?.status === "ready" && this.latest.result) {
        this.showResult(this.latest, false);
        if (this.latestFolder) { void this.enrichCarbon(this.latest, this.latestFolder); }
      } else {
        this.output.show(true);
      }
    });
    this.foldersListener = vscode.workspace.onDidChangeWorkspaceFolders((event) => {
      for (const folder of event.removed) {
        this.unwatch(folder);
      }
      for (const folder of event.added) {
        this.watch(folder);
      }
    });
    for (const folder of vscode.workspace.workspaceFolders ?? []) {
      this.watch(folder);
    }
  }

  public configured(folder: vscode.WorkspaceFolder): void {
    this.latest = undefined;
    this.latestFolder = undefined;
    this.seen.delete(folder.uri.toString());
    this.status.text = "$(filter) TokenWise Auto: awaiting prompt";
    this.status.tooltip = `Automatic context is configured for ${folder.name}. Start a new Antigravity chat.`;
    this.status.command = "tokenwise.showAutomaticContext";
    this.output.appendLine(`Automatic context enabled for ${folder.uri.fsPath}`);
  }

  private watch(folder: vscode.WorkspaceFolder): void {
    const key = folder.uri.toString();
    const watcher = vscode.workspace.createFileSystemWatcher(
      new vscode.RelativePattern(folder, ".tokenwise/latest.json"),
    );
    const refresh = () => {
      const timer = this.timers.get(key);
      if (timer) {
        clearTimeout(timer);
      }
      this.timers.set(key, setTimeout(() => {
        this.timers.delete(key);
        void this.readActivity(folder, true);
      }, 120));
    };
    this.watchers.set(key, [watcher, watcher.onDidCreate(refresh), watcher.onDidChange(refresh)]);
    void this.readActivity(folder, false);
    void vscode.workspace.fs.readFile(vscode.Uri.joinPath(folder.uri, ".agents", "hooks.json"))
      .then((bytes) => {
        let configured = false;
        try { configured = Boolean(JSON.parse(Buffer.from(bytes).toString("utf8").replace(/^\uFEFF/, ""))["tokenwise-automatic-context"]); }
        catch { /* Unrelated or invalid hook files do not prove TokenWise setup. */ }
        if (configured && !this.latest) {
          this.status.text = "$(filter) TokenWise Auto: awaiting prompt";
          this.status.tooltip = "TokenWise is configured. No context command or hook activity has been observed yet.";
          this.status.command = "tokenwise.showAutomaticContext";
        }
      }, () => undefined);
  }

  private async readActivity(folder: vscode.WorkspaceFolder, openPanel: boolean): Promise<void> {
    try {
      const data = await vscode.workspace.fs.readFile(vscode.Uri.joinPath(folder.uri, ".tokenwise", "latest.json"));
      const activity = parseAutomaticActivity(JSON.parse(Buffer.from(data).toString("utf8")));
      if (!activity) {
        return;
      }
      const key = folder.uri.toString();
      const revision = `${activity.event_id}:${activity.status}`;
      if (this.seen.get(key) === revision) {
        return;
      }
      this.seen.set(key, revision);
      this.latest = activity;
      this.latestFolder = folder;
      this.status.command = "tokenwise.showAutomaticContext";
      const prefix = activity.verification ? "Verification" : openPanel ? "Activity" : "Previous activity";
      if (activity.status === "retrieving") {
        this.status.text = openPanel ? "$(sync~spin) TokenWise retrieving" : "$(filter) TokenWise Auto: awaiting prompt";
        this.status.tooltip = openPanel ? activity.query ?? "Preparing Antigravity context" : "The last retrieval did not finish. Waiting for new prompt activity.";
        this.output.appendLine(`[${activity.timestamp}] ${prefix}: preparing context: ${activity.query ?? ""}`);
      } else if (activity.status === "error") {
        this.status.text = openPanel ? "$(warning) TokenWise unavailable" : "$(warning) TokenWise: last attempt failed";
        this.status.tooltip = activity.error ?? "Automatic context failed. Click for details.";
        this.output.appendLine(`[${activity.timestamp}] ${prefix}: ${activity.error ?? "Automatic context failed"}`);
      } else if (activity.result) {
        const result = activity.result;
        const label = activity.verification ? "TokenWise test" : openPanel ? "TokenWise Auto" : "TokenWise last result";
        const transport = activity.transport === "antigravity-agent-command" ? "agent command" : "hook adapter";
        this.status.text = `$(filter) ${label}: ${result.files.length} files, ${result.pruned_tokens} tokens`;
        this.status.tooltip = activity.verification
          ? "Verification output, not a real Antigravity agent invocation. Click to inspect."
          : `${openPanel ? "Context prepared" : "Previous context"} via ${transport} at ${activity.timestamp}.\n${activity.query ?? ""}\nClick to inspect. Preparation alone does not prove the model used it.`;
        this.output.appendLine(
          `[${activity.timestamp}] ${prefix}: prepared ${result.files.length} files, ${result.pruned_tokens} tokens via ${transport} in ${activity.elapsed_ms ?? 0}ms`,
        );
        this.output.appendLine(result.files.map((file) => file.file_path).join(", "));
        if (openPanel && !activity.verification) { void this.enrichCarbon(activity, folder); }
        if (openPanel && !activity.verification
          && vscode.workspace.getConfiguration("tokenWise").get("autoOpenAutomaticContext", true)) {
          this.showResult(activity, true);
        }
      }
    } catch {
      // The activity file does not exist until the first prompt, or is being replaced.
    }
  }

  private showResult(activity: AutomaticActivity, preserveFocus: boolean): void {
    if (activity.result) {
      this.panel.showWorkspaceResult(this.viewResult(activity), this.extensionUri, preserveFocus);
    }
  }

  private viewResult(activity: AutomaticActivity): WorkspacePruneResponse {
    return {
      ...activity.result!,
      automatic_context: {
        query: activity.query ?? "", timestamp: activity.timestamp, elapsed_ms: activity.elapsed_ms ?? 0,
        event_id: activity.event_id,
      },
    };
  }

  private async enrichCarbon(activity: AutomaticActivity, folder: vscode.WorkspaceFolder): Promise<void> {
    const result = activity.result;
    if (!result || activity.verification || this.disposed || this.latest !== activity
      || ["pending", "ready", "disabled", "unavailable"].includes(result.carbonStatus ?? "")) { return; }
    const cfg = getTokenWiseConfig(folder.uri);
    if (!cfg.enableCarbonEstimation) {
      result.carbonStatus = "disabled";
    } else {
      result.carbonStatus = "pending";
      try {
        if (!result.raw_context_tokens) {
          throw new Error("Update the TokenWise backend and run a new prompt to obtain a matched context baseline.");
        }
        const url = new URL(activity.backend_url ?? cfg.apiUrl);
        if (url.protocol !== "http:" || !["127.0.0.1", "localhost", "[::1]"].includes(url.hostname)
          || url.username || url.password || url.pathname !== "/" || url.search || url.hash) {
          throw new Error("Automatic carbon estimates require the local TokenWise backend.");
        }
        const client = new TokenWiseApiClient({ ...cfg, apiUrl: url.origin, timeoutMs: Math.min(cfg.timeoutMs, 10000) });
        const comparison = await estimateCarbonComparison(client, cfg, result.raw_context_tokens,
          result.pruned_tokens, "formatted-context");
        if (this.disposed || this.latest !== activity) { return; }
        Object.assign(result, comparison);
      } catch (error) {
        if (this.disposed || this.latest !== activity) { return; }
        result.carbonStatus = "unavailable";
        result.carbonError = error instanceof Error ? error.message : String(error);
        this.output.appendLine(`Carbon estimate unavailable: ${result.carbonError}`);
      }
    }
    if (!this.disposed && this.latest === activity) {
      this.panel.updateWorkspaceResult(this.viewResult(activity));
    }
  }

  private unwatch(folder: vscode.WorkspaceFolder): void {
    const key = folder.uri.toString();
    for (const item of this.watchers.get(key) ?? []) {
      item.dispose();
    }
    this.watchers.delete(key);
    this.seen.delete(key);
    if (this.latestFolder?.uri.toString() === key) {
      this.latest = undefined;
      this.latestFolder = undefined;
    }
    const timer = this.timers.get(key);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(key);
    }
  }

  public dispose(): void {
    this.disposed = true;
    for (const items of this.watchers.values()) {
      for (const item of items) {
        item.dispose();
      }
    }
    for (const timer of this.timers.values()) {
      clearTimeout(timer);
    }
    this.foldersListener.dispose();
    this.command.dispose();
    this.output.dispose();
  }
}
