import * as vscode from "vscode";

export interface TokenWiseConfig {
  apiUrl: string;
  enableLocalGoalModel: boolean;
  localLlmUrl: string;
  localLlmModelName: string;
  timeoutMs: number;
  defaultThreshold: number;
  repositoryTokenBudget: number;
  autoOpenResultPanel: boolean;
  enableCarbonEstimation: boolean;
  targetModelName: string;
  targetModelSizeB?: number;
  targetGpuType?: string;
  targetMmluProScore?: number;
  targetBbhScore?: number;
  expectedOutputTokens: number;
  latencyPerInputTokenMs?: number;
  latencyPerOutputTokenMs?: number;
  carbonIntensityGPerKwh: number;
}

function optionalNumber(cfg: vscode.WorkspaceConfiguration, key: string): number | undefined {
  const value = cfg.get<number>(key);
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

export function getTokenWiseConfig(resource?: vscode.Uri): TokenWiseConfig {
  const cfg = vscode.workspace.getConfiguration("tokenWise", resource);
  return {
    apiUrl: String(cfg.get("apiUrl", "http://127.0.0.1:8000")).replace(/\/$/, ""),
    enableLocalGoalModel: Boolean(cfg.get("enableLocalGoalModel", false)),
    localLlmUrl: String(cfg.get("localLlmUrl", "http://127.0.0.1:11434/v1")).replace(/\/$/, ""),
    localLlmModelName: String(cfg.get("localLlmModelName", "qwen2.5-coder:1.5b-instruct-q4_k_m")),
    timeoutMs: Number(cfg.get("timeoutMs", 120000)),
    defaultThreshold: Number(cfg.get("defaultThreshold", 0.45)),
    repositoryTokenBudget: Number(cfg.get("repositoryTokenBudget", 8192)),
    autoOpenResultPanel: Boolean(cfg.get("autoOpenResultPanel", true)),
    enableCarbonEstimation: Boolean(cfg.get("enableCarbonEstimation", true)),
    targetModelName: String(cfg.get("targetModelName", "meta-llama-3-8b-instruct")),
    targetModelSizeB: optionalNumber(cfg, "targetModelSizeB"),
    targetGpuType: cfg.get<string>("targetGpuType"),
    targetMmluProScore: optionalNumber(cfg, "targetMmluProScore"),
    targetBbhScore: optionalNumber(cfg, "targetBbhScore"),
    expectedOutputTokens: Number(cfg.get("expectedOutputTokens", 256)),
    latencyPerInputTokenMs: optionalNumber(cfg, "latencyPerInputTokenMs"),
    latencyPerOutputTokenMs: optionalNumber(cfg, "latencyPerOutputTokenMs"),
    carbonIntensityGPerKwh: Number(cfg.get("carbonIntensityGPerKwh", 475)),
  };
}
