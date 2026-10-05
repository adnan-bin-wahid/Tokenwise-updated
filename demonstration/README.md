# TokenWise Demonstration Repositories

Start with [the complete teacher presentation guide](../demonstation.md).

Open one leaf folder at a time in Antigravity:

| Project | Focus | Tests |
| --- | --- | --- |
| [01_account_security](01_account_security/README.md) | Lockout and session boundaries | 8 |
| [02_checkout_delivery](02_checkout_delivery/README.md) | Coupon expiry, pricing, inventory | 8 |
| [03_issue_tracker](03_issue_tracker/README.md) | Permissions, transitions, audit | 6 |
| [baseline_lab](baseline_lab/README.md) | Source-empty fresh-chat comparison | None |

Run `py -3.12 demonstration/run_checks.py` from the checkout root to check all
projects without installing application dependencies. The local 0.6.2 extension
adds **TokenWise: Compare Context Strategies**; it needs the matching backend.
Use [the results worksheet](results-template.md) for actual observations.
See [the local verification record](VERIFICATION.md) for measured packet sizes
and the limits of the automated checks.

Do not enable TokenWise in `baseline_lab`, and do not open this parent folder
as the workspace during a single-project retrieval experiment. Generated
packets and metrics under `results/` are ignored by Git. No committed table
pretends that source-marker checks are cloud-agent answer-quality scores.
