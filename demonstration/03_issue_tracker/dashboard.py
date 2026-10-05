from collections import Counter
from tracker.models import Issue


def status_counts(issues: list[Issue]) -> dict[str, int]:
    return dict(sorted(Counter(issue.status for issue in issues).items()))


def search_titles(issues: list[Issue], phrase: str) -> list[str]:
    phrase = phrase.casefold().strip()
    if not phrase:
        return []
    return sorted(issue.identifier for issue in issues if phrase in issue.title.casefold())


def owner_workload(issues: list[Issue]) -> dict[str, int]:
    return dict(sorted(Counter(issue.owner for issue in issues if issue.status == "open").items()))
