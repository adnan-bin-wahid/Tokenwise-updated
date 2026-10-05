# TokenWise: Teacher Demonstration and Evaluation Guide

This is the practical presentation guide. Open the independent projects under
`demonstration/` in Antigravity, not the entire TokenWise checkout. The examples
use real Python code, executable tests, configuration dependencies, and unrelated
modules. Nothing here is a prewritten successful AI answer or an invented benchmark.

## 1. What Your Teacher Probably Meant

Your teacher's wording can reasonably mean the following. This is an
interpretation, not confirmation of their exact experimental requirements.

| Phrase | What to demonstrate | Question it answers |
| --- | --- | --- |
| All code as context | Give the assistant all indexed Python source, including tests | How much input is required without retrieval or pruning? |
| Only selected code as context | Give it one manually selected file or excerpt | Is small context sufficient, or does it miss dependencies and tests? |
| Cross conversation as context | Test follow-ups, topic switches, and new conversations | Does context stay relevant without using stale or another chat's task? |
| TokenWise automatic context | Retrieve and pack files from a normal task, without selection | Can automatic context keep useful evidence under a budget? |

Before the defense, ask: "For cross-conversation context, do you mean follow-ups
within one chat, or persistent memory between different chats? I can show
follow-ups and separation between chats. TokenWise does not implement a general
cross-chat memory system."

The main comparison has **three context strategies**: all Python code, manual
selection, and TokenWise automatic retrieval. Conversation behavior is a
**separate experiment**, not a fourth context strategy with identical inputs.

The strongest conclusion is not "the smallest packet wins." It is:
"The packet should retain evidence needed for the task while avoiding unnecessary
input. I evaluate both packet size and answer correctness."

## 2. What Has Been Added

- Three independent, runnable repositories with 22 standard-library tests.
- `TokenWise: Compare Context Strategies`, which prepares three copyable packets
  for the same task and repository snapshot.
- A comparison table with complete packet token counts, source token counts,
  included files, changes relative to all-code, and optional energy/CO2 estimates.
- A JSON export containing the actual packets and measurements.
- Bounded prior-user-topic support for recognized ambiguous native-hook follow-ups.
- Rule instructions to resolve fallback-command follow-ups within the same chat.
- An empty-source baseline workspace and repeatable test/result-export scripts.

These comparison features require the **local 0.6.2 build and updated backend**.
Do not install the public 0.6.1 download and expect the new command to exist.
This guide does not claim that 0.6.2 has been published to GitHub.

## 3. Folder Map

| Folder to open | Subject | Manual baseline file | Tests |
| --- | --- | --- | --- |
| `demonstration/01_account_security` | Login lockout, expiry, reset, sessions | `security/auth_service.py` | 8 |
| `demonstration/02_checkout_delivery` | Coupon expiry, tax, checkout, inventory | `checkout/coupons.py` | 8 |
| `demonstration/03_issue_tracker` | Permissions, issue transitions, audit, dashboard | `tracker/issue_service.py` | 6 |
| `demonstration/baseline_lab` | Fresh-chat, pasted-context answer comparison | No Python source | None |

The projects intentionally distribute the answer across files. A service file
can contain the control flow but omit configuration values and executable tests.
Unrelated real modules give all-code retrieval a meaningful extra cost without
adding fake repeated text merely to manufacture large savings.

These are small teaching projects, not production authentication, payment, or
issue-management products. They use in-memory state and deterministic integer
timestamps. The password digest is an explicitly simplified teaching fixture,
not a production password-storage design. Checkout does not contact a payment
provider. No external database, web server, or API key is needed to run them.

## 4. Install and Rehearse Before Presentation Day

### Normal Installation

