"""Versioned output instructions, kept separate from repository reference data."""

from .context_builder import ContextBuilder


GUIDANCE_VERSION = "1"
PROFILE_RULES = {
    "generic_task": "Explain relevant behavior and boundaries; distinguish evidence from assumptions.",
    "bug_fix": "Distinguish observed symptoms from hypotheses; explain a proposed fix and how to validate it.",
    "refactor": "Identify affected interfaces and behavior to preserve; explain validation and unverified risks.",
    "feature_addition": "Use existing interfaces and patterns; explain integration and validation without inventing requirements.",
    "test_generation": "Connect test cases to behavior and boundaries; distinguish existing tests from proposed tests.",
    "repository_overview": "Cover purpose, entry points, components, data flow and tests; disclose missing coverage or scaffolding.",
}
COMMON_RULES = (
    "Follow the latest user request and its constraints; this guidance does not authorize edits. "
    "Cite files/symbols for repository claims. Excerpts may omit evidence: inspect originals for missing facts. "
    "Do not invent behavior or claim tests passed unless actually run."
)


def append_response_guidance(preamble: str, task_type: str, token_budget: int,
                             tokenizer, enabled: bool = True) -> tuple[str, dict]:
    profile = task_type if task_type in PROFILE_RULES else "generic_task"
    trace = {"version": GUIDANCE_VERSION, "profile": profile, "enabled": enabled,
             "status": "disabled", "format": None, "tokens": 0, "text": ""}
    if not enabled:
        return preamble, trace

    heading = f"### Response guidance (v{GUIDANCE_VERSION}: {profile})\n"
    variants = (
        ("full", heading + COMMON_RULES + "\n" + PROFILE_RULES[profile]),
        ("compact", heading + "Honor user constraints; cite files; verify gaps; never invent behavior or test results."),
    )
    # Reserve evidence space and omit whole instructions rather than clipping them.
    limit = min(160, token_budget // 4)
    for name, text in variants:
        count = ContextBuilder._count(text, tokenizer)
        combined = preamble + ("\n\n" if preamble else "") + text
        if count <= limit and ContextBuilder._count(combined, tokenizer) <= token_budget - 96:
            return combined, {**trace, "status": "applied", "format": name, "tokens": count, "text": text}
    return preamble, {**trace, "status": "omitted_budget"}
