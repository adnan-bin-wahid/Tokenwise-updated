const assert = require("node:assert/strict");
const { test, beforeEach } = require("node:test");
const Module = require("node:module");

const originalLoad = Module._load;
const watcherCallbacks = [];
let currentActivity;
let currentHooks;
const outputLines = [];
const commandCallbacks = new Map();
let settings, carbonRequests, carbonClients, carbonResponder, comparisonRequests, comparisonResponder;
function makePanel(panels = [], updates = []) {
  return {
    showWorkspaceResult: (...args) => panels.push(args),
    updateWorkspaceResult: (result) => {
      if (panels.at(-1)?.[0].automatic_context?.event_id !== result.automatic_context?.event_id) { return false; }
      updates.push(result);
      return true;
    },
  };
}
function estimate(request) {
  return {
    prefill_joules: request.input_tokens, decode_joules: 256,
    total_joules: request.input_tokens + 256, co2_grams: request.input_tokens / 1000,
    carbon_intensity_g_per_kwh: 475, model_name: "meta-llama-3-8b-instruct",
    prefill_route: "xgboost_interpolation", decode_route: "xgboost_interpolation", features_source: "registry",
  };
}
class FakeClient {
  constructor(config) { carbonClients.push(config); }
  async estimateCarbon(request) {
    carbonRequests.push(request);
    return carbonResponder ? carbonResponder(request) : estimate(request);
  }
  async comparePreparedWorkspace(root, query, prepared) {
    comparisonRequests.push({ root, query, prepared });
    return comparisonResponder ? comparisonResponder(root, query, prepared) : {
      query, repository_fingerprint: prepared.repository_fingerprint, selection_scope: "none (automatic comparison)",
      measurement_scope: "prepared_packets", notes: [],
      methods: [{ id: "all_python", title: "All Python", input_tokens: 600, source_tokens: 500,
        files: ["auth.py", "test_auth.py"], context: "all code" },
      { id: "tokenwise", title: "TokenWise", input_tokens: prepared.pruned_tokens, source_tokens: 100,
        files: prepared.files.map(file => file.file_path), context: prepared.unified_prompt }],
    };
  }
}
const vscodeStub = {
  window: { createOutputChannel: () => ({ appendLine: (line) => outputLines.push(line), show() {}, dispose() {} }) },
  commands: { registerCommand: (name, handler) => { commandCallbacks.set(name, handler); return { dispose() {} }; } },
  Uri: { joinPath: (...parts) => parts.join("/") },
  RelativePattern: class {},
  env: {},
  ConfigurationTarget: { WorkspaceFolder: 3 },
  workspace: {
    isTrusted: true,
    workspaceFolders: [],
    onDidChangeWorkspaceFolders: () => ({ dispose() {} }),
    fs: { readFile: async (uri) => Buffer.from(JSON.stringify(String(uri).endsWith("/.agents/hooks.json") ? currentHooks ?? {} : currentActivity)), stat: async () => ({}) },
    getConfiguration: () => ({ get: (key, fallback) => settings[key] ?? fallback }),
    createFileSystemWatcher: () => ({
      onDidCreate: (handler) => { watcherCallbacks.push(handler); return { dispose() {} }; },
      onDidChange: (handler) => { watcherCallbacks.push(handler); return { dispose() {} }; },
      dispose() {},
    }),
  },
};
Module._load = function (request, ...args) {
  if (request === "./apiClient") { return { TokenWiseApiClient: FakeClient }; }
  return request === "vscode" ? vscodeStub : originalLoad.call(this, request, ...args);
};
const { parseAutomaticActivity, AutomaticContextMonitor } = require("../dist/services/automaticContext.js");
Module._load = originalLoad;
beforeEach(() => {
  settings = { enableCarbonEstimation: false };
  carbonRequests = []; carbonClients = []; carbonResponder = undefined;
  comparisonRequests = []; comparisonResponder = undefined;
  vscodeStub.workspace.isTrusted = true; vscodeStub.env.remoteName = undefined;
  watcherCallbacks.length = 0; outputLines.length = 0;
  commandCallbacks.clear(); currentHooks = undefined;
});

const ready = {
  event_id: "new-prompt", timestamp: "2026-10-02T00:00:00Z", status: "ready", backend_url: "http://127.0.0.1:8005",
  result: {
    structured_goal: {}, unified_prompt: "[TokenWise automatic context]", pruned_tokens: 100, original_tokens: 500,
    raw_context_tokens: 600,
    files: [{ file_path: "services/payment_service.py", relation: "prompt-selected file", tier: 1, score: 0.5, original_tokens: 500, pruned_tokens: 100 }],
  },
};

