const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { execFile } = require("node:child_process");
const { promisify } = require("node:util");
const { EXTENSION_ID, safeChild } = require("../dist/services/cleanupFiles");
const { registerLifecycle, buildCleanupPlan, rememberWorkspace } = require("../dist/services/cleanupRegistry");
const { runCleanup, cleanupSettings } = require("../dist/services/uninstallCleanup");
const { ownsBackend, ownsInstaller, stopOwnedProcesses } = require("../dist/services/cleanupProcesses");
const { registerBackend, configureAutomaticContext } = require("../dist/services/automaticSetup");
const { launchUninstallWorker } = require("../dist/uninstall");
const templates = path.resolve(__dirname, "../resources/automatic-context");
const launcher = process.platform === "win32" ? "tokenwise-context.ps1" : "tokenwise-launcher.py";
const put = async (root, name, value) => {
  const target = path.join(root, name);
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, typeof value === "string" ? value : JSON.stringify(value));
};
const missing = async (name) => assert.rejects(fs.stat(name), { code: "ENOENT" });
const readJSON = async (name) => JSON.parse(await fs.readFile(name, "utf8"));
const outcome = () => ({ removed: [], preserved: [], warnings: [] });

async function fixture(t, managed = true) {
  const parent = await fs.realpath(os.tmpdir());
  const root = await fs.mkdtemp(path.join(parent, "tokenwise-uninstall-test-"));
  t.after(async () => {
    assert.equal(path.dirname(await fs.realpath(root)), parent);
    assert.ok(path.basename(root).startsWith("tokenwise-uninstall-test-"));
    await fs.rm(root, { recursive: true, force: true });
  });
  const extension = path.join(root, "extensions", `${EXTENSION_ID}-0.5.0`);
  const user = path.join(root, "User");
  const storage = path.join(user, "globalStorage", EXTENSION_ID);
  const workspace = path.join(root, "Python Project");
  await fs.mkdir(extension, { recursive: true });
  await fs.mkdir(workspace);
  await registerLifecycle(storage, extension);
  const installation = managed ? path.join(storage, "backend/managed/0.4.0-fixture") : path.join(root, "Existing Backend");
  for (const name of [process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python",
    "scripts/antigravity_context.py", "scripts/antigravity_hook.py", "swe-pruner/swe-pruner/src/swe_pruner/online_serving.py",
    ...["model.safetensors", "tokenizer.json", "config.json", "tokenizer_config.json", "backbone/config.json"].map(name => `swe-pruner/swe-pruner/model/${name}`)]) {
    await put(installation, name, "fixture");
  }
  if (managed) { await put(installation, "managed-install.json", { schema_version: 1 }); }
  const backend = await registerBackend(installation, storage);
  await configureAutomaticContext(workspace, backend, templates);
  await put(workspace, "app.py", "def answer():\n    return 42\n");
  await put(workspace, ".tokenwise/latest.json", { event_id: "test", query: "explain", transport: "antigravity-agent-command" });
  await put(workspace, `.tokenwise/conversations/${"a".repeat(64)}.json`, { prompt_id: "prompt", event_id: "test" });
  await put(workspace, `.tokenwise/conversations/${"a".repeat(64)}.lock`, "123");
  await put(storage, "backend/downloads/model.part", "download");
  await put(storage, "backend/pip-cache/test", "wheel");
  return { root, extension, user, storage, workspace, installation, backend };
}

test("normal cleanup removes all generated workspace/backend/cache/registry data", async t => {
  const f = await fixture(t);
  await put(f.user, "settings.json", '{\n  // Keep this setting\n  "editor.fontSize": 14,\n  "tokenWise.apiUrl": "http://127.0.0.1:8001",\n}\n');
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.deepEqual(result.warnings, []);
  assert.deepEqual(result.preserved, []);
  for (const name of [".agents", ".tokenwise", ".gitignore"]) { await missing(path.join(f.workspace, name)); }
  await missing(f.storage);
  await missing(path.join(f.root, "extensions/.tokenwise-cleanup"));
  assert.equal(await fs.readFile(path.join(f.workspace, "app.py"), "utf8"), "def answer():\n    return 42\n");
  const settings = await fs.readFile(path.join(f.user, "settings.json"), "utf8");
  assert.ok(settings.includes("Keep this setting"));
  assert.ok(settings.includes('"editor.fontSize": 14'));
  assert.ok(!settings.includes("tokenWise"));
});

