const fs = require("node:fs/promises");
const path = require("node:path");
const { createHash } = require("node:crypto");

async function main() {
  const root = path.resolve(__dirname, "..");
  const manifest = JSON.parse(await fs.readFile(path.join(root, "vscode-extension/package.json"), "utf8"));
  if (!/^\d+\.\d+\.\d+$/.test(manifest.version) || !/^[a-z0-9-]+$/.test(manifest.name)) { throw new Error("Invalid package metadata."); }
  const release = path.join(root, "releases", `TokenWise-${manifest.version}`);
  await fs.mkdir(release, { recursive: true });
  const artifact = `${manifest.name}-${manifest.version}.vsix`;
  const files = [[path.join(root, "vscode-extension", artifact), artifact], [path.join(root, "README.md"), "README.md"],
    [path.join(root, "LICENSE"), "LICENSE"], [path.join(root, "docs/THIRD-PARTY-NOTICES.md"), "THIRD-PARTY-NOTICES.md"]];
  for (const name of ["ANTIGRAVITY.md", "PROJECT-EVALUATION.md", "DEVELOPMENT.md", "THIRD-PARTY-NOTICES.md"]) {
    files.push([path.join(root, "docs", name), `docs/${name}`]);
  }
  const checksums = [];
  for (const [source, name] of files) {
    const bytes = await fs.readFile(source);
    await fs.mkdir(path.dirname(path.join(release, name)), { recursive: true });
    await fs.copyFile(source, path.join(release, name));
    checksums.push(`${createHash("sha256").update(bytes).digest("hex")}  ${name}`);
  }
  await fs.writeFile(path.join(release, "SHA256SUMS.txt"), checksums.join("\n") + "\n");
  console.log(`Shareable release: ${release}`);
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