test("accepts a complete hook activity record", () => {
  assert.equal(parseAutomaticActivity(ready).result.files[0].file_path, "services/payment_service.py");
});

test("bounded memory traces accept agent references and reject malformed renderer inputs", () => {
  const trace = { mode: "conversation", current_query: "Which tests cover that behavior?", effective_query: "lockout",
    scope: "repository", threshold: .45, history_text: "Explain lockout", history_source: "agent_supplied_user_turns",
    memory: { version: "1", enabled: true, selection: "bounded selection", summary: "Explain lockout", requirements: [],
      considered_messages: 1, omitted_messages: 0, characters: 15, truncated: false,
      messages: [{ position: 1, text: "Explain lockout", reason: "topic anchor" }],
      packet: { status: "applied", tokens: 20, text: "reference" } } };
  const activity = { ...ready, result: { ...ready.result, input_trace: trace } };
  assert.ok(parseAutomaticActivity(activity));
  for (const change of [{ messages: null }, { characters: 4001 }, { packet: { status: "applied", tokens: -1, text: "bad" } },
    { messages: [{ position: 0, text: "x", reason: "bad" }] }, { requirements: [null] }]) {
    assert.equal(parseAutomaticActivity({ ...activity, result: { ...activity.result, input_trace: { ...trace, memory: { ...trace.memory, ...change } } } }), undefined);
  }
});

test("guidance traces are optional for old records and malformed metadata is rejected", () => {
  const guidance = { version: "1", profile: "generic_task", enabled: true, status: "applied",
    format: "full", tokens: 80, text: "Ground answers in evidence." };
  const record = response_guidance => ({ ...ready, result: { ...ready.result, response_guidance } });
  assert.deepEqual(parseAutomaticActivity(record(guidance)).result.response_guidance, guidance);
  assert.ok(parseAutomaticActivity(record(null)));
  for (const change of [{ version: 1 }, { enabled: "true" }, { status: "success" }, { format: "partial" },
    { tokens: -1 }, { tokens: .5 }, { text: [] }, { profile: null }]) {
    assert.equal(parseAutomaticActivity(record({ ...guidance, ...change })), undefined);
  }
  assert.equal(parseAutomaticActivity(record([])), undefined);
});

test("explicit exclusion metadata is optional but must contain string arrays", () => {
  const record = topics => ({ ...ready, result: { ...ready.result, structured_goal: { excluded_topics: topics } } });
  assert.ok(parseAutomaticActivity(record(["invoice pricing"])));
  assert.equal(parseAutomaticActivity(record("invoice pricing")), undefined);
  assert.equal(parseAutomaticActivity(record([42])), undefined);
  const withSymbols = symbols => ({ ...ready, result: { ...ready.result,
    files: [{ ...ready.result.files[0], excluded_symbols: symbols }] } });
  assert.ok(parseAutomaticActivity(withSymbols(["invoice_total"])));
  assert.equal(parseAutomaticActivity(withSymbols("invoice_total")), undefined);
});

test("validates input provenance and thresholds without rejecting older records", () => {
  const trace = { mode: "conversation", current_query: "Which tests cover that behavior?", effective_query: "Account lockout tests",
    scope: "Repository discovery without editor hints", history_text: "Explain account lockout", history_source: "native_scoped_user_turns",
    threshold: .45, indexed_files: 6 };
  const record = input_trace => ({ ...ready, result: { ...ready.result, input_trace } });
  assert.equal(parseAutomaticActivity(record(trace)).result.input_trace.history_source, "native_scoped_user_turns");
  assert.ok(parseAutomaticActivity(record(null)));
  for (const change of [{ mode: "global_memory" }, { threshold: NaN }, { threshold: 1.1 }, { history_source: "all_chats" },
    { effective_query: 42 }, { indexed_files: -1 }, { first_line: 0 }]) {
    assert.equal(parseAutomaticActivity(record({ ...trace, ...change })), undefined);
  }
  assert.equal(parseAutomaticActivity(record([])), undefined);
  const withFile = file => ({ ...ready, result: { ...ready.result, files: [{ ...ready.result.files[0], ...file }] } });
  assert.ok(parseAutomaticActivity(withFile({ pruning_method: "neural_lines", effective_threshold: .6 })));
  assert.equal(parseAutomaticActivity(withFile({ effective_threshold: "0.6" })), undefined);
});

