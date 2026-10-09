# TokenWise: Classroom Demonstration

Use TokenWise **0.6.8** and the single **`demonstration/tokenwise_demo`** folder.
Run commands through **Ctrl+Shift+P**. All commands below start with **TokenWise:**.

## 1. Prepare Before Class

1. Install the 0.6.8 VSIX and reload Antigravity.
2. Open `demonstration/tokenwise_demo`, not the whole TokenWise checkout.
3. Run **Set Up Backend**, **Enable Automatic Context**, then **Start Backend**. Re-enable after upgrading to refresh the rule/launcher.
4. Run **Diagnose Setup**. Resolve setup errors before presenting; use **Retry Failed Step** if offered.
5. In the demo folder's terminal, run:

```powershell
py -3.12 app.py
py -3.12 -m unittest discover -s tests -v
```

Show: the application runs and **20 tests pass**.

Save copies of `.agents/tokenwise.json` and `.agents/rules/tokenwise.md` outside
`.agents`. Restore them after temporary demonstrations. Keep the same model,
effort, permissions and saved source for both comparison conditions.

## 2. Explain the Project

Say:

> TokenWise finds relevant Python code and tests for my prompt, prunes unnecessary
> context, and prepares a bounded packet for Antigravity. It does not edit source.

Process: **Prompt -> repository index -> retrieval -> pruning -> budgeted context -> Antigravity answer.**

## 3. WITHOUT TokenWise

Yes: use the same prompt with `enabled: false` and `enabled: true`.
Changing that value alone does not deactivate the workspace rule.

1. Run **Configure Automatic Comparison** and disable automatic packet comparison for this timed pair.
2. In `.agents/tokenwise.json`, change only the existing `enabled` value to **`false`**. Save.
3. In **Agent Settings > Customizations > Rules**, set only the TokenWise rule to **Manual**. Do not invoke it. Check that no duplicate TokenWise rule remains active.
4. Close the old TokenWise result panel. Close source editors, clear selections, and attach no files manually.
5. Start a **new Antigravity chat**. Start timing and send:

```text
Explain account lockout after failed login attempts and its related tests.
Do not modify any files. Cite relevant files and test names.
```

6. Save the final answer, visible tool/file-read trace and total answer time.
7. Confirm **no fresh TokenWise retrieval or injected packet**. An old `latest.json` is not new activity.

**Antigravity may still read files using its own tools. That is the correct baseline.**
If TokenWise is invoked, fix the controls and repeat in another new chat.

## 4. WITH TokenWise

1. Set the existing `enabled` value back to **`true`**. Save.
2. Restore the TokenWise rule's original activation, normally **Always On**.
3. Keep the same model, effort, permissions, source and editor state.
4. Start another **new chat**. Start timing and send the **exact prompt from Section 3**.
5. Show the current TokenWise retrieval/tool output and the final answer.
6. Run **Show Automatic Context**. Check the current task, timestamp, new event ID and included files; do not present a verification fixture as live activity.
7. Save the answer and trace. Record total answer time and TokenWise preparation time separately.

Show the actual excerpts supplied, including relevant implementation, settings
and tests when retained. Check the answer against the original files.

## 5. Validate and Compare the Answers

Ground truth: `security/auth_service.py`, `security/settings.py`, `security/models.py`, `tests/test_auth.py`.

| Check | Correct behavior |
| --- | --- |
| Threshold | Three failed attempts |
| Duration | Sixty seconds from the triggering failure |
| Before expiry | Even a correct password is rejected |
| Exact expiry | Lockout resets; a correct password succeeds |
| Test evidence | Real tests such as `test_lockout_threshold`, `test_correct_password_rejected_during_lockout`, `test_expiry_boundary` |

For a precise boundary check, send this same question in a fresh chat under each condition:

```text
Three wrong attempts happen at time 100. What happens with the correct password
at 159 and 160, and a wrong password at expiry? Cite tests. Do not modify files.
```

Correct: rejected at **159**; succeeds at **160** with both counters cleared;
a wrong password at expiry returns false, starts failure count **1**, and clears the old deadline.

