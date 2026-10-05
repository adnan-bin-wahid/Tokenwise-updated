const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const pythonPattern = "**/*.[pP][yY]";
async function until(condition) {
  for (let attempt = 0; attempt < 200; attempt++) {
    if (condition()) { return; }
    await delay(10);
  }
  assert.ok(condition(), "Expected indexing activity did not arrive");
}
function event() {
  const listeners = new Set();
  return { subscribe: listener => { listeners.add(listener); return { dispose: () => listeners.delete(listener) }; },
    emit: value => { for (const listener of [...listeners]) { listener(value); } } };
}
const uri = (fsPath, scheme = "file") => ({ fsPath, scheme, authority: "", with: () => uri(fsPath), toString: () => `${scheme}:${fsPath}` });
const response = body => ({ ok: true, status: 200, json: async () => ({ indexed_files: 2,
  repository_fingerprint: (body.action === "update" ? "b" : "a").repeat(64), retrieval_cache_hit: true }) });

async function fixture(t, options = {}) {
  const temporary = await fs.realpath(os.tmpdir());
  const root = await fs.mkdtemp(path.join(temporary, "tokenwise-index-sync-test-"));
  const workspace = path.join(root, "Python Repository");
  const storage = path.join(root, "User/globalStorage/adnan-bin-wahid.tokenwise-vscode");
  await fs.mkdir(workspace, { recursive: true });
  const put = async (relative, data) => {
    const filename = path.join(workspace, relative);
    await fs.mkdir(path.dirname(filename), { recursive: true });
    await fs.writeFile(filename, JSON.stringify(data));
  };
  if (options.configured !== false) {
    await put(".tokenwise/backend-link.json", { schema_version: 1, registration_path: path.join(storage, "backend/installation.json") });
    await put(".agents/tokenwise.json", options.settings ?? { enabled: true });
  }
  const folder = { name: "Python Repository", uri: uri(workspace, options.scheme) };
  const requests = [], endpoints = [], logs = [], watchers = [];
  const folders = event(), trust = event(), rename = event(), deleted = event();
  const api = {
    env: { remoteName: options.remote },
    workspace: {
      isTrusted: options.trusted ?? true, workspaceFolders: [folder],
      onDidChangeWorkspaceFolders: folders.subscribe,
      onDidGrantWorkspaceTrust: trust.subscribe,
      onDidRenameFiles: rename.subscribe, onDidDeleteFiles: deleted.subscribe,
      createFileSystemWatcher: pattern => {
        const create = event(), change = event(), remove = event();
        const watcher = { pattern: pattern.pattern, create, change, remove, disposed: false,
          onDidCreate: create.subscribe, onDidChange: change.subscribe, onDidDelete: remove.subscribe,
          dispose() { this.disposed = true; } };
        watchers.push(watcher);
        return watcher;
      },
    },
    RelativePattern: class { constructor(_, pattern) { this.pattern = pattern; } },
    window: { createOutputChannel: () => ({ appendLine: line => logs.push(line), dispose() {} }) },
  };
  const filename = require.resolve("../dist/services/repositoryIndexSync");
  delete require.cache[filename];
  const load = Module._load;
  Module._load = function(request, ...args) { return request === "vscode" ? api : load.call(this, request, ...args); };
  let IndexSync;
  try { IndexSync = require(filename).RepositoryIndexSync; }
  finally { Module._load = load; delete require.cache[filename]; }
  const originalFetch = global.fetch;
  global.fetch = async (url, init) => {
    const request = { url, body: JSON.parse(init.body), signal: init.signal };
    requests.push(request);
    const work = Promise.resolve().then(() => options.handle ? options.handle(request) : response(request.body));
    return new Promise((resolve, reject) => {
      const abort = () => reject(new Error("Index request aborted"));
      if (init.signal.aborted) { abort(); }
      else { init.signal.addEventListener("abort", abort, { once: true }); }
      work.then(resolve, reject).finally(() => init.signal.removeEventListener("abort", abort));
    });
  };
  const context = { globalStorageUri: uri(storage, "vscode-userdata") };
  const index = new IndexSync(context, async start => {
    endpoints.push(start);
    return options.endpoint ? options.endpoint(start) : "http://127.0.0.1:8800";
  }, 2, options.heartbeatMs ?? 30000);
  t.after(async () => {
    index.dispose();
    await delay(30);
    global.fetch = originalFetch;
    assert.equal(path.dirname(await fs.realpath(root)), temporary);
    assert.ok(path.basename(root).startsWith("tokenwise-index-sync-test-"));
    await fs.rm(root, { recursive: true, force: true });
  });
  const actions = name => requests.filter(request => request.body.action === name);
  const source = () => watchers.find(watcher => watcher.pattern === pythonPattern && !watcher.disposed);
  const changed = relative => source().change.emit(uri(path.join(workspace, relative)));
  return { root, workspace, folder, put, api, index, requests, endpoints, logs, watchers, folders, trust, rename, deleted, actions, changed, source };
}

