"""Recognize explicit topic contrasts, not arbitrary grammatical negation."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class QueryFocus:
    positive_query: str
    excluded_topics: tuple[str, ...] = ()


def query_focus(query: str) -> QueryFocus:
    # A contrast marker is required: "not revoked" alone is a positive task.
    pattern = r"(?:,\s*not\s+|\bbut\s+not\s+|\brather\s+than\s+|\bexcluding\s+)([^,.!?;\n]+)"
    excluded: list[str] = []

    def contrast(match: re.Match) -> str:
        topic = match.group(1).strip()
        if re.match(r"(?:only|just|necessarily|because|when|if|modify|change|edit|write|delete|run|execute)\b", topic, re.I):
            return match.group(0)
        if not re.search(r"[a-zA-Z_]", topic):
            return match.group(0)
        excluded.append(topic)
        return " "

    positive = re.sub(pattern, contrast, query, flags=re.I).strip()
    if not re.search(r"[a-zA-Z_]", positive):
        return QueryFocus(query)
    return QueryFocus(positive, tuple(dict.fromkeys(excluded)))
