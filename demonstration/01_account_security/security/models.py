from dataclasses import dataclass
from hashlib import sha256


def password_digest(password: str) -> str:
    """Teaching fixture only: real passwords require a salted password KDF."""
    return sha256(password.encode("utf-8")).hexdigest()


@dataclass
class Account:
    username: str
    digest: str
    failed_attempts: int = 0
    locked_until: int = 0


@dataclass
class Session:
    username: str
    expires_at: int
    revoked: bool = False