| Record | WITHOUT | WITH |
| --- | --- | --- |
| Correct supported facts | Fill after the run | Fill after the run |
| Missing or incorrect claims | Fill after the run | Fill after the run |
| Observed tool/file-read calls | Fill after the run | Fill after the run |
| Total answer time | Fill after the run | Fill after the run |
| Actual reported input tokens | Value or N/A | Value or N/A |

Repeat the same pair three times, alternating order. Use new chats every time.
For the formal three-task, eighteen-run pilot, follow [validation.md](validation.md)
and fill [the results worksheet](demonstration/results-template.md).

**Both answers may be correct. Report the observed difference; do not force the baseline to fail.**

## 6. Show Automatic Token Comparison

1. Keep TokenWise enabled. Run **Configure Automatic Comparison** -> **Enable automatic packet comparison**.
2. Start a new chat and send the Section 3 prompt without selecting or attaching code.
3. Run **Show Automatic Context**. Wait for the comparison to finish.
4. Show **All-Python baseline**, **TokenWise packet**, token change, both file lists and **Export Comparison**.
5. Save the export. Disable comparison before further timed workflow trials.

Say: **These are complete local context-packet counts, not actual Antigravity IDE usage.**
The all-Python baseline assumes every indexed Python file is supplied; native
Antigravity does not necessarily do that. Small projects can show an increase.

## 7. Show Repository Pruning: No Selection

1. Run **Demonstrate Pruning Inputs** -> **Repository: no selected file**.
2. Enter `Explain session expiry and revocation, not invoice pricing.`
3. Enter threshold **`0.45`**.
4. Show the input mode, effective objective, excluded topics, included files,
   pruning methods, applied thresholds and final context. Inspect any missing evidence.
5. Use **Export Pruning Run**.

Say: **The repository is available for discovery; only retrieved and retained context is packed. Not all code is sent.**
This teaching command prepares context; it does not automatically send it into chat.

Then send this in an actual new chat to demonstrate the overview route:

```text
Give me the full overview of this project. Do not modify any files.
```

Show **Repository overview** and the actual coverage/warnings, rather than only a tiny initializer file.

## 8. Show Selected File and Selected Excerpt

| Run | What to do | What to show |
| --- | --- | --- |
| Entire file | Open `security/models.py`, clear highlights; **Demonstrate Pruning Inputs** -> **Selected file or highlighted excerpt**; task `Explain the Session class.`; threshold `0.45` | **Selected entire file**, Original, line scores/mask and Pruned context |
| Excerpt | Highlight the Session `@dataclass` and class body; repeat the same command/task/threshold | **Selected excerpt**, original starting line and exact captured input |

Session fields: `username`, `expires_at`, `revoked = False`.
Check whether necessary lines, including the decorator, survive; do not claim completeness from reduction alone.

Say: **In excerpt mode, unselected Account code was never input. Its absence is not evidence of pruning.**

Regular shortcuts: **Prune Current File** always uses the whole file;
**Prune Selected Code** uses only the highlight.

## 9. Show the Threshold Effect

1. Open `workflows.py` and clear highlights.
2. Use selected-file mode with `Explain session expiry and revocation, not invoice pricing.`
3. Run at **`0.45`**, then **`0.85`**, without changing the task or source.
4. Compare actual masks, final excerpts, token counts and missing facts. Export both runs.

Say: **Threshold changes initial line selection. Higher reduction does not guarantee a better answer.**

## 10. Show Conversation Context

In one actual new Antigravity chat, send these in order:

```text
Explain account lockout after failed login attempts and its related tests.
Do not modify any files.
```

```text
What about its expiry boundary? Do not modify any files.
```

```text
Which tests cover that behavior? Do not modify any files.
```

Show fresh retrieval output and effective objectives. Expand **Conversation
memory**: show selected earlier messages, reasons, omitted count and outgoing
reference status. Confirm the subject remains account lockout, not session expiry.
Native hooks use verified same-chat user turns; fallback labels its references
**Agent-supplied earlier user turns (not native capture)**.

