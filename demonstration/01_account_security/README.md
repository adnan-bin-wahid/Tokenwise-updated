# Account Security

A deterministic, in-memory teaching application. Failed logins cause a timed
lockout; sessions expire independently. This is not a production identity system.
The report module is an unrelated working feature, not padding.

From this folder:

```powershell
py -3.12 app.py
py -3.12 -m unittest discover -s tests -v
```

Open this folder itself in Antigravity and enable TokenWise. For the controlled
manual baseline, open `security/auth_service.py` without selecting text.

Task: Explain account lockout after failed login attempts, the expiry boundary,
and its related tests. Do not modify any files.

The settings, implementation, and tests are deliberately in different files.
See the parent demonstration guide for the complete comparison protocol.
