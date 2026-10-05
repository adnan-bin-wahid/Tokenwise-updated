# TokenWise Demo: Account Security and Billing

A deterministic, in-memory Python teaching application for one complete TokenWise
presentation. It is not a production identity, accounting, or shipping system.

## Run

Open this folder itself in Antigravity. From its terminal:

```powershell
py -3.12 app.py
py -3.12 -m unittest discover -s tests -v
```

Twenty tests verify all features. Application source uses only Python's standard
library. Time is supplied explicitly as integers, so no live clock, sleeping,
network, API key, database, or external application dependency is needed.

## Behavior

- Three failed logins lock the account for 60 seconds. Even a correct password
  fails before the deadline. At the exact deadline the timed lockout resets;
  a correct password succeeds and a wrong password starts a new failure count.
- A successful login before lockout resets accumulated failures.
- Sessions last 300 seconds and are valid only while `now < expires_at` and
  `revoked` is false. Issuing a session without a username is rejected.
- Revoking a session makes it invalid even before its expiry.
- Invoices use integer cents, validate nonnegative subtotal/shipping and tax
  from 0 through 100, and round half a tax cent upward.
- Normal shipping takes 2, 4, or 10 days for local, regional, or international
  zones; express shipping takes 1 day. Unknown zones are rejected.
- Activity reports produce sorted action counts and an actor/action CSV.

`password_digest` uses SHA-256 only for a deterministic fixture. Real password
storage needs a salted password KDF and a complete production security design.

## Source Map

| File | Purpose |
| --- | --- |
| `app.py` | Runs all features and prints repeatable boundary examples |
| `security/models.py` | `Account`, `Session`, and the teaching password digest |
| `security/settings.py` | Lockout threshold/duration and session duration |
| `security/auth_service.py` | Failed-login counter, timed lockout, reset |
| `workflows.py` | Session operations plus independent invoice/shipping functions |
| `reports.py` | Action counts and CSV export |
| `tests/test_auth.py` | Five lockout/reset boundary tests |
| `tests/test_workflows.py` | Ten session, invoice, and shipping tests |
| `tests/test_models.py` | Two model/default and digest tests |
| `tests/test_reports.py` | Three count/CSV tests |

The package initializer is also indexed, making eleven Python files. Several
relevant facts live in different files, while `workflows.py` deliberately puts
unrelated operations in one input for a visible neural-pruning experiment.

## Presentation Prompts

```text
Give me the full overview of my project. Do not modify any files.
```

```text
Explain account lockout after failed login attempts, the expiry boundary,
and its related tests. Do not modify any files.
```

```text
Explain session expiry and revocation, not invoice pricing. Do not modify files.
```

For selected-source pruning, open `security/models.py` and ask
`Explain the Session class.` For the mixed-file comparison, open `workflows.py`
and ask `Explain session expiry and revocation, not invoice pricing.`

Use **TokenWise: Demonstrate Pruning Inputs** to control the scope, or type the
normal repository prompt in a new Antigravity chat after enabling automatic
context. Those are different workflows; a teaching-command panel does not itself
send the context to the agent.

The full step-by-step script, exact expected facts, explanation of CO2 estimates,
and teacher defense questions are in [demonstation.md](../../demonstation.md).
