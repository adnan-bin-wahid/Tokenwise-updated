const assert = require("node:assert/strict");
const { test } = require("node:test");
const Module = require("node:module");

const uri = { scheme: "file", fsPath: "/demo/session.py" };
const resources = [], requests = [], results = [];
let enabled;
const vscode = {
  workspace: {
    getConfiguration: (name, resource) => {
      assert.equal(name, "tokenWise"); resources.push(resource);
      return { get: (key, fallback) => key === "enableResponseGuidance" ? enabled ?? fallback
        : key === "enableCarbonEstimation" ? false : fallback };
    },
    getWorkspaceFolder: () => ({ uri: { fsPath: "/demo" } }),
  },
  languages: { getDiagnostics: () => [] }, DiagnosticSeverity: { Error: 0, Warning: 1 },
  ProgressLocation: { Notification: 1 },
  window: {
    activeTextEditor: { document: { uri, languageId: "python", getText: () => "", getWordRangeAtPosition: () => undefined },
      selection: { active: {} } },
    showInputBox: async () => "Explain session expiry. Do not modify files.",
    withProgress: async (_, action) => action(), showInformationMessage() {},
    showErrorMessage: message => assert.fail(message), showWarningMessage: message => assert.fail(message),
  },
};
const load = Module._load;
Module._load = function (name, ...args) {
  if (name === "vscode") { return vscode; }
  if (name === "../services/apiClient") { return { TokenWiseApiClient: class {
    async pruneWorkspace(request) { requests.push(request); return { pruned_tokens: 200 }; }
  } }; }
  return load.call(this, name, ...args);
};
let getConfig, create;
try {
  ({ getTokenWiseConfig: getConfig } = require("../dist/services/config.js"));
  ({ createBuildRepositoryContextCommand: create } = require("../dist/commands/buildRepositoryContext.js"));
} finally { Module._load = load; }

test("guidance config defaults to true and preserves a resource-scoped false", () => {
  enabled = undefined;
  assert.equal(getConfig(uri).enableResponseGuidance, true);
  enabled = false;
  assert.equal(getConfig(uri).enableResponseGuidance, false);
  assert.equal(resources.at(-1), uri);
  const property = require("../package.json").contributes.configuration.properties["tokenWise.enableResponseGuidance"];
  assert.equal(property.type, "boolean");
  assert.equal(property.default, true);
});

test("manual repository command forwards scoped guidance without rewriting constraints", async () => {
  for (const value of [undefined, false]) {
    enabled = value;
    await create({ showWorkspaceResult: result => results.push(result) }, "extension")();
    assert.equal(resources.at(-1), uri);
    assert.equal(requests.at(-1).response_guidance, value !== false);
    assert.equal(requests.at(-1).query, "Explain session expiry. Do not modify files.");
    assert.equal(requests.at(-1).active_file, uri.fsPath);
    assert.equal(requests.at(-1).selected_code, undefined);
    assert.equal(results.at(-1).carbonStatus, "disabled");
  }
});
