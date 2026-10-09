# Report Structure and Reference Mapping

## Reference Observations

Inspected on 2026-10-09: `Frineds_report/DeHalu_Final_Report.docx`, titled
"DeHalu: Agentic Hallucination Detection and Mitigation in Local CodeLLMs."
Its main body has seven numbered chapters:

| Reference chapter | Reusable reporting pattern |
|---|---|
| 1. Project Overview | Title, problem, objectives, scope/evolution, deliverables, evidence terminology |
| 2. Requirements Analysis | Grouped functional requirements, non-functional requirements, implementation boundaries |
| 3. Component Level Design | Architecture, component responsibilities, contracts, data, metrics, behavior, deployment |
| 4. Interface Design | Users/actions, controls, transitions, actual screen provenance, accessibility limits |
| 5. Testing | Strategy, pass/fail criteria, observed totals, detailed cases, risks, reproducibility |
| 6. User Manual | Prerequisites, installation, first use, workflows, export, recovery, maintainer checks |
| 7. Conclusion | Achieved outcomes, limitations, future work |

The source document contains 14 tables and 19 drawing elements. These are
observations, not target counts for TokenWise. Its introductory list of figures
does not match all later figure captions; generate a coherent new list rather
than preserving that mismatch. Its statement that it contains exactly seven
sections must not be copied into the adapted eight-chapter report.

The useful style is requirement-to-implementation-to-evidence traceability,
component responsibilities with collaborators, procedure-based test cases, and
explicit separation of fixture screenshots from live outcomes. Do not reuse
DeHalu's database, judge pool, repair pipeline, or deployment as TokenWise features.

## Word Presentation

Observed defaults, unless university instructions supersede them:

- US Letter portrait, 8.5 by 11 inches, with 1-inch margins.
- Default body Arial 11 pt, paragraph line setting approximately 1.15.
- Heading 1: 20 pt; Heading 2: 16 pt; Heading 3: 14 pt.
- Distinct title page, contents, figure list, and footer page numbering.

These are source-document defaults, not a claim that every manually formatted
paragraph uses them. Do not describe them as a university-mandated standard.
Keep tables readable across pages and captions with their associated content.
Use an automatic table of contents in Word where supported; flag field refresh
needs. Do not assign page numbers before pagination.

## Front Matter

Create a TokenWise cover with a descriptive project title, course, verified
student name and ID, verified supervisor/institution, actual submission date,
and an unsigned signature field if required. Follow with a contents list, list
of figures, and list of tables when useful. Include an abstract only when
requested or required by the academic template; the friend's structure is not
permission to invent university rules.

## 1. Project Overview

Suggested subsections:

1.1 Project title and concise definition.
1.2 Problem: irrelevant repository context, manual selection, context limits,
additional retrieval work, and the motivation for sustainability estimation.
1.3 Objectives linked to mechanisms and assessment evidence.
1.4 Implemented scope and evolution from the proposal.
1.5 Deliverables and report organization.
1.6 Evidence basis and key terminology.

Define TokenWise as an editor extension and local Python backend that prepares
task-focused, bounded Python repository context for Antigravity. It is not a new
code-generating LLM. Distinguish retrieval, neural pruning, packing, prompt
guidance, same-chat user-reference memory, and carbon estimation.

## 2. Requirements Analysis

Group functional requirements around managed backend setup; trusted/local
workspace configuration; indexing and updates; task interpretation; retrieval
and dependencies/tests; selected-file and selected-excerpt pruning; repository
overview; complete-packet budgeting; outgoing guidance; conversation memory;
integration/result inspection; comparison/export; and owned-data cleanup.

Use stable IDs from an existing SRS if one exists. Otherwise label new `TW-FR-*`
and `TW-NFR-*` identifiers as the report's organization, not as original proposal
identifiers. For each group distinguish requirement, implemented mechanism,
acceptance evidence, and limitation.

Cover usability and recovery, correctness/freshness, performance, explainability,
privacy/security boundaries, portability, and maintainability. Do not invent
performance thresholds, production guarantees, or unsupported platforms.

## 3. Component Level Design

3.1 Overall runtime architecture and local/external boundaries.
3.2 Component-wise responsibilities and collaborators.
3.3 Principal classes, request/response contracts, and module boundaries.
3.4 Persistent data, caches, ownership, and invalidation.
3.5 Algorithms, token accounting, and carbon formulas.
3.6 Behavioral flows, states, and recovery.
3.7 Backend endpoints and Antigravity transport contracts.
3.8 Packaging and supported deployment.

