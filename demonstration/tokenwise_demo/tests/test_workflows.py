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

    def test_invoice_rounds_half_up_in_integer_cents(self):
        self.assertEqual(invoice_total(10, 15, 0), 12)

    def test_invoice_tax_and_shipping_are_validated(self):
        for subtotal, tax, shipping in ((100, -1, 0), (100, 101, 0), (100, 15, -1)):
            with self.subTest(subtotal=subtotal, tax=tax, shipping=shipping):
                with self.assertRaises(ValueError):
                    invoice_total(subtotal, tax, shipping)

    def test_zero_invoice_is_valid(self):
        self.assertEqual(invoice_total(0, 0, 0), 0)

    def test_shipping_modes(self):
        self.assertEqual(shipping_days("regional"), 4)
        self.assertEqual(shipping_days("regional", True), 1)

    def test_unknown_shipping_zone_is_rejected(self):
        with self.assertRaises(ValueError):
            shipping_days("unknown")
