from tracker.models import Issue


class IssueStore:
    def __init__(self, issues: list[Issue]):
        self.issues = {issue.identifier: issue for issue in issues}
        self.audit_events: list[dict] = []

    def get(self, identifier: str) -> Issue:
        if identifier not in self.issues:
            raise KeyError("Unknown issue")
        return self.issues[identifier]

    def record(self, identifier: str, actor: str, action: str) -> None:
        self.audit_events.append({"issue": identifier, "actor": actor, "action": action})
