const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs/promises");
const path = require("node:path");
const os = require("node:os");
const childProcess = require("node:child_process");
const { parseSetupProgress, parseSetupError, setupProgressMessage, SetupError, findPython312, runSetupProcess, installManagedBackend } = require("../dist/services/managedBackend.js");

test("structured installer progress is separated from normal output", () => {
  assert.deepEqual(parseSetupProgress('TOKENWISE_PROGRESS {"stage":"model","message":"Downloading","current":1,"total":2}'), { stage: "model", message: "Downloading", current: 1, total: 2 });
  assert.equal(parseSetupProgress("Collecting torch"), undefined);
  assert.equal(parseSetupProgress("TOKENWISE_PROGRESS broken"), undefined);
  assert.equal(parseSetupProgress('TOKENWISE_PROGRESS {"stage":1}'), undefined);
});

test("setup progress has readable numbered steps and safe download percentages", () => {
  assert.equal(setupProgressMessage({ stage: "model", message: "Downloading model", step: 5, total_steps: 7, current: 50, total: 100 }), "Step 5/7: Downloading model (50%)");
  assert.equal(setupProgressMessage({ stage: "check", message: "Checking", step: 0, total_steps: 0, current: 0, total: 0 }), "Checking");
});

test("structured errors retain the failed step and recovery advice", () => {
  const error = parseSetupError('pip output\nTOKENWISE_SETUP_ERROR {"stage":"model","message":"offline","hint":"Reconnect, then retry","step":5}\n');
  assert.ok(error instanceof SetupError);
  assert.equal(error.stage, "model"); assert.equal(error.step, 5);
  assert.equal(error.hint, "Reconnect, then retry");
  assert.equal(parseSetupError("TOKENWISE_SETUP_ERROR broken"), undefined);
  assert.equal(parseSetupError('TOKENWISE_SETUP_ERROR {"stage":1,"message":"bad"}'), undefined);
});

test("process failures expose structured setup errors rather than a raw JSON line", async () => {
  const record = { stage: "torch", message: "package unavailable", hint: "Check PyTorch connectivity", step: 4 };
  await assert.rejects(runSetupProcess(process.execPath, ["-e", `console.error('TOKENWISE_SETUP_ERROR '+JSON.stringify(${JSON.stringify(record)})); process.exit(1);`], { log() {} }),
    error => error instanceof SetupError && error.stage === "torch" && error.step === 4 && error.message === "package unavailable");
});

test("cancelling Python detection does not spawn an interpreter", async t => {
  const abort = new AbortController(); abort.abort();
  const call = t.mock.method(childProcess, "execFile", () => { throw new Error("Unexpected spawn"); });
  await assert.rejects(findPython312("python", abort.signal), error => error instanceof SetupError && error.cancelled);
  assert.equal(call.mock.callCount(), 0);
});

test("Python detection checks version and bitness without a shell", async (t) => {
  const calls = [];
  const executable = path.resolve(os.tmpdir(), "Custom Python", "python.exe");
  t.mock.method(childProcess, "execFile", (command, args, options, callback) => {
    calls.push({ command, args, options });
    callback(null, JSON.stringify({ version: [3, 12], bits: 64, executable }));
  });
  const result = await findPython312("C:/Custom Python/python.exe");
  assert.equal(result.executable, executable);
  assert.deepEqual(result.args, []);
  assert.ok(calls[0].args.at(-1).includes("sys.version_info"));
  assert.equal(calls[0].options.windowsHide, true);
  assert.equal(calls[0].options.shell, undefined);
});

test("a launcher resolves to the real interpreter so cancellation owns its process", async (t) => {
  const executable = path.resolve(os.tmpdir(), "Python312", "python.exe");
  t.mock.method(childProcess, "execFile", (_, __, ___, callback) => callback(null, JSON.stringify({ version: [3, 12], bits: 64, executable })));
  assert.deepEqual(await findPython312(), { executable, args: [] });
});

test("wrong Python version fails with an actionable prerequisite message", async (t) => {
  t.mock.method(childProcess, "execFile", (_, __, ___, callback) => callback(null, "unsupported\n"));
  await assert.rejects(findPython312("wrong-python"), /64-bit Python 3.12/);
});

