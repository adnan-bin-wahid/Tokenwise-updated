# Twenty-Repository Comparative Demonstration

Twenty real public Python projects, pinned to the same commits as TokenWise's
existing component study. These are attributed upstream source snapshots, not
projects authored by the TokenWise student. They contain source, tests, project
metadata, documentation and original licenses from the archived repositories.
Nonregular archive entries, if any, are listed in `manifest.json`.

## Open After Cloning

The twenty numbered projects are included in this repository. After cloning,
open one project directly in Antigravity, for example
`demonstration/comparative_study/01_click`. Initial preparation is not required.
Keep the original licenses in each snapshot. These are public upstream projects,
not original TokenWise application code, and their licenses continue to apply.

The local `.gitattributes` preserves snapshot bytes across Git checkouts so that
recorded fingerprints and intentionally unusual test line endings remain valid.
Captured answers, local credentials, runtime files and generated TokenWise
workspace integration are not part of the published corpus.

## Verify, Rebuild Or Retry

From the TokenWise checkout root:

```powershell
python scripts/prepare_comparative_repositories.py
```

Preparation verifies existing files or rebuilds missing files from the pinned
study archives. It uses cached archives when available. On another machine,
download the required archives explicitly to verify or rebuild the source:

```powershell
python scripts/prepare_comparative_repositories.py --download
```

SHA-256 checks enforce the recorded archive pins. Retry verifies existing source
and creates missing files only. Changed upstream files are preserved and reported
as errors; restore them yourself or choose a clean checkout before retrying.
Python 3.12 or newer is required by the preparation script. No additional Python
packages are needed. The script never installs or executes upstream project code.

## Run One Pair

1. Open one numbered folder in Antigravity, for example `01_click`. Do not open
   `comparative_study` or the TokenWise parent as the study workspace.
2. Review source and workspace instructions before granting trust. Upstream code
   and automation are third-party material; installation and test execution are
   not necessary for a read-only context comparison.
3. Set up TokenWise for this folder with **TokenWise: Enable Automatic Context**.
   Keep automatic packet comparison off during timed answer trials.
4. Find this folder's exact prompt in the parent `TASKS.md`. Do not attach the
   task sheet, manifest, worksheet, previous results or handpicked source files.
5. WITHOUT: set `.agents/tokenwise.json` `enabled` to `false`, set only the
   TokenWise rule to Manual without invoking it, and start a fresh chat. Leave
   native repository reading available. Reject a clean-baseline trial if a
   TokenWise invocation occurs.
6. WITH: restore `enabled` to `true` and the rule's original activation. Start
   another fresh chat and send the identical prompt. Check fresh TokenWise tool
   output and current activity, not a saved panel alone.
7. Keep model, effort, permissions, source and editor state identical. Time from
   prompt submission to complete final answer, including retrieval overhead.
8. Score against a source-grounded checklist prepared before reading either
   answer. Save answers and observed traces outside the opened project.
9. Repeat three pairs, alternating order. `results-template.csv` provides all
   120 planned runs across twenty projects. Every row initially says `not_run`.
   Save your completed copy under the ignored parent `results/` folder.

Use `../../validation.md` for scoring and fair controls. Actual provider usage
stays N/A unless genuinely reported. Local packet tokens and observed file reads
are different measurements, not proof of native Antigravity billed usage.

## Scope And Evidence

The numbered folders are source snapshots, not nested Git clones: upstream `.git`
history is not included. `manifest.json` records each origin, ref, complete commit,
archive checksum, file totals, target symbol and regular-file fingerprint.
Original source is not modified to insert study tasks or answers.

The previous local study extracted Python files and selected root metadata.
These new folders extract all regular upstream files, so documentation and other
retrieval inputs can differ. New native trials must be reported as a separate
experiment; they do not retroactively replace the recorded study corpus/results.

No live WITH/WITHOUT trials, upstream tests or answer-quality evaluation are
performed merely by preparing these folders. Do not claim that all projects are
runnable without their own dependencies and platform requirements.

Upstream snapshots are published for direct classroom use, with their original
licenses and attribution in `manifest.json`. They are evaluation fixtures, not
extension runtime dependencies. Captured outputs under `results/`, generated
`.agents` integration, `.tokenwise` activity and private local environment files
remain Git-ignored. Original public upstream test fixtures that happen to match
an ignore pattern are included only after verification against their pinned
archives; this does not authorize publishing new local secrets.

The preparation script and its tests are included. See `LIVE_STUDY.md` for the
native WITH/WITHOUT protocol and `PREFLIGHT.md` for current execution status.
Publishing the source folders does not complete the planned 120 agent runs.