1. In Antigravity, use **Extensions > ... > Install from VSIX...**.
2. Select `releases/TokenWise-0.6.2/tokenwise-vscode-0.6.2.vsix` from this checkout.
3. Reload the editor. Verify TokenWise's installed version is 0.6.2.
4. Open `demonstration/01_account_security` with **File > Open Folder**.
5. Trust this repository only after reviewing it.
6. Run **TokenWise: Set Up Backend**. Use the managed installation/update flow.
7. Wait for installation and model verification to finish. First setup needs
   network access, Python 3.12, and sufficient disk space; do it before class.
8. Run **TokenWise: Enable Automatic Context** for this project.
9. Check the TokenWise Output channel for setup errors. Start a new agent chat.
10. Run one rehearsal task and wait for its actual automatic context result.

Repeat **Enable Automatic Context** once in each of the other two project
folders. They share the centrally managed backend; do not independently install
three copies. Do **not** enable automatic context in `baseline_lab`.

On an existing installation, reinstalling the VSIX alone is insufficient if an
older backend is still running. Use **Set Up Backend** to select/install the new
bundled backend. Re-enable the demo workspaces so their generated rules match
the current extension. Existing unrelated rules are preserved. If an owned
generated rule was customized, inspect the setup warning rather than overwriting
your own instructions blindly.

### Development-Host Alternative

If you are testing from source, open `vscode-extension`, run `npm run compile`,
then press F5. In the Extension Development Host open one of the three leaf
project folders. Compilation updates TypeScript; it does not restart an old
Python backend or update an already installed managed backend automatically.
The managed setup flow is still the recommended way to get the matching backend.

For a classroom demonstration, the installed VSIX avoids the extra development
host window. Do not run a second copy of TokenWise alongside it in the same host.

### Run the Example Code

In a terminal at the TokenWise checkout root:

```powershell
py -3.12 demonstration/run_checks.py
```

Expected: 8, 8, and 6 passing tests, with `app.py` passing for every project.
The runner launches each project in a separate Python process so module names
from one example cannot contaminate another example.

Inside any individual project folder:

```powershell
py -3.12 -m unittest discover -s tests -v
py -3.12 app.py
```

On a non-Windows machine use its Python 3.12 interpreter instead. The example
projects are standard-library-only; native extension installation outside
Windows still has the platform limitations documented in the root README.

## 5. Experiment A: Normal Automatic Antigravity Workflow

Use the account-security project first.

1. Open `demonstration/01_account_security` as the workspace root.
2. Enable TokenWise once, as above.
3. Close source editors or open the README. Do not select code or attach files.
4. Start a new agent conversation and send this exact prompt:

```text
Explain account lockout after failed login attempts, the expiry boundary, and its related tests. Do not modify any files.
```

5. Watch the agent retrieve context through the configured native hook or the
   workspace rule's command launcher. On the command fallback you should see
   the retrieval tool activity; wording can vary by agent model.
6. Open **TokenWise: Show Automatic Context** or click the TokenWise status item.
7. Check the result's task, included paths, retained source, packed tokens,
   formatting overhead, warnings, and carbon status.
8. Compare the explanation against the answer checklist in section 8.

To prove that this was a real current request, inspect `.tokenwise/latest.json`
inside this project. It should have a current timestamp/event ID, the task being
retrieved, a ready result, and `verification: false`. A setup verification result
or a status item still showing an older task does not prove current injection.
The agent transcript/tool result is also important: a result panel proves a
packet was prepared, not that the assistant read or relied on every excerpt.

On the fallback transport, follow-up task text may be rewritten into a
self-contained query using the current chat's earlier user intent. This is
expected; it should not switch to an unrelated previous workspace topic.

The agent may additionally read original files. That is allowed for this
**workflow** experiment and is useful when excerpts omit details. Record the
extra file reads; do not present their answers as a context-only experiment.

## 6. Experiment B: Produce the Three Comparable Packets

