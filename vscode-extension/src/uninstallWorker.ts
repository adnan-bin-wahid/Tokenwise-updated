import * as fs from "node:fs/promises";
import * as os from "node:os";
import * as path from "node:path";
import { runCleanup } from "./services/uninstallCleanup";
import { CleanupPlan } from "./services/cleanupRegistry";
import { parseObject, safeRoot } from "./services/cleanupFiles";

async function main(): Promise<void> {
  const root = await safeRoot(__dirname);
  if (path.dirname(root) !== await fs.realpath(os.tmpdir()) || !path.basename(root).startsWith("tokenwise-uninstall-")) { throw new Error("Invalid uninstall worker directory."); }
  const filename = path.join(root, "plan.json");
  if (process.argv[2] !== filename) { throw new Error("Invalid uninstall plan path."); }
  const result = await runCleanup(parseObject(await fs.readFile(filename)) as CleanupPlan);
  if (result.warnings.length || result.preserved.length) {
    await fs.writeFile(path.join(root, "cleanup-report.json"), JSON.stringify(result, null, 2));
    process.exitCode = 1;
    return;
  }
  // All required code is loaded in memory; remove the worker's own temporary files.
  await fs.rm(root, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 });
}

if (require.main === module) {
  main().catch(async (error) => {
    const root = path.resolve(__dirname);
    if (path.dirname(root) === await fs.realpath(os.tmpdir()) && path.basename(root).startsWith("tokenwise-uninstall-")) {
      await fs.writeFile(path.join(root, "cleanup-report.json"), JSON.stringify({ warnings: [String(error)] }));
    }
    process.exitCode = 1;
  });
}