test("cleanup is idempotent after all owned data is already removed", async t => {
  const f = await fixture(t);
  await runCleanup(await buildCleanupPlan(f.extension));
  const again = await runCleanup(await buildCleanupPlan(f.extension));
  assert.deepEqual(again.warnings, []);
  assert.equal(again.removed.length, 0);
});

test("unrelated hooks/rules/runtime notes and user edits survive cleanup", async t => {
  const f = await fixture(t);
  const hooksPath = path.join(f.workspace, ".agents/hooks.json");
  const hooks = await readJSON(hooksPath);
  hooks.team = { enabled: true, PostInvocation: [{ command: "team-hook" }] };
  hooks["tokenwise-automatic-context"].PreInvocation.unshift({ command: "team-before" });
  await put(f.workspace, ".agents/hooks.json", hooks);
  await put(f.workspace, ".agents/rules/team.md", "Do not remove team rules.\n");
  await put(f.workspace, ".tokenwise/my-notes.txt", "My own note");
  await put(f.workspace, ".gitignore", (await fs.readFile(path.join(f.workspace, ".gitignore"), "utf8")) + "dist/\n");
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.deepEqual(result.warnings, []);
  assert.ok(result.preserved.some(name => name.endsWith("my-notes.txt")));
  assert.equal(await fs.readFile(path.join(f.workspace, ".agents/rules/team.md"), "utf8"), "Do not remove team rules.\n");
  const remaining = await readJSON(hooksPath);
  assert.equal(remaining.team.PostInvocation[0].command, "team-hook");
  assert.deepEqual(remaining["tokenwise-automatic-context"].PreInvocation, [{ command: "team-before" }]);
  assert.equal((await fs.readFile(path.join(f.workspace, ".gitignore"), "utf8")).trim(), "dist/");
});

test("restores the exact original gitignore bytes including a missing final newline", async t => {
  const f = await fixture(t);
  await runCleanup(await buildCleanupPlan(f.extension));
  await registerLifecycle(f.storage, f.extension);
  const backend = await registerBackend((await fixture(t, false)).installation, f.storage);
  await put(f.workspace, ".gitignore", "# Original\r\nvenv/");
  await configureAutomaticContext(f.workspace, backend, templates);
  await configureAutomaticContext(f.workspace, backend, templates);
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.deepEqual(result.warnings, []);
  assert.equal(await fs.readFile(path.join(f.workspace, ".gitignore"), "utf8"), "# Original\r\nvenv/");
});

test("customized generated rules and launchers are preserved and reported", async t => {
  const f = await fixture(t);
  await put(f.workspace, ".agents/rules/tokenwise.md", "My customized rule\n");
  await put(f.workspace, `.agents/tokenwise/${launcher}`, "My customized launcher\n");
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.ok(result.preserved.includes(path.join(f.workspace, ".agents/rules/tokenwise.md")));
  assert.ok(result.preserved.includes(path.join(f.workspace, `.agents/tokenwise/${launcher}`)));
  assert.equal(await fs.readFile(path.join(f.workspace, ".agents/rules/tokenwise.md"), "utf8"), "My customized rule\n");
});

test("rules retained in ownership history are cleaned across platform transitions", async t => {
  const f = await fixture(t);
  await configureAutomaticContext(f.workspace, f.backend, templates, "darwin");
  await configureAutomaticContext(f.workspace, f.backend, templates, "win32");
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.deepEqual(result.preserved, []);
  assert.deepEqual(result.warnings, []);
  await missing(path.join(f.workspace, ".agents"));
});

test("existing backend checkouts are not deleted or signalled", async t => {
  const f = await fixture(t, false);
  let stopped = false;
  const plan = await buildCleanupPlan(f.extension);
  plan.profiles[0].backend.pid = 456;
  await runCleanup(plan, { platform: process.platform, probe: async () => { throw new Error("Should not probe existing checkout"); }, stop: async () => { stopped = true; } });
  assert.equal(stopped, false);
  assert.equal(await fs.readFile(path.join(f.installation, "scripts/antigravity_context.py"), "utf8"), "fixture");
  await missing(f.storage);
});