test("opening a configured trusted workspace warms its index in the background", async t => {
  const f = await fixture(t);
  await until(() => f.actions("start").length === 1 && f.logs.some(line => line.includes("2 Python files indexed")));
  assert.deepEqual(f.endpoints, [true]);
  assert.equal(f.actions("start")[0].body.workspace_root, f.workspace);
  assert.ok(f.watchers.some(watcher => watcher.pattern === pythonPattern));
});

test("unconfigured folders do not start a backend or send repository paths", async t => {
  const f = await fixture(t, { configured: false });
  await delay(50);
  assert.equal(f.requests.length, 0); assert.equal(f.endpoints.length, 0);
  assert.ok(!f.watchers.some(watcher => watcher.pattern === pythonPattern));
  await f.put(".tokenwise/backend-link.json", { schema_version: 1, registration_path: path.join(f.root, "User/globalStorage/adnan-bin-wahid.tokenwise-vscode/backend/installation.json") });
  f.index.configured(f.folder);
  await until(() => f.actions("start").length === 1);
});

test("untrusted windows remain idle until workspace trust is granted", async t => {
  const f = await fixture(t, { trusted: false });
  await delay(40);
  assert.equal(f.requests.length, 0); assert.equal(f.watchers.length, 0);
  f.api.workspace.isTrusted = true;
  f.trust.emit();
  await until(() => f.actions("start").length === 1);
});

test("remote and virtual workspaces never warm local indexes", async t => {
  const f = await fixture(t, { remote: "ssh-remote", scheme: "vscode-remote" });
  await delay(40);
  assert.equal(f.requests.length, 0); assert.equal(f.endpoints.length, 0); assert.equal(f.watchers.length, 0);
});

test("another profile's backend link is not indexed", async t => {
  const f = await fixture(t, { configured: false });
  await f.put(".tokenwise/backend-link.json", { schema_version: 1, registration_path: path.join(f.root, "Other/backend/installation.json") });
  f.index.configured(f.folder);
  await delay(40);
  assert.equal(f.requests.length, 0); assert.equal(f.endpoints.length, 0);
});

test("bursts of Python edits are deduplicated and excluded files are ignored", async t => {
  const f = await fixture(t);
  await until(() => f.actions("start").length === 1);
  for (let number = 0; number < 50; number++) { f.changed("auth.py"); }
  f.changed(".venv/private.py"); f.changed("README.md"); f.changed("../outside.py");
  await until(() => f.actions("update").length === 1);
  await delay(30);
  assert.deepEqual(f.actions("update")[0].body.paths, ["auth.py"]);
  assert.equal(f.actions("update").length, 1);
});

test("folder renames queue both old and new subtrees", async t => {
  const f = await fixture(t);
  await until(() => f.actions("start").length === 1);
  f.rename.emit({ files: [{ oldUri: uri(path.join(f.workspace, "models")), newUri: uri(path.join(f.workspace, "services")) }] });
  await until(() => f.actions("update").length === 1);
  assert.deepEqual(f.actions("update")[0].body.paths, ["models", "services"]);
});

test("creation, deletion, and uppercase Python extensions reach the index", async t => {
  const f = await fixture(t);
  await until(() => f.actions("start").length === 1);
  f.source().create.emit(uri(path.join(f.workspace, "added.PY")));
  f.source().remove.emit(uri(path.join(f.workspace, "removed.py")));
  f.deleted.emit({ files: [uri(path.join(f.workspace, "old-package"))] });
  await until(() => f.actions("update").length === 1);
  assert.deepEqual(f.actions("update")[0].body.paths, ["added.PY", "removed.py", "old-package"]);
});

test("an edit arriving during an in-flight update is not lost", async t => {
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  let updates = 0;
  const f = await fixture(t, { handle: async request => {
    if (request.body.action === "update" && ++updates === 1) { await gate; }
    return response(request.body);
  } });
  await until(() => f.actions("start").length === 1);
  f.changed("auth.py");
  await until(() => f.actions("update").length === 1);
  f.changed("auth.py");
  release();
  await until(() => f.actions("update").length === 2);
  assert.deepEqual(f.actions("update").map(request => request.body.paths), [["auth.py"], ["auth.py"]]);
  assert.ok(f.actions("update")[1].body.sequence > f.actions("update")[0].body.sequence);
});

test("large event bursts stay inside the API's 512-path batch limit", async t => {
  const f = await fixture(t);
  await until(() => f.actions("start").length === 1);
  for (let number = 0; number < 513; number++) { f.changed(`file${number}.py`); }
  await until(() => f.actions("update").length === 2);
  assert.deepEqual(f.actions("update").map(request => request.body.paths.length), [512, 1]);
});

