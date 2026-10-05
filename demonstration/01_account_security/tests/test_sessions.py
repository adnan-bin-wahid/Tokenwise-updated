import unittest
from security.session_service import SessionService


class SessionTests(unittest.TestCase):
    def test_expiry_is_exclusive(self):
        service = SessionService()
        session = service.issue("student", 100)
        self.assertTrue(service.valid(session, 399))
        self.assertFalse(service.valid(session, 400))

    def test_revocation(self):
        service = SessionService()
        session = service.issue("student", 100)
        service.revoke(session)
        self.assertFalse(service.valid(session, 101))
