# Development and Source Setup

Normal users should follow the root README and install the VSIX. These commands
are for working on TokenWise itself.

## Windows Backend Checkout

Install 64-bit Python 3.12 and Node.js/npm, then from the checkout root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1 -TorchMode cpu
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/copy-model.ps1 -Source 'C:\path\to\model.safetensors'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Use the official pinned weights linked in the root README or an already verified
local copy. The model is not committed to Git. Do not copy `.venv` between machines.
For an end-user environment, use the extension's managed installer instead.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s swe-pruner/swe-pruner/tests -v
cd vscode-extension
npm test
npm run package
cd ..
```

With the original checkout backend already running:

```powershell
node scripts/verify-portable-context.cjs
.\.venv\Scripts\python.exe scripts/verify_antigravity.py
```

The verifiers do not call Antigravity's cloud model. The portable verifier uses
two temporary repositories outside the checkout and leaves real workspace
activity alone. The original demo verifier marks its activity `verification: true`.

## Shareable Package

`npm run package` prepares an integrity-manifested backend bundle, compiles the
extension, creates the VSIX, and writes the release folder under `releases/`.
Only explicitly selected backend files are bundled; weights, virtual
environments, `.tokenwise` data, developer tests, and research PDFs are excluded.
Generated bundle/release outputs are ignored by Git.

Public registry publishing and native macOS/Linux verification are separate
release gates. This repository does not claim that a local package build publishes
to Open VSX or the Visual Studio Marketplace.