Explain the actual lifecycle: enable workspace; prepare/update index; capture
current task and available bounded user references; compile goal; retrieve
candidates; expand relevant dependencies/tests; rank and prune where applicable;
pack under a tokenizer budget with guidance/reference overhead; record activity;
deliver through the supported adapter or rule/command fallback; inspect/export.
Verify this flow in current code rather than imposing it on every mode.

Discuss explicit-file/excerpt pruning separately from repository discovery and
overview behavior. Explain threshold masks, formatting gaps, truncation, and why
pruned excerpts are reference material rather than guaranteed runnable programs.
Treat the local index/search cache, workspace activity files, managed environment,
downloaded weights, and estimator artifacts as distinct storage categories.
Do not invent an SQL database or ER schema; use a file/data-ownership design
appropriate to the implementation. Explain cache invalidation from saved edits
and reconciliation, not perfect observation of unsaved buffers.

Derive documented formulas with units and clear baseline definitions. For token
reduction use `(baseline - prepared) / baseline * 100` when baseline is positive;
otherwise report N/A. Preserve signed increases instead of hiding them. Match
the UI's actual field semantics when discussing content-only and full-packet
overhead. For operational carbon conversion use
`CO2_g = energy_J / 3_600_000 * intensity_g_per_kWh` and state estimator assumptions.

## 4. Interface Design

4.1 User roles, tasks, and navigation.
4.2 Actual controls and commands with observable feedback.
4.3 Loading, success, unavailable/error, stale, and recovery states.
4.4 Screen descriptions with red screenshot placeholders and provenance.
4.5 Readability, responsive checks, and accessibility limits.

Describe the extension's command palette, status bar, diagnostics, result panels,
line decisions, memory inspector, local comparisons, usage import, copy, and
export only where implemented. Do not turn the extension into the friend's web
application. Browser-fixture views are not native IDE screenshots.

## 5. Testing

5.1 Strategy and distinct test levels.
5.2 Item-specific pass/fail criteria.
5.3 Dated observed results and skipped cases.
5.4 Representative extension/backend test cases.
5.5 Demonstration tests and browser fixture checks.
5.6 Defects, test limitations, risks, and contingencies.
5.7 Reproduction commands and artifact locations.

Use a case table with ID, requirement link, preconditions/input, steps, expected
result, observed result, evidence path, and scope. Mark unexecuted cases as
planned, not passed. Do not duplicate unit totals when summarizing an inclusive
suite. Keep software regression tests separate from research effectiveness.

## 6. User Manual

6.1 Prerequisites and supported environment.
6.2 VSIX installation and upgrade.
6.3 Managed backend setup, progress, retry, and diagnostics.
6.4 Enable automatic context in an arbitrary trusted local Python folder.
6.5 First ordinary Antigravity prompt and evidence of fresh retrieval.
6.6 Manual file/excerpt and repository discovery workflows.
6.7 Memory, outgoing guidance, comparison, and export controls.
6.8 Troubleshooting and individual-step recovery.
6.9 Disable/cleanup/uninstall boundaries and maintainer-only source workflow.

Normal users should not be instructed to clone, compile, press F5, or start
development processes. Verify exact current command titles in the manifest.
Use the one `demonstration/tokenwise_demo` project for all examples.

## 7. Validation and Comparative Study

This chapter immediately follows the user manual. Its suggested subsections:

7.1 Research questions and distinction between validation and effectiveness.
7.2 Functional validation: current retrieval event, actual transport output,
budget, cross-file evidence, memory isolation, freshness, and read-only behavior.
7.3 Baselines and controls: all indexed Python, selected source, matched neural
excerpt, retrieval-only ablation, and memory off/on.
7.4 Completed twenty-repository dataset, commit pins, protocol, settings, and
ground-truth proxy.
7.5 Measured token results, evidence retention, latency, and memory differences.
7.6 Carbon estimates with assumptions and excluded local costs.
7.7 Failed full-file pilot, negative findings, and threats to validity.
7.8 Native Antigravity with/without protocol and genuinely collected results, if
available; otherwise explicitly an unperformed evaluation plan with blank fields.
7.9 Interpretation: established benefit, trade-offs, and remaining evidence.

Use source-linked tables and figure placeholders instead of fabricated graphs
or screenshots. The short prompt
"Explain account lockout after failed login attempts and its related tests. Do
not modify any files." is suitable for a paired native demonstration when both
runs use independent fresh chats and the same snapshot, model, and permissions.
Do not disable the baseline's native source-reading tools to make it fail.

## 8. Conclusion and References

Summarize achieved objectives with corresponding evidence, useful contributions,
observed weaknesses, and prioritized future work. Avoid "perfect," "always
better," or unsupported superiority. Cite the proposal, followed papers,
third-party assets, actual code/documentation, and measurement artifacts.
Keep proposed improvements separate from delivered capabilities.
