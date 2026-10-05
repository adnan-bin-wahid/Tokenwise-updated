const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs");
const path = require("node:path");

test("the extension references a packaged square PNG icon at editor-compatible resolution", () => {
  const root = path.resolve(__dirname, "..");
  const manifest = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
  assert.equal(manifest.icon, "resources/icon.png");
  const bytes = fs.readFileSync(path.join(root, manifest.icon));
  assert.deepEqual(bytes.subarray(0, 8), Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
  assert.equal(bytes.subarray(12, 16).toString("ascii"), "IHDR");
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  assert.equal(width, height);
  assert.ok(width >= 128, "Extension icons require at least 128 pixels per side");
});
