# Evidence and Claim Boundaries

## Source Priority and Freshness

Use current source code and current reproducible artifacts to resolve conflicts.
Then use the current manifest/README and dated release notes. Explanatory guides
can be stale: `study.md` and `validation.md` include older embedded results even
when their introductions refer to a later version. Reconcile dates and versions;
do not silently combine historical observations into a new experiment.

Proposal and research papers motivate design but do not establish that a planned
feature was implemented or that TokenWise reproduced a paper's benchmark.

| Topic | Repository sources to inspect |
|---|---|
| Current version, commands, settings | `vscode-extension/package.json`, `README.md`, `CHANGELOG.md` |
| Activation and editor integration | `vscode-extension/src/extension.ts`, `src/services/automaticSetup.ts`, `automaticContext.ts`, `backendManager.ts`, `managedBackend.ts` under `vscode-extension/` |
| Index synchronization | `vscode-extension/src/services/repositoryIndexSync.ts`; `repository/repository_index.py`, `python_indexer.py`, `dependency_graph.py` under the backend package |
| Goal and retrieval | `goal_compiler.py`; `retrieval/lexical_retriever.py`, `graph_retriever.py`, `candidate_ranker.py`, `workspace_context.py`, `context_builder.py`, `repository_overview.py` |
| Neural runtime and serving | `swepruner.py`, `model_structure.py`, `prune_wrapper.py`, `online_serving.py` |
| Prompt guidance and memory | `retrieval/response_guidance.py`, `retrieval/conversation_memory.py`, `conversation_context.py`, `antigravity_context.py`, `antigravity_hook.py` |
| Result and comparison interface | `vscode-extension/src/ui/resultPanel.ts`, `src/commands/compareContextStrategies.ts`, `importAntigravityComparison.ts`, `src/services/antigravityUsage.ts` |
| Carbon | `carbon-engine/src/carbon_engine/`, its `scripts/` and actual artifacts; backend `carbon_estimator.py`, `carbon_model_engine.py` |
| Product lifecycle | `scripts/install_backend.py`, extension cleanup/uninstall modules, `docs/PUBLISHING.md` |
| Demo and manual | `demonstration/tokenwise_demo/`, `demonstation.md`, `demonstration2.md`, `validation.md` |
| Regression evidence | `tests.md`, extension/backend test directories, `evaluation/test-validation/browser-checks.json` |
| Study evidence | `comparative_study.md`, `evaluation/comparative-study/{cases,snapshots,results,summary}.json`, `metrics.csv`, `full-file-pilot.json`, `test_protocol.py` |
| Study mechanics | `scripts/run_comparative_study.py`, `summarize_comparative_study.py`, `plot-comparative-study.cjs` |
| Proposal and research attribution | `spl3-1442.docx.pdf` or `docs/TokenWise-Proposal.pdf`; `SWE-pruner.pdf` or `docs/papers/SWE-Pruner.pdf`; `carbon-emissioin.pdf` or `docs/papers/SEAL-Carbon-Estimation.pdf`; `THIRD_PARTY_NOTICES.md` |

Backend package-relative files are rooted at
`swe-pruner/swe-pruner/src/swe_pruner/`. Check actual paths before linking.
Some report inputs are local-only or ignored; missing original packets must be
disclosed when discussing reproducibility. Never execute downloaded repository
code just to prepare report prose.

## Dated Reference Snapshot, Not Permanent Constants

The following is the verified report basis recorded on 2026-10-09 for version
0.6.8, Windows beta, implementation commit `573b82b`. Recheck source artifacts
when updating; do not label these numbers as a newly executed run.

### Software Validation

- Extension: 193 discovered, 193 passed, zero failures/skips.
- Backend: 142 discovered, 141 passed, one skipped, zero failures/errors.
- Demonstration: 20 discovered, 20 passed.
- Combined three suites: 355 discovered, 354 passed, one skipped.
- Browser: ten separate fixture views, five states across desktop/mobile sizes;
  not ten live Antigravity sessions or extra backend unit cases.
