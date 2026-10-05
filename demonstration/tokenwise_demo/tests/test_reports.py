import unittest
from reports import activity_summary, export_activity


class ReportTests(unittest.TestCase):
    def test_counts_and_csv(self):
        events = [{"actor": "student", "action": "view"}, {"actor": "teacher", "action": "view"}]
        self.assertEqual(activity_summary(events), {"view": 2})
        self.assertIn("teacher,view", export_activity(events))

    def test_empty_activity_has_no_counts_and_csv_has_a_header(self):
        self.assertEqual(activity_summary([]), {})
        self.assertEqual(export_activity([]).strip(), "actor,action")

    def test_summary_is_sorted_and_counts_each_action(self):
        events = [{"actor": "student", "action": action} for action in ("view", "login", "view")]
        summary = activity_summary(events)
        self.assertEqual(list(summary), ["login", "view"])
        self.assertEqual(summary, {"login": 1, "view": 2})
