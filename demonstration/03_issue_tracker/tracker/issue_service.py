from tracker.models import Issue
from tracker.permissions import require_permission
from tracker.store import IssueStore


class IssueService:
    def __init__(self, store: IssueStore):
        self.store = store

    def close(self, identifier: str, actor: str, role: str) -> Issue:
        require_permission(role, "close")
        issue = self.store.get(identifier)
        if issue.status != "open":
            raise ValueError("Only an open issue can be closed")
        issue.status = "closed"
        issue.closed_by = actor
        self.store.record(identifier, actor, "close")
        return issue

    def reopen(self, identifier: str, actor: str, role: str) -> Issue:
        require_permission(role, "reopen")
        issue = self.store.get(identifier)
        if issue.status != "closed":
            raise ValueError("Only a closed issue can be reopened")
        issue.status = "open"
        issue.closed_by = None
        self.store.record(identifier, actor, "reopen")
        return issue