- Study protocol: ten additional harness tests, separately reported.
- Skip: `RepositoryCacheTests.test_retargeted_symlink_removes_previous_cached_content`
  in `test_repository_cache.py`; this Windows account could not create symlinks.
- No line/branch coverage percentage was measured. Mocks and fixtures validate
  contracts, not pretrained pruning accuracy or cloud answer quality.

### Completed Local Component Study

- Twenty pinned public Python repositories, 538 indexed Python files, seven
  conditions each, 140 measured packets; real neural calls on twenty bounded
  function/method excerpts. No downstream cloud answer generation was performed.
- Seven conditions: `all_python`, `selected_file`, `selected_excerpt`,
  `neural_excerpt`, `retrieval_only`, `history_off`, `history_on`.
- All-Python full packet total: 1,107,232 tokens; retrieval-only total: 71,119,
  an aggregate 93.58% reduction against that hypothetical baseline. This is an
  ablation, not the complete production neural pipeline, and not observed native
  Antigravity behavior when TokenWise is disabled.
- Same selected excerpt before/after real neural pruning: complete-packet total
  7,575 to 7,329, aggregate 3.25% reduction; three smaller, sixteen equal, one
  larger. Implementation evidence anchors survived in seventeen of twenty.
- Memory off/on required-file candidate coverage: 33/43 to 40/43; six cases
  improved, thirteen tied, one worsened. This is pre-packing file coverage, not
  full evidence or answer quality. Final packed anchors: 4/59 to 6/59.
- Retrieval-only final anchor retention: 6/59 despite retrieving 40/43 required
  candidate files. Interface-only packing can omit essential function bodies.
- Full-file automatic CPU pilot timed out after 600 seconds on its first case.
  Subsequent connection failures were caused by termination of that study
  backend, not nineteen independent repository failures. Do not omit this pilot
  or describe the bounded replacement study as successful full-file evaluation.
- The oracle is a frozen syntactic declaration/body-line/test association proxy,
  not a blinded expert answer-quality rubric. The focused excerpt baseline is
  informed and already small; this affects interpretation of pruning benefit.
- Carbon estimates for the matched excerpt packets: approximately 2.485763 g to
  2.481059 g aggregate, about 0.004704 g saved under the configured estimator,
  not measured emissions. Read exact model, output-token and intensity settings
  from the study artifacts before publishing a table.

## Claims to Make and Avoid

Describe automatic bounded context preparation and inspectable references as
implemented capabilities. Describe task-aware outgoing guidance as prompt
engineering designed to support grounded answers, not proven answer improvement.
Describe memory as selected, bounded same-chat user references, not complete
chat retention or perfect semantic memory; it excludes assistant/tool output.

Distinguish native supported hooks from an agent-followed rule/command fallback.
Do not promise universal interception before the first model request. A fresh
local activity record proves preparation, not that the cloud model consumed it.
Visible tool output and grounded answers provide different operational evidence.

Do not describe an all-code packet comparison as a live enabled/disabled trial.
Actual usage import relies on genuinely reported independent successful CLI
logs. Missing provider counters remain N/A, not zero or local-tokenizer estimates.
Record source/model/settings, tools, total workflow time, failures, answer rubric,
and repeat/order controls for native comparisons; otherwise label them planned.

Keep prefill and decode estimates separate. Carbon predictions exclude local
pruning/index/download overhead and do not prove net environmental benefit.
Token reduction is not equal to proportional total-carbon reduction.

Credit SWE-Pruner, Qwen pretrained/tokenizer assets, and the SEAL-derived
estimation approach as appropriate. State the student's concrete engineering,
adaptation, training work supported by artifacts, integration, evaluation, and
productization. Do not claim to have invented or trained pretrained assets from
scratch. Use actual paper bibliographic metadata rather than guessing authors,
venues, dates, or reported numbers.
