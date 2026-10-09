"""Bounded, extractive user memory; no assistant facts or cross-chat activity."""

import re
from .query_focus import query_focus
from .retrieval.lexical_retriever import terms

HINT_LIMIT = 4000
USER_TURN_LIMIT = 8
STORED_TURN_LIMIT = 32
MESSAGE_LIMIT = 2000
STOP_WORDS = set("a an any all the this that those these it its their them and or to of in on for with from my me please can could would how why what which is are be do does did explain describe show give tell find add change fix use include exclude skip also now then continue keep focus more detail detailed code project repository test testing tests cover verify behavior behaviour boundary case expiry expiration duration threshold reset logic related relevant file files function class attempt failed failure after before not only no without using output answer format cite citation modify edit write make bullet point prose json table concise brief verbose instead about earlier previous again same plain english".split())
STOP_WORDS.update("fail error edge scenario assertion happen happens work working expand source existing return respond reply".split())


def _clauses(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[.!?]\s+|[;\n]+", text) if part.strip()]


def _tags(text: str) -> set[str]:
    patterns = {"edits": r"\b(?:modify|edit|write|change)\s+(?:any\s+|the\s+)?(?:files?|code|source)\b|\bread.only\b",
                "tests": r"\b(?:include|exclude|skip|without|no|only|focus on)\s+(?:the\s+)?tests?\b",
                "format": r"\b(?:bullet|prose|json|table|concise|brief|verbose)\b",
                "exclusions": r",\s*not\s+|\b(?:excluding|rather than|but not)\b"}
    return {name for name, pattern in patterns.items() if re.search(pattern, text, re.I)}


def _topic(text: str) -> set[str]:
    return set(terms(query_focus(text).positive_query)) - STOP_WORDS


def is_follow_up(query: str) -> bool:
    explicit = bool(re.search(
        r"^\s*(?:(?:what|how)\s+about\s+(?:it|its|that|this|those|their|them|tests|the\s+tests)\b|"
        r"and\s+(?:its|that|this|those|their|the\s+tests)\b|"
        r"(?:why\s+(?:does|is|did)|does)\s+(?:it|that|this)\b|"
        r"show\s+(?:me\s+)?(?:its|those|their)\b|"
        r"which\s+tests\s+(?:cover|verify|test)\s+(?:it|that|this)\b|"
        r"what\s+happens\s+(?:when|after)\s+(?:it|that|this)\b)", query, re.IGNORECASE,
    ))
    return explicit or bool(_tags(query) and not _topic(query)) \
        or bool(re.search(r"\b(?:it|its|that|those|their|them)\b", query, re.I) and not _topic(query)) \
        or bool(re.match(r"\s*(?:also|continue|keep|include|use|focus|make|more|now|add|expand)\b", query, re.I) and not _topic(query))


def stored_user_turns(turns: list) -> list[str]:
    valid = [turn.strip()[:MESSAGE_LIMIT] for turn in turns if isinstance(turn, str) and turn.strip()
             and not turn.lstrip().startswith("[TokenWise automatic context]")]
    return [valid[0], *valid[-(STORED_TURN_LIMIT - 1):]] if len(valid) > STORED_TURN_LIMIT else valid


def select_memory(query: str, turns: list) -> dict:
    """Select a related topic segment and remove recognized superseded clauses."""
    prior = stored_user_turns(turns)
    segments: list[list[tuple[int, str]]] = []
    for number, text in enumerate(prior, 1):
        if not segments or (not is_follow_up(text) and _topic(text)
                            and not (_topic(text) & _topic(segments[-1][0][1]))):
            segments.append([])
        segments[-1].append((number, text))
    selected = []
    reset = bool(re.search(r"\b(?:start over|new topic|new task|forget (?:the )?(?:earlier|previous)|ignore (?:the )?(?:earlier|previous))\b", query, re.I))
    if segments and not reset:
        if is_follow_up(query) and not _topic(query):
            selected = segments[-1]
        elif _topic(query):
            selected = next((segment for segment in reversed(segments)
                             if _topic(query) & _topic(segment[0][1])), [])
    # Latest explicit constraint wins; recognized replacements remove old clauses.
    superseded = _tags(query)
    filtered = []
    for number, text in reversed(selected):
        clauses = []
        for clause in _clauses(text):
            if _tags(clause) & superseded:
                clause = re.split(r"\b(?:do not|don't|include|exclude|skip|without|use|only|focus on|but not|rather than)\b|,\s*not\s+", clause, maxsplit=1, flags=re.I)[0].strip()
                if not _topic(clause):
                    continue
            clauses.append(clause)
        superseded |= _tags(text)
        if clauses:
            filtered.append((number, ". ".join(clauses)))
    filtered.reverse()
    anchor = filtered[:1]
    constraints = [item for item in filtered[1:] if _tags(item[1])]
    recent = filtered[-(USER_TURN_LIMIT - 1):]
    picked = dict(anchor + constraints[-(USER_TURN_LIMIT - 1):])
    for number, text in reversed(recent):
        if len(picked) < USER_TURN_LIMIT:
            picked[number] = text
    chosen = sorted(picked.items())
    allowance = (HINT_LIMIT - 2 * max(0, len(chosen) - 1)) // max(1, len(chosen))
    messages = [{"position": number, "text": text[:allowance],
                 "reason": "topic anchor" if index == 0 else "earlier requirement" if _tags(text) else "related user turn"}
                for index, (number, text) in enumerate(chosen)]
    hint = "\n\n".join(item["text"] for item in messages)
    return {"version": "1", "selection": "bounded lexical topic/requirement selection",
            "summary": messages[0]["text"][:512] if messages else "",
            "requirements": [clause for item in messages for clause in _clauses(item["text"]) if _tags(clause)],
            "messages": messages, "considered_messages": len(prior),
            "omitted_messages": len(prior) - len(messages), "characters": len(hint),
            "truncated": any(len(text) > allowance for _, text in chosen) or len(turns) > STORED_TURN_LIMIT
                         or any(isinstance(text, str) and len(text) > MESSAGE_LIMIT for text in turns),
            "hint": hint}


def conversation_hint(query: str, previous: dict, scoped: bool) -> str:
    return select_memory(query, prior_user_turns(previous))["hint"] if scoped else ""


def bound_user_turns(turns: list) -> list[str]:
    valid = [turn.strip() for turn in turns if isinstance(turn, str) and turn.strip()]
    if len(valid) > USER_TURN_LIMIT:
        valid = [valid[0], *valid[-(USER_TURN_LIMIT - 1):]]
    allowance = (HINT_LIMIT - 2 * max(0, len(valid) - 1)) // max(1, len(valid))
    return [turn[:allowance] for turn in valid]


def prior_user_turns(previous: dict) -> list[str]:
    turns = previous.get("user_turns")
    if isinstance(turns, list):
        return stored_user_turns(turns)
    return stored_user_turns([previous.get("topic_query")])


def next_user_turns(query: str, previous: dict, scoped: bool) -> list[str]:
    if not scoped:
        return []
    prior = prior_user_turns(previous)
    if select_memory(query, prior)["hint"]:
        return stored_user_turns([*prior, query])
    return [] if is_follow_up(query) else stored_user_turns([query])
