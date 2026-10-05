import unittest
from reports import activity_summary, export_activity


class ReportTests(unittest.TestCase):
    def test_counts_and_csv(self):
        events = [{"actor": "student", "action": "view"}, {"actor": "teacher", "action": "view"}]
        self.assertEqual(activity_summary(events), {"view": 2})
        self.assertIn("teacher,view", export_activity(events))