1. In the same project, open and save `security/auth_service.py`.
2. Clear any text selection to use the whole file as the manual baseline.
3. Run **TokenWise: Compare Context Strategies** from the command palette.
4. Enter the same account-lockout prompt from section 5.
5. Wait for the comparison view. The three rows are all indexed Python source,
   manually selected code, and TokenWise automatic context.
6. Click **Export Comparison** and choose a JSON result file. Store exports in
   `demonstration/results/` if you want to keep generated evidence out of Git.
7. Use each **Copy** button to obtain the exact packet for answer testing.

The selection applies only to the manual baseline. The automatic method receives
the task but **no active-file, selected-code, current-symbol, diagnostics, or
conversation-topic hint from the chosen baseline**. This prevents giving the
automatic strategy a hidden oracle advantage from your manual choice.

For an excerpt baseline, select a saved function before running the command.
Record whether the baseline was an entire file or an excerpt. Do not silently
change the selection between repetitions. If you want a stronger expert manual
baseline that includes multiple files, discuss that additional experiment with
your teacher; this command's manual baseline is one file/excerpt, not every
possible manual strategy.

All-code means **all indexed Python files, including tests**, not the README,
images, credentials, ignored files, virtual environments, or every byte on disk.
That scope is explicit in the result. Comparisons support at most 200 indexed
Python files and 2 MiB of Python source. They fail visibly instead of silently
truncating the supposedly complete baseline. These demo projects fit comfortably.

Every packet uses the same local TokenWise tokenizer. Input token counts include
the actual packet headers and fences. Source token counts describe source only.
The three packet wrappers are not identical in content, so explain formatting
overhead rather than pretending input size equals source size. The exported
repository fingerprint lets you check that the packets came from one snapshot.

The comparison command does not call the Antigravity model or grade its answers.
It prepares evidence for the next experiment. Running this command alone is not
a demonstration of automatic chat injection; that is section 5.

## 7. Experiment C: Fair Answer Quality Comparison

Use `demonstration/baseline_lab` as a separate, source-empty Antigravity workspace.
Do not enable TokenWise there. This avoids automatically retrieving an additional
packet during an all-code or manual baseline trial.

For each strategy, create a **fresh agent chat**, paste the corresponding packet
copied in section 6, and append the same instructions and question:

```text
Use only the repository reference packet above to answer the question below.
Do not use terminal, file-reading, search, browser, or other tools.
Do not use repository information from another conversation.
If required evidence is missing, say which facts cannot be determined.
Cite the provided file paths for supported statements. Do not modify files.

Question: Explain account lockout after failed login attempts, the expiry boundary, and its related tests.
```

Use the same Antigravity model/version and settings for all three. Keep the
question and answer constraints identical; only the reference packet changes.
Do not paste the teacher answer checklist or a previous answer into any trial.
Log the actual model name, date, repository fingerprint, token budget, and selected
file. New chats may still have global editor rules; note any such common rules.

Inspect the agent activity. If it reads source, searches the checkout, or calls
tools anyway, label that run a **protocol violation** and repeat it. These text
instructions are not a security sandbox and cannot guarantee the agent will obey.
Do not compare an unrestricted tool-enabled TokenWise answer against baselines
that were forbidden from using tools and call it a fair context comparison.

Run the three trials at least twice in a rehearsal if time permits. Vary their
order between repetitions and use fresh chats. Report variation, not only the
most favorable answer. Do not claim significance from a few small examples.

Score each answer against five facts for its project, one point per correct,
supported fact. An unsupported numerical guess does not earn a point. "The
provided packet does not show the threshold" is an honest limitation, not a
hallucination, but it does not provide that missing fact. Record unsupported
claims separately and record tool violations separately from correctness.

Possible outcomes are all legitimate:

- All-code may answer best or tie TokenWise because it contains complete source.
- Manual selection may use the fewest tokens but omit tests and constants.
- TokenWise may retain sufficient cross-file evidence with less input than all-code.
- TokenWise may omit important evidence or be larger than all-code on a tiny task.
- A shorter packet may not reduce total response time because local retrieval has
  overhead, cloud latency varies, or the assistant performs additional reads.

