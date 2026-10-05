"""Small session and billing workflows; unrelated units share one pruning input."""

from security.models import Session
from security.settings import SESSION_SECONDS


def issue_session(username: str, now: int) -> Session:
    if not username:
        raise ValueError("Username is required")
    return Session(username, now + SESSION_SECONDS)


def session_is_valid(session: Session, now: int) -> bool:
    return not session.revoked and now < session.expires_at


def revoke_session(session: Session) -> None:
    session.revoked = True


def invoice_total(subtotal_cents: int, tax_percent: int, shipping_cents: int) -> int:
    if subtotal_cents < 0 or shipping_cents < 0 or not 0 <= tax_percent <= 100:
        raise ValueError("Invalid invoice amounts")
    tax_cents = (subtotal_cents * tax_percent + 50) // 100
    return subtotal_cents + tax_cents + shipping_cents


def shipping_days(zone: str, express: bool = False) -> int:
    normal_days = {"local": 2, "regional": 4, "international": 10}
    if zone not in normal_days:
        raise ValueError("Unknown shipping zone")
    return 1 if express else normal_days[zone]
