# Publish a GitHub Release

Normal users download the VSIX from GitHub Releases. GitHub Pages and a hosted
Python server are not required. This workflow publishes a Windows-tested beta;
macOS/Linux need native testing before advertising verified support.

## Prepare

Update `vscode-extension/package.json` and its lockfile together when changing
versions. Keep download links, the changelog, and `docs/release-notes/vVERSION.md`
consistent with that version. Run the tests and build:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location).Path 'swe-pruner\swe-pruner\src')
.\.venv\Scripts\python.exe -m unittest discover -s swe-pruner/swe-pruner/tests -v
cd vscode-extension
npm test
npm run package
cd ..
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/publish-github-release.ps1 -PrepareOnly
```

Preparation verifies the allowlisted release files and their checksums and
creates `releases/TokenWise-VERSION.zip`. The ZIP contains the installer and
guides and tracked demonstration projects, not model weights, virtual environments, private runtime records, or
research data. The publishing script also generates checksums for the VSIX/ZIP.

## Commit, Tag, and Push

Review and commit only the intended source/documentation changes. Generated
artifacts are ignored and uploaded as release assets, not committed to Git.
Push without force and create an annotated version tag on the release commit:

```powershell
git push origin main
git tag -a v0.6.2 -m "TokenWise 0.6.2 - Windows Beta"
git push origin v0.6.2
```

Use the new version instead of `v0.6.2` for future releases. Never move a
published tag or replace a published installer; release a new version instead.

## Publish

The Windows publishing helper uses the existing Git Credential Manager login
in memory for GitHub's API. It never prints credentials or writes them to a file.
Sign in through your normal GitHub/Git Credential Manager workflow first if
authentication is missing. Do not put tokens in the repository or chat.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/publish-github-release.ps1
```

The helper requires a clean `main` branch with its exact commit and annotated
tag already pushed. It creates a draft, uploads the VSIX, installer/demo/docs ZIP,
and `SHA256SUMS.txt`, checks the GitHub asset sizes/digests, and then publishes a
pre-release. It refuses to replace an existing published release or alter an
unrelated draft. If an upload was interrupted, inspect the draft and re-run with
`-ResumeDraft` to resume this version's matching draft.

Demo archive paths are derived from Git's tracked `demonstration/` inventory,
restricted to Python/JSON/Markdown without private runtime/results folders, and
must match the package-generated checksum manifest. Unexpected release files,
missing demo files, and symbolic links are rejected before any upload.

After publication, download the public assets and verify their SHA-256 hashes.
Share the tag's release URL, not `/releases/latest`: GitHub pre-releases are not
the latest stable release. The official workflow is documented at
[GitHub release management](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

Publishing to Open VSX/Visual Studio Marketplace is a separate operation and
requires the relevant publisher account and editor compatibility checks.