Use [the blank results worksheet](demonstration/results-template.md) to record
observations. Do not fill it with predicted successful results before the defense.

## 8. Exact Prompts and Teacher Answer Checklists

### Project 1: Account Security

Main prompt: the exact account-lockout prompt in section 5.

Five scoring facts:

1. Three wrong passwords trigger lockout, from `security/settings.py` and the
   threshold condition in `security/auth_service.py`.
2. Lockout lasts 60 seconds; three failures at time 100 produce deadline 160.
3. A correct password is rejected before the lockout deadline; at exactly the
   deadline the lock has expired, and a correct password succeeds.
4. Successful login resets failures. A wrong password at expiry starts a fresh
   failure count of one rather than preserving the previous locked count.
5. `tests/test_auth.py` covers threshold, blocked correct password, expiry
   boundary, successful reset, and failure counting after expiry.

`security/auth_service.py` alone imports the configuration names but does not
show their numeric values or the test implementations. `reports.py` is unrelated
to this question. Session behavior is a separate topic with separate tests.

### Project 2: Checkout and Delivery

Open `demonstration/02_checkout_delivery`, enable TokenWise, and ask:

```text
Explain coupon expiry, its effect on checkout totals, and the tests for expiry and rounding. Do not modify any files.
```

Use `checkout/coupons.py` as the manual baseline for the comparison command.

Five scoring facts:

1. A coupon is invalid when `now >= expires_at`; one expiring at 1000 is valid
   at 999 and expired at 1000, subject to its other validity conditions.
2. For the tested expired coupon/cart, subtotal is 10000 cents, discount is 0,
   tax is 1500, shipping is 500, and total is 12000 cents.
3. Tax is 15%, calculated using integer half-up rounding; 10 cents yields
   2 cents tax while 9 cents yields 1 cent tax.
4. Percentage discounts floor fractional cents; 10% of 999 cents is 99 cents.
5. Coupon boundary tests are in `tests/test_coupons.py`; expiry's effect on the
   order and the rounding examples are in `tests/test_orders.py`.

The complete flow spans coupon lookup, order coordination, pricing, configuration,
models, inventory, and tests. `delivery.py` is real but unrelated to coupon expiry.
Do not claim that a valid coupon and expired coupon produce the same total.

### Project 3: Issue Tracker

Open `demonstration/03_issue_tracker`, enable TokenWise, and ask:

```text
Explain who can close and reopen an issue, the state changes, audit events, and related permission tests. Do not modify any files.
```

Use `tracker/issue_service.py` as the manual baseline.

Five scoring facts:

1. Maintainers can close and reopen; viewers and reporters cannot perform these
   actions, according to `tracker/permissions.py`.
2. Closing requires an open issue, changes status to closed, and records the actor
   in `closed_by`.
3. Reopening requires a closed issue, changes status to open, and clears `closed_by`.
4. Authorized transitions append audit events. Permission checks occur before
   mutating the issue; rejected actions do not change state or audit history.
5. `tests/test_issues.py` checks denied actions, allowed close/audit behavior,
   reopen cleanup, invalid transitions, and unknown issue IDs.

The issue service alone delegates authorization to another file; it cannot
fully explain role permissions without that dependency. `dashboard.py` is a
separate topic for the conversation-switch experiment.

## 9. Experiment D: Follow-ups and Conversation Isolation

Use normal automatic context in a real demo workspace, not `baseline_lab`.

### Same Chat, Ambiguous Follow-up

After the account-lockout main prompt, send in the **same chat**:

```text
Which tests cover that behavior? Do not modify any files.
```

Expected: interpret "that behavior" as account lockout and retrieve fresh relevant
evidence, including its tests. Do not simply reuse an earlier packet without
checking the new request/current source.

