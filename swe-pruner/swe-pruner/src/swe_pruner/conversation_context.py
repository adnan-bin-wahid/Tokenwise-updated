"""Small, explicit conversation hints; never read another chat's activity record."""

import re

HINT_LIMIT = 2000
USER_TURN_LIMIT = 3


def is_follow_up(query: str) -> bool:
    return bool(re.search(
        r"^\s*(?:(?:what|how)\s+about\s+(?:it|its|that|this|those|their|them|tests|the\s+tests)\b|"
        r"and\s+(?:its|that|this|those|their|the\s+tests)\b|"
        r"(?:why\s+(?:does|is|did)|does)\s+(?:it|that|this)\b|"
        r"show\s+(?:me\s+)?(?:its|those|their)\b|"
        r"which\s+tests\s+(?:cover|verify|test)\s+(?:it|that|this)\b|"
        r"what\s+happens\s+(?:when|after)\s+(?:it|that|this)\b)", query, re.IGNORECASE,
    ))


def conversation_hint(query: str, previous: dict, scoped: bool) -> str:
    if scoped and is_follow_up(query):
        return "\n\n".join(prior_user_turns(previous))
    return ""


def bound_user_turns(turns: list) -> list[str]:
    valid = [turn.strip() for turn in turns if isinstance(turn, str) and turn.strip()]
    if len(valid) > USER_TURN_LIMIT:
        valid = [valid[0], *valid[-(USER_TURN_LIMIT - 1):]]
    allowance = (HINT_LIMIT - 2 * max(0, len(valid) - 1)) // max(1, len(valid))
    return [turn[:allowance] for turn in valid]


def prior_user_turns(previous: dict) -> list[str]:
    turns = previous.get("user_turns")
    if isinstance(turns, list):
        return bound_user_turns(turns)
    return bound_user_turns([previous.get("topic_query")])


def next_user_turns(query: str, previous: dict, scoped: bool) -> list[str]:
    if not scoped:
        return []
    if not is_follow_up(query):
        return bound_user_turns([query])
    prior = prior_user_turns(previous)
    return bound_user_turns([*prior, query]) if prior else []
