import unittest

from services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    def test_successful_login_and_validation(self):
        service = AuthService()
        token = service.authenticate_user("admin", "adminSecret123")
        self.assertIsNotNone(token)
        payload = service.validate_session(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["username"], "admin")

    def test_account_locks_after_five_failures(self):
        service = AuthService()
        for _ in range(5):
            self.assertIsNone(service.authenticate_user("admin", "wrong-password"))
        self.assertFalse(service._users["admin"].is_active)
        self.assertIsNone(service.authenticate_user("admin", "adminSecret123"))

    def test_revoke_invalidates_session(self):
        service = AuthService()
        token = service.authenticate_user("admin", "adminSecret123")
        self.assertIsNotNone(token)
        session_id = next(iter(service._sessions))
        self.assertTrue(service.revoke_session(session_id))
        self.assertIsNone(service.validate_session(token))


if __name__ == "__main__":
    unittest.main()
