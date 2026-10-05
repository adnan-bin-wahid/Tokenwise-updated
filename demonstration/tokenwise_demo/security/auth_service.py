from hmac import compare_digest

from security.models import Account, password_digest
from security.settings import LOCKOUT_SECONDS, LOCKOUT_THRESHOLD


class AuthService:
    """Account lockout after failed login attempts, with a timed reset."""

    def authenticate(self, account: Account, password: str, now: int) -> bool:
        if now < account.locked_until:
            return False
        if account.locked_until:
            account.locked_until = 0
            account.failed_attempts = 0
        if compare_digest(account.digest, password_digest(password)):
            account.failed_attempts = 0
            return True
        account.failed_attempts += 1
        if account.failed_attempts >= LOCKOUT_THRESHOLD:
            account.locked_until = now + LOCKOUT_SECONDS
        return False
