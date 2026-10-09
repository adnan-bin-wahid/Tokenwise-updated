const assert = require("node:assert/strict");
const { test } = require("node:test");
const { parseAntigravityUsage, compareAntigravityUsage } = require("../dist/services/antigravityUsage.js");
const result = (id = "without", input = 100) => ({ conversation_id: id, status: "SUCCESS", response: "Evidence-based answer",
  duration_seconds: 2, num_turns: 1, usage: { input_tokens: input, output_tokens: 20, thinking_tokens: 10, cache_read_tokens: 30, total_tokens: input + 20 } });
const stream = (id = "without", input = 100, model = "model-a") => {
  const tool = { conversation_id: id, step_index: 2, step_type: "tool", state: "DONE", tool_name: "view_file",
    tool_info: { parameters: { AbsolutePath: "C:/demo/auth.py" }, output: "source" } };
  return [ { event: "init", conversation_id: id, init: { model } },
    { event: "step_update", step_update: { ...tool, state: "ACTIVE" } },
    { event: "step_update", step_update: tool }, { event: "step_update", step_update: tool },
    { event: "result", result: result(id, input) } ].map(value => JSON.stringify(value)).join("\n");
};
test("CLI JSON retains reported counters without adding thinking or cache reads", () => {
  const run = parseAntigravityUsage("\uFEFF" + JSON.stringify(result()));
  assert.equal(run.usage.total_tokens, 120);
  assert.equal(run.toolTraceAvailable, false);
  assert.deepEqual(run.tools, []);
});
test("stream JSON counts each completed tool step once and uses terminal usage only", () => {
  const run = parseAntigravityUsage(stream());
  assert.equal(run.model, "model-a");
  assert.equal(run.tools.length, 1);
  assert.equal(run.tools[0].parameters.AbsolutePath, "C:/demo/auth.py");
  assert.equal(run.tools[0].output, undefined);
  assert.equal(run.usage.input_tokens, 100);
});
test("rejects failed, resumed, missing, invalid and zero reported usage", () => {
  for (const change of [{ status: "ERROR" }, { num_turns: 2 }, { response: "" }, { duration_seconds: -1 },
    { usage: {} }, { usage: { input_tokens: -1, output_tokens: 2, total_tokens: 1 } },
    { usage: { input_tokens: 1.5, output_tokens: 2, total_tokens: 3 } },
    { usage: { input_tokens: 0, output_tokens: 0, total_tokens: 0 } }]) {
    assert.throws(() => parseAntigravityUsage(JSON.stringify({ ...result(), ...change })));
  }
  assert.throws(() => parseAntigravityUsage("{bad json"));
  assert.throws(() => parseAntigravityUsage(JSON.stringify([])));
  assert.throws(() => parseAntigravityUsage(stream() + "\n" + JSON.stringify({ event: "result", result: result() })));
  assert.throws(() => parseAntigravityUsage(stream().replace('"conversation_id":"without"', '"conversation_id":"other"')), /Mixed/);
  assert.throws(() => parseAntigravityUsage(" ".repeat(10 * 1024 * 1024 + 1)), /10 MiB/);
});
test("independent same-model comparisons preserve answers and disclose user labels", () => {
  const comparison = compareAntigravityUsage(parseAntigravityUsage(stream()), parseAntigravityUsage(stream("with", 60)));
  assert.equal(comparison.measurement_scope, "imported_antigravity_cli_usage");
  assert.equal(comparison.with.usage.input_tokens, 60);
  assert.ok(comparison.notes.some(note => /assigned by the user/.test(note)));
});
test("same session and different pinned models cannot form a controlled pair", () => {
  assert.throws(() => compareAntigravityUsage(parseAntigravityUsage(stream()), parseAntigravityUsage(stream())), /different fresh/);
  assert.throws(() => compareAntigravityUsage(parseAntigravityUsage(stream()), parseAntigravityUsage(stream("with", 60, "model-b"))), /models differ/);
  const comparison = compareAntigravityUsage(parseAntigravityUsage(JSON.stringify(result())), parseAntigravityUsage(JSON.stringify(result("with"))));
  assert.ok(comparison.notes.some(note => /unverified/.test(note)));
});
