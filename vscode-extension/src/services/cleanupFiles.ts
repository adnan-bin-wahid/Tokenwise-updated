import { createHash, randomBytes } from "node:crypto";
import * as fs from "node:fs/promises";
import * as path from "node:path";
import { applyEdits, modify, parse, ParseError } from "jsonc-parser";

export const EXTENSION_ID = "adnan-bin-wahid.tokenwise-vscode";
export const hash = (value: Buffer | string): string => createHash("sha256").update(value).digest("hex");
export const isObject = (value: unknown): value is Record<string, any> => value !== null && typeof value === "object" && !Array.isArray(value);

export async function readOptional(filename: string): Promise<Buffer | undefined> {
  try { return await fs.readFile(filename); }
  catch (error) { if ((error as NodeJS.ErrnoException).code === "ENOENT") { return undefined; } throw error; }
}

export function parseObject(bytes: Buffer | string): Record<string, any> {
  const errors: ParseError[] = [];
  const value: unknown = parse(bytes.toString().replace(/^\uFEFF/, ""), errors, { allowTrailingComma: true });
  if (errors.length || !isObject(value)) { throw new Error("Invalid JSON/JSONC; preserving the file."); }
  return value;
}

export async function safeRoot(root: string): Promise<string> {
  if (!path.isAbsolute(root) || (await fs.lstat(root)).isSymbolicLink()) { throw new Error(`Unsafe cleanup root: ${root}`); }
  const actual = await fs.realpath(root);
  const expected = path.resolve(root);
  if (process.platform === "win32" ? expected.toLowerCase() !== actual.toLowerCase() : expected !== actual) { throw new Error(`Cleanup root was redirected or moved: ${root}`); }
  return actual;
}

export async function safeChild(root: string, relative: string): Promise<string> {
  await safeRoot(root);
  const target = path.resolve(root, relative);
  const inside = path.relative(root, target);
  if (!inside || inside === ".." || inside.startsWith(`..${path.sep}`) || path.isAbsolute(inside)) { throw new Error("Cleanup paths must stay inside their owned root."); }
  let current = root;
  for (const segment of inside.split(path.sep)) {
    current = path.join(current, segment);
    try { if ((await fs.lstat(current)).isSymbolicLink()) { throw new Error(`Refusing a symbolic link or junction: ${current}`); } }
    catch (error) { if ((error as NodeJS.ErrnoException).code === "ENOENT") { break; } throw error; }
  }
  return target;
}

export async function atomicWrite(filename: string, bytes: Buffer | string): Promise<void> {
  await fs.mkdir(path.dirname(filename), { recursive: true });
  const temporary = `${filename}.${randomBytes(8).toString("hex")}.tmp`;
  try { await fs.writeFile(temporary, bytes, { flag: "wx" }); await fs.rename(temporary, filename); }
  finally { await fs.unlink(temporary).catch((error: NodeJS.ErrnoException) => { if (error.code !== "ENOENT") { throw error; } }); }
}

export async function replaceUnchanged(filename: string, previous: Buffer, next?: Buffer): Promise<void> {
  const current = await readOptional(filename);
  if (!current?.equals(previous)) { throw new Error(`A file changed during cleanup; preserving it: ${filename}`); }
  if (next) { await atomicWrite(filename, next); } else { await fs.unlink(filename); }
}

export function editJSON(text: string, propertyPath: (string | number)[], value: unknown): string {
  const bom = text.startsWith("\uFEFF") ? "\uFEFF" : "";
  const content = text.slice(bom.length);
  return bom + applyEdits(content, modify(content, propertyPath, value, { formattingOptions: { insertSpaces: true, tabSize: 2, eol: text.includes("\r\n") ? "\r\n" : "\n" } }));
}

export async function emptyDirectory(root: string, relative: string): Promise<void> {
  try { await fs.rmdir(await safeChild(root, relative)); }
  catch (error) { if (!["ENOENT", "ENOTEMPTY", "EEXIST"].includes((error as NodeJS.ErrnoException).code ?? "")) { throw error; } }
}

export async function removeOwnedTree(root: string, relative: string): Promise<void> {
  const target = await safeChild(root, relative);
  await fs.rm(target, { recursive: true, force: true, maxRetries: 8, retryDelay: 300 });
}