test("rejects incomplete activity instead of crashing the result view", () => {
  assert.equal(parseAutomaticActivity({ ...ready, result: {} }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, pruned_tokens: "100" } }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, files: [{ file_path: "payment.py" }] } }), undefined);
  assert.equal(parseAutomaticActivity(null), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, files: [null] } }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, verification: "true" }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, transport: 42 }), undefined);
});

test("accepts failure records so startup problems remain visible", () => {
  assert.equal(parseAutomaticActivity({ ...ready, status: "error", result: undefined, error: "offline" }).error, "offline");
});

test("a new hook result updates the status and opens the panel without stealing focus", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "demo" } }];
  currentActivity = { ...ready, status: "retrieving", result: undefined };
  const status = {};
  const panels = [];
  const monitor = new AutomaticContextMonitor(status, makePanel(panels), "extension");
  await new Promise((resolve) => setImmediate(resolve));
  assert.match(status.text, /awaiting prompt/);
  currentActivity = { ...ready, query: "Explain payment retries", elapsed_ms: 5400 };
  watcherCallbacks.at(-1)();
  await new Promise((resolve) => setTimeout(resolve, 180));
  assert.match(status.text, /1 files, 100 tokens/);
  assert.equal(panels.length, 1);
  assert.equal(panels[0][0].automatic_context.query, currentActivity.query);
  assert.equal(panels[0][2], true);
  assert.ok(outputLines.some((line) => line.includes("services/payment_service.py")));
  monitor.dispose();
});

test("loading an old result does not present it as fresh agent activity", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "demo" } }];
  currentActivity = ready;
  const status = {};
  const panels = [];
  const monitor = new AutomaticContextMonitor(status, makePanel(panels), "extension");
  await new Promise((resolve) => setImmediate(resolve));
  assert.match(status.text, /last result/);
  assert.match(status.tooltip, /Previous context/);
  assert.equal(panels.length, 0);
  monitor.dispose();
});

test("verification reports are labeled as tests and never open a live result panel", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "demo" } }];
  currentActivity = { ...ready, event_id: "old-result" };
  const status = {};
  const panels = [];
  const monitor = new AutomaticContextMonitor(status, makePanel(panels), "extension");
  await new Promise((resolve) => setImmediate(resolve));
  currentActivity = { ...ready, verification: true };
  watcherCallbacks.at(-1)();
  await new Promise((resolve) => setTimeout(resolve, 180));
  assert.match(status.text, /TokenWise test/);
  assert.match(status.tooltip, /not a real Antigravity/);
  assert.equal(panels.length, 0);
  monitor.dispose();
});

test("a fresh agent-command result shows its transport and opens the panel", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "demo" } }];
  currentActivity = { ...ready, event_id: "old-result" };
  const status = {};
  const panels = [];
  const monitor = new AutomaticContextMonitor(status, makePanel(panels), "extension");
  await new Promise((resolve) => setImmediate(resolve));
  currentActivity = { ...ready, transport: "antigravity-agent-command", query: "Explain account lockout" };
  watcherCallbacks.at(-1)();
  await new Promise((resolve) => setTimeout(resolve, 180));
  assert.match(status.text, /TokenWise Auto/);
  assert.match(status.tooltip, /agent command/);
  assert.equal(panels.length, 1);
  monitor.dispose();
});

test("enabling a repository clears stale context and waits for real prompt activity", async () => {
  const folder = { name: "New Repository", uri: { fsPath: "C:/New Repository", toString: () => "new-repo" } };
  vscodeStub.workspace.workspaceFolders = [folder];
  currentActivity = ready;
  const status = {};
  const monitor = new AutomaticContextMonitor(status, makePanel(), "extension");
  await new Promise((resolve) => setImmediate(resolve));
  monitor.configured(folder);
  assert.match(status.text, /awaiting prompt/);
  assert.match(status.tooltip, /New Repository/);
  assert.equal(monitor.latest, undefined);
  monitor.dispose();
});

test("unrelated hooks do not present an unconfigured repository as enabled", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "plain-repo" } }];
  currentActivity = undefined;
  currentHooks = { team: { enabled: true } };
  const status = { text: "TokenWise" };
  const monitor = new AutomaticContextMonitor(status, makePanel(), "extension");
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(status.text, "TokenWise");
  monitor.dispose();
});

test("owned hook setup without previous activity shows awaiting prompt", async () => {
  vscodeStub.workspace.workspaceFolders = [{ uri: { toString: () => "enabled-repo" } }];
  currentActivity = undefined;
  currentHooks = { "tokenwise-automatic-context": { enabled: true, PreInvocation: [] } };
  const status = {};
  const monitor = new AutomaticContextMonitor(status, makePanel(), "extension");
  await new Promise((resolve) => setImmediate(resolve));
  assert.match(status.text, /awaiting prompt/);
  monitor.dispose();
});

