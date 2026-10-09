import * as vscode from "vscode";
import { compareAntigravityUsage, parseAntigravityUsage } from "../services/antigravityUsage";
import { ResultPanel } from "../ui/resultPanel";

export function createImportAntigravityComparisonCommand(panel: ResultPanel) {
  return async () => {
    try {
      const runs = [];
      for (const label of ["WITHOUT TokenWise", "WITH TokenWise"]) {
        const files = await vscode.window.showOpenDialog({ title: `Select Antigravity CLI log: ${label}`,
          canSelectMany: false, canSelectFolders: false, canSelectFiles: true,
          filters: { "Usage logs": ["json", "jsonl", "ndjson", "txt"] } });
        if (!files?.[0]) { return; }
        const stat = await vscode.workspace.fs.stat(files[0]);
        if (stat.size > 10 * 1024 * 1024) { throw new Error("Usage logs must be at most 10 MiB."); }
        runs.push(parseAntigravityUsage(Buffer.from(await vscode.workspace.fs.readFile(files[0])).toString("utf8")));
      }
      panel.showAgentUsageComparison(compareAntigravityUsage(runs[0], runs[1]));
    } catch (error) {
      await vscode.window.showErrorMessage(`TokenWise usage import: ${error instanceof Error ? error.message : String(error)}`);
    }
  };
}
