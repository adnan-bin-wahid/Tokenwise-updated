import * as vscode from "vscode";

export function getSelectedOrFullCode(editor: vscode.TextEditor): {
  code: string;
  isSelection: boolean;
} {
  const selection = editor.selection;
  if (!selection.isEmpty) {
    return {
      code: editor.document.getText(selection),
      isSelection: true,
    };
  }

  return {
    code: editor.document.getText(),
    isSelection: false,
  };
}

export async function askQuery(): Promise<string | undefined> {
  return vscode.window.showInputBox({
    title: "TokenWise: Task Query",
    prompt:
      "Describe what context should be kept (for example: authentication logic, error handling)",
    placeHolder: "Find authentication and session-related logic",
    ignoreFocusOut: true,
    validateInput: (value) =>
      value.trim().length === 0 ? "Query is required." : null,
  });
}

export async function askThreshold(
  defaultThreshold: number,
): Promise<number | undefined> {
  const value = await vscode.window.showInputBox({
    title: "TokenWise: Pruning Threshold",
    prompt: "Enter threshold between 0 and 1",
    value: String(defaultThreshold),
    ignoreFocusOut: true,
    validateInput: (raw) => {
      const n = Number(raw);
      if (Number.isNaN(n)) {
        return "Threshold must be a number.";
      }
      if (n < 0 || n > 1) {
        return "Threshold must be between 0 and 1.";
      }
      return null;
    },
  });

  if (value === undefined) {
    return undefined;
  }
  return Number(value);
}
