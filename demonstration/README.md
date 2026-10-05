# TokenWise Demonstration Repositories

Start with [the complete teacher presentation guide](../demonstation.md).

Open one leaf folder at a time in Antigravity:

| Project | Focus | Tests |
| --- | --- | --- |
| [01_account_security](01_account_security/README.md) | Lockout and session boundaries | 8 |
| [02_checkout_delivery](02_checkout_delivery/README.md) | Coupon expiry, pricing, inventory | 8 |
| [03_issue_tracker](03_issue_tracker/README.md) | Permissions, transitions, audit | 6 |
| [04_pruning_inputs](04_pruning_inputs/README.md) | Session logic versus unrelated invoice/shipping source | 6 |
| [baseline_lab](baseline_lab/README.md) | Source-empty fresh-chat comparison | None |

Run `py -3.12 demonstration/run_checks.py` from the checkout root to check all
projects without installing application dependencies: four apps and 28 tests.
Start with `04_pruning_inputs` and the local **0.6.3** build's **TokenWise:
Demonstrate Pruning Inputs** to inspect repository discovery, exact selected-source
neural pruning, and a clearly labeled user-history replay. Install its matching
backend too. The published 0.6.2 release is unchanged and lacks this new command.
Its **Compare Context Strategies** command remains an optional packet comparison,
not the primary demonstration of how pruning decisions are made.
Use [the results worksheet](results-template.md) for actual observations.
See [the verification record](VERIFICATION.md) for dated checks and their limits.

Do not enable TokenWise in `baseline_lab`, and do not open this parent folder
as the workspace during a single-project retrieval experiment. Generated
packets and metrics under `results/` are ignored by Git. No committed table
pretends that source-marker checks are cloud-agent answer-quality scores.
