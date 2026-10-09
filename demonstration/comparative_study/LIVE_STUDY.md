# Live Antigravity WITH/WITHOUT Study

**Status: first live baseline attempted, blocked by CLI command permissions;
zero valid comparison pairs completed.**

The requested study is twenty repositories, three independent pairs per
repository: sixty pairs and 120 one-turn Antigravity runs. Preparing the source
folders or running the earlier local component study does not complete these
live comparisons. This document is a protocol, not a results claim.
See [PREFLIGHT.md](PREFLIGHT.md) for the actual failed attempt and next action.

## Conditions

WITHOUT is native Antigravity repository assistance with TokenWise integration
inactive. WITH is the same assistance with a fresh TokenWise context invocation.
Both conditions retain the same native repository-reading tools. An all-Python
packet substituted for the baseline is a different experiment and must not be
labeled an observed native WITHOUT workflow.

Use one pinned model and reasoning effort throughout, the same saved upstream
commit and exact task per pair, no manually attached source, and a new chat for
each run. Alternate WITHOUT/WITH, WITH/WITHOUT, WITHOUT/WITH for the three pairs.
Record backend warm/cold state. Disable automatic packet-comparison measurement
work during timed runs. Preparation overhead belongs in total answer time.

Run each numbered repository as its own workspace. Never provide `TASKS.md`, the
manifest, expected answers, evaluation artifacts, or previous trial answers as
model context. Source and test execution are unnecessary for read-only tasks;
do not enable unrestricted command execution or blanket permission bypass.

## Measurements

| Measurement | WITHOUT | WITH | Collection rule |
|---|---|---|---|
| Correct supported facts | Not collected | Not collected | Freeze a repository-specific six-item rubric before answers; record one point per supported item |
| Incorrect or unsupported claims | Not collected | Not collected | Review distinct claims against source and real tests; record reasons, not keyword guesses |
| Total answer time | Not collected | Not collected | Wall-clock submission through complete final answer, including TokenWise/tool overhead |
| Observed tool/file-reading calls | Not collected | Not collected | Deduplicate completed streamed tool steps; report total tools separately from visible source reads |
| Actual reported input tokens | N/A | N/A | Use the terminal result's reported usage once; missing counters remain N/A |

These placeholders mean no observation exists. They are not zero-valued results.
The `/6` rubric must be defined independently for each task; it is not the
existing syntactic evidence-anchor score. Source/test association alone does
not establish answer correctness. AI-assisted scoring requires supporting source
references and should be reviewed by the student or supervisor before submission.

For a valid CLI log, capture one fresh terminal result with a distinct
conversation ID and matching pinned model. Retain complete stdout/stderr,
task/settings, timestamps, exit status, source fingerprints and tool trace.
CLI usage measures that CLI run, not a prior IDE chat. Do not sum cumulative
terminal usage together with per-step usage or add cached counters twice.

## Reporting

Use `results-template.csv` for the planned 120 runs. All rows initially say
`not_run`. Keep raw answers, logs and filled worksheets in `results/`, outside
the active project context. Record errors, permission denials, missing context,
timeouts and quota failures. A failure must not become a successful zero-token
answer, and replacement trials must remain linked to the original record.

Report per-repository pairs plus aggregate paired summaries, successful/failed
counts, median/range of timings and the number of pairs with comparable actual
usage. Missing scores are ungraded, not zero. Do not aggregate different models
or compare successful WITH runs only against failed WITHOUT runs as if that
established quality superiority. Observed calls are not complete internal reads.

The earlier `evaluation/comparative-study` results remain a separate local
component study. No live answer quality, cloud usage or native workflow benefit
is inferred from its packet-token reductions.

## Official CLI References

- [Headless runs, streamed tools and usage](https://www.antigravity.google/docs/cli/headless/)
- [CLI installation and authentication](https://www.antigravity.google/docs/cli/install/)

Authentication and model availability must be established before the first
trial. An open signed-in IDE alone does not prove the CLI is ready.
