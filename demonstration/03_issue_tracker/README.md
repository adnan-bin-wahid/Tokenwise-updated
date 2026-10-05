# Issue Tracker

An in-memory role-based issue workflow. Maintainers can close and reopen issues;
viewers cannot. State transitions write an audit event. Dashboard reporting is
a separate feature. There is no network, database, or shared cross-project state.

```powershell
py -3.12 app.py
py -3.12 -m unittest discover -s tests -v
```

Open this folder itself in Antigravity. Use `tracker/issue_service.py` as the
manual baseline. Task: Explain who can close and reopen an issue, the state
changes, audit events, and related permission tests. Do not modify any files.

Follow up in the same chat: Which tests cover that behavior? Do not modify files.
Then switch topic explicitly: Explain dashboard status counts and their tests.