The native hook stores one bounded user-topic hint, at most 2000 characters,
scoped to workspace and conversation ID. Recognized follow-ups can use it;
assistant answers, injected code, and another chat's activity are not topic memory.
The topic is retained across successive recognized follow-ups and replaced by a
new self-contained user task. It is not an unlimited transcript or semantic memory.

When the native hint path is used, the panel reports "Current-chat user topic
included." When Antigravity uses the fallback rule, the agent instead rewrites
the retrieval query using earlier **user intent in that chat**. In that case the
panel may say "Latest task only" because the query is already self-contained.
Inspect the task/tool call to distinguish the two, rather than expecting one
fixed flag for every Antigravity build.

### Same Chat, Explicit New Topic

Now send:

```text
Explain session expiry and revocation and their tests. Do not modify any files.
```

Expected: context should include `security/session_service.py` and relevant
session tests, not use account lockout as the topic hint. Sessions last 300
seconds, are invalid at exactly `expires_at`, and revoked sessions are invalid.
It is permissible to include shared models/configuration; overlapping file paths
alone do not establish stale context.

Equivalent topic-switch prompts in the other projects:

```text
Explain atomic inventory reservation for duplicate product codes and its tests. Do not modify any files.
```

```text
Explain dashboard status counts and their tests. Do not modify any files.
```

### New Chat, Missing Referent

Create a **new conversation** and ask only:

```text
Which tests cover that behavior? Do not modify any files.
```

Expected: ask what behavior you mean, rather than silently using the previous
chat's lockout topic. With a native request lacking prior topic evidence, the
backend marks clarification as required. The fallback rule should ask before
retrieval. Therefore there may be **no new retrieval event**; an old status item
remaining on screen is not a new result and not proof of leakage.

If the hook payload has no usable conversation ID, TokenWise disables topic
reuse. Follow-up detection is intentionally conservative, not a complete natural
language coreference system. For unrecognized or complicated references, restate
the subject explicitly. The live assistant's behavior still depends on honoring
the workspace rule; demonstrate the transcript rather than claiming certainty.

### Different Workspace

Open the checkout project in a new window/chat and ask its self-contained main
prompt. Check that the activity file, task, included paths, and response belong to
checkout. There should be no account-security source injected from the other
workspace. Shared central backend/model weights are not shared task memory.

## 10. Token and Carbon Measurements

The comparison's primary size metric is the **complete packet input token count**.
For each strategy, a fair size change relative to all indexed Python code is:

```text
percentage change = 100 * (all-code packet tokens - strategy packet tokens)
                         / all-code packet tokens
```

Positive means reduction. If negative, report the absolute percentage as an
**increase**, not a confusing negative saving. The ordinary automatic panel's
source reduction is a different metric: selected raw source versus retained
source, with formatting overhead reported separately. It is not a claim that
the entire repository was sent before TokenWise.

The comparison command estimates energy and CO2 for each packet with identical
configured model, expected output length, and carbon-intensity assumptions.
Default configuration uses a supported Llama 8B scenario, 256 expected output
tokens, and 475 gCO2/kWh. The result shows the actual configured scenario; it is
**not detection of Gemini's hardware or measured Antigravity emissions**.

CO2 differences can be calculated from the exported strategy estimates. Small
differences may be visually tiny; preserve precision and units. If the estimator
is unavailable or disabled, report that state, not an invented zero. Approximate
models can have prediction variation; never force monotonic savings by clamping.

Local indexing/pruning energy, extra tool calls, prompt/history outside the packet,
actual cloud output length, and network overhead are not measured by this
configured packet comparison. Consequently it does not prove net end-to-end
carbon savings. The reduction in unnecessary context and the modeled inference
impact are useful results with those limitations clearly stated.

"Prepared in ..." measures local context preparation, not the whole agent answer.
For responsiveness, separately time cold startup, warm retrieval, and end-to-end
agent answer. Repeated identical requests can use caches; do not label an exact
cache hit as a new neural inference or compare only warm TokenWise against cold
baseline setup.

