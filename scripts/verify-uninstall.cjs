const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { execFile, spawn } = require("node:child_process");
const { promisify } = require("node:util");
const execute = promisify(execFile);
const source = path.resolve(__dirname, "..");
const { EXTENSION_ID } = require("../vscode-extension/dist/services/cleanupFiles");
const { registerLifecycle } = require("../vscode-extension/dist/services/cleanupRegistry");
const { registerBackend, configureAutomaticContext } = require("../vscode-extension/dist/services/automaticSetup");
const { findPython312 } = require("../vscode-extension/dist/services/managedBackend");

async function put(root, filename, content) {
  const target = path.join(root, filename);
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, typeof content === "string" ? content : JSON.stringify(content));
}
const quote = text => "'" + text.replace(/'/g, "''") + "'";
async function cli(arguments_) {
  const launcher = path.join(process.env.LOCALAPPDATA, "Programs/Antigravity IDE/bin/antigravity-ide.cmd");
  const command = `& ${quote(launcher)} ${arguments_.map(quote).join(" ")}; exit $LASTEXITCODE`;
  const result = await execute("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", command], { windowsHide: true, timeout: 120000, maxBuffer: 262144 });
  process.stdout.write(result.stdout);
}

async function stopSpawned(child) {
  if (!child || child.exitCode !== null || child.signalCode) { return; }
  let failure;
  try { await execute("taskkill.exe", ["/PID", String(child.pid), "/T", "/F"], { windowsHide: true, timeout: 15000 }); }
  catch (error) { failure = error; }
  // taskkill can fail for a child that exits concurrently after its parent stops.
  for (let attempt = 0; attempt < 30; attempt++) {
    if (child.exitCode !== null || child.signalCode) { return; }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw failure ?? new Error(`Isolated process ${child.pid} did not exit`);
}

async function main() {
  if (process.platform !== "win32") { throw new Error("This native Antigravity uninstall verifier is Windows-only."); }
  const manifest = JSON.parse(await fs.readFile(path.join(source, "vscode-extension/package.json"), "utf8"));
  const vsix = path.join(source, "vscode-extension", `${manifest.name}-${manifest.version}.vsix`);
  const temp = await fs.realpath(os.tmpdir());
  const root = await fs.mkdtemp(path.join(temp, "tokenwise-uninstall-smoke-"));
  const extensions = path.join(root, "extensions");
  const userData = path.join(root, "user-data");
  const workspace = path.join(root, "Python Repository");
  let job;
  let ide;
  let succeeded = false;
  const common = ["--user-data-dir", userData, "--extensions-dir", extensions];
  try {
    await cli([...common, "--install-extension", vsix, "--force"]);
    const names = await fs.readdir(extensions);
    const installed = names.find(name => name.startsWith(`${EXTENSION_ID}-${manifest.version}`));
    assert.ok(installed, "VSIX must install into the isolated extension directory");
    const extension = path.join(extensions, installed);
    const storage = path.join(userData, "User/globalStorage", EXTENSION_ID);
    await registerLifecycle(storage, extension);
    const backendRoot = path.join(storage, `backend/managed/${manifest.version}-smoke`);
    const python = await findPython312();
    await execute(python.executable, ["-m", "venv", "--without-pip", path.join(backendRoot, ".venv")], { windowsHide: true, timeout: 60000 });
    for (const filename of ["scripts/antigravity_context.py", "scripts/antigravity_hook.py", "swe-pruner/swe-pruner/src/swe_pruner/online_serving.py",
      ...["model.safetensors", "tokenizer.json", "config.json", "tokenizer_config.json", "backbone/config.json"].map(name => `swe-pruner/swe-pruner/model/${name}`)]) {
      await put(backendRoot, filename, "fixture");
    }
    await put(backendRoot, "managed-install.json", { schema_version: 1 });
    // A harmless sleeping module reproduces the real venv-wrapper/PID relationship.
    await put(backendRoot, "uvicorn.py", "import os, json, time\nprint(json.dumps({'pid': os.getpid()}), flush=True)\nwhile True:\n    time.sleep(1)\n");
    job = spawn(path.join(backendRoot, ".venv/Scripts/python.exe"), ["-m", "uvicorn", "swe_pruner.online_serving:app", "--host", "127.0.0.1", "--port", "8123"], { cwd: backendRoot, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
    const pid = await new Promise((resolve, reject) => {
      let output = "";
      const timer = setTimeout(() => reject(new Error("Private backend fixture did not start")), 15000);
      job.once("error", error => { clearTimeout(timer); reject(error); });
      job.stdout.on("data", bytes => {
        output += bytes.toString("utf8");
        if (output.includes("\n")) { clearTimeout(timer); resolve(JSON.parse(output.trim()).pid); }
      });
    });
    await fs.mkdir(workspace);
    await put(workspace, "app.py", "print('Keep this application')\n");
    const backend = await registerBackend(backendRoot, storage);
    await put(storage, "backend/runtime/backend.json", { project_root: backendRoot, pid, port: 8123 });
    await configureAutomaticContext(workspace, backend, path.join(source, "vscode-extension/resources/automatic-context"));
    await put(workspace, ".tokenwise/latest.json", { event_id: "smoke", transport: "antigravity-agent-command", query: "test" });
    await put(path.dirname(path.dirname(storage)), "settings.json", '{\n// Keep my settings\n"editor.fontSize": 15,\n"tokenWise.apiUrl": "http://127.0.0.1:8123"\n}\n');
    await cli([...common, "--uninstall-extension", EXTENSION_ID]);
    // The CLI removes profile registration; the IDE's shared process runs deferred cleanup.
    await cli([...common, "--list-extensions", "--show-versions"]);
    const ideEnvironment = { ...process.env };
    delete ideEnvironment.ELECTRON_RUN_AS_NODE;
    delete ideEnvironment.VSCODE_CLI;
    ide = spawn(path.join(process.env.LOCALAPPDATA, "Programs/Antigravity IDE/Antigravity IDE.exe"),
      [...common, "--disable-extensions", "--skip-welcome", "--skip-release-notes", "--disable-workspace-trust", "--new-window"],
      { windowsHide: true, stdio: "ignore", env: ideEnvironment });
    await new Promise((resolve, reject) => { ide.once("spawn", resolve); ide.once("error", reject); });
    let restarted = false;
    for (let attempt = 0; attempt < 120; attempt++) {
      if (!await fs.stat(storage).catch(() => undefined)
        && !await fs.stat(path.join(workspace, ".agents")).catch(() => undefined)
        && !await fs.stat(path.join(extensions, ".tokenwise-cleanup")).catch(() => undefined)) { succeeded = true; break; }
      // CLI uninstall may only mark the extension obsolete during the first IDE startup.
      if (!restarted && await fs.stat(path.join(extensions, ".obsolete")).catch(() => undefined)) {
        await stopSpawned(ide);
        await new Promise(resolve => setTimeout(resolve, 1500));
        ide = spawn(path.join(process.env.LOCALAPPDATA, "Programs/Antigravity IDE/Antigravity IDE.exe"),
          [...common, "--disable-extensions", "--skip-welcome", "--skip-release-notes", "--disable-workspace-trust", "--new-window"],
          { windowsHide: true, stdio: "ignore", env: ideEnvironment });
        await new Promise((resolve, reject) => { ide.once("spawn", resolve); ide.once("error", reject); });
        restarted = true;
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    assert.ok(succeeded, `Uninstall did not finish. Inspect the isolated IDE logs: ${userData}`);
    assert.equal(await fs.readFile(path.join(workspace, "app.py"), "utf8"), "print('Keep this application')\n");
    assert.equal(await fs.stat(path.join(workspace, ".tokenwise")).catch(() => undefined), undefined);
    assert.equal(await fs.stat(path.join(workspace, ".gitignore")).catch(() => undefined), undefined);
    const settings = await fs.readFile(path.join(userData, "User/settings.json"), "utf8");
    assert.ok(settings.includes("Keep my settings")); assert.ok(!settings.includes("tokenWise"));
    await new Promise(resolve => setTimeout(resolve, 500));
    assert.notEqual(job.exitCode, null, "The owned private Python backend must be stopped");
    console.log("ISOLATED_ANTIGRAVITY_UNINSTALL_OK: hook ran, native venv/backend stopped, owned data removed, application/settings preserved.");
  } finally {
    for (const child of [ide, job]) {
      await stopSpawned(child).catch(error => { succeeded = false; process.exitCode = 1; console.error(error.message); });
    }
    if (succeeded) {
      assert.equal(path.dirname(await fs.realpath(root)), temp);
      assert.ok(path.basename(root).startsWith("tokenwise-uninstall-smoke-"));
      await fs.rm(root, { recursive: true, force: true, maxRetries: 8, retryDelay: 300 });
    } else { console.error(`Isolated fixture retained for diagnosis: ${root}`); }
  }
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
