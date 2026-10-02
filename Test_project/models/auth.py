from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

@dataclass
class UserAccount:
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: List[str] = field(default_factory=lambda: ["user"])
    is_active: bool = True
    failed_login_attempts: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class AuthSession:
    session_id: str
    user_id: str
    token: str
    created_at: float
    is_revoked: bool = False
