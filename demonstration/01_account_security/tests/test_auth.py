import unittest

from security.auth_service import AuthService
from security.models import Account, password_digest
from security.settings import LOCKOUT_SECONDS, LOCKOUT_THRESHOLD


class AccountLockoutTests(unittest.TestCase):
    def setUp(self):
        self.account = Account("student", password_digest("correct"))
        self.service = AuthService()

    def lock(self):
        for _ in range(LOCKOUT_THRESHOLD):
            self.assertFalse(self.service.authenticate(self.account, "wrong", 100))

    def test_lockout_threshold(self):
        for _ in range(LOCKOUT_THRESHOLD - 1):
            self.service.authenticate(self.account, "wrong", 100)
        self.assertEqual(self.account.locked_until, 0)
        self.service.authenticate(self.account, "wrong", 100)
        self.assertEqual(self.account.locked_until, 100 + LOCKOUT_SECONDS)

    def test_correct_password_rejected_during_lockout(self):
        self.lock()
        self.assertFalse(self.service.authenticate(self.account, "correct", 101))
        self.assertEqual(self.account.failed_attempts, LOCKOUT_THRESHOLD)

    def test_expiry_boundary(self):
        self.lock()
        deadline = self.account.locked_until
        self.assertFalse(self.service.authenticate(self.account, "correct", deadline - 1))
        self.assertTrue(self.service.authenticate(self.account, "correct", deadline))
        self.assertEqual(self.account.failed_attempts, 0)
        self.assertEqual(self.account.locked_until, 0)

    def test_success_resets_failures_before_lockout(self):
        self.service.authenticate(self.account, "wrong", 100)
        self.assertTrue(self.service.authenticate(self.account, "correct", 101))
        self.assertEqual(self.account.failed_attempts, 0)

    def test_wrong_password_after_expiry_starts_a_new_count(self):
        self.lock()
        self.assertFalse(self.service.authenticate(self.account, "wrong", self.account.locked_until))
        self.assertEqual(self.account.failed_attempts, 1)
        self.assertEqual(self.account.locked_until, 0)
