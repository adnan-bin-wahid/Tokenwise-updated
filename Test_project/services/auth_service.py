import time
import uuid

from models.auth import AuthSession, UserAccount
from utils.crypto import generate_jwt_token, hash_password, verify_jwt_token
from utils.logger import log_audit, log_error, log_info


class AuthService:
    """Authentication and session-management service used by the TokenWise demo."""

    def __init__(self):
        self._users: dict[str, UserAccount] = {}
        self._sessions: dict[str, AuthSession] = {}
        self._initialize_demo_users()

    def _initialize_demo_users(self) -> None:
        admin = UserAccount(
            user_id='usr_admin_01',
            username='admin',
            email='admin@enterprise.com',
            password_hash=hash_password('adminSecret123'),
            roles=['admin', 'user'],
        )
        self._users[admin.username] = admin

    def authenticate_user(self, username: str, password_raw: str) -> str | None:
        """Authenticate a user, lock repeated failures, and create a session token."""
        user = self._users.get(username)
        if not user:
            log_audit(username, 'login', 'FAILED_USER_NOT_FOUND')
            return None

        if not user.is_active:
            log_audit(user.user_id, 'login', 'FAILED_USER_INACTIVE')
            return None

        if user.password_hash != hash_password(password_raw):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.is_active = False
                log_error(f'User {username} account locked due to excessive failed attempts')
            log_audit(user.user_id, 'login', 'FAILED_INVALID_PASSWORD')
            return None

        user.failed_login_attempts = 0
        token = generate_jwt_token({
            'user_id': user.user_id,
            'username': user.username,
            'roles': user.roles,
        })
        session_id = f'sess_{uuid.uuid4().hex[:8]}'
        self._sessions[session_id] = AuthSession(
            session_id=session_id,
            user_id=user.user_id,
            token=token,
            created_at=time.time(),
        )
        log_info(f'User {username} logged in successfully. Session ID: {session_id}')
        log_audit(user.user_id, 'login', 'SUCCESS')
        return token

    def validate_session(self, token: str) -> dict | None:
        payload = verify_jwt_token(token)
        if not payload:
            return None
        if not any(session.token == token and not session.is_revoked for session in self._sessions.values()):
            return None
        return payload

    def revoke_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.is_revoked = True
        log_audit(session.user_id, 'logout', 'SUCCESS')
        return True
