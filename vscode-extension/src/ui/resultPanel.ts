import * as vscode from "vscode";
import { CarbonImpactViewModel, PruneResultViewModel, WorkspacePruneResponse } from "../types";

export class ResultPanel {
  private static readonly viewType = "tokenwise.resultPanel";
  private panel: vscode.WebviewPanel | undefined;
  private latestResult: PruneResultViewModel | undefined;
  private latestWorkspaceResult: WorkspacePruneResponse | undefined;

  private ensurePanel(preserveFocus = false): vscode.WebviewPanel {
    if (this.panel) {
      return this.panel;
    }

    this.panel = vscode.window.createWebviewPanel(
      ResultPanel.viewType,
      "TokenWise Result",
      { viewColumn: vscode.ViewColumn.Beside, preserveFocus },
      { enableScripts: true, retainContextWhenHidden: true },
    );

    this.panel.onDidDispose(() => {
      this.panel = undefined;
      this.latestResult = undefined;
      this.latestWorkspaceResult = undefined;
    });

    this.panel.webview.onDidReceiveMessage(async (message: { command?: string }) => {
      if (message.command === "copyPruned" && this.latestResult) {
        await vscode.env.clipboard.writeText(this.latestResult.prunedCode);
        void vscode.window.showInformationMessage("TokenWise: pruned context copied.");
        return;
      }

      if (message.command === "copyWorkspace" && this.latestWorkspaceResult) {
        await vscode.env.clipboard.writeText(this.latestWorkspaceResult.unified_prompt);
        void vscode.window.showInformationMessage("TokenWise: repository context copied.");
      }
    });

    return this.panel;
  }

  public show(
    result: PruneResultViewModel,
    _extensionUri: vscode.Uri,
  ): void {
    this.latestResult = result;
    this.latestWorkspaceResult = undefined;
    const panel = this.ensurePanel();
    panel.title = "TokenWise Prune Result";
    panel.webview.html = this.getHtml(result);
    panel.reveal(vscode.ViewColumn.Beside);
  }

  public showWorkspaceResult(
    result: WorkspacePruneResponse,
    _extensionUri: vscode.Uri,
    preserveFocus = false,
  ): void {
    this.latestWorkspaceResult = result;
    this.latestResult = undefined;
    const panel = this.ensurePanel(preserveFocus);
    panel.title = "TokenWise Repository Context";
    panel.webview.html = this.getWorkspaceHtml(result);
    panel.reveal(vscode.ViewColumn.Beside, preserveFocus);
  }

  public updateWorkspaceResult(result: WorkspacePruneResponse): boolean {
    const eventId = result.automatic_context?.event_id;
    if (!this.panel || !eventId || this.latestWorkspaceResult?.automatic_context?.event_id !== eventId) {
      return false;
    }
    this.latestWorkspaceResult = result;
    this.panel.webview.html = this.getWorkspaceHtml(result);
    return true;
  }

  private getHtml(result: PruneResultViewModel): string {
    const carbon = this.renderCarbonSection(result);
    const kept = result.keptFrags.length > 0 ? result.keptFrags.join(", ") : "none";

    return this.shell(
      "TokenWise — Neural Pruning",
      `
      <div class="subtle">Task: <strong>${escapeHtml(result.query)}</strong></div>
      <div class="stats">
        ${stat("Relevance", result.score.toFixed(4))}
        ${stat("Original", `${result.originTokenCount} tokens`)}
        ${stat("Pruned", `${result.prunedTokenCount} tokens`)}
        ${stat(result.reductionPercent < 0 ? "Source increase" : "Reduction", `${Math.abs(result.reductionPercent).toFixed(2)}%`, result.reductionPercent > 0)}
      </div>
      ${carbon}
      <div class="card">
        <div class="card-title">Pruning details</div>
        <div class="meta-grid">
          <span>Model input tokens</span><strong>${result.modelInputTokenCount}</strong>
          <span>Kept line fragments</span><strong>${escapeHtml(kept)}</strong>
        </div>
      </div>
      <div class="actions"><button onclick="send('copyPruned')">Copy Pruned Context</button></div>
      <div class="code-grid">
        <div class="card"><div class="card-title">Original</div><pre>${escapeHtml(result.originalCode)}</pre></div>
        <div class="card"><div class="card-title">Pruned context</div><pre>${escapeHtml(result.prunedCode)}</pre></div>
      </div>
      <div class="notice">The pruned output is context for an AI coding workflow, not a source-code patch. TokenWise therefore does not insert it into your file automatically.</div>
      `,
    );
  }

