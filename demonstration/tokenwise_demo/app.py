from reports import activity_summary
from security.auth_service import AuthService
from security.models import Account, password_digest
from workflows import invoice_total, issue_session, revoke_session, session_is_valid, shipping_days


def main() -> None:
    account = Account("student", password_digest("demo-pass"))
    auth = AuthService()
    for _ in range(3):
        auth.authenticate(account, "wrong", 100)
    deadline = account.locked_until
    print("Locked until:", deadline)
    print("Login before expiry:", auth.authenticate(account, "demo-pass", deadline - 1))
    print("Login at expiry:", auth.authenticate(account, "demo-pass", deadline))
    session = issue_session(account.username, 100)
    print("Session expiry:", session.expires_at)
    print("Session at 399:", session_is_valid(session, 399))
    print("Session at 400:", session_is_valid(session, 400))
    revoke_session(session)
    print("Revoked session at 101:", session_is_valid(session, 101))
    print("Invoice total:", invoice_total(10000, 15, 500))
    print("Shipping days:", shipping_days("regional"))
    print("Activity:", activity_summary([
        {"actor": "student", "action": "login"},
        {"actor": "student", "action": "invoice"},
    ]))


if __name__ == "__main__":
    main()