test("all tracked profiles and repositories are removed together", async t => {
  const f = await fixture(t, false);
  const storage = path.join(f.user, "profiles/second/globalStorage", EXTENSION_ID);
  const workspace = path.join(f.root, "Second Python Repo");
  await fs.mkdir(workspace);
  await registerLifecycle(storage, f.extension);
  const backend = await registerBackend(f.installation, storage);
  await configureAutomaticContext(workspace, backend, templates);
  await put(path.dirname(path.dirname(storage)), "settings.json", '{"tokenWise.defaultThreshold":0.7,"editor.fontSize":16}');
  const plan = await buildCleanupPlan(f.extension);
  assert.equal(plan.profiles.length, 2);
  const result = await runCleanup(plan);
  assert.deepEqual(result.warnings, []);
  await missing(storage); await missing(f.storage);
  await missing(path.join(workspace, ".agents"));
  const settings = await readJSON(path.join(path.dirname(path.dirname(storage)), "settings.json"));
  assert.deepEqual(settings, { "editor.fontSize": 16 });
});

test("IDE workspace history discovers a closed v0.4 repository with no new inventory", async t => {
  const f = await fixture(t);
  await fs.rm(path.join(f.storage, "backend/workspaces"), { recursive: true });
  await put(f.user, "workspaceStorage/history/workspace.json", { folder: pathToFileURL(f.workspace).href });
  const manifestPath = path.join(f.workspace, ".agents/tokenwise/setup.json");
  const manifest = await readJSON(manifestPath);
  delete manifest.cleanup;
  await put(f.workspace, ".agents/tokenwise/setup.json", manifest);
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.deepEqual(result.warnings, []);
  await missing(path.join(f.workspace, ".agents"));
  await missing(path.join(f.workspace, ".tokenwise"));
});

test("another IDE profile's workspace link is never cleaned", async t => {
  const f = await fixture(t);
  await put(f.workspace, ".tokenwise/backend-link.json", { schema_version: 1, registration_path: path.join(f.root, "other/backend/installation.json") });
  await put(f.workspace, ".vscode/settings.json", { "tokenWise.apiUrl": "keep" });
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.deepEqual(result.warnings, []);
  assert.ok((await fs.readFile(path.join(f.workspace, ".agents/rules/tokenwise.md"), "utf8")).length);
  assert.equal((await readJSON(path.join(f.workspace, ".vscode/settings.json")))["tokenWise.apiUrl"], "keep");
});

test("malformed hooks are preserved and their workspace remains in the retry inventory", async t => {
  const f = await fixture(t);
  await put(f.workspace, ".agents/hooks.json", '{"bad":');
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.ok(result.warnings.some(message => message.includes("Invalid JSON")));
  assert.equal(await fs.readFile(path.join(f.workspace, ".agents/hooks.json"), "utf8"), '{"bad":');
  await missing(f.storage);
  const retry = await buildCleanupPlan(f.extension);
  assert.ok(retry.profiles[0].workspaceRoots.includes(f.workspace));
  await put(f.workspace, ".agents/hooks.json", { "tokenwise-automatic-context": { enabled: true, PreInvocation: [{ command: process.platform === "win32" ? "powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise/tokenwise-hook.ps1" : "python3 .agents/tokenwise/tokenwise-launcher.py --hook" }] } });
  assert.deepEqual((await runCleanup(retry)).warnings, []);
  await missing(path.join(f.workspace, ".tokenwise"));
});

test("a malicious ownership manifest cannot delete an application file", async t => {
  const f = await fixture(t);
  const filename = path.join(f.workspace, ".agents/tokenwise/setup.json");
  const manifest = await readJSON(filename);
  manifest.files["app.py"] = require("node:crypto").createHash("sha256").update(await fs.readFile(path.join(f.workspace, "app.py"))).digest("hex");
  await put(f.workspace, ".agents/tokenwise/setup.json", manifest);
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.ok(result.warnings.some(message => message.includes("invalid owned path")));
  assert.equal(await fs.readFile(path.join(f.workspace, "app.py"), "utf8"), "def answer():\n    return 42\n");
});

