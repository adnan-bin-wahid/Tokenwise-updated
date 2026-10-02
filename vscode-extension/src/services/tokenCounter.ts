import { encode } from "gpt-tokenizer";

export function countTokens(text: string): number {
  try {
    return encode(text).length;
  } catch {
    // Fallback for unexpected tokenizer errors.
    return Math.max(
      0,
      text.trim().length === 0 ? 0 : Math.ceil(text.length / 4),
    );
  }
}
