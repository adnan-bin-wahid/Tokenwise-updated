import * as fs from "node:fs/promises";
import * as os from "node:os";
import * as path from "node:path";
import { spawn } from "node:child_process";
import { buildCleanupPlan } from "./services/cleanupRegistry";
import { safeRoot } from "./services/cleanupFiles";

export async function launchUninstallWorker(extensionRoot: string): Promise<string | undefined> {
  const plan = await buildCleanupPlan(extensionRoot);
  if (!plan.profiles.length) { return undefined; }
  const temporaryRoot = await fs.realpath(os.tmpdir());
  const workerRoot = await fs.mkdtemp(path.join(temporaryRoot, "tokenwise-uninstall-"));
  await safeRoot(workerRoot);
  await fs.mkdir(path.join(workerRoot, "services"));
  for (const name of ["cleanupFiles", "cleanupRegistry", "cleanupProcesses", "uninstallCleanup"]) {
    await fs.copyFile(path.join(extensionRoot, `dist/services/${name}.js`), path.join(workerRoot, `services/${name}.js`));
  }
  await fs.copyFile(path.join(extensionRoot, "dist/uninstallWorker.js"), path.join(workerRoot, "uninstallWorker.js"));
  const moduleRoot = path.join(workerRoot, "node_modules/jsonc-parser");
  await fs.cp(path.dirname(require.resolve("jsonc-parser")), moduleRoot, { recursive: true });
  await fs.writeFile(path.join(moduleRoot, "package.json"), JSON.stringify({ main: "main.js" }));
  const planPath = path.join(workerRoot, "plan.json");
  await fs.writeFile(planPath, JSON.stringify(plan));
  const child = spawn(process.execPath, [path.join(workerRoot, "uninstallWorker.js"), planPath], {
    detached: true, windowsHide: true, stdio: "ignore", env: { ...process.env, ELECTRON_RUN_AS_NODE: "1" },
  });
  await new Promise<void>((resolve, reject) => { child.once("spawn", () => resolve()); child.once("error", reject); });
  child.unref();
  return workerRoot;
}

if (require.main === module) {
  if (!process.argv.includes("--type=extension-post-uninstall")) {
    console.error("This entry point is reserved for the editor uninstall hook. Use TokenWise: Remove All Local Data inside the editor.");
    process.exitCode = 1;
  } else {
    launchUninstallWorker(path.resolve(__dirname, "..")).then((worker) => {
      console.log(worker ? `TokenWise cleanup started. Any preserved-file report will be at ${worker}/cleanup-report.json` : "No tracked TokenWise installation data to clean up.");
      process.exit(0);
    }).catch((error) => { console.error(String(error)); process.exit(1); });
  }
}
