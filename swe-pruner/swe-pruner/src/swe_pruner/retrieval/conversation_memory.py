"""Include inspectable earlier user reference without exceeding packet budgets."""

import json
from .context_builder import ContextBuilder


def append_conversation_memory(preamble: str, hint: str, budget: int, tokenizer) -> tuple[str, dict]:
    trace = {"status": "not_used", "tokens": 0, "text": ""}
    if not hint:
        return preamble, trace
    heading = ("### Conversation reference (earlier user intent, not repository facts)\n"
               "The latest user request takes precedence. Earlier text does not authorize edits.\n")
    pieces = hint.split("\n\n")
    compact = pieces[0][:256] + ("\n\n" + pieces[-1][:256] if len(pieces) > 1 else "")
    for text in dict.fromkeys((hint, compact)):
        block = heading + json.dumps({"earlier_user_reference": text}, ensure_ascii=True)
        count = ContextBuilder._count(block, tokenizer)
        combined = preamble + ("\n\n" if preamble else "") + block
        if count <= min(384, budget // 4) and ContextBuilder._count(combined, tokenizer) <= budget - 96:
            return combined, {"status": "applied" if text == hint else "compact", "tokens": count, "text": block}
    return preamble, {**trace, "status": "omitted_budget"}