async function freshMonitor(panel = makePanel()) {
  vscodeStub.workspace.workspaceFolders = [{ uri: { scheme: "file", fsPath: "C:/demo", toString: () => "demo" } }];
  currentActivity = { ...ready, status: "retrieving", result: undefined };
  const monitor = new AutomaticContextMonitor({}, panel, "extension");
  await new Promise(resolve => setImmediate(resolve));
  currentActivity = ready;
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  return monitor;
}

test("fresh automatic context gets carbon values from its actual backend without reopening the panel", async () => {
  settings.enableCarbonEstimation = true;
  const panels = [], updates = [];
  const monitor = await freshMonitor(makePanel(panels, updates));
  assert.equal(panels.length, 1);
  assert.equal(panels[0][0].carbonStatus, "pending");
  assert.equal(updates.length, 1);
  assert.equal(updates[0].carbonStatus, "ready");
  assert.equal(updates[0].carbonBefore.co2Grams, 0.6);
  assert.equal(updates[0].carbonAfter.co2Grams, 0.1);
  assert.equal(updates[0].carbonSavings.co2GramsSaved, 0.5);
  assert.equal(carbonClients[0].apiUrl, "http://127.0.0.1:8005");
  assert.deepEqual(carbonRequests.map(item => item.input_tokens), [600, 100]);
  assert.equal(updates[0].carbonBaseline, "formatted-context");
  monitor.dispose();
});

test("automatic comparison is opt-in and requires a fresh recorded snapshot", async () => {
  const monitor = await freshMonitor();
  assert.equal(comparisonRequests.length, 0);
  settings.autoCompareAutomaticContext = true;
  currentActivity = { ...ready, event_id: "missing-snapshot", query: "Explain auth" };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(comparisonRequests.length, 0);
  assert.equal(monitor.latest.result.comparisonStatus, "unavailable");
  assert.match(monitor.latest.result.comparisonError, /snapshot/);
  monitor.dispose();
});

test("fresh automatic comparison uses the exact packet and local backend, without an editor", async () => {
  settings.autoCompareAutomaticContext = true;
  const panels = [], updates = [];
  const monitor = await freshMonitor(makePanel(panels, updates));
  currentActivity = { ...ready, event_id: "compare-turn", query: "Explain auth", result: {
    ...ready.result, repository_fingerprint: "a".repeat(64), retained_source_tokens: 100 } };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(comparisonRequests.length, 1);
  assert.equal(comparisonRequests[0].root, "C:/demo");
  assert.equal(comparisonRequests[0].prepared.unified_prompt, ready.result.unified_prompt);
  assert.equal(carbonClients.at(-1).apiUrl, ready.backend_url);
  assert.equal(monitor.latest.result.comparisonStatus, "ready");
  assert.equal(monitor.latest.result.comparison.carbonStatus, "disabled");
  assert.ok(updates.some(update => update.comparisonStatus === "ready"));
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(comparisonRequests.length, 1);
  monitor.dispose();
});

test("failed automatic comparison leaves context usable, and stale results never update a newer prompt", async () => {
  settings.autoCompareAutomaticContext = true;
  comparisonResponder = () => { throw new Error("Repository changed. Retrieve again."); };
  const panels = [], updates = [];
  const monitor = await freshMonitor(makePanel(panels, updates));
  const activity = { ...ready, query: "Explain auth", result: { ...ready.result, repository_fingerprint: "a".repeat(64) } };
  currentActivity = { ...activity, event_id: "failed-comparison" };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(monitor.latest.result.comparisonStatus, "unavailable");
  assert.equal(monitor.latest.result.unified_prompt, ready.result.unified_prompt);
  let resolve;
  comparisonResponder = () => new Promise(done => { resolve = done; });
  currentActivity = { ...activity, event_id: "late-comparison" };
  watcherCallbacks.at(-1)();
  await new Promise(done => setTimeout(done, 180));
  currentActivity = { ...ready, event_id: "next-prompt", status: "retrieving", result: undefined };
  watcherCallbacks.at(-1)();
  await new Promise(done => setTimeout(done, 180));
  const count = updates.length;
  resolve({ methods: [], notes: [] });
  await new Promise(done => setImmediate(done));
  assert.equal(updates.length, count);
  monitor.dispose();
});

