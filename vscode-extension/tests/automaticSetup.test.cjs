const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { configureAutomaticContext, registerBackend, discoverRegisteredBackend } = require("../dist/services/automaticSetup.js");

const templates = path.resolve(__dirname, "../resources/automatic-context");
const legacyCommand = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise-hook.ps1";
const command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise/tokenwise-hook.ps1";

async function put(root, relative, content) {
  const filename = path.join(root, relative);
  await fs.mkdir(path.dirname(filename), { recursive: true });
  await fs.writeFile(filename, typeof content === "string" ? content : JSON.stringify(content));
}
async function json(root, relative) { return JSON.parse(await fs.readFile(path.join(root, relative), "utf8")); }
async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "tokenwise-setup-test-"));
  t.after(async () => {
    assert.equal(path.dirname(root), await fs.realpath(os.tmpdir()));
    assert.ok(path.basename(root).startsWith("tokenwise-setup-test-"));
    await fs.rm(root, { recursive: true, force: true });
  });
  const installation = path.join(root, "Shared Backend");
  const required = [
    process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python",
    "scripts/antigravity_context.py", "scripts/antigravity_hook.py",
    "swe-pruner/swe-pruner/src/swe_pruner/online_serving.py",
    ...["model.safetensors", "tokenizer.json", "config.json", "tokenizer_config.json", "backbone/config.json"].map((name) => `swe-pruner/swe-pruner/model/${name}`),
  ];
  for (const filename of required) { await put(installation, filename, "fixture"); }
  const storage = path.join(root, "Extension User Storage");
  const workspace = path.join(root, "External Python Repository");
  await fs.mkdir(workspace);
  const backend = await registerBackend(installation, storage);
  return { root, installation, storage, workspace, backend };
}

test("external repositories share a centrally registered backend; setup is idempotent", async (t) => {
  const { root, installation, storage, workspace, backend } = await fixture(t);
  const first = await configureAutomaticContext(workspace, backend, templates);
  assert.equal(first.rulePath, ".agents/rules/tokenwise.md");
  assert.equal(first.changedFiles.length, 9);
  assert.equal(await discoverRegisteredBackend(storage), await fs.realpath(installation));
  const link = await json(workspace, ".tokenwise/backend-link.json");
  assert.equal(link.registration_path, backend.registrationPath);
  assert.equal(backend.registration.runtime_dir, path.join(await fs.realpath(storage), "backend/runtime"));
  const second = path.join(root, "Another Repository");
  await fs.mkdir(second);
  await configureAutomaticContext(second, backend, templates);
  assert.deepEqual(await json(second, ".tokenwise/backend-link.json"), link);
  assert.deepEqual((await configureAutomaticContext(workspace, backend, templates)).changedFiles, []);
  const rule = await fs.readFile(path.join(workspace, first.rulePath), "utf8");
  assert.ok(!rule.includes(installation));
  assert.match(rule, /\.agents\/tokenwise\/tokenwise-context\.ps1/);
});

test("preserves custom rules, handlers, settings, and existing ignore bytes", async (t) => {
  const { workspace, backend } = await fixture(t);
  const customRule = "---\ntrigger: always_on\n---\nMy own TokenWise instructions.\n";
  await put(workspace, ".agents/rules/tokenwise.md", customRule);
  await put(workspace, ".agents/rules/team.md", "Team rules\n");
  await put(workspace, ".agents/tokenwise.json", { enabled: false, token_budget: 1024, threshold: 0.6, custom_setting: "keep" });
  const customHandler = { type: "command", command: "team-hook.ps1", timeout: 10 };
  await put(workspace, ".agents/hooks.json", {
    team: { enabled: true, PostInvocation: [customHandler] },
    "tokenwise-automatic-context": { note: "keep", PreInvocation: [customHandler, { type: "command", command: legacyCommand }] },
  });
  await put(workspace, ".gitignore", "# Team ignores\r\nvenv/\r\n");
  const result = await configureAutomaticContext(workspace, backend, templates);
  assert.equal(result.rulePath, ".agents/rules/tokenwise-automatic-context.md");
  assert.equal(await fs.readFile(path.join(workspace, ".agents/rules/tokenwise.md"), "utf8"), customRule);
  assert.equal(await fs.readFile(path.join(workspace, ".agents/rules/team.md"), "utf8"), "Team rules\n");
  const hooks = await json(workspace, ".agents/hooks.json");
  assert.deepEqual(hooks.team.PostInvocation, [customHandler]);
  assert.equal(hooks["tokenwise-automatic-context"].note, "keep");
  assert.deepEqual(hooks["tokenwise-automatic-context"].PreInvocation[0], customHandler);
  assert.equal(hooks["tokenwise-automatic-context"].PreInvocation[1].command, command);
  const settings = await json(workspace, ".agents/tokenwise.json");
  assert.equal(settings.token_budget, 1024);
  assert.equal(settings.threshold, 0.6);
  assert.equal(settings.custom_setting, "keep");
  assert.equal(settings.enabled, true);
  assert.equal(await fs.readFile(path.join(workspace, ".gitignore"), "utf8"), "# Team ignores\r\nvenv/\r\n# TokenWise local context and backend link\r\n/.tokenwise/\r\n");
  assert.deepEqual((await configureAutomaticContext(workspace, backend, templates)).changedFiles, []);
});

