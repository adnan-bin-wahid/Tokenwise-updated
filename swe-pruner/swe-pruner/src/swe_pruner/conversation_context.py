"""Small, explicit conversation hints; never read another chat's activity record."""

import re

HINT_LIMIT = 2000


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
    topic = previous.get("topic_query")
    if scoped and is_follow_up(query) and isinstance(topic, str):
        return topic.strip()[:HINT_LIMIT]
    return ""