test("process runner delivers progress and Unicode log output", async () => {
  const log = [], progress = [];
  const script = "console.log('dependency output'); console.log('TOKENWISE_PROGRESS '+JSON.stringify({stage:'complete',message:'done'})); console.log('Unicode: \\u2713')";
  const output = await runSetupProcess(process.execPath, ["-e", script], { log: (line) => log.push(line), progress: (item) => progress.push(item) });
  assert.equal(progress[0].stage, "complete");
  assert.ok(log.includes("Unicode: \u2713"));
  assert.match(output, /dependency output/);
});

test("nonzero process exit reports its error instead of claiming installation success", async () => {
  await assert.rejects(runSetupProcess(process.execPath, ["-e", "console.error('dependency install failed'); process.exit(2)"], { log() {} }), /dependency install failed/);
});

test("cancellation before spawn never starts setup", async () => {
  const abort = new AbortController();
  abort.abort();
  await assert.rejects(runSetupProcess(process.execPath, ["-e", "process.exit(0)"], { signal: abort.signal, log() {} }), /cancelled/);
});

test("cancellation stops an owned setup process", async () => {
  const abort = new AbortController();
  await assert.rejects(runSetupProcess(process.execPath, ["-e", "console.log('ready'); setInterval(()=>{},1000)"], {
    signal: abort.signal, log: (line) => { if (line === "ready") { abort.abort(); } },
  }), /cancelled/);
});

test("installer completion is restricted to managed storage", async (t) => {
  const root = await fs.mkdtemp(path.join(await fs.realpath(os.tmpdir()), "tokenwise-managed-test-"));
  t.after(async () => {
    assert.equal(path.dirname(root), await fs.realpath(os.tmpdir()));
    assert.ok(path.basename(root).startsWith("tokenwise-managed-test-"));
    await fs.rm(root, { recursive: true, force: true });
  });
  const bundle = path.join(root, "bundle");
  const storage = path.join(root, "storage");
  await fs.mkdir(path.join(bundle, "scripts"), { recursive: true });
  const entry = path.join(bundle, "scripts/install_backend.py");
  const installed = path.join(storage, "backend/managed/0.4.0-fixture");
  const source = `const fs=require('node:fs'); fs.mkdirSync(${JSON.stringify(installed)},{recursive:true}); fs.writeFileSync(${JSON.stringify(path.join(installed, "managed-install.json"))},'{}'); console.log('TOKENWISE_PROGRESS '+JSON.stringify({stage:'complete',message:'done',installation_root:${JSON.stringify(installed)}}));`;
  await fs.writeFile(entry, source);
  assert.equal(await installManagedBackend({ executable: process.execPath, args: [] }, bundle, storage, "0.4.0", { log() {} }), installed);
  await fs.writeFile(entry, "console.log('TOKENWISE_PROGRESS '+JSON.stringify({stage:'complete',message:'done',installation_root:'C:/outside'}));");
  await assert.rejects(installManagedBackend({ executable: process.execPath, args: [] }, bundle, storage, "0.4.0", { log() {} }), /outside managed|completed installation/);
});

test("cancelled managed setup removes only the lock owned by its installer", async (t) => {
  const root = await fs.mkdtemp(path.join(await fs.realpath(os.tmpdir()), "tokenwise-cancel-test-"));
  t.after(async () => {
    assert.equal(path.dirname(root), await fs.realpath(os.tmpdir()));
    assert.ok(path.basename(root).startsWith("tokenwise-cancel-test-"));
    await fs.rm(root, { recursive: true, force: true });
  });
  const bundle = path.join(root, "bundle"), storage = path.join(root, "storage");
  const lock = path.join(storage, "backend/install.lock");
  await fs.mkdir(path.join(bundle, "scripts"), { recursive: true });
  await fs.mkdir(path.dirname(lock), { recursive: true });
  await fs.writeFile(path.join(bundle, "scripts/install_backend.py"), `require('node:fs').writeFileSync(${JSON.stringify(lock)},String(process.pid)); console.log('ready'); setInterval(()=>{},1000);`);
  const abort = new AbortController();
  await assert.rejects(installManagedBackend({ executable: process.execPath, args: [] }, bundle, storage, "0.4.0", {
    signal: abort.signal, log: (line) => { if (line === "ready") { abort.abort(); } },
  }), /cancelled/);
  await assert.rejects(fs.stat(lock), { code: "ENOENT" });
});
