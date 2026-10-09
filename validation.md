# TokenWise: Validation and With/Without Comparison

This 0.6.8 guide is the practical evidence plan for the project defense. It is a protocol,
not a completed Antigravity comparison or a promise that TokenWise always wins.
Use the single `demonstration/tokenwise_demo` repository throughout.

## Classroom Quick Route

For the shortest classroom script, open [demonstration2.md](demonstration2.md).

Before class install the 0.6.8 VSIX, reload, update through **Set Up Backend**,
and open the ZIP's `demonstration/tokenwise_demo` folder. Run **Enable Automatic
Context** and **Start Backend**. No compilation or F5 is required.

After upgrading, run **Enable Automatic Context** again to refresh the owned
rule/launcher. Version 0.6.8 keeps selected earlier user references visible in
**Conversation memory**. New-chat isolation remains required for paired trials.

For the short demonstration:

1. Run **TokenWise: Open Validation Guide** to keep this script beside the editor.
2. Run **TokenWise: Configure Automatic Comparison**, choose **Enable automatic
   packet comparison**, and ask the exact account-lockout question in Section 6.
3. Show the fresh retrieval, both packet/file lists, token change and **Export
   Comparison**. Explain that this is a local packet comparison, not actual IDE usage.
4. Disable measurement mode through the same command. Show one recorded pair of
   independent native with/without answers using Sections 4-7, or run the pair
   live after preparing the baseline. Score both against the six required facts.
5. Present the worksheet across all pilot runs, not only the best example.
   Missing reported usage stays N/A. If you have CLI logs, **Import Antigravity
   Usage Comparison** shows their reported counters, answers and observed tools.

Practice and collect the repeated trials before class. Label recorded evidence
as recorded; do not pretend two chat answers establish the entire study.

## 1. What the Teacher Is Asking

There are two separate questions:

1. **Validation:** Does the implemented system actually work as specified?
2. **Comparison:** Under the same task and conditions, what changes when
   TokenWise is used rather than not used?

Tests and a context dashboard help answer the first question. Actual independent
agent runs and source-grounded answer scoring are needed for the second. An
all-code packet is not a recording of how native Antigravity behaves without
TokenWise; the native agent may retrieve its own relevant files successfully.

## 2. Evidence Already Available

On October 9, the 0.6.7 release code passed 191 extension tests and 121 backend
tests, with one additional backend test skipped for platform reasons. Those
checks cover contracts such as packet limits, cache invalidation, comparison
snapshots, late-response rejection, exports, and usage-log parsing. They do not
establish better live Antigravity answers or lower cloud token consumption.

The single demonstration was checked again for this guide: its twenty tests and
deterministic application output passed. Repeat it from the checkout root:

```powershell
.\.venv\Scripts\python.exe demonstration/run_checks.py
```

Keep the command output, date, machine, code revision and extension/backend
version with the submitted evidence. The new automatic comparison and usage-log
import features are included in 0.6.7, not changes to public 0.6.6.

## 3. First Validate the Live Integration

Use the account-lockout task in Section 6. Enable automatic context and start a
fresh chat. Do not highlight a file or manually attach repository excerpts.

| Check | Evidence to save | What it establishes |
| --- | --- | --- |
| Prompt reaches retrieval | Current task, tool invocation, timestamp and event ID | This is fresh activity, not an old panel |
| Context is delivered | TokenWise's actual tool output or observed hook injection | Preparation reached the agent workflow |
| Cross-file evidence exists | Configuration, implementation and test excerpts | Relevant facts are available in the packet |
| Budget holds | Packet count and configured local-tokenizer budget | The supplied packet is bounded |
| Answer is grounded | Accurate behavior and real file/test citations | The answer uses verifiable repository evidence |
| No source edits | Saved source diff or file hashes before/after | The read-only task remained read-only |
| Snapshot updates | Save a reversible source edit, retrieve again, then restore it | Changed saved evidence is not served stale |

Do the reversible-edit test as a separate validation run, not during a paired
comparison. Check that the restored source and twenty tests pass before starting
the experiment. A generated transcript or `verification: true` activity is a
test fixture, not proof of a live cloud interaction. A prepared packet alone
does not prove the model consumed it. Answer citations support an operational
claim of grounded use, not a claim about the model's internal reasoning.

## 4. Main Experiment: Native Antigravity With and Without TokenWise

This experiment directly answers the teacher's question. Allow the native agent
the same normal repository tools in both conditions. Do not prevent the baseline
from reading source merely to make it fail.

### A. WITHOUT TokenWise

