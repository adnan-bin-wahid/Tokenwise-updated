# Changelog

## 0.4.0 - 2026-10-04

First public Windows-tested beta for Antigravity users.

### Added

- Managed local backend installation from the VSIX, without a source checkout,
  Node.js, Git, F5, or a manually started server.
- Consent-based CPU dependency and model downloads, pinned model checksums,
  download progress, resumable model transfers, cancellation, and retry.
- Automatic context setup for arbitrary local Python repositories, with one
  centrally managed backend shared across workspaces.
- Setup diagnostics, backend warm-up, a bundled guide, and first-run onboarding.
- Portable macOS/Linux launchers; native platform validation is still pending.
- Shareable release artifacts, SHA-256 checksums, and draft-first publishing.

### Fixed

- Local Antigravity `vscode-userdata` storage is no longer mistaken for a remote
  workspace.
- Portable Python launchers correctly handle Windows paths containing spaces.
- Python launcher resolution uses the real executable for owned setup-process
  cancellation and installation-lock cleanup.
- Existing unrelated rules, hook handlers, and context settings are preserved.

### Validation and Limits

- 51 Node tests and 36 Python tests cover setup, retrieval integration, downloads,
  configuration preservation, cancellation, and failure handling.
- A fresh managed environment, CPU cold start, and bounded retrieval from two
  repositories outside the checkout were tested on Windows.
- The fresh install reused checksum-verified local weights. A real HTTPS range
  request was verified; a full 1.35 GB network download was not re-run.
- Stable Antigravity uses an agent rule/tool-output fallback, not guaranteed
  interception before the first model call.
- Remote/virtual workspaces are unsupported. Carbon values remain estimates,
  not measurements of a user's cloud-model consumption.