test("junctions cannot redirect recursive backend cleanup outside owned storage", async t => {
  const f = await fixture(t);
  const elsewhere = path.join(f.root, "Do Not Touch");
  await fs.mkdir(elsewhere);
  await put(elsewhere, "important.txt", "keep");
  await fs.rename(f.storage, path.join(f.root, "original-storage"));
  await fs.symlink(elsewhere, f.storage, process.platform === "win32" ? "junction" : "dir");
  await assert.rejects(buildCleanupPlan(f.extension), /Unsafe cleanup root/);
  await assert.rejects(safeChild(path.dirname(f.storage), EXTENSION_ID), /symbolic link or junction/);
  assert.equal(await fs.readFile(path.join(elsewhere, "important.txt"), "utf8"), "keep");
});

test("settings cleanup preserves JSONC comments and rejects malformed JSONC", async t => {
  const f = await fixture(t);
  await put(f.user, "settings.json", '{\n// My font\n"editor.fontSize": 18,\n"tokenWise.pythonPath": "remove",\n"files.autoSave": "off",\n}\n');
  const result = outcome();
  await cleanupSettings(path.join(f.user, "settings.json"), result);
  const text = await fs.readFile(path.join(f.user, "settings.json"), "utf8");
  assert.ok(text.includes("// My font")); assert.ok(text.includes('"files.autoSave": "off"')); assert.ok(!text.includes("tokenWise"));
  await put(f.user, "settings.json", '{"broken":');
  await assert.rejects(cleanupSettings(path.join(f.user, "settings.json"), result), /Invalid JSON/);
  assert.equal(await fs.readFile(path.join(f.user, "settings.json"), "utf8"), '{"broken":');
});

test("PID ownership requires the managed virtual environment, not just a process number", async t => {
  const f = await fixture(t);
  const profile = (await buildCleanupPlan(f.extension)).profiles[0];
  profile.backend.pid = 123; profile.backend.port = 8002;
  const command = '"C:\\Python\\python.exe" -m uvicorn swe_pruner.online_serving:app --host 127.0.0.1 --port 8002';
  const identity = { pid: 123, executable: "C:\\Python\\python.exe", command };
  assert.equal(ownsBackend(identity, profile, "win32"), false);
  identity.parent = { executable: path.join(f.installation, ".venv/Scripts/python.exe"), command };
  assert.equal(ownsBackend(identity, profile, "win32"), true);
  assert.equal(ownsBackend({ ...identity, command: command.replace("8002", "8003") }, profile, "win32"), false);
  profile.backend.managed = false;
  assert.equal(ownsBackend(identity, profile, "win32"), false);
});

test("UTF-8 BOM and language-specific preferences are cleaned without losing other settings", async t => {
  const f = await fixture(t);
  await put(f.user, "settings.json", '\uFEFF{\n"[python]": {"tokenWise.apiUrl": "remove", "editor.tabSize": 4},\n"editor.fontSize": 14\n}\n');
  await cleanupSettings(path.join(f.user, "settings.json"), outcome());
  const text = await fs.readFile(path.join(f.user, "settings.json"), "utf8");
  assert.ok(text.startsWith("\uFEFF")); assert.ok(!text.includes("tokenWise")); assert.ok(text.includes('"editor.tabSize": 4'));
});

test("corrupt IDE history does not prevent cleanup of registered repositories", async t => {
  const f = await fixture(t);
  await put(f.user, "workspaceStorage/bad/workspace.json", '{"broken":');
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.ok(result.warnings.some(message => message.includes("workspace history")));
  await missing(path.join(f.workspace, ".agents")); await missing(f.storage);
});

test("a malformed multi-root workspace does not prevent cleanup of registered repositories", async t => {
  const f = await fixture(t);
  const configuration = path.join(f.root, "broken.code-workspace");
  await put(f.root, "broken.code-workspace", '{"folders":');
  await put(f.user, "workspaceStorage/bad/workspace.json", { workspace: pathToFileURL(configuration).href });
  const result = await runCleanup(await buildCleanupPlan(f.extension));
  assert.ok(result.warnings.some(message => message.includes("workspace configuration")));
  await missing(path.join(f.workspace, ".agents")); await missing(f.storage);
  assert.equal(await fs.readFile(configuration, "utf8"), '{"folders":');
});

