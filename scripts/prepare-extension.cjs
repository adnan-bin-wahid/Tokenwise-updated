const fs = require("node:fs/promises");
const path = require("node:path");
const { createHash } = require("node:crypto");

const root = path.resolve(__dirname, "..");
const backend = "swe-pruner/swe-pruner";
const target = path.join(root, "vscode-extension/resources/backend-bundle");
const modelFiles = ["config.json", "tokenizer.json", "tokenizer_config.json", "backbone/config.json", "added_tokens.json", "special_tokens_map.json", "chat_template.jinja", "merges.txt", "vocab.json", "README.md"];
const files = ["scripts/antigravity_context.py", "scripts/antigravity_hook.py", "scripts/install_backend.py", "scripts/backend_control.py", `${backend}/pyproject.toml`, `${backend}/README.md`, `${backend}/LICENSE`, ...modelFiles.map((name) => `${backend}/model/${name}`)];

async function collect(directory, suffixes) {
  for (const entry of await fs.readdir(path.join(root, directory), { withFileTypes: true })) {
    const relative = `${directory}/${entry.name}`;
    if (entry.isDirectory() && entry.name !== "__pycache__") { await collect(relative, suffixes); }
    else if (entry.isFile() && suffixes.some((suffix) => entry.name.endsWith(suffix))) { files.push(relative); }
  }
}

async function main() {
  await collect(`${backend}/src`, [".py"]);
  await collect(`${backend}/carbon_artifacts`, [".json", ".pkl"]);
  const resourceRoot = path.join(root, "vscode-extension/resources");
  if (path.dirname(target) !== resourceRoot || path.basename(target) !== "backend-bundle") { throw new Error("Invalid generated bundle target."); }
  const actualRoot = await fs.realpath(root);
  const actualResources = await fs.realpath(resourceRoot);
  const inside = path.relative(actualRoot, actualResources);
  if (!inside || inside.startsWith("..") || path.isAbsolute(inside)) { throw new Error("Resources must remain inside the checkout."); }
  try { if ((await fs.lstat(target)).isSymbolicLink()) { throw new Error("The generated bundle cannot be a symbolic link."); } }
  catch (error) { if (error.code !== "ENOENT") { throw error; } }
  await fs.rm(target, { recursive: true, force: true });
  await fs.mkdir(target, { recursive: true });
  const manifest = { schema_version: 1, files: [], model: {
    repository: "ayanami-kitasan/code-pruner", revision: "863cee3198c715c9df1faa422a3490e0832bb734",
    url: "https://huggingface.co/ayanami-kitasan/code-pruner/resolve/863cee3198c715c9df1faa422a3490e0832bb734/model.safetensors",
    sha256: "373b77f5262c3298b803303d49ea38949d3e92f08dc3bbb90b03f490413adae9", size: 1345834856,
  } };
  for (const relative of files.sort()) {
    const source = await fs.readFile(path.join(root, relative));
    const destination = path.join(target, relative);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.writeFile(destination, source);
    manifest.files.push({ path: relative, sha256: createHash("sha256").update(source).digest("hex"), size: source.length });
  }
  await fs.writeFile(path.join(target, "backend-manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
  await fs.copyFile(path.join(root, "README.md"), path.join(resourceRoot, "user-guide.md"));
  await fs.copyFile(path.join(root, "demonstation.md"), path.join(resourceRoot, "demonstation.md"));
  await fs.copyFile(path.join(root, "study.md"), path.join(resourceRoot, "study.md"));
  const demoTarget = path.join(resourceRoot, "demonstration");
  const demoSource = path.join(root, "demonstration");
  const demoCases = JSON.parse(await fs.readFile(path.join(demoSource, "cases.json"), "utf8")).cases;
  if (!Array.isArray(demoCases) || !demoCases.length || demoCases.some(item => !item || typeof item.project !== "string" || !/^[a-z0-9_]+$/.test(item.project))) {
    throw new Error("Invalid demonstration project manifest.");
  }
  const demoProjects = new Set(demoCases.map(item => item.project));
  try { if ((await fs.lstat(demoTarget)).isSymbolicLink()) { throw new Error("The generated demonstration cannot be a symbolic link."); } }
  catch (error) { if (error.code !== "ENOENT") { throw error; } }
  // Replace generated examples so deleted source projects cannot survive an upgrade.
  await fs.rm(demoTarget, { recursive: true, force: true });
  await fs.cp(demoSource, demoTarget, {
    recursive: true,
    filter: async source => {
      if (["results", "__pycache__", ".agents", ".tokenwise"].includes(path.basename(source))) { return false; }
      const entry = await fs.lstat(source);
      const relative = path.relative(demoSource, source);
      if (relative && entry.isDirectory() && !demoProjects.has(relative.split(path.sep)[0])) { return false; }
      return entry.isDirectory() || (entry.isFile() && /\.(py|json|md)$/.test(source));
    },
  });
  await fs.copyFile(path.join(root, "docs/THIRD-PARTY-NOTICES.md"), path.join(resourceRoot, "THIRD-PARTY-NOTICES.md"));
  await fs.mkdir(path.join(resourceRoot, "docs"), { recursive: true });
  for (const name of ["ANTIGRAVITY.md", "PROJECT-EVALUATION.md", "DEVELOPMENT.md", "PUBLISHING.md", "THIRD-PARTY-NOTICES.md"]) {
    await fs.copyFile(path.join(root, "docs", name), path.join(resourceRoot, "docs", name));
  }
  console.log(`Prepared ${files.length} backend files; model weights will be downloaded separately.`);
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
