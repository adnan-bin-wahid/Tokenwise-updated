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
    [path.join(root, "demonstation.md"), "demonstation.md"],
    [path.join(root, "LICENSE"), "LICENSE"], [path.join(root, "docs/THIRD-PARTY-NOTICES.md"), "THIRD-PARTY-NOTICES.md"],
    [path.join(root, "CHANGELOG.md"), "CHANGELOG.md"], [path.join(root, `docs/release-notes/v${manifest.version}.md`), "RELEASE-NOTES.md"]];
  for (const name of ["ANTIGRAVITY.md", "PROJECT-EVALUATION.md", "DEVELOPMENT.md", "PUBLISHING.md", "THIRD-PARTY-NOTICES.md"]) {
    files.push([path.join(root, "docs", name), `docs/${name}`]);
  }
  const checksums = [];
  const demoCases = JSON.parse(await fs.readFile(path.join(root, "demonstration/cases.json"), "utf8")).cases;
  if (!Array.isArray(demoCases) || !demoCases.length || demoCases.some(item => !item || typeof item.project !== "string" || !/^[a-z0-9_]+$/.test(item.project))) {
    throw new Error("Invalid demonstration project manifest.");
  }
  const demoProjects = new Set(demoCases.map(item => item.project));
  async function demoFiles(relative) {
    for (const entry of await fs.readdir(path.join(root, relative), { withFileTypes: true })) {
      if (["results", "__pycache__", ".agents", ".tokenwise"].includes(entry.name)) { continue; }
      const name = `${relative}/${entry.name}`;
      if (entry.isDirectory() && (relative !== "demonstration" || demoProjects.has(entry.name))) { await demoFiles(name); }
      else if (entry.isFile() && /\.(py|json|md)$/.test(entry.name)) { files.push([path.join(root, name), name]); }
    }
  }
  await demoFiles("demonstration");
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