test("automatic comparison never sends source to a remote server or runs verification reports", async () => {
  settings.autoCompareAutomaticContext = true;
  const monitor = await freshMonitor();
  const result = { ...ready.result, repository_fingerprint: "a".repeat(64) };
  currentActivity = { ...ready, result, event_id: "remote-comparison", query: "Explain auth", backend_url: "https://example.com" };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(comparisonRequests.length, 0);
  assert.match(monitor.latest.result.comparisonError, /local TokenWise backend/);
  currentActivity = { ...ready, result: { ...result }, event_id: "verification-comparison", query: "Explain auth", verification: true };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(comparisonRequests.length, 0);
  monitor.dispose();
});

test("disabled carbon remains explicit and performs no estimation requests", async () => {
  const monitor = await freshMonitor();
  assert.equal(monitor.latest.result.carbonStatus, "disabled");
  assert.equal(carbonRequests.length, 0);
  monitor.dispose();
});

test("carbon failure leaves the prepared context usable and records its reason", async () => {
  settings.enableCarbonEstimation = true;
  carbonResponder = () => { throw new Error("Carbon models are unavailable"); };
  const panels = [], updates = [];
  const monitor = await freshMonitor(makePanel(panels, updates));
  assert.equal(panels.length, 1);
  assert.equal(updates[0].carbonStatus, "unavailable");
  assert.match(updates[0].carbonError, /models are unavailable/);
  assert.equal(updates[0].unified_prompt, ready.result.unified_prompt);
  monitor.dispose();
});

test("late carbon results cannot overwrite a newer user prompt", async () => {
  settings.enableCarbonEstimation = true;
  const deferred = [];
  carbonResponder = request => new Promise(resolve => deferred.push(() => resolve(estimate(request))));
  const panels = [], updates = [];
  const monitor = await freshMonitor(makePanel(panels, updates));
  assert.equal(deferred.length, 2);
  currentActivity = { ...ready, event_id: "next-turn", status: "retrieving", result: undefined };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  deferred.forEach(resolve => resolve());
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(monitor.latest.event_id, "next-turn");
  assert.equal(updates.length, 0);
  monitor.dispose();
});

test("verification does not estimate carbon as though it were a live prompt", async () => {
  settings.enableCarbonEstimation = true;
  const monitor = await freshMonitor();
  carbonRequests.length = 0;
  currentActivity = { ...ready, event_id: "verification-turn", verification: true };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(carbonRequests.length, 0);
  monitor.dispose();
});

test("automatic carbon cannot send requests to a remote URL from an activity file", async () => {
  settings.enableCarbonEstimation = true;
  const monitor = await freshMonitor();
  carbonRequests.length = 0;
  currentActivity = { ...ready, event_id: "remote-turn", backend_url: "https://example.com" };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(carbonRequests.length, 0);
  assert.equal(monitor.latest.result.carbonStatus, "unavailable");
  assert.match(monitor.latest.result.carbonError, /local TokenWise backend/);
  monitor.dispose();
});

test("older backend results request an upgrade instead of comparing mismatched carbon baselines", async () => {
  settings.enableCarbonEstimation = true;
  const monitor = await freshMonitor();
  carbonRequests.length = 0;
  currentActivity = { ...ready, event_id: "legacy-turn", result: { ...ready.result, raw_context_tokens: undefined } };
  watcherCallbacks.at(-1)();
  await new Promise(resolve => setTimeout(resolve, 180));
  assert.equal(carbonRequests.length, 0);
  assert.match(monitor.latest.result.carbonError, /Update the TokenWise backend/);
  monitor.dispose();
});

test("automatic carbon is still prepared when automatic panel opening is disabled", async () => {
  settings.enableCarbonEstimation = true;
  settings.autoOpenAutomaticContext = false;
  const panels = [];
  const monitor = await freshMonitor(makePanel(panels));
  assert.equal(panels.length, 0);
  assert.equal(monitor.latest.result.carbonStatus, "ready");
  commandCallbacks.get("tokenwise.showAutomaticContext")();
  assert.equal(panels.length, 1);
  assert.equal(panels[0][0].carbonStatus, "ready");
  monitor.dispose();
});

test("malformed optional token metrics and warnings are rejected", () => {
  for (const value of [-1, "100", NaN]) {
    assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, raw_context_tokens: value } }), undefined);
  }
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, warnings: [42] } }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, context_hint_used: "true" } }), undefined);
  assert.ok(parseAutomaticActivity({ ...ready, result: { ...ready.result, context_hint_used: true } }));
  assert.equal(parseAutomaticActivity({ ...ready, backend_url: 42 }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, original_tokens: -17 } }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, structured_goal: { identifiers: "GIVE" } } }), undefined);
  assert.equal(parseAutomaticActivity({ ...ready, result: { ...ready.result, files: [] } }), undefined);
});