## 11. Repeatable Verification and Export

The following commands are for the checkout's developer environment, not required
for a friend installing the VSIX. Run from the TokenWise root on this machine:

```powershell
.\.venv\Scripts\python.exe demonstration/run_checks.py
.\.venv\Scripts\python.exe scripts/verify_demonstration.py
```

The second command starts its own isolated loopback backend, loads the real local
pruning weights and trained carbon artifacts, prepares all three comparisons,
checks follow-up/topic isolation, and stops only its own process afterward. It
does not edit demo application code or your live workspace's activity record.

Generated evidence is written under the ignored `demonstration/results/`:

- Per-project `comparison.json`: actual API response, three complete packets,
  modeled carbon values, and marker-based evidence diagnostics.
- `all_python.md`, `selected.md`, `tokenwise.md`: exact exported context packets.
- `metrics.csv`: nine rows, three projects times three methods.
- `verification.json`: real-backend and conversation-check outcome flags.

Marker checks look for known source strings. They help inspect omissions, but are
**not automated semantic answer grading**. `agent_answer_scored` remains false
until a human performs the fresh-chat experiment. The verifier does not call the
Antigravity cloud agent or certify its answer quality.

See [the dated local verification record](demonstration/VERIFICATION.md) for
observed packet sizes, carbon predictions, timing, and test results from this
checkout. Those numbers are not guaranteed on another machine or another run.

If you already have a matching backend running and know its actual local URL:

```powershell
py -3.12 demonstration/run_checks.py --api-url http://127.0.0.1:8000
```

Use its actual port, not an assumed 8000 if startup selected another port. This
path makes requests to the existing service but does not stop it. The compiled
extension carbon helper and backend dependencies must be available for these
developer exports. The comparison UI is the simpler normal-user route.

## 12. A 15-Minute Live Presentation

| Time | What you show | What you say |
| --- | --- | --- |
| 0-2 min | Three small repositories and passing tests | "The examples have executable expected behavior and cross-file evidence." |
| 2-5 min | Account-security automatic prompt, no file selection | "The task retrieves implementation, configuration, and tests automatically." |
| 5-8 min | Comparison command and exported packets | "Here are the actual input sizes for all-code, manual selection, and automatic retrieval." |
| 8-11 min | Fresh-chat answer trials or recorded rehearsal evidence | "I score supported facts, not just token savings. These trials have the same tools/model constraints." |
| 11-13 min | Same-chat follow-up, explicit topic switch, new-chat ambiguity | "Context follows the current task; a new chat does not inherit another chat's topic." |
| 13-15 min | Checkout/tracker quick examples and limitations | "The workflow generalizes to separate repositories; modeled carbon is not measured cloud carbon." |

If time is short, do one complete comparison live and show the other two projects'
dated rehearsal exports. Label recorded evidence as recorded, not live. Have a
local copy of the guide, test output, packets, and screenshots available in case
the cloud agent is unavailable. Local retrieval can run after setup without new
downloads, but a working local backend does not guarantee cloud-model access.

## 13. Short Defense Script

"TokenWise prepares task-specific Python repository context for an IDE assistant.
Without selection, my prompt is compiled into a retrieval goal. The backend uses
an indexed repository, lexical evidence and dependency relationships to choose
relevant files, preserves useful interfaces and tests, and packs excerpts under
a tokenizer-checked budget. The local model handles focused pruning, while broad
overview requests use a separate coverage-oriented path.

"My experiment compares all indexed Python source, one manual selection, and
automatic context from the same saved repository and task. I compare packet size
and supported answer facts separately. A manually selected file can be smaller
but miss configuration and tests; all-code can be complete but include unrelated
modules. The automatic strategy aims to retain sufficient task evidence without
requiring the user to find those files.

