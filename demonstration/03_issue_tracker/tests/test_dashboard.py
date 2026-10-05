import unittest
from dashboard import owner_workload, search_titles, status_counts
from tracker.models import Issue


class DashboardTests(unittest.TestCase):
    def test_status_counts_and_open_workload(self):
        issues = [Issue("A", "Login screen", "student"), Issue("B", "Checkout bug", "student", "closed")]
        self.assertEqual(status_counts(issues), {"closed": 1, "open": 1})
        self.assertEqual(owner_workload(issues), {"student": 1})
        self.assertEqual(search_titles(issues, "LOGIN"), ["A"])
        self.assertEqual(search_titles(issues, ""), [])
