// Exercise installed workspace resources against the real model, not Antigravity's cloud agent.
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { execFile } = require("node:child_process");
const { configureAutomaticContext, registerBackend } = require("../vscode-extension/dist/services/automaticSetup.js");

const checkout = path.resolve(__dirname, "..");
const option = (name) => { const index = process.argv.indexOf(name); return index < 0 ? undefined : process.argv[index + 1]; };
const installation = path.resolve(option("--backend") ?? checkout);
const templates = path.join(checkout, "vscode-extension/resources/automatic-context");
const marker = "[TokenWise automatic context]";

function run(file, args, cwd, input = "") {
  return new Promise((resolve, reject) => {
    const child = execFile(file, args, { cwd, encoding: "utf8", windowsHide: true, timeout: 150000, maxBuffer: 2 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (error) { reject(new Error(`${file} failed: ${stderr || error.message}`)); return; }
      assert.equal(stderr, "");
      resolve(stdout);
    });
    child.stdin.end(input);
  });
}

async function put(root, relative, content) {
  const filename = path.join(root, relative);
  await fs.mkdir(path.dirname(filename), { recursive: true });
  await fs.writeFile(filename, content);
}
async function json(filename) { return JSON.parse(await fs.readFile(filename, "utf8")); }

async function main() {
  assert.equal(process.platform, "win32", "This verifier exercises the Windows launchers.");
  const tempRoot = await fs.mkdtemp(path.join(await fs.realpath(os.tmpdir()), "tokenwise-portable-verification-"));
  try {
    const backend = await registerBackend(installation, path.resolve(option("--storage") ?? path.join(tempRoot, "User Storage")));
    const contexts = [];
    const urls = [];
    const query = 'Explain customer\'s invoice retries, "InvoiceService", and the related tests. Do not modify files. \u2713';
    for (const name of ["External Python Repo", "Second Independent Repo"]) {
      const workspace = path.join(tempRoot, name);
      assert.ok(!workspace.startsWith(installation + path.sep));
      await put(workspace, "services/invoice_service.py", "class InvoiceService:\n    def charge_invoice(self, gateway, amount, attempts=3):\n        for attempt in range(attempts):\n            try:\n                return gateway.charge(amount)\n            except ConnectionError:\n                if attempt == attempts - 1:\n                    raise\n");
      await put(workspace, "tests/test_invoice.py", "from services.invoice_service import InvoiceService\n\ndef test_invoice_retries():\n    class Gateway:\n        calls = 0\n        def charge(self, amount):\n            self.calls += 1\n            if self.calls < 3:\n                raise ConnectionError('retry invoice')\n            return amount\n    gateway = Gateway()\n    assert InvoiceService().charge_invoice(gateway, 100) == 100\n    assert gateway.calls == 3\n");
      await put(workspace, ".agents/rules/team.md", "Keep the team's rules.\n");
      await put(workspace, ".agents/hooks.json", JSON.stringify({ team: { enabled: true, PreInvocation: [] } }));
      // Do not spawn a detached server as a verifier side effect. Start the backend beforehand.
      await put(workspace, ".agents/tokenwise.json", JSON.stringify({ token_budget: 1024, auto_start_backend: false }));
      await configureAutomaticContext(workspace, backend, templates);
      assert.equal(await fs.readFile(path.join(workspace, ".agents/rules/team.md"), "utf8"), "Keep the team's rules.\n");
      assert.deepEqual((await json(path.join(workspace, ".agents/hooks.json"))).team, { enabled: true, PreInvocation: [] });
      const escaped = query.replace(/'/g, "''");
      const command = `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .agents/tokenwise/tokenwise-context.ps1 -QueryBase64 ([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('${escaped}'))) -Verification`;
      const output = await run("powershell.exe", ["-NoProfile", "-Command", command], workspace);
      assert.ok(output.startsWith(marker), output.slice(0, 200));
      const activity = await json(path.join(workspace, ".tokenwise/latest.json"));
      assert.equal(activity.query, query);
      assert.equal(activity.status, "ready");
      assert.equal(activity.transport, "antigravity-agent-command");
      assert.equal(activity.verification, true);
      const files = activity.result.files.map((file) => file.file_path);
      assert.ok(files.includes("services/invoice_service.py"), files);
      assert.ok(files.includes("tests/test_invoice.py"), files);
      assert.ok(activity.result.pruned_tokens <= 1024);
      assert.equal(output.trimEnd().replace(/\r\n/g, "\n"), activity.result.unified_prompt.trimEnd());
      contexts.push({ text: activity.result.unified_prompt, count: activity.result.pruned_tokens });
      urls.push(activity.backend_url);
      console.log(`${name}: ${files.join(", ")}; ${activity.result.pruned_tokens}/1024 tokens; ${activity.backend_url}; ${activity.elapsed_ms}ms`);

      const transcript = path.join(workspace, ".tokenwise/transcript.jsonl");
      await fs.writeFile(transcript, JSON.stringify({ type: "USER_INPUT", source: "USER_EXPLICIT", step_index: 1, content: query }) + "\n");
      const payload = { conversationId: `tokenwise-verification-${name}`, workspacePaths: [workspace], transcriptPath: transcript, invocationNum: 0, tokenwiseVerification: true };
      const hookArgs = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".agents/tokenwise/tokenwise-hook.ps1"];
      const injected = JSON.parse(await run("powershell.exe", hookArgs, workspace, JSON.stringify(payload)));
      assert.ok(injected.injectSteps[0].userMessage.startsWith(marker));
      assert.deepEqual(JSON.parse(await run("powershell.exe", hookArgs, workspace, JSON.stringify({ ...payload, invocationNum: 1 }))), {});
      await put(workspace, ".agents/tokenwise/tokenwise-launcher.py", await fs.readFile(path.join(templates, "tokenwise-launcher.py")));
      const portable = await run(backend.registration.python_path, [".agents/tokenwise/tokenwise-launcher.py", "--query-base64", Buffer.from(query).toString("base64"), "--verification"], workspace);
      assert.ok(portable.startsWith(marker), "The portable bootstrap must retrieve real context too.");
      assert.deepEqual((await configureAutomaticContext(workspace, backend, templates)).changedFiles, []);
    }
    assert.equal(urls[0], urls[1], "Independent workspaces must share one backend process.");
    const countScript = "import json,sys; from tokenizers import Tokenizer; t=Tokenizer.from_file(sys.argv[1]); items=json.load(sys.stdin); assert all(len(t.encode(x['text'],add_special_tokens=False).ids)==x['count'] for x in items); print('Exact tokenizer counts verified')";
    console.log((await run(backend.registration.python_path, ["-c", countScript, path.join(installation, "swe-pruner/swe-pruner/model/tokenizer.json")], installation, JSON.stringify(contexts))).trim());
    const registration = await json(path.join(backend.registration.runtime_dir, "backend.json"));
    assert.equal(registration.project_root, installation);
    console.log("PORTABLE_AUTOMATIC_CONTEXT_OK: two external repositories, shared backend, preserved configuration, command and native-hook adapters");
  } finally {
    assert.equal(path.dirname(tempRoot), await fs.realpath(os.tmpdir()));
    assert.ok(path.basename(tempRoot).startsWith("tokenwise-portable-verification-"));
    await fs.rm(tempRoot, { recursive: true, force: true });
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
