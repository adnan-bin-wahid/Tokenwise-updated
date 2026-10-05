import unittest

from security.models import Account, Session, password_digest


class ModelTests(unittest.TestCase):
    def test_model_defaults(self):
        account = Account("student", password_digest("demo-pass"))
        self.assertEqual(account.failed_attempts, 0)
        self.assertEqual(account.locked_until, 0)
        session = Session("student", 400)
        self.assertEqual(session.username, "student")
        self.assertEqual(session.expires_at, 400)
        self.assertFalse(session.revoked)

    def test_teaching_digest_is_deterministic_and_password_sensitive(self):
        self.assertEqual(password_digest("correct"), password_digest("correct"))
        self.assertNotEqual(password_digest("correct"), password_digest("wrong"))
