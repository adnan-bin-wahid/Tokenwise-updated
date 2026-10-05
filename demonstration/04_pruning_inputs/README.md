# Mixed-Topic Pruning Inputs

Open this leaf folder in Antigravity. `workflows.py` deliberately contains two
small, real areas: session expiry/revocation and invoice/shipping calculations.
This makes a task-dependent line mask easier to inspect than a file where every
line belongs to the requested behavior. It is a teaching fixture, not production
authentication or financial software.

Run `py -3.12 -m unittest discover -s tests -v` and `py -3.12 app.py`.

Use **TokenWise: Demonstrate Pruning Inputs** from the local 0.6.3 build:

- Repository mode: no file selection or active-file hint is sent.
- Selected mode: open `workflows.py`, clear the selection for the entire file,
  or highlight `session_is_valid` for an excerpt-only request.
- Conversation replay: supply an earlier user task, then a referring follow-up.
  It is a reproducible replay, not automatic capture of an Antigravity chat.

Task: `Explain session expiry and revocation, not invoice pricing.` Try thresholds
0.45 and 0.85 on the same captured source. Inspect real line scores/masks; do not
assume a particular line disappears or that higher compression is more correct.
See [the teacher guide](../../demonstation.md) for actual-chat follow-up testing.
