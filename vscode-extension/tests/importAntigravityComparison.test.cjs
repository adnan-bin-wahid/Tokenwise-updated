const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");
let dialogs, files, errors, shown;
const load = Module._load;
Module._load = function (name, ...args) {
  if (name === "vscode") { return {
    window: { showOpenDialog: async () => dialogs.shift(), showErrorMessage: async message => errors.push(message) },
    workspace: { fs: { stat: async uri => ({ size: Buffer.byteLength(files[uri]) }), readFile: async uri => Buffer.from(files[uri]) } },
  }; }
  return load.call(this, name, ...args);
};
const { createImportAntigravityComparisonCommand } = require("../dist/commands/importAntigravityComparison.js");
Module._load = load;
const result = id => JSON.stringify({ conversation_id: id, status: "SUCCESS", response: "answer", duration_seconds: 1, num_turns: 1,
  usage: { input_tokens: 100, output_tokens: 10, total_tokens: 110 } });
function command() {
  dialogs = [["without.json"], ["with.json"]]; files = { "without.json": result("without"), "with.json": result("with") };
  errors = []; shown = [];
  return createImportAntigravityComparisonCommand({ showAgentUsageComparison: value => shown.push(value) });
}
test("imports two explicitly labeled logs without sending prompts or modifying files", async () => {
  await command()();
  assert.equal(errors.length, 0);
  assert.equal(shown[0].without.conversationId, "without");
  assert.equal(shown[0].with.conversationId, "with");
});
test("cancel and invalid second log leave the current report unchanged", async () => {
  let run = command(); dialogs[1] = undefined; await run();
  assert.equal(shown.length, 0); assert.equal(errors.length, 0);
  run = command(); files["with.json"] = "invalid"; await run();
  assert.equal(shown.length, 0); assert.equal(errors.length, 1);
});
test("oversized logs and accidentally choosing the same run twice fail visibly", async () => {
  let run = command(); files["without.json"] = " ".repeat(10 * 1024 * 1024 + 1); await run();
  assert.match(errors[0], /10 MiB/);
  run = command(); dialogs[1] = ["without.json"]; await run();
  assert.match(errors[0], /different fresh/); assert.equal(shown.length, 0);
});
