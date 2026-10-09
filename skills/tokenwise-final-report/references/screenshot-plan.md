# Red Screenshot Instructions

The user wants instructions telling them what screenshots to add, not images.
Select placements useful to the report; do not add a screenshot after every
paragraph. All instructions must remain visible and understandable without color.

## Representation

For Markdown report output use:

```html
<span style="color: #ff0000;">ADD SCREENSHOT - Figure N: After sending the account-lockout prompt, capture the TokenWise Repository Context panel with the exact task, current event, included files, packed tokens and budget visible. Caption: Fresh automatic repository context for the account-lockout task. Label this live or recorded according to its actual origin.</span>
```

In final content replace `N` with the report's sequential figure number. For DOCX
use a normal readable paragraph with run color `FF0000`, not raw HTML. If color
is not supported by the target format, retain `ADD SCREENSHOT` and disclose the
plain-text limitation. The instruction is a future insertion request, not a
claim the image has already been captured.

Describe diagrams separately as `ADD DIAGRAM`; architecture drawings are not
screenshots. Do not invent measured charts. Existing study figure data can be
described and linked, but do not embed images while the user requests placeholders.

## Placement Catalog

| Location | Screenshot to request | Required visible evidence and caption subject |
|---|---|---|
| Interface / installation | Extensions view after VSIX installation | TokenWise name, actual installed version and icon; installed extension |
| Manual / backend setup | Managed setup progress or completion | Current setup step and status, no private paths/keys where avoidable; managed backend setup |
| Manual / recovery | Genuine failed step with supported retry action, if available | Actual error and Retry Failed Step control; recoverable installation. Do not stage an artificial failure as a real observed defect |
| Manual / readiness | Diagnose Setup / health output | Reachable backend and applicable environment/version; backend readiness |
| Interface / workspace | Single demo folder open with status bar | `demonstration/tokenwise_demo` contents and TokenWise automatic status; configured Python workspace |
| Manual / ordinary prompt | Fresh Antigravity task with TokenWise invocation | Exact read-only lockout question and real retrieval tool output; automatic workflow without selected files |
| Interface / repository result | Repository Context result panel | Task, input mode, file list, relation/tier, source/packed accounting and full-packet budget; bounded repository context |
| Interface / selected source | Real selected-file or excerpt pruning result | Correct input scope, threshold, original/pruned context and line decisions; inspectable neural pruning |
| Interface / prompt guidance | Outgoing context showing response guidance | Actual bounded guidance and source-reference separation; task-aware outgoing prompting. Do not claim the screenshot proves better answers |
| Interface / conversation memory | Follow-up result and expanded memory inspector | Current follow-up, selected earlier user turns, reasons and outgoing status; bounded user-reference continuity |
| Interface / carbon | Carbon comparison region | Before/after, prefill/decode, units, model/intensity assumptions, estimate disclaimer; configured carbon estimates |
| Interface / automatic comparison | Prepared packet comparison | Both labeled all-Python and TokenWise packets/file lists, local token counts and signed difference; hypothetical packet comparison |
| Interface / actual usage import | Imported independent successful CLI pair, only if logs exist | Reported model/session identity, actual counters, tool observations; reported agent usage. If absent, mark optional/unperformed instead of fabricating a view |
| Testing | Actual extension/backend test summaries | Passed/discovered/skipped totals and command, aligned with date/version; observed software verification |
| Testing | Actual demo test result | Twenty demo cases and deterministic output, if currently still true; teaching application verification |
| Validation | Live current task/event match | Prompt, current timestamp/event and actual transport output; freshness and successful context delivery |
| Validation | Separate controlled changed-file check | Before/after known saved edit with fresh retrieval, restored afterward; cache freshness. Keep outside paired study trials |
| Native comparison / without | Independent baseline answer and visible tools | Same task/model, TokenWise disabled and no retrieval, factual answer; native Antigravity baseline, not a model deliberately denied tools |
| Native comparison / with | Independent enabled answer and visible tools | Same task/model, actual TokenWise context and factual answer; TokenWise-enabled native workflow |
| Native comparison / scored results | Real completed worksheet or imported comparison | Repeats, fact scores, times, reported usage or N/A, failures; observed paired outcomes, only after trials are completed |
| Local study / results | Recorded twenty-repository results table | Named seven conditions, dataset size and dated totals; component-study results, not live agent accuracy |

A comparison screenshot must identify its baseline, exact task, scope, and
whether its data are local packet counts, provider counters, or estimates.
Do not use a screen saying the agent "read fewer files" as proof of fewer billed
tokens or higher quality. A screenshot is supporting evidence, not the dataset.

## Capture Safety and Consistency

Use only the user's project screens. Never copy the friend's figures, account
details, or screenshots. Redact secrets and unrelated personal information;
keep relevant code paths, models, units, and condition labels inspectable.
Use the same source snapshot and task for paired screenshots, independent fresh
chats for independent trials, and accurate live/recorded/fixture labels. When a
screen does not exist in the current implementation, remove that request rather
than inventing it. Keep captions, figure list entries, and in-text references
consistent after the user supplies images.
