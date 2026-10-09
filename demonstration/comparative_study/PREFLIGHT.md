# Live Study Preflight

Date: 9 October 2026. Requested scope: 20 repositories, three pairs each,
120 independent Antigravity runs. Completed valid pairs: **0/60**.

## Actual Attempt

One fresh WITHOUT trial was submitted for `01_click`, using the unchanged task
in `TASKS.md`, model `gemini-3.8-flash-high`, official signed CLI 1.3.2,
default reasoning configuration and normal request-review permissions.
The six-fact Click rubric was saved before submission.

Authentication worked. The CLI attempted `git grep -n "IntRange"`, but its
permission check denied that command. The terminal result said `SUCCESS` with
an **empty response** and a recorded denied action. This is a failed preflight,
not a valid baseline answer or evidence of TokenWise superiority.

| Observation | Actual value |
|---|---:|
| Total wall time, including CLI startup | 25.373 s |
| CLI-reported duration | 8.8158954 s |
| Reported input tokens | 11,696 |
| Reported output tokens | 387 |
| Reported thinking tokens, kept separate | 294 |
| Reported cache-read tokens | 0 |
| Reported total tokens, not recalculated | 12,083 |
| Observed attempted tool calls | 1 |
| Observed successful completed tool calls | 0 |
| Observed failed tool calls | 1 |
| Supported facts / incorrect claims | N/A: no answer to grade |
| Source bytes before versus after | Unchanged |

Conversation ID: `b386b2ec-bd86-4714-a57b-218673aea882`.
Local raw evidence: `results/01_click-pair1-without/`.
These logs describe a CLI run, not telemetry from the IDE Agent panel.
Do not include this failed attempt in successful paired averages.

## Required Before Continuing

Headless CLI runs cannot approve shell-command permission dialogs. The CLI
needs an explicitly approved, narrowly scoped read-only command policy before
the study can continue. The WITH condition also needs permission for the
specific TokenWise launcher. IDE "Always Proceed" does not establish that the
separate CLI has those permissions.

Do not enable blanket permission bypass. Do not work around the denied command
using alternative tools in the same run. No global permissions have been
changed, and no further inference calls were made after this denial.

The prepared projects are source snapshots, not separate Git checkouts, so
Git commands can discover the parent TokenWise repository. Successful replacement
trials must confirm searches stay within the numbered project and validate both
native file reading and receipt of fresh TokenWise context before launching
the full study. Retain this failed trial separately when repeating the pair.

The capture script currently supports isolated WITHOUT trials only. It is not
a completed 120-run WITH/WITHOUT harness. Additional repository rubrics, the
WITH integration and semantic answer grading remain required.

Official reference: [Antigravity CLI permissions](https://www.antigravity.google/docs/permissions?tab=cli).
