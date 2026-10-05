from security.auth_service import AuthService
from security.models import Account, password_digest
from security.session_service import SessionService
from reports import activity_summary


def main() -> None:
    account = Account("student", password_digest("demo-pass"))
    auth = AuthService()
    for now in range(3):
        auth.authenticate(account, "wrong", now)
    print("Locked until:", account.locked_until)
    print("Login at expiry:", auth.authenticate(account, "demo-pass", account.locked_until))
    session = SessionService().issue(account.username, 100)
    print("Session expiry:", session.expires_at)
    print("Activity:", activity_summary([{"actor": "student", "action": "demo"}]))


if __name__ == "__main__":
    main()