1. Keep the same saved repository and other project/global customizations.
2. Back up the exact TokenWise workspace rule and `.agents/tokenwise.json` settings.
3. Set only the TokenWise rule's activation to **Manual** and do not mention it
   in chat. Set `enabled` to the JSON boolean `false` in `.agents/tokenwise.json`
   to prevent the TokenWise hook/launcher from supplying context.
4. Start a fresh independent chat. Verify no TokenWise retrieval or injected
   packet occurs. Do not paste a TokenWise packet into this baseline.
5. Send the exact task and common instruction in Section 6. Save the answer,
   visible tool trace, time, and any genuinely reported usage counters.

Antigravity documents explicit manual activation in its
[rules documentation](https://www.antigravity.google/docs/rules/). Interfaces vary
by version: use the rule manager where available. If editing the rule file,
change only its frontmatter activation and preserve its original bytes for
restoration. Do not delete all rules or uninstall/erase the managed backend.
Simply disabling the extension is insufficient if an active workspace rule can
still invoke its launcher. Check for duplicate TokenWise global/legacy rules.
Any TokenWise attempt contaminates the intended clean baseline; record and
repeat it rather than silently retaining that run as a successful baseline.

### B. WITH TokenWise

1. Restore the original TokenWise rule and settings; set `enabled` to `true`.
2. Keep source, model, effort, permissions, other rules and task unchanged.
3. Start another fresh chat, without a manually selected or attached file.
4. Send the same task and common instruction. Verify current retrieval and save
   its output, final answer, tool trace, time and reported usage where available.
5. Record preparation time separately from total time to the complete answer.
   Total time must include TokenWise's retrieval overhead.

Native IDE traces show what you can observe; do not claim they exhaust every
file or model request. The imported Antigravity usage feature currently accepts
CLI logs, not private IDE telemetry. Missing actual usage is **N/A**, not zero,
and cannot be replaced by local packet counts or the agent guessing its usage.

## 5. Control the Experiment

- Fix the repository snapshot, exact question, model, effort and tool permissions.
- Leave all non-TokenWise rules identical. Record automatic response guidance:
  enabled is a complete-system comparison; disabling it in `.agents/tokenwise.json`
  makes a separate retrieval-focused condition. Do not mix these conditions.
- Start a new chat for every independent run. Do not reuse history from the
  previous condition, seed an answer, or coach one agent differently.
- Close the selected editor or keep it identical, clear highlighted selections,
  and attach no files manually in either native-workflow condition.
- Record whether the local backend was cold or warm. For warm studies, warm it
  before timing and disclose that choice; show first-run costs separately.
- Keep automatic packet-comparison study mode off during primary workflow timing.
  It adds measurement work; evaluate its dashboard separately in Section 8.
- Rotate order: repeat 1 without/with, repeat 2 with/without, repeat 3 without/with.
  For a larger study, randomize order with a recorded schedule.
- Record failed and incomplete runs. A timeout is a result, not a reason to
  discard an unfavorable trial. Mark source changes or accidental history/tool
  setup mismatches as invalid; preserve the original record and rerun the pair.

Start with the three tasks below, three repetitions each and two conditions:
**18 independent runs, forming nine matched pairs.** This is a small pilot on one
teaching repository, not evidence of universal behavior across Python projects.

## 6. Fixed Tasks and Ground Truth

Append the same common instruction to every task in both conditions:

```text
Do not modify any files. Explain using repository evidence.
Cite relevant files, functions and test names. If evidence is missing,
say so instead of guessing. Do not estimate your own token usage.
```

### A. Account Lockout

```text
Explain account lockout after failed login attempts. State the threshold
and duration. If three wrong attempts happen at time 100, explain a correct
password at times 159 and 160, and a wrong password at expiry.
Identify the tests verifying the threshold and boundary behavior.
```

Six required items, defined before reading answers:

1. Threshold is three failed attempts.
2. Lockout duration is sixty seconds from the triggering failure.
3. Three failures at 100 produce deadline 160; correct at 159 is rejected.
4. Correct at 160 succeeds and clears both failure count and lockout state.
5. Wrong at expiry returns false, starts count one and clears the old deadline.
6. Cite real `test_lockout_threshold`, `test_expiry_boundary`, and
   `test_wrong_password_after_expiry_starts_a_new_count` evidence.

Ground truth: `security/auth_service.py`, `security/settings.py`,
`security/models.py`, and `tests/test_auth.py`.

### B. Session Expiry and Revocation

```text
Explain session creation, expiry and revocation, not invoice pricing.
State the session duration and what happens for a session issued at 100
when checked at 399 and 400. Explain revocation and an empty username.
Identify the tests verifying expiry and revocation.
```

1. Configured duration is 300 seconds.
2. Issuing at 100 produces `expires_at = 400`.
3. The session is valid at 399 and invalid at the exact deadline 400.
4. Revocation sets `revoked` true and invalidates it even before expiry.
5. An empty username raises `ValueError`.
6. Cite `test_session_expiry_boundary`, `test_revocation`, and
   `test_username_required` with their actual assertions.

Ground truth: `workflows.py`, `security/models.py`, `security/settings.py`,
and `tests/test_workflows.py`. Record unwanted invoice discussion separately.

### C. Invoice Calculation and Validation

```text
Explain invoice_total, its integer rounding and input validation.
Calculate the result for subtotal 10000, tax 15 and shipping 500,
and for subtotal 10, tax 15 and shipping 0. Is a zero invoice allowed?
Identify the tests verifying rounding and invalid inputs.
```

1. First example totals 12000 cents.
2. Tax uses `(subtotal_cents * tax_percent + 50) // 100`, integer half-up rounding.
3. The second example totals 12 cents, not 11 or a floating-point amount.
4. Negative subtotal/shipping and tax outside 0 through 100 raise `ValueError`.
5. The all-zero invoice is allowed and returns zero.
6. Cite `test_invoice_rounds_half_up_in_integer_cents`,
   `test_invoice_tax_and_shipping_are_validated`, and `test_zero_invoice_is_valid`.

Ground truth: `workflows.py` and `tests/test_workflows.py`.

## 7. Score Answers, Not Compression Alone

Award one point per fully correct, supported required item: **coverage / 6**.
Record incorrect/unsupported claims and omissions separately. An honest unknown
gets no coverage point, but is not counted as a hallucination. Extra wording
and length do not earn points. File names alone are not proof of understanding.
Give anonymized answers to the teacher or another reviewer where practical.

For each run save task ID, repetition, order, condition, answer, coverage,
unsupported claims, status, total answer time, TokenWise preparation time when
applicable, observed tool calls, and actual reported token counters if available.
Use [the results worksheet](demonstration/results-template.md).

For paired input-token reduction under the same reported counter:

```text
100 * (without_input_tokens - with_input_tokens) / without_input_tokens
```

An increase is valid evidence too. A zero denominator has no percentage. Keep
provider input/cache/output/thinking/total counters separate; do not add cached
or thinking counters to a total that may already account for them. Report quality,
time and token outcomes together. A context-saving method that loses required
facts or increases total workflow usage has not demonstrated the intended benefit.

Report all pairs, success/failure counts, per-task mean or median and range, and
the number of runs with observable actual usage. Compare token totals only over
matched pairs with the same available metric, and state excluded-pair counts.
Three repeats are exploratory, not a statistically conclusive superiority test.

## 8. Separate Experiment: Supplied Context Efficiency

Use **Configure Automatic Comparison** to export the all-Python and exact
TokenWise packets. This supports the separate question: "How does supplied
context differ under a bounded strategy?" It does not record the native baseline.

For answer comparison, supply each packet and the same task to independent
isolated chats or CLI runs outside the repository, with no automatic rules
injecting more context. Reject or reclassify context-only trials if tools obtain
additional evidence. With CLI telemetry, **Import Antigravity Usage Comparison**
can display reported usage and observed tool parameters; the capture procedure
is in [the demonstration guide](demonstation.md#automatic-comparison-067).
Do not relabel this controlled all-code/pruned CLI study as an IDE workflow study.

Carbon values remain configured inference predictions, not measured Antigravity
emissions. Lower packed tokens alone do not prove lower full-session usage or
net emissions including local pruning. Evaluate prompt guidance separately if
claiming that particular technique improves answers.

## 9. What to Present

Prepare a short evidence pack:

1. One validation slide: dated tests, fresh prompt/tool output, budget and citations.
2. One setup slide: fixed snapshot/model/settings and what without/with means.
3. One results table: all paired quality, time, actual-usage and failure outcomes.
4. One example answer pair, labeled as an illustration rather than the whole study.
5. One limitation slide: small fixture, repetitions, missing IDE telemetry,
   tokenizer differences, and estimated rather than measured CO2.

Only after collecting results, fill in a claim such as:

> On [tasks/repository/model], TokenWise achieved [coverage] versus [baseline
> coverage], with [reported-token change] and [total-time change], across [pairs].
> These are pilot results under the stated conditions, not universal guarantees.

If both answers are equally correct, the contribution may still be fewer observed
retrieval steps, less supplied context, or reduced manual effort. If actual tokens
are unavailable, say so; claim only the measured packet difference. If TokenWise
does not improve a metric, report that honestly and use it to guide development.
