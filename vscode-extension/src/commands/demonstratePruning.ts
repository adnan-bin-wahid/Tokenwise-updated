import * as vscode from "vscode";
import { PruneService } from "../services/pruneService";
import { TokenWiseApiClient } from "../services/apiClient";
import { getTokenWiseConfig } from "../services/config";
import { estimateCarbonComparison } from "../services/carbonComparison";
import { askQuery, askThreshold } from "../utils/editor";
import { ResultPanel } from "../ui/resultPanel";

export function createDemonstratePruningCommand(service: PruneService, panel: ResultPanel,
  extensionUri: vscode.Uri, backendUrl: () => Promise<string | undefined>) {
  return async () => {
    if (!vscode.workspace.isTrusted || vscode.env.remoteName) {
      await vscode.window.showWarningMessage("Use a trusted local Python repository."); return;
    }
    const choice = await vscode.window.showQuickPick([
      { label: "Repository: no selected file", mode: "repository" as const },
      { label: "Selected file or highlighted excerpt", mode: "selection" as const },
      { label: "Conversation: replay earlier user context", mode: "conversation" as const },
    ], { title: "TokenWise: Demonstrate Pruning Inputs" });
    if (!choice) { return; }
    const editor = vscode.window.activeTextEditor;
    const folders = vscode.workspace.workspaceFolders?.filter(folder => folder.uri.scheme === "file") ?? [];
    const folder = folders.length === 1 ? folders[0] : await vscode.window.showWorkspaceFolderPick();
    if (!folder || folder.uri.scheme !== "file") {
      await vscode.window.showWarningMessage("Open a local Python project folder."); return;
    }
    if (choice.mode === "selection" && (!editor || editor.document.languageId !== "python" || editor.document.uri.scheme !== "file")) {
      await vscode.window.showWarningMessage("Open a Python file or highlight an excerpt for the selected-code mode."); return;
    }
    const excerpt = choice.mode === "selection" && editor && !editor.selection.isEmpty;
    const captured = choice.mode === "selection" && editor ? {
      code: editor.document.getText(excerpt ? editor.selection : undefined), resource: editor.document.uri,
      mode: excerpt ? "selected_excerpt" as const : "selected_file" as const,
      firstLine: excerpt ? editor.selection.start.line + 1 : 1,
    } : undefined;
    let history: string | undefined;
    if (choice.mode === "conversation") {
      history = (await vscode.window.showInputBox({ title: "Earlier user task (replay, not live chat capture)",
        prompt: "Enter the earlier user task whose subject the next prompt refers to",
        placeHolder: "Explain account lockout after failed login attempts.", ignoreFocusOut: true,
        validateInput: value => !value.trim() ? "An earlier user task is required." : value.length > 2000 ? "Use at most 2000 characters." : undefined }))?.trim();
      if (!history) { return; }
    }
    const query = (await askQuery())?.trim();
    if (!query) { return; }
    const cfg = getTokenWiseConfig(folder.uri);
    const threshold = await askThreshold(cfg.defaultThreshold);
    if (threshold === undefined) { return; }
    await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: "TokenWise: tracing pruning inputs" }, async () => {
      try {
        if (captured) {
          panel.show(await service.prune(query, captured.code, threshold, captured), extensionUri); return;
        }
        const url = await backendUrl();
        if (!url) { throw new Error("Run TokenWise: Set Up Backend, then retry."); }
        const client = new TokenWiseApiClient({ ...cfg, apiUrl: url });
        const result = await client.pruneWorkspace({ query, workspace_root: folder.uri.fsPath,
          language: "python", diagnostics: [], threshold, token_budget: cfg.repositoryTokenBudget,
          max_candidates: 8, context_hint: history });
        if (!result.input_trace) { throw new Error("Update the backend through TokenWise: Set Up Backend to view pruning inputs."); }
        if (result.context_hint_used && history) { result.input_trace.history_source = "supplied_replay"; }
        try { Object.assign(result, await estimateCarbonComparison(client, cfg, result.raw_context_tokens ?? 0,
          result.pruned_tokens, "formatted-context")); }
        catch (error) { result.carbonStatus = "unavailable"; result.carbonError = String(error); }
        panel.showWorkspaceResult(result, extensionUri);
      } catch (error) { await vscode.window.showErrorMessage(`TokenWise: ${String(error)}`); }
    });
  };
}
