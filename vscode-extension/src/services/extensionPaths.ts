import * as path from "node:path";
import * as vscode from "vscode";

export function localStoragePath(context: vscode.ExtensionContext): string {
  const storage = context.globalStorageUri;
  // Desktop Antigravity maps vscode-userdata to the local file provider.
  if (!["file", "vscode-userdata"].includes(storage.scheme)
    || (storage.scheme === "vscode-userdata" && storage.authority)) {
    throw new Error(`Unsupported extension storage URI (${storage.scheme}). Local file-backed storage is required.`);
  }
  const nativePath = storage.with({ scheme: "file" }).fsPath;
  if (!path.isAbsolute(nativePath)) { throw new Error("The extension storage directory must have an absolute local path."); }
  return nativePath;
}