  private renderCarbonSection(result: CarbonImpactViewModel): string {
    if (!result.carbonBefore || !result.carbonAfter || !result.carbonSavings) {
      const message = result.carbonStatus === "pending" ? "Estimating carbon impact..."
        : result.carbonStatus === "disabled" ? "Carbon estimation is disabled."
        : result.carbonStatus === "unavailable" ? `Carbon estimate unavailable: ${result.carbonError ?? "Backend artifacts are unavailable."}`
        : "";
      return message ? `<div class="notice">${escapeHtml(message)}</div>` : "";
    }

    const energy = result.carbonSavings.totalJoulesSaved;
    const carbon = result.carbonSavings.co2GramsSaved;

    return `
      <div class="card">
        <div class="card-title">Carbon impact — trained SEAL-derived estimator</div>
        <div class="stats">
          ${stat("CO2 before", formatCarbon(result.carbonBefore.co2Grams))}
          ${stat("CO2 after", formatCarbon(result.carbonAfter.co2Grams))}
          ${stat(energy < 0 ? "Energy increase" : "Energy saved", `${Math.abs(energy).toFixed(4)} J`, energy > 0)}
          ${stat(carbon < 0 ? "CO2 increase" : "CO2 saved", formatCarbon(Math.abs(carbon)), carbon > 0)}
        </div>
        <div class="table-wrap"><table>
          <thead><tr><th>Estimated energy</th><th>Before</th><th>After</th></tr></thead>
          <tbody>
            <tr><td>Prefill</td><td>${result.carbonBefore.prefillJoules.toFixed(4)} J</td><td>${result.carbonAfter.prefillJoules.toFixed(4)} J</td></tr>
            <tr><td>Decode</td><td>${result.carbonBefore.decodeJoules.toFixed(4)} J</td><td>${result.carbonAfter.decodeJoules.toFixed(4)} J</td></tr>
            <tr><td>Total</td><td>${result.carbonBefore.totalJoules.toFixed(4)} J</td><td>${result.carbonAfter.totalJoules.toFixed(4)} J</td></tr>
          </tbody></table></div>
        <div class="meta-grid">
          <span>Model</span><strong>${escapeHtml(result.carbonAfter.modelFamily)}</strong>
          <span>Prefill route</span><strong>${escapeHtml(result.carbonAfter.prefillRoute)}</strong>
          <span>Decode route</span><strong>${escapeHtml(result.carbonAfter.decodeRoute)}</strong>
          <span>Feature source</span><strong>${escapeHtml(result.carbonAfter.featuresSource)}</strong>
          <span>Carbon intensity</span><strong>${result.carbonAfter.carbonIntensityGPerKwh.toFixed(2)} gCO₂/kWh</strong>
          <span>Baseline</span><strong>${result.carbonBaseline === "formatted-context" ? "Same files and formatting, without pruning" : "Source text only"}</strong>
        </div>
        <div class="notice">Approximate inference estimates under the configured model and hardware assumptions, not measured emissions.</div>
      </div>`;
  }

  private getWorkspaceHtml(result: WorkspacePruneResponse): string {
    const objective = result.structured_goal.objective ?? "";
    const taskType = result.structured_goal.task_type ?? "generic_task";
    const identifiers = result.structured_goal.identifiers ?? [];
    const observedErrors = result.structured_goal.observed_errors ?? [];
    const retained = result.retained_source_tokens ?? result.files.reduce((sum, file) => sum + file.pruned_tokens, 0);
    const sourceDelta = result.original_tokens - retained;
    const reduction = result.original_tokens > 0
      ? Math.abs(sourceDelta / result.original_tokens) * 100
      : 0;
    const overhead = result.context_overhead_tokens ?? Math.max(0, result.pruned_tokens - retained);
    const overview = result.context_mode === "repository_overview";

    const rows = result.files
      .map(
        (file) => `
        <tr>
          <td>${escapeHtml(file.file_path)}</td>
          <td>${escapeHtml(file.relation)}</td>
          <td class="num">${file.tier}</td>
          <td class="num">${file.original_tokens}</td>
          <td class="num">${file.pruned_tokens}</td>
          <td class="num">${file.score.toFixed(4)}</td>
        </tr>`,
      )
      .join("");

    return this.shell(
      "TokenWise — Repository Context",
      `
      ${result.automatic_context ? `<div class="subtle"><strong>Antigravity automatic context</strong><br>Task: ${escapeHtml(result.automatic_context.query)}<br>Prepared in ${(result.automatic_context.elapsed_ms / 1000).toFixed(2)}s</div>` : ""}
      ${overview ? `<div class="subtle"><strong>Repository overview</strong> | ${result.indexed_files ?? 0} indexed Python files</div>` : ""}
      ${(result.warnings ?? []).map(warning => `<div class="notice">${escapeHtml(warning)}</div>`).join("")}
      <div class="card">
        <div class="card-title">Synthesized goal</div>
        <div class="meta-grid">
          <span>Task type</span><strong>${escapeHtml(taskType)}</strong>
          <span>Objective</span><strong>${escapeHtml(objective)}</strong>
          <span>Identifiers</span><strong>${escapeHtml(identifiers.join(", ") || "none")}</strong>
          <span>Diagnostics</span><strong>${escapeHtml(observedErrors.join(" | ") || "none")}</strong>
        </div>
      </div>
      <div class="stats">
        ${stat("Source tokens", String(result.original_tokens))}
        ${stat("Retained source", String(retained))}
        ${stat("Packed tokens", String(result.pruned_tokens))}
        ${stat(sourceDelta < 0 ? "Source increase" : "Source reduction", `${reduction.toFixed(2)}%`, sourceDelta > 0)}
        ${stat("Formatting overhead", `${overhead} tokens`)}
        ${stat("Files included", String(result.files.length))}
      </div>
      ${this.renderCarbonSection(result)}
      <div class="card">
        <div class="card-title">Included files</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>File</th><th>Relation</th><th>Tier</th><th>Source</th><th>Retained</th><th>${overview ? "Priority" : "Score"}</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </div>
      <div class="actions"><button onclick="send('copyWorkspace')">Copy Unified Context</button></div>
      <div class="card"><div class="card-title">Unified context</div><pre>${escapeHtml(result.unified_prompt)}</pre></div>
      `,
    );
  }

