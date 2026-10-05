from tracker.issue_service import IssueService
from tracker.models import Issue
from tracker.store import IssueStore
from dashboard import status_counts


def main() -> None:
    store = IssueStore([Issue("DEMO-1", "Review the login screen", "student")])
    service = IssueService(store)
    service.close("DEMO-1", "teacher", "maintainer")
    service.reopen("DEMO-1", "teacher", "maintainer")
    print("Status counts:", status_counts(list(store.issues.values())))
    print("Audit:", store.audit_events)


if __name__ == "__main__":
    main()
