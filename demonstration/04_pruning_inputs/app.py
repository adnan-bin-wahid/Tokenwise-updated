from workflows import invoice_total, issue_session, revoke_session, session_is_valid, shipping_days


def main() -> None:
    session = issue_session("student", 100)
    print("Session expires at:", session.expires_at)
    print("Valid before expiry:", session_is_valid(session, 399))
    print("Valid at expiry:", session_is_valid(session, 400))
    revoke_session(session)
    print("Revoked session valid:", session_is_valid(session, 101))
    print("Invoice total cents:", invoice_total(10000, 15, 500))
    print("Regional shipping days:", shipping_days("regional"))


if __name__ == "__main__":
    main()