  private shell(title: string, body: string): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';" />
  <title>${escapeHtml(title)}</title>
  <style>
    :root {
      --bg: var(--vscode-editor-background);
      --fg: var(--vscode-editor-foreground);
      --muted: var(--vscode-descriptionForeground);
      --border: var(--vscode-panel-border);
      --button: var(--vscode-button-background);
      --buttonFg: var(--vscode-button-foreground);
      --buttonHover: var(--vscode-button-hoverBackground);
      --ok: var(--vscode-testing-iconPassedColor);
      --code: var(--vscode-textCodeBlock-background);
    }
    body { margin: 20px; background: var(--bg); color: var(--fg); font-family: var(--vscode-font-family); font-size: 13px; line-height: 1.5; }
    h2 { margin: 0 0 6px; font-size: 20px; }
    .subtle, .notice { color: var(--muted); margin-bottom: 16px; }
    .notice { border-left: 3px solid var(--border); padding-left: 10px; }
    .card { border: 1px solid var(--border); border-radius: 7px; padding: 14px; margin: 14px 0; }
    .card-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0; color: var(--muted); margin-bottom: 10px; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 14px 0; }
    .stat { border: 1px solid var(--border); border-radius: 7px; padding: 10px; }
    .stat-label { color: var(--muted); font-size: 10px; text-transform: uppercase; }
    .stat-value { font-size: 16px; font-weight: 700; margin-top: 3px; }
    .ok { color: var(--ok); }
    .meta-grid { display: grid; grid-template-columns: minmax(120px, .45fr) 1fr; gap: 7px 14px; }
    .meta-grid span { color: var(--muted); }
    .meta-grid strong { min-width: 0; overflow-wrap: anywhere; }
    .code-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    pre { white-space: pre-wrap; word-break: break-word; background: var(--code); padding: 12px; border-radius: 5px; overflow: auto; max-height: 620px; }
    button { border: 0; border-radius: 3px; padding: 7px 12px; background: var(--button); color: var(--buttonFg); cursor: pointer; }
    button:hover { background: var(--buttonHover); }
    .actions { margin: 14px 0; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 7px 8px; border-bottom: 1px solid var(--border); text-align: left; }
    th { color: var(--muted); font-size: 10px; text-transform: uppercase; }
    .num { text-align: right; }
    @media (max-width: 900px) { .stats, .code-grid { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 600px) { .stats, .code-grid { grid-template-columns: 1fr; } .meta-grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <h2>${escapeHtml(title)}</h2>
  ${body}
  <script>
    const vscode = acquireVsCodeApi();
    function send(command) { vscode.postMessage({ command }); }
  </script>
</body>
</html>`;
  }
}

function stat(label: string, value: string, ok = false): string {
  return `<div class="stat"><div class="stat-label">${escapeHtml(label)}</div><div class="stat-value${ok ? " ok" : ""}">${escapeHtml(value)}</div></div>`;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatCarbon(value: number): string {
  return `${value !== 0 && Math.abs(value) < 0.000001 ? value.toExponential(3) : value.toFixed(6)} g`;
}
