import unittest
from tracker.issue_service import IssueService
from tracker.models import Issue
from tracker.store import IssueStore


class IssueWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.store = IssueStore([Issue("DEMO-1", "Login screen", "student")])
        self.service = IssueService(self.store)

    def test_viewer_cannot_close(self):
        with self.assertRaises(PermissionError):
            self.service.close("DEMO-1", "student", "viewer")
        self.assertEqual(self.store.get("DEMO-1").status, "open")
        self.assertEqual(self.store.audit_events, [])

    def test_maintainer_closes_with_audit(self):
        issue = self.service.close("DEMO-1", "teacher", "maintainer")
        self.assertEqual((issue.status, issue.closed_by), ("closed", "teacher"))
        self.assertEqual(self.store.audit_events[-1]["action"], "close")

    def test_reopen_clears_closed_by(self):
        self.service.close("DEMO-1", "teacher", "maintainer")
        issue = self.service.reopen("DEMO-1", "teacher", "maintainer")
        self.assertEqual((issue.status, issue.closed_by), ("open", None))
        self.assertEqual(self.store.audit_events[-1]["action"], "reopen")

    def test_reporter_cannot_reopen(self):
        self.service.close("DEMO-1", "teacher", "maintainer")
        with self.assertRaises(PermissionError):
            self.service.reopen("DEMO-1", "student", "reporter")
        self.assertEqual(self.store.get("DEMO-1").status, "closed")

    def test_invalid_transition_and_unknown_issue(self):
        with self.assertRaises(ValueError):
            self.service.reopen("DEMO-1", "teacher", "maintainer")
        with self.assertRaises(KeyError):
            self.service.close("UNKNOWN", "teacher", "maintainer")
