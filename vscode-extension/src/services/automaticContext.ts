import * as vscode from "vscode";
import { WorkspacePruneResponse } from "../types";
import { ResultPanel } from "../ui/resultPanel";

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
    || (item.elapsed_ms !== undefined && !Number.isFinite(item.elapsed_ms))) {
    return undefined;
  }
  if (item.status === "ready") {
    const result = item.result;
    if (!result || typeof result.unified_prompt !== "string" || !result.structured_goal
      || !Number.isFinite(result.pruned_tokens) || !Number.isFinite(result.original_tokens)
      || !Array.isArray(result.files) || result.files.some((file) =>
        !file || typeof file.file_path !== "string" || typeof file.relation !== "string"
        || ![file.tier, file.score, file.original_tokens, file.pruned_tokens].every(Number.isFinite))) {
      return undefined;
    }
  }
  return item as AutomaticActivity;
}

export class AutomaticContextMonitor implements vscode.Disposable {
  private readonly output = vscode.window.createOutputChannel("TokenWise");
  private readonly watchers = new Map<string, vscode.Disposable[]>();
  private readonly seen = new Map<string, string>();
  private readonly timers = new Map<string, ReturnType<typeof setTimeout>>();
  private latest: AutomaticActivity | undefined;
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
      this.panel.showWorkspaceResult({
        ...activity.result,
        automatic_context: {
          query: activity.query ?? "", timestamp: activity.timestamp, elapsed_ms: activity.elapsed_ms ?? 0,
        },
      }, this.extensionUri, preserveFocus);
    }
  }

  private unwatch(folder: vscode.WorkspaceFolder): void {
    const key = folder.uri.toString();
    for (const item of this.watchers.get(key) ?? []) {
      item.dispose();
    }
    this.watchers.delete(key);
    this.seen.delete(key);
    const timer = this.timers.get(key);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(key);
    }
  }

  public dispose(): void {
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
