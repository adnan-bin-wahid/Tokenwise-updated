export interface AgentUsageRun {
  conversationId: string;
  model?: string;
  durationSeconds: number;
  answer: string;
  usage: { input_tokens: number; output_tokens: number; total_tokens: number;
    thinking_tokens?: number; cache_read_tokens?: number };
  tools: { step: number; name: string; parameters: unknown; failed: boolean }[];
  toolTraceAvailable: boolean;
}

export interface AgentUsageComparison {
  measurement_scope: "imported_antigravity_cli_usage";
  importedAt: string;
  without: AgentUsageRun;
  with: AgentUsageRun;
  notes: string[];
}

function object(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function parseAntigravityUsage(text: string): AgentUsageRun {
  if (Buffer.byteLength(text, "utf8") > 10 * 1024 * 1024) { throw new Error("Usage logs must be at most 10 MiB."); }
  const source = text.replace(/^\uFEFF/, "").trim();
  let records: unknown[];
  try { records = [JSON.parse(source)]; }
  catch { records = source.split(/\r?\n/).filter(line => line.trim()).map(line => JSON.parse(line)); }
  if (!records.length || records.some(record => !object(record))) { throw new Error("Expected Antigravity JSON or stream-json objects."); }
  const events = records as Record<string, unknown>[];
  const envelopes = events.filter(record => record.event === "result").map(record => record.result);
  const streaming = events.some(record => record.event !== undefined);
  if (!streaming && records.length !== 1) { throw new Error("Import one JSON result per log."); }
  if (streaming && envelopes.length !== 1) { throw new Error("Import exactly one completed, fresh conversation per log."); }
  const result = streaming ? envelopes[0] : events[0];
  if (!object(result) || result.status !== "SUCCESS" || result.num_turns !== 1
    || typeof result.conversation_id !== "string" || !result.conversation_id.trim()
    || typeof result.response !== "string" || !result.response.trim()
    || typeof result.duration_seconds !== "number" || !Number.isFinite(result.duration_seconds) || result.duration_seconds < 0
    || !object(result.usage)) { throw new Error("A successful single-turn run with reported usage and an answer is required."); }
  const usage = result.usage;
  for (const key of ["input_tokens", "output_tokens", "total_tokens", "thinking_tokens", "cache_read_tokens"]) {
    if (usage[key] === undefined && ["thinking_tokens", "cache_read_tokens"].includes(key)) { continue; }
    if (!Number.isSafeInteger(usage[key]) || Number(usage[key]) < 0) { throw new Error(`Invalid reported ${key}.`); }
  }
  if (Number(usage.total_tokens) === 0) { throw new Error("Zero-usage logs cannot demonstrate measured savings."); }
  const tools = new Map<number, AgentUsageRun["tools"][number]>();
  let model: string | undefined;
  for (const record of events) {
    if (record.event === "init") {
      if (record.conversation_id !== result.conversation_id) { throw new Error("Mixed conversation IDs in usage log."); }
      if (object(record.init) && typeof record.init.model === "string") { model = record.init.model; }
    }
    const step = record.step_update;
    if (!object(step)) { continue; }
    if (step.conversation_id !== result.conversation_id) { throw new Error("Mixed conversation IDs in usage log."); }
    if (step.state !== "DONE" || step.step_type !== "tool") { continue; }
    if (!Number.isSafeInteger(step.step_index) || Number(step.step_index) < 0) { throw new Error("Invalid tool step index."); }
    const info = object(step.tool_info) ? step.tool_info : {};
    tools.set(Number(step.step_index), { step: Number(step.step_index),
      name: String(step.tool_name ?? info.name ?? "unknown"), parameters: info.parameters ?? null, failed: Boolean(info.error) });
  }
  return { conversationId: result.conversation_id, model, durationSeconds: result.duration_seconds,
    answer: result.response, usage: usage as AgentUsageRun["usage"], tools: [...tools.values()].sort((a, b) => a.step - b.step),
    toolTraceAvailable: streaming };
}

export function compareAntigravityUsage(without: AgentUsageRun, withTokenWise: AgentUsageRun): AgentUsageComparison {
  if (without.conversationId === withTokenWise.conversationId) { throw new Error("Use two different fresh conversations, not the same log twice."); }
  if (without.model && withTokenWise.model && without.model !== withTokenWise.model) { throw new Error("The reported models differ. Repeat both runs with the same pinned model."); }
  return { measurement_scope: "imported_antigravity_cli_usage", importedAt: new Date().toISOString(), without, with: withTokenWise,
    notes: ["Reported CLI usage is distinct from local packet counts and is not telemetry from the IDE chat panel.",
      "Without/with labels are assigned by the user. These logs do not verify identical tasks, settings, or whether TokenWise context was consumed.",
      without.model && withTokenWise.model ? `Both logs report model ${without.model}.` : "Model identity is not reported in both logs; equality is unverified.",
      "Input, cache-read, output, thinking and total counters are kept separate as reported; no cache/thinking counters are added to totals.",
      "Tool traces list observed completed tool calls and parameters, not an exhaustive list of files visible to the model. JSON-only logs have no tool trace.",
      "No automatic answer-quality grade or causal savings claim is inferred from two runs. Repeat and score answers against ground truth."] };
}