Also try `Use bullet points.` followed by `Explain account lockout boundary tests.`
in that same chat. Show the earlier topic and still-active formatting requirement.
Memory selects at most eight earlier user turns and 4000 characters, not every message.
To demonstrate opt-out, set `.agents/tokenwise.json` `conversation_memory` to
`false`, send a fresh same-topic request, and inspect the disabled memory trace.
Restore `true` afterwards. Keep this separate from the with/without baseline.

For an inspectable controlled replay, run **Demonstrate Pruning Inputs** ->
**Conversation: replay earlier user context**. Enter the first lockout task as
earlier context, `Which tests cover that behavior?` as current task, and `0.45`.
Show **Earlier user reference** and **Inference objective**. Label it **replay**, not live capture.

New-chat control: send only `Which tests cover that behavior?` in a fresh chat.
Do not carry over the previous chat. Missing subject requires clarification, not invented lockout history.

## 11. Show Prompt Engineering

1. Keep automatic context enabled. Set the existing `.agents/tokenwise.json` key `response_guidance` to **`true`**.
2. In a new chat, send `Explain session expiry and revocation and identify the related tests. Do not modify any files.`
3. Show the **Response guidance** block and its applied profile: grounding, citations, constraints and missing-evidence handling.
4. Set `response_guidance` to **`false`**, repeat in a fresh chat, and show the disabled trace. Restore **`true`**.

This demonstrates instruction delivery, not proven answer-quality improvement.
If the block says `omitted_budget`, increase the available budget before rehearsing.

## 12. Explain Tokens and CO2

| Value | Meaning |
| --- | --- |
| Original / retained source | Code before and after selection |
| Packed tokens | Complete supplied packet, including formatting and guidance |
| Reduction / increase | Actual change for the stated baseline |
| CO2 before / after | Predictions under the configured model, output and hardware assumptions |
| Energy / CO2 saved | Estimated difference, not measured emissions |

Show the carbon section once estimates finish. Output processing can stay fixed,
so token reduction and CO2 reduction need not match. Missing estimates are unavailable, not zero.

Optional: **Compare Context Strategies** from a saved Python file shows three
packets: all indexed Python, the unpruned selected file/excerpt, and TokenWise context.

Optional: with two real independent successful CLI logs, run **Import Antigravity
Usage Comparison**, choose **WITHOUT** first and **WITH** second, and show reported
counters/answers/tools. This does not import private IDE chat usage. For capture
steps, see [the CLI procedure](demonstation.md#b-actual-reported-antigravity-usage).

## 13. Show Budget and Freshness

1. Record **Settings > TokenWise > Repository Token Budget**. Set it temporarily to **`512`**.
2. Repeat Section 7. Show packed tokens within the budget and any omissions. Restore the original budget.
3. Show **Output > TokenWise Index**. Repeat an identical task and record warm/cache behavior.
4. Separately, change `SESSION_SECONDS = 300` to `301` in `security/settings.py`. Save and wait for the index update.
5. Run repository mode with `Explain SESSION_SECONDS session expiry.` Show current saved evidence containing **`301`**.
6. Restore **`300`**, save, and rerun all twenty tests before further comparisons.

Teaching commands use the editor budget setting. Automatic chat retrieval uses
the separate `token_budget` in `.agents/tokenwise.json`.

## 14. Finish

Save answers, traces, exported runs and comparison tables. Restore original settings/source.
Use **Check Backend Health** or **Diagnose Setup** for failures; update the matching backend if comparison is unavailable.

Only after the presentation, demonstrate **Remove All Local Data** if requested;
it removes owned setup data and can require reinstalling the backend. Uninstall
cleanup can need an IDE restart. Customized files, Python and editor history are not guaranteed to disappear.

Close with:

> I demonstrated automatic retrieval, scoped pruning, conversation-aware context,
> bounded packets, prompt guidance and inspectable comparisons. My reported results
> separate functional validation, answer quality, packet counts and estimated CO2.
