const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs/promises");
const path = require("node:path");
const os = require("node:os");
const { promisify } = require("node:util");
const execFile = promisify(require("node:child_process").execFile);

async function fixture(t) {
  const prefix = path.join(os.tmpdir(), "tokenwise-demo-package-");
  const root = await fs.mkdtemp(prefix);
  t.after(async () => {
    if (!root.startsWith(prefix) || await fs.realpath(root) !== root) { throw new Error("Invalid fixture cleanup path"); }
    await fs.rm(root, { recursive: true, force: true });
  });
  async function write(relative, text = "fixture\n") {
    const destination = path.join(root, relative);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(destination, text);
  }
  const backend = "swe-pruner/swe-pruner";
  const models = ["config.json", "tokenizer.json", "tokenizer_config.json", "backbone/config.json",
    "added_tokens.json", "special_tokens_map.json", "chat_template.jinja", "merges.txt", "vocab.json", "README.md"];
  const documents = ["ANTIGRAVITY.md", "PROJECT-EVALUATION.md", "DEVELOPMENT.md", "PUBLISHING.md", "THIRD-PARTY-NOTICES.md"];
  for (const relative of ["scripts/antigravity_context.py", "scripts/antigravity_hook.py",
    "scripts/install_backend.py", "scripts/backend_control.py", `${backend}/pyproject.toml`,
    `${backend}/README.md`, `${backend}/LICENSE`, `${backend}/src/fixture.py`, `${backend}/carbon_artifacts/fixture.json`,
    ...models.map(name => `${backend}/model/${name}`), "README.md", "demonstation.md", "LICENSE", "CHANGELOG.md",
    "docs/release-notes/v0.6.5.md", ...documents.map(name => `docs/${name}`),
    "demonstration/tokenwise_demo/app.py", "demonstration/tokenwise_demo/tests/test_app.py",
    "demonstration/old_project/app.py", "demonstration/tokenwise_demo/.agents/rules/private.md",
    "demonstration/tokenwise_demo/.tokenwise/latest.json", "demonstration/results/private.json"]) {
    await write(relative);
  }
  await write("demonstration/cases.json", JSON.stringify({ cases: [{ project: "tokenwise_demo" }] }));
  await write("vscode-extension/package.json", JSON.stringify({ name: "tokenwise-vscode", version: "0.6.5" }));
  await write("vscode-extension/tokenwise-vscode-0.6.5.vsix");
  await fs.mkdir(path.join(root, "vscode-extension/resources"), { recursive: true });
  for (const name of ["prepare-extension.cjs", "package-release.cjs"]) {
    await fs.copyFile(path.resolve(__dirname, "../../scripts", name), path.join(root, "scripts", name));
  }
  return { root, write };
}

test("rebundling removes stale demos and includes only manifest projects without private runtime", async t => {
  const { root, write } = await fixture(t);
  const resources = "vscode-extension/resources/demonstration";
  await write(`${resources}/old_project/app.py`);
  await write(`${resources}/tokenwise_demo/removed.py`);
  await execFile(process.execPath, [path.join(root, "scripts/prepare-extension.cjs")], { windowsHide: true, timeout: 30000 });
  assert.deepEqual((await fs.readdir(path.join(root, resources))).sort(), ["cases.json", "tokenwise_demo"]);
  assert.deepEqual((await fs.readdir(path.join(root, resources, "tokenwise_demo"))).sort(), ["app.py", "tests"]);
  assert.equal(await fs.readFile(path.join(root, "demonstration/old_project/app.py"), "utf8"), "fixture\n");
  assert.equal(await fs.readFile(path.join(root, "demonstration/tokenwise_demo/.tokenwise/latest.json"), "utf8"), "fixture\n");
});

test("shareable package contains the one project and hashes it, not unrelated local folders", async t => {
  const { root } = await fixture(t);
  await execFile(process.execPath, [path.join(root, "scripts/package-release.cjs")], { windowsHide: true, timeout: 30000 });
  const release = path.join(root, "releases/TokenWise-0.6.5");
  assert.deepEqual((await fs.readdir(path.join(release, "demonstration"))).sort(), ["cases.json", "tokenwise_demo"]);
  const checksums = await fs.readFile(path.join(release, "SHA256SUMS.txt"), "utf8");
  assert.match(checksums, /demonstration\/tokenwise_demo\/app\.py/);
  assert.doesNotMatch(checksums, /old_project|\.agents|\.tokenwise|private/);
});

test("invalid project manifests fail without erasing the existing generated demo", async t => {
  const { root, write } = await fixture(t);
  const sentinel = "vscode-extension/resources/demonstration/keep.md";
  await write(sentinel, "previous generated evidence\n");
  for (const cases of [[], [{}], [null], [{ project: "../outside" }], [{ project: 123 }]]) {
    await write("demonstration/cases.json", JSON.stringify({ cases }));
    for (const script of ["prepare-extension.cjs", "package-release.cjs"]) {
      await assert.rejects(execFile(process.execPath, [path.join(root, "scripts", script)],
        { windowsHide: true, timeout: 30000 }), error => /Invalid demonstration project manifest/.test(error.stderr));
    }
    assert.equal(await fs.readFile(path.join(root, sentinel), "utf8"), "previous generated evidence\n");
  }
});

test("bundling refuses a demonstration junction and does not touch its destination", async t => {
  const { root, write } = await fixture(t);
  await write("outside/keep.md", "do not change\n");
  const destination = path.join(root, "vscode-extension/resources/demonstration");
  await fs.symlink(path.join(root, "outside"), destination, process.platform === "win32" ? "junction" : "dir");
  await assert.rejects(execFile(process.execPath, [path.join(root, "scripts/prepare-extension.cjs")],
    { windowsHide: true, timeout: 30000 }), error => /demonstration cannot be a symbolic link/.test(error.stderr));
  assert.equal(await fs.readFile(path.join(root, "outside/keep.md"), "utf8"), "do not change\n");
});
