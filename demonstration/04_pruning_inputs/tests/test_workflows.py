import unittest
from workflows import invoice_total, issue_session, revoke_session, session_is_valid, shipping_days


class WorkflowTests(unittest.TestCase):
    def test_session_expiry_boundary(self):
        session = issue_session("student", 100)
        self.assertEqual(session.expires_at, 400)
        self.assertTrue(session_is_valid(session, 399))
        self.assertFalse(session_is_valid(session, 400))

    def test_revocation(self):
        session = issue_session("student", 100)
        revoke_session(session)
        self.assertFalse(session_is_valid(session, 101))

    def test_username_required(self):
        with self.assertRaises(ValueError):
            issue_session("", 100)

    def test_invoice_total(self):
        self.assertEqual(invoice_total(10000, 15, 500), 12000)

    def test_invalid_invoice(self):
        with self.assertRaises(ValueError):
            invoice_total(-1, 15, 500)

    def test_shipping_modes(self):
        self.assertEqual(shipping_days("regional"), 4)
        self.assertEqual(shipping_days("regional", True), 1)
        with self.assertRaises(ValueError):
            shipping_days("unknown")
