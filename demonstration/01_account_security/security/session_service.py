from security.models import Session
from security.settings import SESSION_SECONDS


class SessionService:
    """Session expiry and revocation are independent of login failure counts."""

    def issue(self, username: str, now: int) -> Session:
        return Session(username=username, expires_at=now + SESSION_SECONDS)

    def valid(self, session: Session, now: int) -> bool:
        return not session.revoked and now < session.expires_at

    def revoke(self, session: Session) -> None:
        session.revoked = True