"I also test same-chat follow-ups, explicit topic switches, and fresh-chat
clarification. The native hint is bounded and scoped, not unrestricted memory.
The carbon numbers are predictions for a fixed scenario, not measurements of
the assistant provider. These demonstrations validate behavior on small real
examples; they do not prove universal correctness or guaranteed net savings."

## 14. Questions Your Teacher May Ask

**Why not send everything?** Complete source is a useful baseline. Large inputs
can exceed a budget or include irrelevant material. Retrieval trades completeness
for targeted evidence; correctness must be checked rather than assumed.

**Why not manually choose files?** Manual selection is legitimate but costs user
effort and knowledge of dependencies. Our one-file baseline makes its scope
explicit; a multi-file expert baseline would be another worthwhile experiment.

**Do you always reduce tokens?** No. Formatting and safety instructions can make
tiny packets larger; some tasks need many files. Increases are shown honestly.

**Can a smaller packet still produce a wrong answer?** Yes. That is why the
experiment scores supported facts and missing evidence as well as size.

**Are the generated answers hardcoded?** No. Demo code/tests and question facts
are fixed for repeatability; retrieval runs against current source, and the
agent answers are produced independently in the actual chats.

**What is automated in the comparison?** Retrieval, token counting, packet
export, configured carbon estimates, and source-marker diagnostics. The cloud
answer comparison and semantic grading are not automated by this command.

**Does it remember every conversation?** No. Native automatic context uses a
bounded topic from the current workspace/chat only. The fallback agent resolves
references under a rule. Separate-chat persistent memory is not implemented.

**Will a code edit invalidate context?** Repository file events update the index,
with reconciliation for missed events and fingerprint-based cache invalidation.
For this controlled comparison keep source saved and unchanged; changed snapshots
must be rerun rather than presented as the same experiment.

**Are carbon savings measured?** No. They are model predictions for controlled
assumptions and packet inputs. End-to-end energy accounting is additional work.

**Does it work on every language/project?** These focused experiments cover local
Python repositories on the tested Windows environment. Ignored/generated source,
dynamic dependencies, large repositories, missing evidence, and complex pronouns
can limit retrieval. No demonstration justifies claiming universal perfection.

## 15. Troubleshooting and Retry Checklist

| Problem | What to check | How to retry |
| --- | --- | --- |
| Comparison command missing | Installed extension version/development host | Install the local 0.6.2 VSIX and reload |
| Compare endpoint 404 | Old Python backend | Run Set Up Backend for the updated bundle, then retry |
| No indexed Python files | Opened `baseline_lab` or wrong folder | Open the appropriate leaf project |
| File changed/selection rejected | Unsaved edits or outdated excerpt | Save, select current source, rerun comparison |
| First request slow | Model cold startup/setup still running | Finish setup and separately record cold/warm timing |
| No automatic activity | Enablement, trust, rules, agent tool execution | Re-enable the project, inspect Output, use a fresh explicit task |
| Old task still visible | No new retrieval happened | Check timestamps/event IDs and transcript; do not call it a new result |
| Missing CO2 | Carbon disabled/artifacts not ready/unsupported model | Check configuration and setup error; retain unavailable status until fixed |
| Manual trial reads source | Context-only protocol violated | Start a new `baseline_lab` chat and repeat with the same packet |
| Follow-up ambiguous | No same-chat topic or unrecognized phrasing | Restate the subject; show clarification instead of guessing |
| Retrieval omits a needed fact | Candidate/budget/selection evidence insufficient | Record the omission; read originals in workflow mode, rerun controlled trials only under stated settings |

Final rehearsal checklist: three project tests pass, installed extension/backend
match, all workspaces enabled separately, baseline workspace unconfigured,
packets export/copy correctly, answer facts checked, timing/scenario recorded,
new chats used for independent trials, and limitations stated without claiming
"perfect" results that were not observed.