test("migrates only the exact legacy generated rule", async (t) => {
  const { workspace, backend } = await fixture(t);
  const legacy = await fs.readFile(path.resolve(__dirname, "../../Test_project/.agents/rules/tokenwise.md"));
  await put(workspace, ".agents/rules/tokenwise.md", legacy.toString("utf8"));
  assert.equal((await configureAutomaticContext(workspace, backend, templates)).rulePath, ".agents/rules/tokenwise.md");
  assert.match(await fs.readFile(path.join(workspace, ".agents/rules/tokenwise.md"), "utf8"), /\.agents\/tokenwise\/tokenwise-context/);
});

test("malformed JSON and invalid settings cause no partial workspace setup", async (t) => {
  const { workspace, backend } = await fixture(t);
  for (const [filename, content] of [
    [".agents/hooks.json", '{"unfinished":'], [".agents/tokenwise.json", '{"token_budget": "1024"}'],
    [".agents/tokenwise/setup.json", "[]"],
  ]) {
    await put(workspace, filename, content);
    await assert.rejects(configureAutomaticContext(workspace, backend, templates));
    assert.equal(await fs.readFile(path.join(workspace, filename), "utf8"), content);
    await assert.rejects(fs.stat(path.join(workspace, ".tokenwise/backend-link.json")), { code: "ENOENT" });
    await fs.unlink(path.join(workspace, filename));
  }
});

test("refuses to overwrite customized managed launchers", async (t) => {
  const { workspace, backend } = await fixture(t);
  await configureAutomaticContext(workspace, backend, templates);
  const relative = ".agents/tokenwise/tokenwise-context.ps1";
  await put(workspace, relative, "# My changed launcher\n");
  const hooksBefore = await fs.readFile(path.join(workspace, ".agents/hooks.json"));
  await assert.rejects(configureAutomaticContext(workspace, backend, templates), /customized file/);
  assert.equal(await fs.readFile(path.join(workspace, relative), "utf8"), "# My changed launcher\n");
  assert.deepEqual(await fs.readFile(path.join(workspace, ".agents/hooks.json")), hooksBefore);
});

test("uses another rule filename when a previously managed rule was customized", async (t) => {
  const { workspace, backend } = await fixture(t);
  await configureAutomaticContext(workspace, backend, templates);
  await put(workspace, ".agents/rules/tokenwise.md", "Custom rule\n");
  const result = await configureAutomaticContext(workspace, backend, templates);
  assert.equal(result.rulePath, ".agents/rules/tokenwise-automatic-context.md");
  assert.equal(await fs.readFile(path.join(workspace, ".agents/rules/tokenwise.md"), "utf8"), "Custom rule\n");
});

test("rejects junctions that could redirect writes outside the workspace", async (t) => {
  const { root, workspace, backend } = await fixture(t);
  const other = path.join(root, "Do Not Touch");
  await fs.mkdir(other);
  await fs.symlink(other, path.join(workspace, ".agents"), process.platform === "win32" ? "junction" : "dir");
  await assert.rejects(configureAutomaticContext(workspace, backend, templates), /symbolic link or junction/);
  assert.deepEqual(await fs.readdir(other), []);
});

test("backend discovery rejects missing model assets and recovers after relocation", async (t) => {
  const { root, installation, storage } = await fixture(t);
  const moved = path.join(root, "Relocated Backend");
  await fs.rename(installation, moved);
  assert.equal(await discoverRegisteredBackend(storage), undefined);
  await registerBackend(moved, storage);
  assert.equal(await discoverRegisteredBackend(storage), await fs.realpath(moved));
  await fs.unlink(path.join(moved, "swe-pruner/swe-pruner/model/config.json"));
  await assert.rejects(registerBackend(moved, storage), /config.json/);
});

test("a write failure rolls back only files written by the setup attempt", async (t) => {
  const { workspace, backend } = await fixture(t);
  const settings = '{"token_budget": 1024}\n';
  await put(workspace, ".agents/tokenwise.json", settings);
  await put(workspace, ".agents/rules/team.md", "Leave this rule intact\n");
  const rename = fs.rename;
  t.mock.method(fs, "rename", async (source, target) => {
    if (target === path.join(workspace, ".agents/hooks.json")) { throw new Error("simulated write failure"); }
    return rename(source, target);
  });
  await assert.rejects(configureAutomaticContext(workspace, backend, templates), /simulated write failure/);
  assert.equal(await fs.readFile(path.join(workspace, ".agents/tokenwise.json"), "utf8"), settings);
  assert.equal(await fs.readFile(path.join(workspace, ".agents/rules/team.md"), "utf8"), "Leave this rule intact\n");
  for (const relative of [".gitignore", ".agents/rules/tokenwise.md", ".agents/tokenwise/tokenwise-context.ps1", ".tokenwise/backend-link.json"]) {
    await assert.rejects(fs.stat(path.join(workspace, relative)), { code: "ENOENT" });
  }
});