test("index failures release the lease and retry without losing edits", async t => {
  let failed = false;
  const f = await fixture(t, { handle: request => {
    if (request.body.action === "update" && !failed) { failed = true; return { ok: false, status: 503 }; }
    return response(request.body);
  } });
  await until(() => f.actions("start").length === 1);
  f.changed("auth.py");
  await until(() => f.actions("stop").length === 1);
  f.changed("auth.py");
  await until(() => f.actions("start").length === 2 && f.actions("update").length === 2);
  assert.ok(f.logs.some(line => line.includes("503")));
  assert.deepEqual(f.actions("update")[1].body.paths, ["auth.py"]);
});

test("disabling automatic context stops watchers and releases the backend lease", async t => {
  const f = await fixture(t);
  await until(() => f.actions("start").length === 1);
  await f.put(".agents/tokenwise.json", { enabled: false });
  f.watchers.find(watcher => watcher.pattern === ".agents/tokenwise.json").change.emit();
  await until(() => f.actions("stop").length === 1);
  assert.ok(f.watchers.find(watcher => watcher.pattern === pythonPattern).disposed);
});

test("malformed configuration stops indexing without altering the file", async t => {
  const f = await fixture(t);
  await until(() => f.actions("start").length === 1);
  await f.put(".agents/tokenwise.json", { enabled: "invalid" });
  f.watchers.find(watcher => watcher.pattern === ".agents/tokenwise.json").change.emit();
  await until(() => f.actions("stop").length === 1);
  assert.equal(JSON.parse(await fs.readFile(path.join(f.workspace, ".agents/tokenwise.json"), "utf8")).enabled, "invalid");
  assert.ok(f.logs.some(line => line.includes("Invalid TokenWise workspace configuration")));
  assert.equal(f.source(), undefined);
});

test("closing during an in-flight update aborts it and releases with a newer sequence", async t => {
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  const f = await fixture(t, { handle: async request => {
    if (request.body.action === "update") { await gate; }
    return response(request.body);
  } });
  await until(() => f.actions("start").length === 1);
  f.changed("auth.py");
  await until(() => f.actions("update").length === 1);
  f.folders.emit({ removed: [f.folder], added: [] });
  await until(() => f.actions("stop").length === 1);
  assert.ok(f.actions("update")[0].signal.aborted);
  assert.ok(f.actions("stop")[0].body.sequence > f.actions("update")[0].body.sequence);
  release();
  await delay(30);
  assert.equal(f.actions("start").length, 1);
  assert.ok(f.watchers.every(watcher => watcher.disposed));
});

test("older backends retain retrieval and receive no tight retry loop", async t => {
  const f = await fixture(t, { handle: () => ({ ok: false, status: 404 }) });
  await until(() => f.logs.some(line => line.includes("Context retrieval can still continue")));
  await delay(50);
  assert.equal(f.actions("start").length, 1);
  assert.equal(f.endpoints.length, 1);
});

test("closing a workspace during backend startup sends no late indexing request", async t => {
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  const f = await fixture(t, { endpoint: async () => { await gate; return "http://127.0.0.1:8800"; } });
  await until(() => f.endpoints.length === 1);
  f.folders.emit({ removed: [f.folder], added: [] });
  release();
  await delay(30);
  assert.equal(f.requests.length, 0);
  assert.ok(f.watchers.every(watcher => watcher.disposed));
});

test("heartbeat renews indexing without spawning another backend helper", async t => {
  const f = await fixture(t, { heartbeatMs: 40 });
  await until(() => f.actions("reconcile").length >= 2);
  assert.equal(f.endpoints.length, 1);
});

test("backend replacement reconnects configured workspaces to the new local service", async t => {
  let port = 8800;
  const f = await fixture(t, { endpoint: async () => `http://127.0.0.1:${port}` });
  await until(() => f.actions("start").length === 1);
  port = 8801;
  f.index.backendChanged();
  await until(() => f.actions("start").length === 2);
  assert.equal(f.actions("stop").length, 1);
  assert.equal(f.actions("start")[1].url, "http://127.0.0.1:8801/index-workspace");
});

test("automatic startup disabled in workspace settings is honored", async t => {
  const f = await fixture(t, { settings: { enabled: true, auto_start_backend: false } });
  await until(() => f.actions("start").length === 1);
  assert.deepEqual(f.endpoints, [false]);
});

test("repository paths are never sent to non-local backend URLs", async t => {
  const f = await fixture(t, { endpoint: async () => "https://example.com" });
  await until(() => f.logs.some(line => line.includes("registered local backend")));
  assert.equal(f.requests.length, 0);
});

test("cleanup pauses indexing until explicit workspace setup resumes it", async t => {
  const f = await fixture(t);
  await until(() => f.actions("start").length === 1);
  f.index.pause();
  await until(() => f.actions("stop").length === 1);
  const count = f.requests.length;
  f.rename.emit({ files: [{ oldUri: uri(path.join(f.workspace, "old.py")), newUri: uri(path.join(f.workspace, "new.py")) }] });
  await delay(30);
  assert.equal(f.requests.length, count);
  f.index.configured(f.folder);
  await until(() => f.actions("start").length === 2);
});
