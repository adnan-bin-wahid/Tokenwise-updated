# Local Verification Record

Date: 2026-10-05. Environment: this Windows checkout, Python 3.12, CPU inference,
local pruning weights, trained carbon artifacts, local 0.6.2 code. Command:
`.venv\Scripts\python.exe scripts/verify_demonstration.py`.

These are observations from one local verification run, not predicted outcomes,
cloud-agent answers, or evidence of universal performance. The generated JSON
and CSV are available under ignored `demonstration/results/` in this checkout.
Repeat the verifier to obtain measurements for your own machine/snapshot.

## Actual Packet Counts

| Project | All Python input tokens | One selected file input tokens | TokenWise input tokens | TokenWise change versus all-code |
| --- | --- | --- | --- | --- |
| Account security | 1549 | 202 | 1387 | 10.46% reduction |
| Checkout | 2035 | 174 | 1575 | 22.60% reduction |
| Issue tracker | 1486 | 256 | 1415 | 4.78% reduction |

Counts use the same real TokenWise tokenizer and include packet formatting.
The automatic budget was 4096 tokens with at most eight candidates. All three
automatic packets included eight files. Manual baselines were entire service
files, not multi-file expert selections.

All-code and automatic packets each contained 4/4 checked source markers per
project; the one-file manual baselines each contained 1/4. This is **marker
presence, not semantic answer correctness**. Only the fresh-chat scoring
experiment can evaluate the actual Antigravity answers.

The complete comparison request took 24.784 seconds for the first project,
5.255 for checkout, and 5.111 for the tracker in that run. These times include
local comparison preparation, not cloud answer time; startup/inference warm-up
and competing machine activity can affect them. Do not use them as a guaranteed
latency or a controlled cold-versus-warm benchmark.

## Modeled CO2

Matched scenario: Llama-3 8B, 256 expected output tokens, 475 gCO2/kWh.

| Project | All Python CO2 g | Selected CO2 g | TokenWise CO2 g |
| --- | --- | --- | --- |
| Account security | 0.146667 | 0.120908 | 0.143569 |
| Checkout | 0.155961 | 0.120373 | 0.147164 |
| Issue tracker | 0.145462 | 0.121941 | 0.144105 |

These predictions do not measure Gemini/Antigravity hardware, actual output
length, local pruning energy, tool overhead, or net end-to-end emissions.
The smaller manual packet has less modeled input cost but also less checked
evidence; cost alone is not the quality criterion.

## Other Checks

- 22 demonstration application tests and all three example apps passed.
- 149 extension tests passed.
- Backend suite: 91 tests, 90 passed, one skipped because this Windows account
  cannot create file symlinks.
- Real-weight HTTP checks passed for same-chat hints, new-chat clarification,
  explicit-topic ignoring the old hint, and bounded packets.
- Browser checks passed at 1280x1000 and 390x844, with no page errors or document
  overflow. The table scrolls horizontally where needed; copy/export messages
  were checked, and actual host copy/export handling has regression tests.
- The verifier stopped its own backend and did not edit demo application source.
- **Antigravity's cloud model was not called or graded by these checks.**

This record describes pre-publication local verification. The 0.6.2 installer
and demonstration bundle are distributed through the versioned GitHub release.
Install the VSIX, update the matching backend, and follow `../demonstation.md` to
rehearse the actual agent interaction before presenting it as a live result.