test("an installer PID must name the installer and exact storage argument", async t => {
  const f = await fixture(t);
  const profile = (await buildCleanupPlan(f.extension)).profiles[0];
  profile.backend.installerPid = 456;
  const identity = { pid: 456, executable: "python.exe", command: `python.exe "${f.extension}/scripts/install_backend.py" --storage "${f.storage}"` };
  assert.equal(ownsInstaller(identity, profile), true);
  assert.equal(ownsInstaller({ ...identity, command: identity.command.replace(f.storage, f.root) }, profile), false);
  assert.equal(ownsInstaller({ ...identity, command: "python.exe some-other-tool.py" }, profile), false);
});

test("unverified and reused backend PIDs are never stopped and storage is retained", async t => {
  const f = await fixture(t);
  const plan = await buildCleanupPlan(f.extension);
  plan.profiles[0].backend.pid = 123; plan.profiles[0].backend.port = 8002;
  let signals = 0;
  const result = await runCleanup(plan, { platform: "win32", probe: async () => ({ pid: 123, executable: "unrelated.exe", command: "unrelated" }), stop: async () => signals++ });
  assert.ok(result.warnings.some(message => message.includes("unverified")));
  assert.equal(signals, 0); assert.ok(await fs.stat(f.storage));
  const profile = plan.profiles[0];
  const own = { pid: 123, executable: path.join(f.installation, ".venv/Scripts/python.exe"), command: "python.exe -m uvicorn swe_pruner.online_serving:app --port 8002" };
  let probes = 0;
  await assert.rejects(stopOwnedProcesses(profile, { platform: "win32", probe: async () => ++probes === 1 ? own : { ...own, executable: "other.exe" }, stop: async () => signals++ }), /changed identity/);
  assert.equal(signals, 0);
});

test("verified backend and installer processes are stopped before deleting managed storage", async t => {
  const f = await fixture(t);
  const plan = await buildCleanupPlan(f.extension);
  const profile = plan.profiles[0];
  profile.backend.pid = 123; profile.backend.port = 8002; profile.backend.installerPid = 456;
  const identities = new Map([
    [123, { pid: 123, executable: path.join(f.installation, ".venv/Scripts/python.exe"), command: "python.exe -m uvicorn swe_pruner.online_serving:app --port 8002" }],
    [456, { pid: 456, executable: "python.exe", command: `python.exe "${f.extension}/scripts/install_backend.py" --storage "${f.storage}"` }],
  ]);
  const signals = [];
  const result = await runCleanup(plan, { platform: "win32", probe: async pid => identities.get(pid), stop: async pid => {
    assert.ok(await fs.stat(f.storage));
    assert.ok(await fs.stat(path.join(f.workspace, ".agents/rules/tokenwise.md")), "stop before removing workspace integration");
    signals.push(pid); identities.delete(pid);
  } });
  assert.deepEqual(signals, [456, 123]); assert.deepEqual(result.warnings, []); await missing(f.storage);
});

test("standalone worker survives removal of the original extension directory", async t => {
  const f = await fixture(t);
  await fs.cp(path.resolve(__dirname, "../dist"), path.join(f.extension, "dist"), { recursive: true });
  const started = Date.now();
  const worker = await launchUninstallWorker(f.extension);
  assert.ok(Date.now() - started < 4500, "bootstrap must fit inside the editor's 5-second hook limit");
  assert.equal(path.dirname(f.extension), path.join(f.root, "extensions"));
  await fs.rm(f.extension, { recursive: true });
  for (let attempt = 0; attempt < 200; attempt++) {
    if (!await fs.stat(worker).catch(() => undefined)) { break; }
    const report = await fs.readFile(path.join(worker, "cleanup-report.json"), "utf8").catch(() => undefined);
    if (report) { throw new Error(report); }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  await missing(worker); await missing(f.storage);
  await missing(path.join(f.workspace, ".agents")); await missing(path.join(f.workspace, ".tokenwise"));
  assert.ok(await fs.stat(path.join(f.workspace, "app.py")));
});

test("manual execution without the editor uninstall flag cannot start cleanup", async () => {
  await assert.rejects(promisify(execFile)(process.execPath, [path.resolve(__dirname, "../dist/uninstall.js")]), error => error.code === 1 && error.stderr.includes("reserved for the editor uninstall hook"));
});
