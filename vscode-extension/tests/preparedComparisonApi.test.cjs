const assert = require("node:assert/strict");
const { test } = require("node:test");
const { TokenWiseApiClient } = require("../dist/services/apiClient.js");
test("prepared comparison posts the exact packet without a retrieval call", async () => {
  const original = global.fetch;
  const requests = [];
  global.fetch = async (url, options) => { requests.push({ url, options }); return new Response(JSON.stringify({ methods: [] })); };
  try {
    const client = new TokenWiseApiClient({ apiUrl: "http://127.0.0.1:8005", timeoutMs: 1000 });
    const packet = { unified_prompt: "exact context", pruned_tokens: 12 };
    await client.comparePreparedWorkspace("C:/demo", "Explain auth", packet);
    assert.equal(requests[0].url, "http://127.0.0.1:8005/compare-prepared-workspace");
    assert.deepEqual(JSON.parse(requests[0].options.body), { workspace_root: "C:/demo", query: "Explain auth", prepared_context: packet });
    global.fetch = async () => new Response("missing", { status: 404 });
    await assert.rejects(client.comparePreparedWorkspace("C:/demo", "query", packet), /Set Up Backend/);
    global.fetch = async () => new Response("Snapshot changed", { status: 409 });
    await assert.rejects(client.comparePreparedWorkspace("C:/demo", "query", packet), /Snapshot changed/);
  } finally { global.fetch = original; }
});
