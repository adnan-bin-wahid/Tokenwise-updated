# Final Report

## TokenWise: Sustainable Context Optimization for Coding Agents

**Software Project Lab III**  
**Course code:** [Confirm the official course code]

**Submitted by**  
Adnan Bin Wahid  
BSSE-1442

**Supervised by**  
Mridha Md. Nafis Fuad  
[Confirm the supervisor's current designation before submission]

Institute of Information Technology  
University of Dhaka

**Submission date:** [Enter the actual submission date]  
**Supervisor's signature:** ______________________________

**Report preparation and source inspection:** 9 October 2026.  
**Implementation:** TokenWise 0.6.8, Windows-tested beta.  
**Inspected checkout revision:** `e406080071490fc3cafc67298ee2462c126197bc`.  
**Recorded experiment implementation revision:** `573b82bcb2eb4856f1f4af65eb5735e3f6475404`.

The name, student identifier, institution, and supervisor above are taken from
the supplied project proposal. Its proposal date is not reused as the final
submission date. This editable report follows the organization of the supplied
DeHalu report, with an additional validation and comparative-study chapter
immediately after the user manual. Its content describes TokenWise, not DeHalu.
Screenshots are intentionally absent. Red `ADD SCREENSHOT` lines describe the
evidence to insert; their labels remain readable if a Markdown viewer suppresses
inline color. Diagram instructions are labeled separately.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Requirements Analysis](#2-requirements-analysis)
3. [Component Level Design](#3-component-level-design)
4. [Interface Design](#4-interface-design)
5. [Testing](#5-testing)
6. [User Manual](#6-user-manual)
7. [Validation and Comparative Study](#7-validation-and-comparative-study)
8. [Conclusion](#8-conclusion)
9. [References](#references)

## List of Figures

The following captions identify intended insertion locations, not already
captured images. Page numbers must be generated after final document pagination.

| Figure | Intended caption |
|---|---|
| 1 | TokenWise runtime architecture and local/external processing boundaries |
| 2 | Task-to-context activity flow and the separate overview path |
| 3 | Repository metadata, cache, and owned-file relationships |
| 4 | Automatic prompt retrieval and asynchronous result enrichment |
| 5 | Installed TokenWise extension and version |
| 6 | Configured demonstration workspace and automatic-context status |
| 7 | Bounded repository context and included source evidence |
| 8 | Selected-source neural pruning and line decisions |
| 9 | Task-aware outgoing response guidance |
| 10 | Inspectable bounded conversation memory |
| 11 | Configured inference energy and carbon estimates |
| 12 | Local all-Python versus prepared-packet comparison |
| 13 | Recorded extension and backend test summaries |
| 14 | Demonstration application verification |
| 15 | Managed backend setup and readiness |
| 16 | Fresh automatic retrieval for the account-lockout prompt |
| 17 | Twenty-repository component-study results |
| 18 | Controlled native Antigravity baseline without TokenWise |
| 19 | Controlled native Antigravity workflow with TokenWise |
| 20 | Completed paired-run validation worksheet, when available |

## List of Tables

| Table | Title |
|---|---|
| 1 | Project objectives, implementation, and assessment |
| 2 | Proposal-to-implementation scope |
| 3 | Terminology and evidence categories |
| 4 | Functional requirements and traceability |
| 5 | Non-functional requirements and boundaries |
| 6 | Major components and responsibilities |
| 7 | Storage and ownership categories |
| 8 | Backend API contracts |
| 9 | Important defaults and limits |
| 10 | Recorded carbon-model cross-validation metrics |
| 11 | Interface objects and user actions |
| 12 | Operational states and recovery |
| 13 | Recorded software verification results |
| 14 | Representative validation cases |
| 15 | Browser fixture states |
| 16 | Installation stages and recovery |
| 17 | Everyday workflows and controls |
| 18 | User troubleshooting |
| 19 | Functional integration validation checklist |
| 20 | Comparative-study conditions |
| 21 | Dataset and per-repository packet tokens |
| 22 | Aggregate context and evidence results |
| 23 | Memory-ablation outcomes |
| 24 | Observed component latency |
| 25 | Matched-packet carbon estimates |
| 26 | Source-grounded account-lockout scoring rubric |
| 27 | Native comparison worksheet awaiting real runs |
| 28 | Research threats and interpretation |
| 29 | Achieved outcomes and remaining limitations |

---

## 1. Project Overview

### 1.1 Project Title and Definition

TokenWise: Sustainable Context Optimization for Coding Agents is a developer
extension with a local Python backend for preparing task-relevant repository
evidence. Its primary workflow is integration with Antigravity: a developer
opens a trusted local Python repository, enables automatic context, and submits
an ordinary programming question. TokenWise discovers relevant source and tests,
reduces or structurally represents their content, and returns an organized
reference packet bounded by a configured token budget.

The system also estimates the inference energy and operational carbon difference
between defined before/after context inputs. These estimates use locally trained,
SEAL-derived regression artifacts and explicit model, hardware, workload, and
electricity-intensity assumptions. They are not direct observations of
Antigravity's provider infrastructure.

TokenWise is not a replacement coding assistant and does not generate the final
answer itself. It operates before or within the agent's information-gathering
workflow. Antigravity remains responsible for interpreting the supplied
evidence, reading originals when necessary, answering the user, and performing
authorized edits. TokenWise's preparation does not itself authorize edits.

The source repository is identified in the extension manifest as
`https://github.com/adnan-bin-wahid/Tokenwise-updated`.
The user-facing distribution is a VSIX extension and a versioned presentation
bundle, rather than a GitHub Pages application.

### 1.2 Problem Statement

A repository question is rarely answered by a single isolated file. For example,
account-lockout behavior depends on a service, account fields, configuration,
and tests that establish timing boundaries. A user who selects only the service
can omit the threshold value or the exact expiry semantics. A user who includes
the complete repository supplies unrelated functionality and substantial
formatting and source content that may not help answer the question.

Manual context selection transfers the retrieval burden to the developer. This
is inconvenient when the developer is unfamiliar with the codebase, and it is
especially awkward for follow-up questions whose subject depends on earlier
user intent. Conversely, indiscriminate all-code context is not a reliable
solution: large repositories exceed practical budgets, and the presence of
more code does not establish that the agent will identify the decisive evidence.

The engineering problem is to discover relevant evidence automatically, preserve
enough information to support the task, and bound the complete supplied packet.
The research problem is to establish the trade-off between smaller context and
retained evidence, rather than equating compression with correctness. A separate
sustainability problem is to make the energy implications inspectable while
acknowledging uncertainty in model and hardware assumptions.

The supplied SWE-Pruner paper motivates task-conditioned code skimming. The
supplied SEAL paper motivates benchmark-informed, phase-specific energy
estimation. Their published results establish a research basis, not TokenWise's
own answer-quality or energy-metering results. [R1, R2]

### 1.3 Objectives

**Table 1. Project objectives, implementation, and assessment.**

| ID | Objective | Implemented mechanism | Assessment |
|---|---|---|---|
| O1 | Reduce manual repository selection | Prompt-driven lexical and structural retrieval | Automatic input traces, workspace tests, demonstration procedure |
| O2 | Focus code on the current task | Goal compiler, pretrained neural line scoring, explicit source scope | Selected-source outputs and matched excerpt study |
| O3 | Keep supplied context bounded | Tokenizer-aware final packet packing | Budget assertions and recorded study packets |
| O4 | Preserve useful cross-file context | Dependency/caller expansion, test discovery, short-source/interface handling | Candidate coverage and packed evidence measurements |
| O5 | Support relevant follow-up intent | Bounded same-chat user-reference selection | Memory contract tests and controlled memory ablation |
| O6 | Support grounded agent responses | Task-aware response guidance, provenance and uncertainty instructions | Template/budget tests; downstream improvement remains unmeasured |
| O7 | Expose sustainability assumptions | Separate prefill/decode regressors and carbon conversion | Artifact metrics and configured before/after estimates |
| O8 | Make the extension usable by others | Managed setup, arbitrary-workspace links, retries, diagnostics, VSIX | Setup/lifecycle tests and recorded distribution checks |
| O9 | Keep results inspectable and comparable | Result panels, line masks, memory traces, packet and usage export | UI tests, browser fixtures, study artifacts |

These objectives describe delivered mechanisms and evaluation questions. They
do not imply that every task improves, that every necessary line survives, or
that actual cloud billing and total carbon are reduced in every workflow.

### 1.4 Scope and Evolution

The proposal defines a task-aware skimming, context-pruning, and carbon-tracking
cycle. The implementation extends that cycle with repository discovery,
editor integration, installation and lifecycle handling, explicit measurement
baselines, and bounded conversation memory. These additions make the research
ideas usable as a local developer tool. [R3]

**Table 2. Proposal-to-implementation scope.**

| Proposed direction | Current realization | Boundary |
|---|---|---|
| Goal-driven hint generation | Deterministic structured compiler; optional local model | Default mode makes no extra goal-generation LLM call |
| Line-level neural skimming | SWE-Pruner-derived pretrained runtime | Upstream checkpoint was not trained from scratch by this project |
| Adaptive pruning | User threshold, tier-dependent treatment, source/interface policies | Not a universal syntactic or semantic preservation guarantee |
| Benchmark feature fusion | Performance/quality data preparation and local training | Local corpus, target reconstruction, and evaluation differ from SEAL |
| Prefill/decode carbon estimation | Four phase/range artifacts with model registry | Approximate workload scenarios, not direct provider telemetry |
| Sustainability dashboard | Manual and asynchronously enriched automatic results | Failure of estimation does not invalidate prepared context |
| Lower cost and better answers | Packet comparison and actual-usage import support | Full live answer-quality/billing improvement remains unestablished |

Repository intelligence currently targets Python. A neural endpoint accepting
arbitrary text is not equivalent to repository-aware support for every language.
The supported setup scope is local trusted folders. Windows is the tested native
platform. Portable launchers exist for macOS/Linux, but native validation on
those systems has not been completed. Remote, virtual, browser, and first-run
WSL/dev-container workspaces are not claimed as supported.

### 1.5 Deliverables and Contribution

The delivered project contains a TypeScript editor extension, a local FastAPI
service, Python AST indexing and structural retrieval, neural pruning integration,
bounded packing, goal and response-guidance templates, same-chat reference
selection, a trained estimation workflow, recoverable backend installation,
owned-resource cleanup, and a single runnable teaching application.

The contribution is the design and engineering of this connected workflow:
discovering repository evidence from a prompt, managing computational and packet
limits, exposing provenance, integrating with the editor, and validating the
resulting system. The student developed and adapted these project components.
Pretrained Qwen/SWE-Pruner assets and the followed research remain credited to
their original creators. Building this application from its requirements does
not mean inventing its third-party model architecture or pretrained weights.

### 1.6 Evidence Basis and Terminology

Source descriptions in this report were checked against the current manifest,
retrieval/indexing modules, neural wrapper, carbon pipeline, workspace setup,
demonstration, and saved evaluation artifacts. Test counts refer to recorded
verification on 9 October 2026, not to a newly rerun complete suite during the
writing of this document. The current checkout includes later documentation
commits; experiment records retain their original implementation revision.

**Table 3. Terminology and evidence categories.**

| Term | Meaning |
|---|---|
| Goal | Structured description of the developer's current information need |
| Candidate | File discovered before final packet allocation |
| Anchor | Selected editor source or a file chosen from the task |
| Neural pruning | Learned relevance scoring followed by line selection |
| Interface representation | Structural declarations with implementation bodies omitted |
| Packet | Complete supplied context including source, headings, fences, guidance, and references |
| Token budget | Limit measured with the backend tokenizer, not a provider billing limit |
| Memory | Selected earlier user references, not the whole conversation |
| Evidence anchor | Study proxy requiring a source declaration and a selected body line |
| Ablation | Experimental condition isolating or omitting a component |
| Carbon estimate | Modeled operational inference emissions under stated assumptions |
| Fixture | Controlled test data; not an observed live model outcome |

Implemented capability, observed software behavior, local research measurement,
published paper result, and proposed future evaluation are kept separate
throughout the report.

## 2. Requirements Analysis

### 2.1 Requirement Identification

The `TW-FR-*` and `TW-NFR-*` identifiers below are reporting identifiers created
for this final document. They are not presented as identifiers from the proposal.
Their purpose is to connect obligations to implemented modules and evidence.
Acceptance is scoped to exercised contracts rather than universal correctness.

### 2.2 Functional Requirements

**Table 4. Functional requirements and traceability.**

| ID | Requirement | Implementation and evidence | Limitation |
|---|---|---|---|
| TW-FR-01 | Install and register a usable local backend | Managed backend and installer checkpoint tests | Initial Python/dependency/model access required |
| TW-FR-02 | Retry individual failed installation stages | Verified state, substep reuse, retry controls | Unresolved permissions/network failures still block setup |
| TW-FR-03 | Enable any trusted local Python workspace | Central registration link, owned rule/launchers, setup tests | No requirement that the workspace be inside this checkout |
| TW-FR-04 | Preserve unrelated workspace customization | Validated merges and ownership hashes | Malformed/customized owned files require explicit recovery |
| TW-FR-05 | Index saved Python source and refresh changes | AST cache, watchers, update/reconcile endpoints | Unsaved editor buffers are not the repository snapshot |
| TW-FR-06 | Interpret tasks and identify ambiguity | Structured deterministic goal compiler and optional local model | Clarification flag is guidance, not a forced dialog |
| TW-FR-07 | Discover relevant files without selection | Weighted lexical postings, symbols, graph expansion | Static heuristics may miss dynamic relationships |
| TW-FR-08 | Include relevant dependencies and tests when found | Forward/reverse graph and task matching | Candidate discovery does not guarantee final body retention |
| TW-FR-09 | Prune selected files or text with explicit scope | Direct pruning commands and input trace | Result may omit decorators, imports, or necessary conditions |
| TW-FR-10 | Provide broad repository overviews | Documentation, repository map, representative source mode | Bounded overview is not exhaustive coverage |
| TW-FR-11 | Bound the complete outgoing packet | Tokenizer-aware packing and budget checks | Correct size does not prove correct evidence |
| TW-FR-12 | Add task-aware response guidance | Versioned profiles and bounded instruction insertion | Cannot replace or enforce Antigravity's system prompt |
| TW-FR-13 | Use relevant prior same-chat user intent | Bounded lexical memory, provenance, latest-request precedence | No perfect semantic memory or full transcript injection |
| TW-FR-14 | Deliver context in Antigravity | Native supported hook or workspace rule/command | Fallback depends on agent compliance and command permission |
| TW-FR-15 | Show provenance and source decisions | Result panel, file relations, masks, memory/source traces | UI values must be interpreted with their declared baseline |
| TW-FR-16 | Estimate defined before/after impact | Carbon request with shared model/hardware assumptions | Estimates exclude physical local/cloud metering |
| TW-FR-17 | Compare/export context strategies | Explicit all-code/selected/automatic packets and JSON | All-code baseline is hypothetical, not native agent telemetry |
| TW-FR-18 | Import genuinely reported agent usage | Independent successful CLI log validation | Does not launch paid runs or observe private IDE counters |
| TW-FR-19 | Remove owned resources conservatively | Registry, validated paths/hashes, process identity checks | Modified/shared/unverifiable resources may be retained |

The normal user workflow primarily exercises TW-FR-01 through TW-FR-08 and
TW-FR-11 through TW-FR-16. Manual selected-source commands are complementary
inspection tools, not mandatory steps before every automatic prompt.

### 2.3 Non-Functional Requirements

**Table 5. Non-functional requirements and boundaries.**

| ID | Category | Requirement and assessment boundary |
|---|---|---|
| TW-NFR-01 | Usability | A normal user installs the VSIX and follows managed setup, without compilation/F5 |
| TW-NFR-02 | Recoverability | Failed stages identify their cause and support retry without erasing verified downloads |
| TW-NFR-03 | Freshness | Saved source fingerprints and watcher sequences invalidate affected cached results |
| TW-NFR-04 | Performance | Reuse indexes and search data; bound candidate/neural work; measure cold/warm paths separately |
| TW-NFR-05 | Explainability | Show task, scope, selected files, pruning method, memory provenance, and estimator assumptions |
| TW-NFR-06 | Safety | Require trusted local setup, reject escaped paths, and preserve unrelated resources |
| TW-NFR-07 | Privacy | Process retrieval locally while disclosing downstream model transmission and setup downloads |
| TW-NFR-08 | Compatibility | Operate in the tested Windows editor workflow; disclose untested portable platforms |
| TW-NFR-09 | Maintainability | Separate editor services, backend contracts, retrieval, neural runtime, training, and evaluation |
| TW-NFR-10 | Scientific integrity | Preserve signed changes, failures, missing usage, and limitations without invented superiority |

No universal response-time target or formal accessibility certification is
invented. Responsiveness depends on model input length and hardware; the full-file
CPU pilot demonstrates why indexing performance alone cannot establish the
latency of the entire extension.

### 2.4 Users and Use Cases

The primary user is a developer asking questions about a Python repository.
The evaluator is a teacher inspecting functionality and research evidence.
The maintainer installs dependencies, runs tests, packages releases, and diagnoses
backend issues. These roles describe tasks, not authenticated accounts; the
local extension does not implement a multi-user service.

The main use case is: open a repository, configure it once, submit an ordinary
question, receive fresh automatic context, and inspect the resulting explanation.
Alternative cases include selected-file pruning, selected-excerpt pruning,
repository overview, follow-up memory inspection, comparison export, and retry
after a failed setup stage. Exceptional cases include no Python source, ambiguous
task, unavailable model, stale comparison snapshot, and unsafe cleanup targets.

## 3. Component Level Design

### 3.1 Overall Architecture

The editor extension manages user interaction and integration. It communicates
with a local HTTP service that owns expensive model loading and repository
processing. A central managed backend can serve several configured workspaces,
while small workspace links and launchers point to that installation. This
separation prevents each repository from needing its own model download and
private environment.

At runtime, the Python backend indexes saved source, compiles a goal, retrieves
and ranks candidate files, applies task-appropriate reduction, and constructs a
bounded reference packet. The agent receives that packet through a supported
hook or local command output. A separate extension-side request enriches fresh
automatic results with carbon estimates; context retrieval need not wait for
that enrichment.

The normal backend binds to loopback. Antigravity's downstream model may still
be hosted externally. Initial setup contacts dependency/model hosts, and an
optional goal-generation model can introduce another configured endpoint.
Local retrieval therefore does not mean the complete workflow is offline or
that all supplied source remains on the machine.

<span style="color: #ff0000;">ADD DIAGRAM - Figure 1: Draw the developer, Antigravity editor/agent, TypeScript extension, local FastAPI backend, index/retrieval/pruner, carbon artifacts, and managed storage. Show local loopback requests separately from initial downloads and downstream model transmission. Caption: TokenWise runtime architecture and local/external processing boundaries.</span>

### 3.2 Component Responsibilities

**Table 6. Major components and responsibilities.**

| Component | Responsibility | Principal collaborators |
|---|---|---|
| Extension activation | Register commands, monitors, index synchronization, and lifecycle services | VS Code APIs and editor services |
| Backend manager | Find installation, start verified service, check health | Managed registration and setup controller |
| Automatic workspace setup | Merge configuration, generate owned rule/launchers, register workspace | Cleanup registry, filesystem validation |
| RepositoryIndexSync | Debounce saved changes and renew watcher leases | `/index-workspace`, local workspace link |
| GoalCompiler | Convert query/evidence into structured information need | Task templates, optional generator, scope extraction |
| RepositoryIndex | AST/source metadata, content hashes, incremental updates | PythonASTIndexer, lexical features |
| LexicalRetriever | Weighted term and exact-symbol discovery | Cached postings and file features |
| DependencyGraph/GraphRetriever | Resolve approximate relationships and traverse neighbors | Indexed imports/calls and reverse links |
| WorkspaceContextBuilder | Combine modes, scope, ranking, caching, guidance, and packing | Goal, graph, model, ContextBuilder |
| Neural pruner | Score goal-conditioned tokens and select source lines | Pretrained backbone, compression/document heads |
| ContextBuilder | Allocate source/interface excerpts under final packet budget | Tokenizer, pruning results, metadata |
| Conversation selection | Select same-chat user intent and constraints | Scoped transcript or labeled fallback input |
| Response guidance | Insert bounded task-profile instructions | Goal task type and packet tokenizer |
| Carbon estimator | Resolve scenario features, predict phase energy, convert to carbon | Registry and trained artifacts |
| ResultPanel | Present outputs, provenance, comparisons, copy/export | Validated extension-side result data |
| Usage importer | Validate paired reported CLI records | Session/model/status/tool parsing |
| Cleanup/uninstall | Remove verified owned resources without broad deletion | Paths, hashes, process identities, registry |

These responsibilities are implemented across classes and functions. The table
does not imply that each conceptual stage is an independent process or a class.

### 3.3 End-to-End Task Lifecycle

Enabling a workspace creates a small local integration configuration and a link
to the registered backend. When a configured trusted folder opens, the extension
can warm the repository index in the background. Saving source causes targeted
updates rather than an unconditional rescan of all files on each normal watched
request.

For a focused question, the backend compiles a goal, retrieves lexical matches,
adds exact identifier seeds and structural neighbors, prioritizes the likely
anchor and relevant configuration, and applies explicit topic scope. Automatic
retrieval uses neural pruning on a bounded subset of candidates and reuses the
same result's document score for ranking. Remaining candidates may use compact
interfaces, or retain short task-matched source where the policy allows it.

The packer includes task guidance and selected earlier references only when
they fit alongside an evidence reserve. It records file relations, tiers,
pruning methods, thresholds where meaningful, and source/token metrics. The
adapter records activity and returns context. The extension then displays the
fresh result and, independently, estimation or comparison enrichment when
requested. Each stage can report its own failure rather than fabricating an
otherwise successful observation.

Overview questions take a separate path: representative architecture and project
documents are more useful than a narrow neural search for words such as
"project." That path avoids neural line pruning, selects source/document
representations, allocates space across components, and discloses omitted
coverage or scaffold-only source.

<span style="color: #ff0000;">ADD DIAGRAM - Figure 2: Draw goal compilation, repository index, focused retrieval/scope, neural-or-interface reduction, budget packing, activity recording, and delivery. Add a distinct overview branch using documents/map/representative source without neural line pruning. Caption: Task-to-context activity flow and the separate overview path.</span>

### 3.4 Structured Goal Compilation

The deterministic compiler recognizes information needs such as fixing,
debugging, refactoring, adding features, generating tests, and understanding
behavior. It produces a task type, objective, identifiers, observed diagnostics,
retrieval questions, required context, exclusions, and ambiguity status as
applicable. This gives retrieval and pruning a more explicit focus than passing
an isolated filename.

The optional local generator receives a constrained JSON task. Returned
identifiers are filtered against words present in the query or available editor
evidence. Generation is opt-in; failure falls back to the deterministic path.
The default workflow does not require Ollama or another goal-generation model.

Vague requests and unresolved follow-ups can set `clarification_required`.
The packet then advises clarification. This is not a dedicated enforced
conversation state machine: the downstream agent must still decide how to
respond. Rule-based task classification is also not perfect intent understanding;
its behavior depends on wording and supplied evidence.

### 3.5 Python AST Indexing

The indexer uses Python's standard `ast` parser rather than executing repository
modules. It records functions/classes, line ranges, imports, calls, selected
class relationships, and test indicators. Interface construction retains
structural declarations, imports and assignments while replacing function
bodies with ellipses where appropriate. This avoids repeatedly generating
free-form summaries and preserves real signatures/defaults better than an
invented explanation.

Source content remains available even when parsing fails; structural metadata
can be empty and interface generation limited. The existence of source in the
index does not prove successful semantic analysis. Dynamic imports, aliasing,
reflection, inherited APIs, and complex cross-file resolution remain limitations
of a lightweight static index.

The repository walker excludes known environment, generated, editor, and runtime
directories including `.git`, `.venv`, `node_modules`, `__pycache__`, `build`,
`dist`, `.agents`, and `.tokenwise`. Its eligible repository scope is not a
claim to ingest every Git-tracked asset or to implement comprehensive secret
detection. Python-only indexing is distinct from bounded root-document loading
used by overview mode.

### 3.6 Incremental Updates and Search Caches

File metadata stores version information and a SHA-256 content digest. An
unchanged digest allows AST metadata and derived caches to be reused. Updates
commit a new repository fingerprint and serve copy-on-write snapshots so a
request can operate against a coherent indexed view. Escaped, excluded, missing,
renamed, and directory-subtree paths receive explicit treatment.

The editor batches change bursts with a 150 ms debounce and sends sequenced
updates. A 30-second heartbeat renews a backend watcher lease. The backend's
90-second lease prevents a closed editor from indefinitely convincing the
backend that filesystem observation remains reliable. Periodic reconciliation
approximately every 120 seconds verifies bytes, including changes whose file
timestamps were preserved. When no valid watcher exists, retrieval conservatively
checks the repository before serving a request.

Freshness is eventual across these boundaries: a just-saved edit becomes
available after its update completes, while a missed event can remain unseen
until reconciliation. This is not a promise of instantaneous unsaved-buffer
visibility. Multiple revisions and sequence checks guard against late updates
overwriting newer state.

Prepared lexical postings and dependency graphs are cached by workspace and
repository fingerprint. Source metadata carries term counts, interfaces, and
token-count caches. These reusable search structures benefit different queries.
Complete prepared answers require an exact cache key including query, structured
goal, snapshot, active file, thresholds, budget, candidate limit, reference hint,
and guidance version/state. Similar-looking prompts are not treated as identical.

### 3.7 Lexical Retrieval

Search normalizes snake-case and camel-case identifiers, lowercases terms, and
applies a small plural normalization. It removes common task words and considers
positive query scope. Each file's cached feature combines content frequency,
path terms, and symbol terms. A term contributes a capped content count, plus a
path weight of five and a symbol weight of three. An inverse-frequency factor
reduces the value of common words.

The implemented scoring can be summarized as:

```text
term_weight = ln(1 + number_of_files / (1 + content_document_frequency))
file_term_evidence = 5 * path_match + 3 * symbol_match + min(content_count, 4)
file_score = sum(term_weight * file_term_evidence for matching query terms)
```

This is a lightweight weighted lexical method, not a claim of full BM25,
embedding retrieval, or universal semantic matching. Exact class/function
identifiers add seeds separately. The lack of a useful lexical match is reported
or handled through fallback anchoring rather than an invented high-confidence
match.

### 3.8 Structural Retrieval and Explicit Topic Scope

The dependency graph stores forward import/call approximations, reverse
dependents, and symbol definitions. Two-hop neighbor retrieval can expose an
implementation's configuration and callers, including tests that import or
exercise it. Reverse links matter because a service typically does not import
its own tests.

Automatic retrieval can reserve short configuration dependencies so candidate
expansion does not crowd out constants. Positive lexical evidence and neural
document scores are combined for ordering. Static graph matches remain
heuristics, not a sound whole-program call graph.

Scope processing recognizes explicit exclusions such as "session expiry, not
invoice pricing." It can filter unrelated symbols even when they share one
file. Shared imports, configuration, or supporting declarations may remain when
necessary to interpret the included behavior. An exclusion therefore does not
mean deleting every occurrence of an associated word regardless of dependency.

### 3.9 Neural Pruner and Research Foundation

The supplied SWE-Pruner research describes goal-conditioned code skimming that
scores source relevance and returns selected lines. TokenWise integrates that
approach through a pretrained runtime associated with a Qwen3-Reranker-0.6B
backbone. The approximately 1.35 GB checkpoint is a downloaded third-party
asset, not a new language model trained in this application. [R1, R4]

The model uses token-level compression and document-level relevance outputs.
Its multi-layer path combines earlier, middle, and later backbone
representations before compression processing. The runtime converts token
logits to sigmoid probabilities and aggregates relevant code token positions
into line scores. At the requested threshold, scored lines are retained, with
limited preservation/readability and gap-bridging behavior.

Although the implementation includes CRF-related components, the deployed
pruning wrapper's selection is based on probabilities and line thresholds.
It should not be described as using Viterbi decoding for every live prune.
Likewise, a reported relevance score is not a calibrated probability that an
answer is correct.

The working model window is 8,192 tokens including query/instruction overhead.
Long source is split into overlapping chunks, processed, and mapped back to
original positions. Input is not padded to a full 8k sequence for every small
request, avoiding unnecessary CPU work. Nonetheless, long inputs and fusion
attention can impose substantial time and memory cost. The failed CPU pilot in
Chapter 7 is evidence of this remaining constraint.

### 3.10 Line Decisions and Semantic Boundaries

A line at or above threshold can be selected; optional first-fragment
preservation and one-line gap bridging can change the decision mask. Output
formatting can restore tiny gaps when a filtered marker would cost more than
the original text. Consequently the decision mask, emitted source, and measured
token difference are related but not identical representations.

Filtered-line markers tell the agent that surrounding source was omitted.
They are not Python syntax and do not make an excerpt executable. The pruner
does not universally preserve imports, decorators, enclosing conditions,
exception paths, or invariants. For example, retaining the `Session` class fields
but removing `@dataclass` loses useful initialization/equality context. An agent
must inspect originals before editing or making claims that the excerpt cannot
support.

Lower thresholds generally retain more scored material; higher thresholds can
remove more evidence. They do not guarantee a target compression ratio or
monotonic downstream answer quality. The defaults must be evaluated against
real tasks, not justified by a large reduction percentage alone.

### 3.11 Tiered Packing and Complete-Packet Budget

Tier 1 represents the active or prompt-selected anchor with relatively light
pruning. Tier 2 handles direct/high-relevance evidence more aggressively. Tier 3
can use interfaces for distant or unpruned dependencies. The current automatic
path bounds neural work to a small subset, reuses prepruned results, and can
retain short task-matched source. Manual anchored workflows can use a different
ranking/pruning sequence. These are policies, not equal treatment of every file.

The final budget includes all formatting, path headers, fenced blocks, relation
labels, safety text, guidance, repository map, and selected references. The
packer calculates available space, truncates content when necessary, and
recounts the concatenated packet before accepting a block. It stops when the
next block cannot fit. Overview mode also reserves a fair share for later
components instead of letting a long README consume the entire packet.

The hard bound controls the context supplied by TokenWise. It does not constrain
Antigravity's system instructions, extra tool reads, subsequent rounds, or
provider-tokenizer accounting. Nor does it guarantee complete evidence: a
relevant candidate can be present as an interface while its decisive body is
missing. Chapter 7 measures precisely this distinction.

### 3.12 Token Statistics and Honest Reduction

Source-only counts compare included original content with retained content.
Packed counts describe the complete supplied reference. Formatting overhead is
reported separately, with care that tokenization across boundaries is not
strictly additive. A raw-context baseline can retain matching packet formatting
to make a like-for-like comparison.

For a positive baseline `B` and prepared packet `P`, the signed difference is:

```text
token_difference = B - P
reduction_percent = 100 * (B - P) / B
```

A zero baseline makes the percentage undefined and should be N/A. Negative
values are genuine increases under the defined comparison, not percentages to
clamp into a misleading saving. A separate source-only reduction must not compare
17 source tokens against a 117-token wrapper. If all 17 source tokens remain,
source reduction is zero; the additional 100 tokens are overhead. This explains
and corrects the earlier misleading -588.24% presentation without asserting
that small packets never expand.

### 3.13 Outgoing Prompt Engineering

TokenWise adds versioned response guidance separate from repository reference
data. Common guidance asks the agent to honor the latest request and constraints,
cite real files/symbols, inspect originals when evidence is omitted, distinguish
facts from assumptions, and avoid claiming unexecuted tests passed. Task profiles
specialize this for bug fixes, refactors, features, tests, overviews, and generic
explanations.

The guidance follows full, compact, or omitted forms. Its insertion limit is at
most 160 tokens or one quarter of the configured packet budget, and it retains
an evidence reserve of 96 tokens. It adds no extra LLM inference call. State and
template version participate in cache identity.

These are real prompt-engineering mechanisms: task framing, constraint
preservation, grounded-answer instructions, explicit uncertainty, and separation
of instructions from source data. They are designed to support better answers,
but this project has not yet established their downstream improvement through a
controlled live guidance-on/off answer-quality study.

### 3.14 Bounded Conversation Memory

Version 0.6.8 selects relevant earlier user intent instead of using only the
latest message. It considers bounded user-turn candidates and recognizes
topic continuity, follow-ups, recognized requirements, resets, and supersession
through deterministic lexical heuristics. It excludes assistant answers, tool
output, and previously injected packets to avoid treating generated claims as
new user requirements.

Candidate storage is bounded to 32 turns, each at most 2,000 characters. Up to
eight selected earlier turns share at most 4,000 characters. A native transcript
reader scans a bounded 16 MiB tail and up to 64 qualifying earlier user turns
before normalization. Identity checks require a matching conversation identity
or verified chat-scoped path; state from another chat is not automatically
carried forward.

Fallback transport accepts separately supplied user references and labels their
origin. It is not an invisible unrestricted reader of the native IDE chat.
The outgoing quoted reference block is at most 384 tokens or a quarter of the
packet, can be compact or omitted, and preserves an evidence reserve. The
inspector distinguishes selection from the actual outgoing reference status.
The latest activity file remains a latest-result record, not a complete archive
of every message. Lexical selection is useful but cannot guarantee perfect
meaning recognition or preservation of all historical constraints.

### 3.15 Persistent Data and Ownership

**Table 7. Storage and ownership categories.**

| Data category | Purpose | Ownership/freshness boundary |
|---|---|---|
| Managed private environment | Backend dependencies and interpreter | Installed in user/profile-managed storage, not each repository |
| Registration and workspace link | Resolve central runtime | Verified paths and schema; repository does not choose arbitrary executable settings |
| Downloaded checkpoint/tokenizer | Local neural inference | Pinned integrity checks; third-party license applies |
| Carbon artifacts and registry | Scenario predictions and feature lookup | Versioned local files; not live provider instrumentation |
| In-memory repository/search caches | AST, features, postings, graph, exact context reuse | Fingerprint and watcher/reconciliation invalidation |
| `.agents` owned files | Rule, configuration, hook/launcher integration | Merge rather than erase unrelated customization |
| `.tokenwise/latest.json` and related state | Latest activity/provenance and bounded reference state | Snapshot/task/event interpretation required |
| Evaluation records | Reproducible study cases, pins, results, summaries | Separate from runtime state and from physical energy logs |

There is no PostgreSQL or other relational service in the normal TokenWise
architecture. A database ER diagram copied from the friend's report would be
misleading. Its appropriate data design is file ownership and cache/snapshot
relationships.

<span style="color: #ff0000;">ADD DIAGRAM - Figure 3: Show a central managed registration referenced by workspace links, owned rule/configuration/launchers, latest activity, bounded user-reference state, and source-fingerprint-linked in-memory caches. Keep research artifacts separate. Caption: Repository metadata, cache, and owned-file relationships.</span>

### 3.16 Backend Contracts and Concurrency

**Table 8. Backend API contracts.**

| Operation | Purpose | Important boundary |
|---|---|---|
| `GET /health` | Report service/model/estimator readiness | Availability is not pruning accuracy |
| `POST /index-workspace` | Start/update/reconcile/stop sequenced watcher state | Valid local paths, bounded update lists |
| `POST /prune` | Direct task-conditioned text pruning | Threshold and input scope explicitly supplied |
| `POST /prune-workspace` | Goal/retrieval/packing for a repository | Valid workspace and total packet budget |
| `POST /compare-workspace` | Build explicit comparison strategies | Selected-source validation and export guardrails |
| `POST /compare-prepared-workspace` | Compare an already prepared packet without another prune | Reconciled snapshot must match; stale comparison rejected |
| `POST /estimate-carbon` | Estimate prefill/decode energy and emissions | Requires valid token counts and scenario features |

Pydantic models validate request types and ranges. Missing neural readiness can
produce a 503; invalid workspace/input can produce a client error. Oversized
comparisons use 413 and stale/inconsistent prepared comparisons can use 409.
These are explicit failure states rather than valid zero-valued results.

Neural requests share an inference lock to avoid uncontrolled CPU
oversubscription. Default CPU parallelism is four threads, bounded by configured
limits. Serialization protects resource use but can queue requests; concurrent
users or workspaces do not gain unlimited independent model throughput.

**Table 9. Important defaults and limits.**

| Setting | Current scope/value |
|---|---|
| Extension version | 0.6.8 |
| Manual repository-context budget | 8,192 tokens by default |
| Newly generated automatic workspace budget | 4,096 tokens |
| Automatic workspace candidate default | Six |
| Backend request candidate range | One through 32; default eight |
| Repository budget range | 256 through 32,768 |
| Default extension threshold | 0.45 |
| Prepared retrieval cache | Up to eight workspace entries |
| Complete workspace-context cache | Up to sixteen exact entries |
| All-code comparison export guard | At most 200 Python files and 2 MiB source |
| Default estimator model | `meta-llama-3-8b-instruct` |
| Default expected output | 256 tokens |
| Default carbon intensity | 475 gCO2/kWh |

Defaults differ by workflow and existing user settings are preserved. A study
using eight candidates is not the same configuration as a fresh automatic
workspace using six.

### 3.17 Carbon Data Preparation and Training

The estimation workflow follows the SEAL idea of combining benchmark-derived
performance attributes with model-quality attributes and training separate
phase models. The local pipeline acquires/normalizes performance and quality
tables, matches model/precision identity, handles GPU categories, constructs
features, splits by configured size range, cross-validates, fits, and saves
artifacts. [R2]

Recorded local preparation contains 1,612 normalized quality rows and 12,822
normalized performance rows. Merge statistics record 3,407 matched rows and
101 final deduplicated rows. These numbers differ from the paper's corpus and
must not be described as an exact replication. Performance inputs include
multiple configurations, so careful identity/deduplication matters.

Eight numerical/encoded feature columns are input tokens, output tokens, model
size, per-input-token latency, per-output-token latency, GPU category, MMLU-Pro,
and BBH. Quality scores are explanatory features associated with models, not
the quality score of the current user prompt. GPU encoding is a local categorical
representation, not a physical law of energy consumption.

Measured energy fields are converted to joules where present. The fetch pipeline
can synthesize missing phase energy from GPU TDP and latency assumptions. Those
targets are proxies, not independently measured ground truth. Their presence
limits the strength of later accuracy claims and can create dependence between
latency predictors and constructed targets.

Four artifacts are trained: prefill/decode XGBoost interpolation models and
prefill/decode Ridge extrapolation models. The local configured interpolation
range is 7 through 111 billion parameters. Training uses five shuffled KFold
splits with seed 42, not the paper's ten-fold evaluation. XGBoost uses 100
estimators, depth three, and learning rate 0.3; Ridge uses alpha 1.0.

**Table 10. Recorded carbon-model cross-validation metrics.**

| Artifact | MAPE | MAE, J | RMSE, J | R-squared |
|---|---:|---:|---:|---:|
| XGBoost prefill interpolation | 13.83% | 16.846 | 32.349 | 0.879 |
| XGBoost decode interpolation | 22.41% | 409.597 | 1,008.756 | 0.246 |
| Ridge prefill extrapolation | 22.08% | 2.776 | 4.251 | 0.993 |
| Ridge decode extrapolation | 46.59% | 109.631 | 149.419 | 0.901 |

These are recorded local artifact metrics, not measurements rerun for this
report. Weak decode interpolation fit and high decode extrapolation percentage
error constrain confidence. High R-squared alone does not establish small
relative error or reliable behavior outside the observed data. Random-row
validation is also weaker than a fully independent model/hardware holdout.

A separate saved two-sample external-reference check reports approximately
365.72 J against 349.96 J for one sample, and 419.12 J against 602.27 J for the
other, averaging 17.46% relative error. This is a small published-reference
comparison, not a local power-meter experiment or broad external validation.
The artifact files are linked in References.

### 3.18 Runtime Energy and Carbon Calculation

Runtime feature lookup uses a model registry and explicit request overrides.
The estimator identifies the feature source and interpolation/extrapolation
route. Missing or incompatible artifacts lead to unavailable/error reporting,
not silently successful carbon measurement.

The local artifact convention predicts a reference workload of 256 input and
128 output tokens. Phase predictions are then scaled once to the request's
actual token counts, avoiding using the actual count both as a feature and as a
second multiplier:

```text
prefill_J = max(0, reference_prefill_J) * actual_input_tokens / 256
decode_J = max(0, reference_decode_J) * expected_output_tokens / 128
total_J = prefill_J + decode_J
CO2_g = total_J / 3,600,000 * intensity_g_per_kWh
estimated_difference_g = before_CO2_g - after_CO2_g
```

This linear phase-scaling convention is an explicit approximation. It does not
model all batching, caching, queueing, quantization, network, or datacenter
effects. When expected output length remains fixed, decode estimates remain
fixed while input reduction changes prefill. Input-token reduction therefore
need not equal total energy or carbon reduction.

The estimates omit TokenWise's own inference/index/setup energy, downloaded
model training, idle backend use, embodied hardware, and unknown future agent
rounds. An avoided-input scenario is not proven net environmental benefit.
The configured target model is not automatically Antigravity's actual model.

### 3.19 Integration, Trust, and Cleanup

Native-hook support can inject context where the editor exposes a compatible
invocation event. Stable fallback behavior uses an always-on workspace rule
that asks the agent to run a local launcher and read its output. The fallback
depends on the agent following the rule and having permission; it is not
universal interception before the first model call. Neither mode claims to
replace every subsequent native file read.

Repository excerpts are labeled reference data rather than instructions.
The backend installation is centrally registered rather than blindly chosen
by arbitrary repository settings. Workspace setup rejects unsafe escaped/link
targets and preserves unrelated customizations. These are practical safety
controls, not a formal guarantee against prompt injection or malicious local
processes. The loopback service is not an authenticated public internet API.

Cleanup uses recorded ownership, content hashes, path constraints, and verified
process identity. PID reuse and junctions make broad deletion or stopping every
process with a saved PID unsafe. Customized owned files, unverifiable processes,
and user-owned checkout backends can be preserved with warnings. The project
must not promise that uninstall deletes every file containing the word
TokenWise, including user data and shared caches.

<span style="color: #ff0000;">ADD DIAGRAM - Figure 4: Show user prompt, supported hook or rule-triggered launcher, backend request, packed context/tool output, activity record, result monitor, and separate carbon/comparison enrichment. Show failures and permission dependence. Caption: Automatic prompt retrieval and asynchronous result enrichment.</span>

## 4. Interface Design

### 4.1 Users, Navigation, and Interaction Model

TokenWise uses the editor's command palette, status bar, output channels, and
result webview. It does not require a separate website or a sequence of forms
before each task. Automatic results can open beside the editor without taking
keyboard focus, keeping the prompt workflow central while making the context
visible.

The status bar offers a compact indication of current automatic activity.
Detailed panels expose selected files and excerpts. Diagnostics and setup
channels serve recovery. Commands that build context manually coexist with
automatic integration so a teacher can inspect the exact input scope and
selection process.

### 4.2 Interface Objects and Actions

**Table 11. Interface objects and user actions.**

| Object/control | Action | Observable result |
|---|---|---|
| Install from VSIX | Install downloaded package | TokenWise listed with version/icon |
| Set Up Backend | Start or update managed installation | Numbered stages, progress, logs, retry |
| Enable Automatic Context | Configure selected workspace | Owned rule/launchers and central link |
| Automatic status | Inspect prepared activity | Current versus last/test result labeling |
| Repository Context | Read included files and unified context | Relations, tiers, token metrics, warnings |
| Prune Current File / Selected Code | Supply task for explicit source | Original/pruned content and source trace |
| Line decisions | Inspect selected mask and mean relevance | Source-line relevance and preservation detail |
| Conversation memory | Expand selected references | Turn selection, origin, omissions, outgoing status |
| Carbon result | Inspect scenario | Phase joules, before/after CO2, assumptions |
| Configure Automatic Comparison | Enable/disable/retry local comparison | All-Python and exact prepared packet comparison |
| Compare Context Strategies | Compare selected/all/automatic inputs | Labeled packet strategy results and export |
| Import Antigravity Usage Comparison | Select real independent CLI logs | Reported counters/answers/tools or validation error |
| Copy/Export | Transfer displayed context or evidence | Clipboard or downloadable JSON/message feedback |
| Diagnose Setup / guides | Inspect readiness/instructions | Relevant error, environment, next action |

### 4.3 States, Freshness, and Failure Feedback

**Table 12. Operational states and recovery.**

| State | Meaning | User response |
|---|---|---|
| Awaiting prompt | Configured but no current automatic result | Submit an ordinary question in a new chat |
| Setup in progress | Backend dependencies/assets being prepared | Wait or inspect the current numbered step |
| Setup failure | Identified stage did not complete | Correct cause and retry that step |
| Ready context | Current task produced a packet | Inspect actual chat delivery and source evidence |
| Last result | Saved historical activity | Do not treat it as a fresh response |
| Verification/test result | Controlled validation activity | Do not relabel it as a live agent run |
| Carbon pending/disabled/unavailable | Separate estimation state | Context can remain useful; inspect estimation settings/errors |
| Comparison pending | Background measurement not finished | Keep the fresh prepared result and await enrichment |
| Comparison stale/unavailable | Snapshot changed or size/service guard failed | Submit a new prompt or retry after correction |

The interface keeps successful retrieval separate from optional measurement
availability. Missing data are not displayed as measured zero. A view is
interpreted using its task, timestamp, event, and snapshot, not merely because
it is the most recently open tab.

### 4.4 Screens and Screenshot Instructions

The following instructions describe future screenshot insertion. No native
screenshots are embedded and no example screen is presented as a live result.

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 5: Capture the Extensions view after installing the actual TokenWise 0.6.8 VSIX. Keep the extension name, icon and installed version visible. Caption: Installed TokenWise extension and version.</span>

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 6: Open only demonstration/tokenwise_demo, then capture the Explorer and TokenWise automatic status bar after configuration. Caption: Configured demonstration workspace and automatic-context status.</span>

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 7: After the read-only lockout question, capture the Repository Context panel with exact task, current input mode, included files, retained source, packed tokens and budget. Caption: Bounded repository context and included source evidence.</span>

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 8: Prune security/models.py for an explanation of Session. Capture scope, threshold, original/pruned content and line decisions, including any omitted decorator/import. Caption: Selected-source neural pruning and line decisions. Do not hide evidence losses.</span>

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 9: Expand the actual outgoing packet so the Response guidance section and separate source-reference text are visible. Caption: Task-aware outgoing response guidance. This establishes instruction construction, not improved answer quality.</span>

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 10: Ask a related follow-up in the same chat and expand Conversation memory. Show current task, selected earlier user intent, source/reasons, omissions and exact outgoing-reference status. Caption: Inspectable bounded conversation memory.</span>

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 11: Capture the complete carbon section with phase energy, CO2 before/after, model, intensity and estimate disclaimer. Caption: Configured inference energy and carbon estimates.</span>

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 12: Enable local automatic packet comparison, send a fresh task, and capture both labeled packet/file lists and signed local token difference. Caption: Local all-Python versus prepared-packet comparison. Do not label these provider usage counters.</span>

### 4.5 Readability and Verification Scope

The result panel must keep task, scope, assumptions, and metrics readable without
misleading overlap. HTML escaping protects source and task text in the generated
view. Copy/export controls act on the displayed evidence, not an inferred
successful model answer.

Ten controlled browser views cover five states at desktop and narrow dimensions.
They check selected overflow/error/interaction properties of the rendered
webview, not the full native editor interface or every browser/device. Keyboard,
screen-reader, high-contrast, and broader native-editor accessibility assessment
remain further work. No formal compliance certification is claimed.

## 5. Testing

### 5.1 Testing Strategy

Testing addresses extension contracts, backend processing, demonstration
correctness, and result-panel rendering. The purpose is to verify observable
behavior at each boundary: installation recovery, safe workspace setup, source
scope, memory isolation, cache invalidation, packet limits, estimation states,
comparison identity, export behavior, and conservative cleanup.

The recorded tests use controlled doubles where deterministic behavior is
necessary. A mocked model permits precise assertions about packing and errors;
a real tokenizer permits precise local token-budget assertions. Neither alone
establishes learned relevance accuracy. The comparative study separately invokes
the real neural checkpoint on bounded excerpts.

The result summaries below are the saved verification basis from 9 October 2026.
They are not described as a fresh complete test execution performed while
writing this report. Their detailed record is [tests.md](../tests.md). [R5]

### 5.2 Pass/Fail Criteria

An executed assertion is a pass only when its runner reports success. A designed
case, inspected code, or intended screenshot is not a passed test. A skipped
case remains skipped. Expected negative-test error logs are not failures when
the assertion explicitly verifies rejection or unavailable-state behavior.

Packet correctness requires validating the complete token count and the stated
baseline; source selection requires validating actual input scope and source
identity. Memory correctness requires preventing cross-chat contamination and
respecting limits and current instructions. Setup and cleanup correctness
requires preserving unrelated files and rejecting unsafe targets. Estimation
correctness requires accurate unit conversion and assumption provenance, not
agreement with a physical meter that was never attached.

### 5.3 Recorded Results

**Table 13. Recorded software verification results.**

| Group | Discovered/exercised | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| Extension automated suite | 193 | 193 | 0 | 0 |
| Backend automated suite | 142 | 141 | 0 | 1 |
| Teaching application tests | 20 | 20 | 0 | 0 |
| Three-suite total | 355 | 354 | 0 | 1 |
| Separate browser fixture views | 10 | 10 | 0 | 0 |
| Separate study-harness checks | 10 | 10 | 0 | 0 |

The ten browser views are presentation scenarios, not ten additional backend
unit tests. The ten study-harness checks verify research instrumentation and
remain outside the 193/141/20 implementation counts. The deterministic demo
entry point also completed successfully, but is not another unittest case.

The recorded environment used Node.js 22.12.0 and Python 3.12.4 on Windows 11.
No line/branch coverage percentage, mutation score, universal correctness rate,
or 354-session live agent evaluation is supported by these totals.

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 13: Capture actual extension and backend runner summaries from a dated run, showing commands, discovered/passed/skipped totals and no hidden failures. If newly rerun totals differ, update the table rather than relabeling old evidence. Caption: Recorded extension and backend test summaries.</span>

### 5.4 Representative Test Cases and Traceability

**Table 14. Representative validation cases.**

| Case | Requirement | Input/procedure | Expected behavior | Recorded evidence and scope |
|---|---|---|---|---|
| TC01 | TW-FR-01/02 | Simulate valid/failed setup stages and rerun installer | Checkpoints verified, retry/resume bounded, corrupt assets rejected | Extension setup suites and backend `test_installer.py`; controlled paths |
| TC02 | TW-FR-03/04 | Enable a local workspace with existing rules/hooks | Owned integration added; unrelated customization preserved | `automaticSetup.test.cjs`, `enableAutomaticContext.test.cjs`; mocked editor |
| TC03 | TW-FR-05 | Save/create/delete/rename source and reconcile | Changed metadata replaces prior snapshot; late sequences do not regress state | `repositoryIndexSync.test.cjs`, `test_repository_cache.py` |
| TC04 | TW-FR-06 | Supply vague, explicit, overview and excluded-topic tasks | Correct recorded goal/scope, ambiguity remains visible | Overview/query-focus/backend contracts |
| TC05 | TW-FR-09 | Capture a file and then an exact highlighted excerpt | Captured scope and first source line differ correctly | `pruningInputs.test.cjs`, `test_demonstration.py` |
| TC06 | TW-FR-10/11 | Prepare scaffold and multi-component overview under budget | Coverage/scaffold warnings and bounded complete packet | `test_overview.py`; controlled repository fixtures |
| TC07 | TW-FR-12 | Toggle guidance and vary available budget | Full/compact/disabled/omitted trace and correct token accounting | `responseGuidance.test.cjs`, `test_response_guidance.py` |
| TC08 | TW-FR-13 | Follow-up, superseded requirement, new chat, bounded transcript | Relevant user references only, correct provenance and limits | `test_conversation_memory.py`, automatic-result tests |
| TC09 | TW-FR-16 | Before/after estimate including zero/invalid overrides | Valid assumptions preserved; failure displayed unavailable | `carbonComparison.test.cjs` and client verification |
| TC10 | TW-FR-17 | Compare saved and changed snapshots | Valid same-snapshot comparison or explicit stale rejection | `compareContextStrategies.test.cjs`, `preparedComparisonApi.test.cjs` |
| TC11 | TW-FR-18 | Pair valid/failed/resumed/identical-session usage logs | Only admissible independent reported runs accepted | `antigravityUsage.test.cjs`, `importAntigravityComparison.test.cjs` |
| TC12 | TW-FR-19 | Test owned/custom files, junctions and reused/foreign PIDs | Unsafe/unknown resources retained; unrelated resources preserved | Uninstall/ownership suites; simulated lifecycle operations |

These case descriptions summarize exercised suites rather than inventing new
per-case executions. Precise assertion names and fixture inputs remain in the
linked test directories. Passing controlled conditions does not imply every
native editor or installation environment has been tested.

### 5.5 Skipped Platform Case

The skipped backend case is
`test_repository_cache.RepositoryCacheTests.test_retargeted_symlink_removes_previous_cached_content`.
Its recorded reason is: `This Windows account cannot create file symlinks`.
The intended case creates a symlink, changes its target, and verifies invalidation
of previous cached content. It did not pass under this account and must not be
counted as successful retargeted-symlink validation. An environment with file
symlink permission is needed to complete this check.

### 5.6 Teaching Application Verification

The single teaching repository contains eleven Python files, including the
package initializer, and twenty unittest cases: five authentication, ten
workflow, two model, and three reporting tests. It has no required third-party
application dependency. The parent runner also invokes the deterministic
application entry point.

Authentication tests establish three failures, the 60-second deadline, rejection
before expiry, acceptance/reset at expiry, successful reset before lockout, and
a fresh count after expiry. Workflow tests establish session expiry/revocation
and invoice/shipping boundaries. These facts form source-grounded demonstration
criteria; they do not prove Antigravity answers correctly with TokenWise.

The digest helper is explicitly teaching-only unsalted SHA-256. In-memory
dataclasses and integer clocks make controlled evaluation easy, but the fixture
is not production authentication or billing software.

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 14: In the demo folder, run its unittest discovery and app.py. Capture twenty successful tests and deterministic application output, with the command and folder visible. Caption: Demonstration application verification.</span>

### 5.7 Browser Fixture Verification

The compiled result renderer was checked in Playwright/Chromium at 1280x1000
and 390x844 using synthetic data and a mocked webview host.

**Table 15. Browser fixture states.**

| State | Desktop | Narrow | Interpretation |
|---|---|---|---|
| Conversation memory | Passed | Passed | Rendering selected-reference details |
| Automatic packet comparison | Passed | Passed | Two-packet metrics and actions |
| Comparison pending | Passed | Passed | Loading presentation |
| Comparison unavailable | Passed | Passed | Visible measurement failure |
| Imported CLI usage | Passed | Passed | Rendering controlled imported counters |

Recorded checks show no page errors, no document-level horizontal overflow,
no overflowing statistic elements, and no overlapping statistics in those ten
views. Copy/export message assertions passed. The retained record is
[browser-checks.json](../evaluation/test-validation/browser-checks.json).
These are not screenshots of ten native live Antigravity chats.

### 5.8 Reproduction

From `vscode-extension`, with development dependencies installed:

```powershell
npm test
```

Its pretest compiles TypeScript and then runs Node's test runner. From the
checkout root, using the configured development Python environment:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s swe-pruner/swe-pruner/tests -v
.\.venv\Scripts\python.exe demonstration/run_checks.py
.\.venv\Scripts\python.exe evaluation/comparative-study/test_protocol.py -v
```

Each line is a separate invocation. The `.venv` path is a developer-checkout
prerequisite, not a path available to every installed-extension user. Browser
verification additionally requires an installed Playwright module and Chromium.
Its script is [verify-comparison-panels.cjs](../scripts/verify-comparison-panels.cjs);
use the documented local module/browser paths from [tests.md](../tests.md) or
substitute an actual installation. Ignored temporary paths are not bundled
prerequisites guaranteed on a friend's machine.

### 5.9 Defects, Risks, and Test Limits

Known contracts and failure handling are extensively exercised, but model
relevance, live integration, installed-platform compatibility, and physical
energy accuracy are separate concerns. Mocks cannot establish cloud quota,
native hook availability, every process lifecycle, or all adversarial source
behavior. The symlink skip and untested native macOS/Linux workflow remain gaps.

Research failures are not suppressed because software tests pass. Three neural
implementation anchors were lost, packed retrieval-only evidence was sparse,
and the full-file CPU pilot failed to finish. These observations inform future
engineering priorities in Chapter 8.

## 6. User Manual

### 6.1 Prerequisites and Distribution

A normal user needs Antigravity with compatible workspace-rule/command
capabilities, a trusted local Python source folder, 64-bit Python 3.12, internet
access for initial dependency/model setup, and sufficient disk/memory capacity.
The README recommends approximately 10 GB free disk space and identifies 8 GB
RAM as a practical starting recommendation. That RAM statement is not a
guarantee for long neural inputs: the recorded CPU pilot used considerably more
memory. A GPU, Ollama, and an MCP server are not required for the default workflow.

The manifest advertises a VS Code-compatible engine, but the automatic workflow
described here targets Antigravity integration. Windows is the tested native
setup environment. TokenWise itself requires no cloud API key; Antigravity
model access and billing remain separate.

Use the versioned [0.6.8 release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.8)
identified by the README. Choose the VSIX installer, not the automatically
generated source-code ZIP. The presentation ZIP includes the teaching project
and guides. This is beta distribution, not a claim of marketplace publication.

### 6.2 Install and Upgrade

1. Download `tokenwise-vscode-0.6.8.vsix` from the versioned release.
2. Open Antigravity's Extensions view and choose **... > Install from VSIX...**.
3. Select the downloaded file and reload the editor when requested.
4. Run **TokenWise: Set Up Backend** through `Ctrl+Shift+P`.
5. Open the intended repository and run **TokenWise: Enable Automatic Context**.
6. Start a new chat after setup or upgrade, rather than inspecting a stale result.

Normal users do not compile TypeScript, press F5, clone this checkout, or start
the backend manually from a development terminal. F5 is a developer extension
host workflow, not the installation procedure.

When upgrading an existing installation, update both the extension and managed
backend. Re-run **Enable Automatic Context** to refresh generated rules and
launchers while preserving unrelated customization. Verified model downloads
can be reused. A running older Python service does not acquire new code merely
because the VSIX was replaced.

### 6.3 Managed Backend Setup and Recovery

The managed workflow detects Python, prepares verified backend files, creates
a private environment, installs CPU/runtime packages, obtains pinned weights,
verifies required components, and registers the installation. Installation
requires explicit confirmation and can take several minutes.

**Table 16. Installation stages and recovery.**

| Stage | Operation | Recovery if it fails |
|---|---|---|
| 1. Prerequisites | Find 64-bit Python 3.12 and bundled files | Install/repair Python, restart editor, set Python Path if necessary |
| 2. Backend files | Copy integrity-checked runtime to private storage | Correct disk/permission issue; retry |
| 3. Environment | Create or verify private environment | Repair Python/environment cause; retain model cache |
| 4. Dependencies | Install packaging, CPU PyTorch, backend packages | Check network/proxy/package hosts and available space; retry validated substeps |
| 5. Model | Download roughly 1.35 GB and verify pinned checksum | Check model-host access and space; resume/revalidate supported download |
| 6. Verification | Check imports, tokenizer, estimation artifacts | Read exact import/artifact failure and correct dependency issue |
| 7. Registration | Save verified runtime and user setting | Correct storage/settings permission; retry |

Read **Output > TokenWise Setup** for detail. Use **Retry Failed Step** where
offered. If the notification was dismissed, run **Set Up Backend** again in the
same profile. Do not delete model/cache folders as the first recovery action.
An installer lock may belong to a still-running setup; do not remove it without
checking that no TokenWise installation process remains active.

An existing full checkout backend is an alternative for maintainers. Choose
the actual backend root, not the target Python application or an inner package
folder. Checkout-backed processes remain user-owned and are not equivalent to
managed installation ownership.

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 15: Capture managed setup completion or a real numbered stage, then the Diagnose Setup readiness output. Keep backend/version/readiness visible and redact unrelated personal data. Caption: Managed backend setup and readiness.</span>

### 6.4 Enable an Arbitrary Workspace

1. Use **File > Open Folder** to open the Python application root.
2. Trust the folder only if its contents are trusted.
3. Run **TokenWise: Enable Automatic Context**.
4. Select/install the managed backend if no registered runtime exists.
5. Confirm workspace configuration and inspect the TokenWise rule in
   **Agent Settings > Customizations > Rules**.
6. In a multi-folder window, repeat for each workspace to enable it separately.

The application can reside anywhere on the local filesystem; it need not be
inside the TokenWise checkout. Generated launchers use a central registration
link. Existing rules/hooks/settings are merged rather than broadly replaced.
Malformed JSON and modified owned launchers are not silently overwritten.

For class demonstration, open `demonstration/tokenwise_demo` itself, not its
parent TokenWise checkout. Opening the parent changes the indexed repository
and invalidates comparisons with the small teaching application.

### 6.5 First Automatic Prompt

Start a fresh Antigravity chat with no source highlight or attached file and
submit:

```text
Explain account lockout after failed login attempts and its related tests.
Do not modify any files. Cite relevant files and test names.
```

Approve the specific local command if the editor permission policy requests it.
There is no requirement to allow unrestricted terminal execution. The initial
model load or cold processing can take longer than a warmed request.

Check the current chat's actual TokenWise tool output or observed supported-hook
context. Then run **TokenWise: Show Automatic Context**. Confirm the current
query, fresh timestamp/event, ready activity, and expected input scope. A saved
`latest.json`, old result tab, or status-bar count alone is insufficient proof
of fresh delivery. Verification activity must not be relabeled live.

For the demo, useful evidence comes from `security/auth_service.py`,
`security/settings.py`, `security/models.py`, and `tests/test_auth.py` when
retrieved and retained. Inspect actual excerpts rather than asserting that
every run necessarily includes every required body.

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 16: Capture the exact lockout prompt, fresh TokenWise invocation/tool output, and matching current task/event in the result. Show that no source file was manually attached. Caption: Fresh automatic retrieval for the account-lockout prompt.</span>

### 6.6 Everyday Demonstration Workflows

**Table 17. Everyday workflows and controls.**

| Workflow | Procedure | What to inspect |
|---|---|---|
| Repository discovery | Demonstrate Pruning Inputs > Repository: no selected file | Task-selected files, scope, applied methods/thresholds |
| Entire file | Open `security/models.py`, clear highlights, use Prune Current File or selected-file demonstration | Entire captured source and Session-focused decisions |
| Exact excerpt | Highlight Session decorator/class body, use Prune Selected Code | Original start line; unselected Account was never input |
| Broad overview | Ask for full project overview in a fresh chat | Overview mode, map/docs, representative modules, coverage warnings |
| Explicit exclusion | Ask for session expiry/revocation, not invoice pricing | Filtered unrelated symbols and remaining supporting context |
| Threshold effect | Same `workflows.py` task at 0.45 and 0.85 | Actual masks, content, token change, and any evidence loss |
| Same-chat follow-up | Ask lockout question, then expiry/test follow-up | Selected earlier user intent and current objective |
| Outgoing guidance | Toggle workspace `response_guidance` for separate runs | Applied/disabled/omitted profile trace |
| Local comparison | Configure Automatic Comparison, then new prompt | Exact prepared packet versus hypothetical all-Python baseline |
| Explicit strategies | Compare Context Strategies from saved Python source | Unpruned selected and all-source inputs versus automatic context |

Teaching commands prepare inspectable context but do not necessarily send it
into an actual chat. A controlled history replay is labeled replay, not native
capture. Excerpt mode cannot claim to have pruned source that was never included.

For session demonstration, `issue_session` requires a nonempty username and
sets expiry to `now + 300`. Validity requires both not revoked and strictly
`now < expires_at`; equality is expired. `revoke_session` sets the revoked flag.
These facts reside in `workflows.py`, with Session fields in the model and
duration in settings. Invoice/shipping functions in the same workflow file
provide task distractors.

For invoice demonstration, integer half-up tax is computed before adding
subtotal and shipping. Negative subtotal/shipping or a tax percentage outside
0 through 100 is rejected. Reports separately count actions and export CSV.
These are teaching behaviors, not real payment or network integrations.

### 6.7 Conversation Memory and Prompt Guidance

In one fresh chat, ask the lockout question, then:

```text
What about its expiry boundary? Do not modify any files.
```

Then ask:

```text
Which tests cover that behavior? Do not modify any files.
```

Expand **Conversation memory**. Check that the subject remains account lockout,
that selected references are earlier user messages, and that source and outgoing
status are visible. A fallback label identifies agent-supplied references rather
than native transcript capture.

As a separate isolation control, start a different chat with only the final
vague follow-up. No previous lockout topic should be invented. To opt out,
change the existing `conversation_memory` JSON boolean to `false` in
`.agents/tokenwise.json`. To demonstrate guidance opt-out, separately change
`response_guidance` to `false`. Restore intended values afterward. Edit those
keys inside valid existing JSON rather than replacing all workspace settings.

These controls demonstrate delivery/selection behavior. They do not by
themselves prove better answers. Memory retains a bounded relevant subset, not
every message, and older recognized requirements can be omitted if they do not
fit the packet.

### 6.8 Compare and Export

Run **TokenWise: Configure Automatic Comparison** and choose **Enable automatic
packet comparison**. Send a new prompt and wait for the current result's
comparison to finish. Inspect both packet/file lists, task-plus-packet metrics,
signed difference, and configured carbon estimates. Use **Export Comparison**
to retain evidence. Disable measurement mode before primary timed agent trials,
because constructing the comparison introduces additional measurement work.

The all-Python packet assumes all indexed source is supplied. It is not an
observation of native Antigravity without TokenWise. Small repositories can
have packet increases, and changed saved snapshots require a fresh comparison.
The export size guard can reject larger repositories explicitly.

For actual provider usage, collect two independent successful single-turn CLI
JSON/stream-JSON logs using the same reported model and task. Run **TokenWise:
Import Antigravity Usage Comparison**. Failed/resumed, identical-session, and
differing-model runs are rejected. The importer preserves reported counters,
answers, timings, and completed tool traces; it makes no cloud request itself.
It is not an automatic grader or complete private IDE telemetry observer.

### 6.9 Troubleshooting

**Table 18. User troubleshooting.**

| Symptom | Likely boundary | Supported response |
|---|---|---|
| Python unavailable | Wrong version/architecture or PATH | Install 64-bit 3.12, restart editor, verify Python Path |
| Setup download fails | Connectivity, proxy, host access, disk | Read failed stage, fix cause, retry; reuse verified assets |
| Local-folder-only warning | Remote/virtual workspace or editor environment | Use a genuinely local file folder in the supported workflow |
| No TokenWise invocation | Rule missing/inactive, old chat, command denied | Re-enable workspace, inspect rule, fresh chat, approve needed command |
| Status shows old result | No current retrieval | Verify current event/query and actual tool output |
| Overview shows only initializer | Wrong root or package scaffold | Open real application folder; do not invent functionality |
| CO2 missing | Pending, disabled, incompatible/missing estimator | Wait/check settings and backend; unavailable is not zero |
| Large task is slow | Cold load or expensive source pruning | Rehearse small inputs, inspect diagnostics, disclose timeout; indexing alone is not total latency |
| Recent edit absent | Update still pending or watcher event missed | Wait for update, reconcile/retry, inspect index fingerprint |
| Comparison stale | Saved source changed after prepared packet | Send fresh task; do not compare different snapshots |
| History irrelevant | No verified same-chat subject or lexical mismatch | Supply explicit current subject; inspect provenance/opt-out |
| Customized setup/cleanup retained | Ownership mismatch or unsafe path | Read diagnostics, preserve user data; avoid broad deletion |

### 6.10 Disable, Cleanup, and Maintainer Operations

Setting `enabled: false` stops automatic retrieval/indexing for the configured
workspace, but a workspace rule can still ask the agent to invoke the launcher.
For a clean baseline, also set only TokenWise's rule to Manual and do not invoke
it. Check for duplicate legacy/global rules. Restore the exact configuration
after the trial rather than deleting unrelated customization.

**Remove All Local Data** and uninstall invoke ownership-aware cleanup. They
are not upgrade steps. Uninstall can depend on host behavior, locks, ownership,
and verifiable processes; retained modified/shared resources require honest
diagnostics. User-owned application source and checkout backends must not be
removed to satisfy a broad "nothing left" claim.

Maintainers, unlike normal users, work in the checkout, install development
dependencies, run `npm run compile`, use F5 if debugging, execute Python tests,
and build the VSIX with the project packaging scripts. Source development,
public release publication, and live paid experiments are separate operations.
None is required merely to ask a repository question after installation.

## 7. Validation and Comparative Study

### 7.1 Validation Questions

Validation asks whether the software works as specified: source scope is
correct, a fresh prompt triggers retrieval, the context is delivered, the packet
is bounded, references remain scoped, changes invalidate caches, and failures
are visible. Comparative evaluation asks what changes when a defined component
or the whole system is enabled rather than disabled under controlled conditions.

This report contains a completed twenty-repository local component study and
recorded software verification. It does not contain a completed paired native
Antigravity answer-quality/billing study. That distinction determines which
conclusions can be made.

The local research questions are:

1. How much smaller are defined prepared packets than all indexed Python source?
2. What additional change does actual neural pruning make to the same selected excerpt?
3. How much predefined source-body evidence survives final packing?
4. How does selected earlier user intent affect a vague follow-up's candidate coverage?
5. What local latency and configured carbon differences are observed?
6. Which constraints prevent these findings from establishing downstream superiority?

### 7.2 Functional Integration Validation

**Table 19. Functional integration validation checklist.**

| Check | Required observation | What it does and does not establish |
|---|---|---|
| Fresh prompt reaches retrieval | Matching current task, event/timestamp, actual invocation | Preparation for this task, not an old report |
| Context delivered | Actual tool output or supported hook injection | Workflow delivery, not private model reasoning |
| Cross-file evidence | Relevant settings/service/models/test excerpts | Available evidence; filenames alone are insufficient |
| Complete budget | Count of entire supplied packet | TokenWise budget compliance, not provider billed usage |
| Grounded answer | Correct behavior and genuine file/test citations | Observable source-supported response, not universal correctness |
| Read-only task | Source hashes/diff unchanged | No source edits during this validation |
| Saved-edit freshness | Controlled change then fresh snapshot/output | Exercised cache update path |
| Same-chat memory | Related user references and correct provenance | Bounded continuity without cross-chat carryover |

The checklist is a procedure for additional live evidence, not a table of newly
executed native checks. A reversible source edit belongs in a separate freshness
validation run; restore it and pass the demo tests before any paired comparison.
Preparation and citation evidence support operational use but do not expose the
model's internal reasoning or every hidden request.

### 7.3 Completed Study Protocol

The final protocol is `tokenwise-context-study-v2-bounded-neural`, recorded on
9 October 2026. The run used real local neural weights and twenty pinned public
Python repositories. Each repository supplied one fixed explanation task, a
target function/method, and seven packet conditions. There were 140 measured
packets and twenty actual bounded neural calls, with no Antigravity cloud answer
generation. [R6]

The study indexed 538 Python files comprising 4,381,075 source bytes. A prepared
1024-token excerpt ceiling limited neural inputs; none of the selected excerpts
required clipping. The bounded packing budget was 4,096 tokens, threshold 0.45,
and candidate limit eight. Guidance was enabled. The local service used four
CPU threads on Windows 11/Python 3.12.4; the recorded machine had sixteen logical
processors, with the accompanying study reporting an Intel Core i5-13400 and
approximately 15.77 GiB visible memory.

Snapshots include exact commit identifiers and archive/content fingerprints.
Downloaded repository code was parsed as source, not imported, installed, or
executed. Preparation selected the reference evidence before inspecting neural
outputs. Cases use releases chosen for controlled evaluation, not a claim that
they are current versions or recommendations.

### 7.4 Experimental Conditions

**Table 20. Comparative-study conditions.**

| Condition | Definition | Valid interpretation |
|---|---|---|
| `all_python` | Formatted full content of every indexed Python file | Hypothetical all-code prepared context |
| `selected_file` | Complete informed implementation file | Manual selection baseline |
| `selected_excerpt` | Known target function/method with matched formatting | Already focused, informed excerpt baseline |
| `neural_excerpt` | Real `/prune` on that same excerpt and task | Matched neural contribution |
| `retrieval_only` | Lexical/identifier/graph discovery and bounded interface/short-source packing | Retrieval ablation, not complete production pipeline |
| `history_off` | Same vague follow-up without earlier intent | No-hint retrieval-only control |
| `history_on` | Same follow-up plus selected task and formatting user reference | Controlled memory/retrieval ablation |

The retrieval-only conditions deliberately avoid neural ranking/line pruning.
Their explicit lexical/graph/interface policy does not reproduce every
production candidate reservation, exclusion, or allocation decision. They must
not be relabeled as the complete automatic extension.

The history task is `Which tests cover that behavior? Do not modify any files.`
The on condition supplies the preceding explicit repository task and a bullet-
point requirement. This is controlled user-reference input, not a captured live
native Antigravity conversation.

### 7.5 Evidence Rubric and Measurement

Each repository has one implementation anchor and up to two qualifying related
test anchors, frozen before neural inference. Click contributes two anchors;
the other nineteen cases contribute three each, giving 59 total. An anchor
requires both a declaration and a selected non-comment body/assertion line in
the correct file's code fence after whitespace normalization. A filename,
query, reference block, or declaration alone does not satisfy it.

Selection uses qualified AST symbols, implementation-overload handling, and
deterministic test association/order. This is a syntactic evidence proxy, not
independently adjudicated comprehensive ground truth. A missing line can indicate
an omission under the rubric without proving that every possible answer fails;
a retained line cannot establish complete behavior either.

Required-file coverage measures discovery before packing, with 43 required
implementation/test file locations counted across cases. Final evidence
retention measures content actually present after packing. Confusing these
metrics would conceal the important interface-packing losses.

Complete-packet tokens use the same local tokenizer. Aggregate reduction is a
ratio of summed tokens; mean per-repository reduction gives every repository
equal weight. There are no significance tests or population confidence claims
for this small purposive corpus. The output scorer was corrected to handle
variable-length fences/embedded headings and re-applied to preserved originals;
it did not regenerate prompts, outputs, timings, or source oracles.

### 7.6 Dataset and Per-Repository Results

**Table 21. Dataset and per-repository packet tokens.**

| Repository, fixed tag | Python files | All Python | Selected file | Excerpt before | Neural after | Retrieval-only |
|---|---:|---:|---:|---:|---:|---:|
| pallets/click, 8.1.8 | 70 | 135,043 | 8,292 | 264 | 265 | 4,095 |
| pallets/itsdangerous, 2.2.0 | 15 | 14,370 | 1,810 | 721 | 719 | 4,096 |
| pallets/markupsafe, 3.0.2 | 11 | 7,695 | 3,427 | 278 | 278 | 2,348 |
| pallets-eco/blinker, 1.9.0 | 7 | 8,612 | 4,188 | 436 | 436 | 2,243 |
| psf/requests, v2.32.3 | 36 | 88,709 | 7,590 | 378 | 378 | 4,096 |
| pallets/flask, 3.1.0 | 83 | 133,434 | 3,382 | 329 | 329 | 4,095 |
| hukkin/tomli, 2.2.1 | 14 | 13,128 | 6,533 | 600 | 600 | 2,954 |
| hukkin/tomli-w, 1.2.0 | 10 | 5,827 | 1,840 | 104 | 104 | 2,069 |
| tqdm/tqdm, v4.67.1 | 62 | 75,649 | 13,079 | 622 | 440 | 4,095 |
| theskumar/python-dotenv, v1.0.1 | 18 | 15,937 | 2,787 | 342 | 342 | 4,096 |
| dbader/schedule, 1.2.2 | 4 | 29,086 | 7,190 | 166 | 166 | 2,765 |
| mahmoud/boltons, 24.1.0 | 65 | 196,713 | 7,239 | 162 | 162 | 4,096 |
| pypa/packaging, 24.2 | 35 | 119,637 | 4,330 | 357 | 357 | 4,095 |
| tox-dev/platformdirs, 4.3.6 | 15 | 24,480 | 2,633 | 149 | 149 | 4,096 |
| tox-dev/filelock, 3.16.1 | 13 | 18,619 | 3,282 | 779 | 716 | 4,096 |
| tkem/cachetools, v5.5.1 | 18 | 22,669 | 5,613 | 125 | 125 | 3,141 |
| un33k/python-slugify, v8.0.4 | 7 | 10,110 | 1,480 | 993 | 993 | 2,356 |
| more-itertools/more-itertools, v10.6.0 | 8 | 123,127 | 41,677 | 539 | 539 | 4,096 |
| python-semver/python-semver, 3.0.3 | 26 | 28,000 | 5,943 | 157 | 157 | 4,096 |
| jd/tenacity, 9.0.0 | 21 | 36,387 | 1,026 | 74 | 74 | 4,095 |

Exact full commit pins and measured memory rows are in
[the generated tables](../evaluation/comparative-study/tables.md) and
[snapshots.json](../evaluation/comparative-study/snapshots.json). Each case's
query, target symbol, and settings are in
[cases.json](../evaluation/comparative-study/cases.json). The complete dataset
is retained in [results.json](../evaluation/comparative-study/results.json) and
[metrics.csv](../evaluation/comparative-study/metrics.csv).

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 17: Capture the actual generated twenty-repository results table with protocol/date, condition labels and totals visible. Caption: Twenty-repository component-study results. Label this recorded local component evidence, not live Antigravity answer accuracy.</span>

### 7.7 Aggregate Context and Evidence

**Table 22. Aggregate context and evidence results.**

| Condition | Total packet tokens | Mean per repository | Retained anchors / 59 | Cases above 4,096 |
|---|---:|---:|---:|---:|
| All Python | 1,107,232 | 55,361.60 | 59 | 20 |
| Selected file | 133,341 | 6,667.05 | 20 | 11 |
| Selected excerpt | 7,575 | 378.75 | 20 | 0 |
| Neural excerpt | 7,329 | 366.45 | 17 | 0 |
| Retrieval-only | 71,119 | 3,555.95 | 6 | 0 |
| History off | 71,558 | 3,577.90 | 4 | 0 |
| History on | 71,248 | 3,562.40 | 6 | 0 |

Retrieval-only packets are 93.58% smaller in aggregate than the hypothetical
all-Python packets. Mean per-repository reduction is 84.75%, a different
statistic because large repositories dominate the summed baseline. Every
bounded retrieval/history packet fits 4,096 tokens. All full-repository packets
exceed that benchmark budget.

The large reduction demonstrates capacity control under the defined ablation,
not preservation of all behavior. Retrieval-only discovers 40/43 required files
but retains only 6/59 predefined body anchors. Interfaces often omit the very
implementation or assertion needed to explain behavior. This is a material
negative result and a priority for improved allocation.

Selected source has fewer tests because it contains only the informed
implementation file/excerpt. Missing related-test anchors already absent from
that baseline cannot be attributed to neural deletion.

### 7.8 Matched Neural Comparison

The fair neural-only comparison is the same selected excerpt before and after
actual pruning, with matched task and packet format. Summed complete packets
fall from 7,575 to 7,329 tokens: a 3.25% aggregate reduction. Raw source tokens
fall from 6,664 to 6,418. The per-case median reduction is zero and the mean is
1.86%. Three packets shrink, sixteen remain equal, and one grows.

Click changes from 264 to 265 packet tokens, a 0.38% increase. Itsdangerous
changes from 721 to 719, while losing its implementation anchor. tqdm changes
from 622 to 440, a 29.26% reduction, but also loses the required implementation
anchor. Filelock changes from 779 to 716, an 8.09% reduction with its implementation
anchor retained. Across all twenty cases, seventeen implementation anchors
survive; Click, Itsdangerous, and tqdm lose theirs under the frozen rubric.

The result is not that the pretrained model never helps. It is that already
focused short inputs provide limited additional compression in this sample,
and reduction can remove meaningful evidence. Reporting only the strongest
29.26% example without its evidence loss would misrepresent effectiveness.

### 7.9 Conversation-Memory Ablation

**Table 23. Memory-ablation outcomes.**

| Metric | History off | History on |
|---|---:|---:|
| Required-file candidate coverage | 33/43, 76.74% | 40/43, 93.02% |
| Macro per-case required-file coverage | 77.50% | 93.33% |
| Retained packed anchors | 4/59 | 6/59 |
| Goal clarification flags | 20/20 | 0/20 |
| Total packet tokens | 71,558 | 71,248 |

Six cases improve candidate-file coverage, thirteen tie, and one worsens.
Improvements occur for Click, Requests, Flask, Boltons, Cachetools, and Semver.
Platformdirs regresses from 3/3 required files to 2/3. Tomli-W improves final
anchors from zero to two even though its file coverage ties.

Selected history helps resolve the deliberately vague follow-up in this
controlled setting. The large file-coverage gain and small packed-anchor gain
must both be reported. They do not prove that complete chat retention is useful,
that memory always saves tokens, or that every relevant requirement survives.
Native transcript capture and downstream answer quality were not evaluated
through these ablation records.

### 7.10 Latency and Failed Full-File Pilot

**Table 24. Observed component latency.**

| Operation | Minimum | Median | Mean | Maximum |
|---|---:|---:|---:|---:|
| Index and search-structure preparation | 16.75 ms | 73.48 ms | 126.80 ms | 318.93 ms |
| Warm search, median of three calls per repository | 0.245 ms | 0.290 ms | 0.306 ms | 0.466 ms |
| Actual bounded neural HTTP request | 0.472 s | 1.476 s | 2.281 s | 13.865 s |

Warm search excludes neural inference, packet formatting/tokenization, HTTP,
the editor, and downstream generation. The extension does not complete an
entire task in 0.290 ms. First-forward effects and fixed order can affect the
bounded inference results; no stable p95 guarantee or repeated independent
latency distribution is established.

Before the bounded protocol, an actual full-file `/prune-workspace` CPU pilot
on the Click snapshot reached a 600-second local HTTP timeout. One process
observation recorded approximately 4.74 GiB working set and 8.89 GiB private
memory; these are not instrumented peaks. The owned study backend was stopped
to recover resources. Later reset/refusal records follow that termination and
are not nineteen further independent repository failures.

No successful complete automatic packet was obtained from that pilot. The
bounded neural/retrieval-ablation study is a deliberately narrower replacement
protocol, not proof the full-file workflow succeeded. A final output budget does
not itself bound neural input work or memory. The raw failed record remains in
[full-file-pilot.json](../evaluation/comparative-study/full-file-pilot.json).

### 7.11 Carbon Estimates

All study estimates use the same configured scenario: target
`meta-llama-3-8b-instruct`, 256 expected output tokens, and 475 gCO2/kWh.
Registry-backed features select XGBoost interpolation for both phases.
Actual `/estimate-carbon` calls produced the saved values; no physical
energy meter or downstream Antigravity inference was used.

**Table 25. Matched-packet carbon estimates.**

| Quantity | Recorded estimate |
|---|---:|
| Selected excerpts before, summed across twenty tasks | 2.485763 g CO2 |
| Neural excerpts after, summed across twenty tasks | 2.481059 g CO2 |
| Difference | 0.004704 g CO2 |
| Aggregate estimated CO2 reduction | 0.1893% |
| Aggregate matched packet-token reduction | 3.2475% |

The percentage differs because expected decode workload remains fixed. For
the defined all-Python and retrieval-only scenarios, summed predictions are
approximately 23.514830 g and 3.700934 g respectively. Many all-source packets
would not fit a practical target request, so those predictions are hypothetical
scaling comparisons, not accepted cloud requests or observed consumption.

The estimator cannot establish actual Antigravity emissions, billed savings,
or net environmental benefit after added TokenWise computation. Its weak local
fit in some routes, reconstructed training targets, and workload assumptions
must remain visible alongside these numerical estimates.

### 7.12 Native Antigravity With and Without TokenWise

**Status: protocol provided; a completed live paired dataset is not present in
the reported study.** The procedure below is the correct next evaluation, not
an already observed result. It uses the same prompt under enabled and disabled
conditions, while allowing native source-reading tools in both.

1. Freeze the demo source and record its hashes/revision, installed extension/
   backend, actual agent model, effort, permissions, and other active rules.
2. Back up the exact TokenWise workspace rule and configuration outside the
   rule-discovery folder. Keep unrelated customizations unchanged.
3. Disable automatic packet-comparison mode during primary workflow timing.
4. For WITHOUT, set the existing workspace `enabled` to `false`; set only the
   TokenWise rule to Manual; check for duplicate active TokenWise rules.
5. Clear highlights/attachments and use a fresh independent chat. Send the exact
   common prompt from Section 6.5, allowing ordinary native tools.
6. Save the final answer, visible tool trace, full answer time, failures, and
   genuinely reported usage. Confirm no fresh TokenWise invocation/injection.
7. For WITH, restore the original rule and `enabled: true`; keep everything else
   identical. Start another fresh chat and send the exact same prompt.
8. Save the answer, actual supplied packet, task/event/snapshot, tool trace,
   preparation time, total answer time, and reported usage.
9. Score both answers against predefined facts, repeat with alternating order,
   and report ties, regressions, and failures as well as improvements.

Disabling only the extension can leave a workspace rule/launcher active. Setting
only the configuration flag can still allow an attempted invocation. An
unintended TokenWise attempt contaminates the intended clean baseline and must
be recorded and rerun, not quietly ignored. Do not deny native reading to the
baseline just to make it fail.

Use three paired repetitions for the lockout demonstration. A broader planned
pilot can use lockout, session expiry/revocation, and invoice validation with
three repetitions per condition, eighteen independent runs total. Keep it
separate from the twenty-repository component study. Live model calls can
incur cost and require actual model access; this report did not launch them.

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 18: After performing a genuine fresh-chat WITHOUT trial, capture the exact prompt, reported model, final answer and visible native tool trace with no fresh TokenWise activity. Caption: Controlled native Antigravity baseline without TokenWise. Do not disable native file-reading tools.</span>

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 19: After performing the independent matched WITH trial, capture the same prompt/model, real TokenWise invocation/context and final answer. Caption: Controlled native Antigravity workflow with TokenWise. Label recorded evidence with its actual capture date.</span>

### 7.13 Answer Scoring and Worksheet

The demo uses `LOCKOUT_THRESHOLD = 3` and `LOCKOUT_SECONDS = 60`.
`AuthService.authenticate` returns false immediately while `now < locked_until`.
At an existing deadline it clears failures/deadline before checking the new
password. Success before lockout also resets failures. A wrong password at
expiry returns false with a fresh count of one.

**Table 26. Source-grounded account-lockout scoring rubric.**

| Fact | Correct statement | Source/test |
|---|---|---|
| F1 | Third failed attempt triggers lockout | Settings and `test_lockout_threshold` |
| F2 | Deadline is triggering time plus 60 seconds | Service and threshold test |
| F3 | Even correct password is rejected before deadline | `test_correct_password_rejected_during_lockout` |
| F4 | At exact deadline correct password succeeds and both fields reset | `test_expiry_boundary` |
| F5 | Success before lockout resets failures | `test_success_resets_failures_before_lockout` |
| F6 | Wrong password at expiry starts a fresh failure count of one | `test_wrong_password_after_expiry_starts_a_new_count` |

For a precision question, use the same source and ask both conditions what
happens after three wrong attempts at time 100. The correct password is rejected
at 159 and accepted at 160; a wrong password at expiry resets old lock state
and produces one new failure. The teaching service has no automatic background
unlock thread, permanent account disable, JWT subsystem, or user database.
Such claims would be unsupported.

Score one point for each accurately stated supported fact, zero for a missing
or incorrect fact. Separately record citations, unsupported statements, relevant
test identification, read-only compliance, and failures. Six facts are a task
rubric, not a general model accuracy metric. Do not retroactively change the
rubric after seeing which condition wins.

**Table 27. Native comparison worksheet awaiting real runs.**

| Observation | WITHOUT TokenWise | WITH TokenWise |
|---|---|---|
| Run ID/date/repetition | Not collected | Not collected |
| Independent chat ID/model/settings | Not collected | Not collected |
| Correct supported facts, out of six | Not collected | Not collected |
| Missing/incorrect/unsupported claims | Not collected | Not collected |
| Genuine cited files/test names | Not collected | Not collected |
| Visible tool/file-read operations | Not collected | Not collected |
| Complete answer time | Not collected | Not collected |
| TokenWise preparation time | Not applicable | Not collected |
| Reported input/output/cache tokens | N/A until reported | N/A until reported |
| Source unchanged / completed or failed | Not collected | Not collected |

Actual provider input/output/cache counters must remain separately labeled.
Local packet tokens cannot replace missing cloud counters. A visible tool trace
is not necessarily exhaustive, and a terminal command can inspect many files.
Do not ask the model to guess its own billed token count.

Both conditions may produce correct answers. The evidence should report whether
context organization, factual coverage, measured time, or reported usage changes
under the controls, not promise that native Antigravity must fail without this
extension. An improvement in one metric can coexist with a regression in another.

<span style="color: #ff0000;">ADD SCREENSHOT - Figure 20: Only after completing repeated paired trials, capture the real filled worksheet or validated imported usage comparison, including failures/ties, fact scores, total times and reported usage or N/A. Caption: Completed paired-run validation worksheet. Until then leave this insertion unfulfilled and the results uncollected.</span>

### 7.14 Threats to Validity

**Table 28. Research threats and interpretation.**

| Threat | Consequence | Appropriate handling |
|---|---|---|
| Small purposive corpus, one main task per repo | Limited generalization | Report exact pins/tasks; expand independent tasks |
| Informed selected excerpts | Already little irrelevant source | Interpret 3.25% as additional matched pruning, not full retrieval gain |
| Syntactic oracle | Partial semantic evidence proxy | Report declaration/body criteria and expert evaluation gap |
| Retrieval-only ablation | Not complete production policy | Label ablation; do not claim end-to-end extension accuracy |
| Candidate versus packed evidence | High file coverage can conceal missing bodies | Report both coverage and retention |
| Fixed order and single inference per case | Initialization/cache effects | Use descriptive timing, not a service guarantee |
| Full-file CPU timeout | Practical resource constraint | Preserve failed pilot and distinguish narrower successful run |
| Controlled rather than native history | Does not validate transcript capture quality | Separate live integration checks |
| Hypothetical all-code baseline | Not native IDE behavior | Do not label it observed WITHOUT usage |
| Predicted energy and proxy targets | Not measured net emissions | Disclose scenario, target construction, overhead exclusions |
| Local tokenizer | Provider counting differs | Import actual counters when available |
| Regression fixtures and mocks | Not live model effectiveness | Keep software tests separate from research outcomes |

### 7.15 Reproduction and Integrity

Research inputs, locks, raw measurement records, generated tables, summary,
pilot failures, and scoring tests are in
[evaluation/comparative-study](../evaluation/comparative-study/README.md).
Original packet files and downloaded archives are stored in ignored local
scratch paths, with recorded SHA-256 values. They may not exist in every public
checkout; absence must be disclosed rather than claiming fully self-contained
raw-output reproduction.

With the development environment and required model already available, validate
the instrumentation first:

```powershell
.\.venv\Scripts\python.exe evaluation/comparative-study/test_protocol.py -v
```

Preparation and measurement are separate commands:

```powershell
.\.venv\Scripts\python.exe scripts/run_comparative_study.py --prepare-only
.\.venv\Scripts\python.exe scripts/run_comparative_study.py
```

Preparation can require public-network access to pinned archives. Measurement
starts a local real-weight service and consumes meaningful CPU/memory; it does
not call Antigravity's cloud model. Preserve a dated copy of existing results
before rerunning because output files can be replaced. Re-scoring requires the
original local packets:

```powershell
.\.venv\Scripts\python.exe scripts/run_comparative_study.py --rescore
.\.venv\Scripts\python.exe scripts/summarize_comparative_study.py
```

The plot script derives charts from measured JSON. This report links evidence
but embeds neither charts nor screenshots, respecting the user's insertion
workflow. Re-running the study was not necessary to write this report and was
not performed during report preparation.

### 7.16 Defensible Comparative Conclusion

The completed study supports three scoped observations. Bounded retrieval-only
packing uses substantially less supplied context than the defined all-source
baseline. Real neural pruning gives modest additional aggregate reduction on
the same already focused excerpts, with evidence losses in three cases.
Selected earlier user intent improves required-file candidate coverage for a
vague follow-up in most changing cases, but can regress and does not solve final
evidence loss by itself.

These observations show that TokenWise provides measurable context-management
mechanisms and an inspectable workflow. They do not yet prove more accurate
Antigravity answers, lower billed provider usage, faster end-to-end completion,
or positive net carbon impact. Those claims require the controlled native
experiment and, for environmental claims, appropriate independent energy
measurement. Reporting this distinction makes the project scientifically
stronger, not less useful.

## 8. Conclusion

### 8.1 Achieved Outcomes

TokenWise delivers an integrated local context-preparation extension rather
than a standalone pruning script. It connects natural-language tasks, Python
repository metadata, lexical/structural discovery, pretrained neural pruning,
bounded packing, same-chat user references, outgoing prompting, approximate
carbon estimates, and inspectable editor results. Managed setup and central
workspace registration allow another developer to use the extension without
the author's development checkout.

The recorded three implementation suites contain 355 discovered tests with
354 passes and one platform skip. Ten synthetic browser views and ten separate
study-protocol tests supplement that verification. The twenty-repository study
adds actual component measurements, including limitations not visible in
passing unit tests.

**Table 29. Achieved outcomes and remaining limitations.**

| Outcome | Evidence | Remaining boundary |
|---|---|---|
| Automatic repository discovery | Source pipeline, input traces, tested contracts | Agent-followed fallback and static retrieval limits |
| Explicit source pruning | Real neural excerpt measurements and line masks | Incomplete structural/behavioral retention |
| Complete packet limits | Tokenizer checks and bounded study packets | Essential evidence can still be omitted |
| Reusable search metadata | Incremental cache and warm-search measurements | Neural/agent work still dominates many tasks |
| Bounded prior user intent | Memory tests and coverage ablation | Lexical selection and one observed regression |
| Outgoing prompt engineering | Real templates, trace and budget tests | Downstream answer-quality improvement unmeasured |
| Sustainability visibility | Trained artifacts and phase-specific predictions | Not actual or net carbon measurement |
| Recoverable user installation | Managed stages, retry/integrity/lifecycle tests | Native portability and resource constraints remain |
| Scientific comparison support | Labeled baselines, raw records, usage importer | Native paired outcomes remain to be collected |

### 8.2 Limitations

The most important limitation is evidence preservation under tight context and
compute budgets. Candidate-file discovery can be good while final packed source
lacks required bodies. Neural pruning can remove decisive conditions/decorators,
and large-file CPU inference can consume impractical resources despite a small
output budget. These are engineering and research challenges, not cosmetic
dashboard issues.

Other limits include Python-focused static relationships, saved-file rather
than unsaved-buffer indexing, eventual watcher/reconciliation freshness,
editor-dependent hook/fallback delivery, and heuristic bounded memory. Native
macOS/Linux, broader IDE versions, accessibility, and adversarial source
handling require further validation.

Carbon results remain scenario estimates with imperfect learned fits,
partially reconstructed benchmark targets, simplified token scaling, and
excluded local overhead. Software-test success cannot establish model accuracy
or net sustainability. Completed native paired answer-quality and usage
measurements are still needed before claiming superiority over Antigravity's
normal retrieval.

### 8.3 Prioritized Future Work

First, improve final evidence allocation: reserve task-relevant function bodies,
configuration, and assertions instead of favoring interfaces solely because
they fit. Evaluate packing against fact-level ground truth rather than filenames
and compression alone.

Second, bound neural input computation independently from output size. Evaluate
function-level preselection, chunk/token work caps, compatible lower-memory
execution, cancellation, and fallbacks on the large-file cases that caused the
CPU pilot limitation. Measure total overhead and retained evidence together.

Third, conduct repeated native with/without trials using fixed source/model/
permissions, alternating order, independently scored facts, actual reported
usage, and failure accounting. Run separate ablations for outgoing guidance and
memory rather than attributing every effect to neural pruning.

Fourth, validate estimation on independent model/hardware groups and measured
workloads. Retain provenance for measured versus reconstructed targets, quantify
uncertainty, and include local TokenWise energy in any net-benefit claim.

Fifth, broaden native installation, editor compatibility, security, and
accessibility evaluation while retaining ownership-aware setup and cleanup.
Additional repository languages require appropriate parsers/resolvers and new
evaluation, not simply accepting non-Python text at the neural endpoint.

### 8.4 Final Assessment

The project's strongest demonstrated contribution is a usable, inspectable
context-management system with explicit constraints and reproducible component
evidence. It automates a meaningful developer task and makes its inputs,
selection decisions, assumptions, and failures visible. The findings also
identify where smaller context ceases to be sufficient context. A sound defense
can therefore explain both why the system is useful and what remains necessary
to prove broader downstream and sustainability benefits.

## References

**R1.** Wang, Y., Shi, Y., Yang, M., Zhang, R., He, S., Lian, H., Chen, Y.,
Ye, S., Cai, K., and Gu, X. *SWE-Pruner: Self-Adaptive Context Pruning for
Coding Agents*. arXiv:2601.16746v3, 26 April 2026. Supplied
[research PDF](../SWE-pruner.pdf). The report uses this as a research foundation;
the paper's agent benchmark results are not attributed to TokenWise.

**R2.** Pathania, P., Mehra, R., Sharma, V. S., Kaulgud, V., Nevels, T.,
Podder, S., and Burden, A. P. *SEALing the Gap: A Reference Framework for LLM
Inference Carbon Estimation via Multi-Benchmark Driven Embodiment*. ICSE 2026
NIER; arXiv:2603.02949v1. DOI: 10.1145/3786582.3786846. Supplied
[research PDF](../carbon-emissioin.pdf). Local datasets and validation differ
from the paper's implementation.

**R3.** Wahid, A. B. *TokenWise: Sustainable Context Optimization for Coding
Agents*. Institute of Information Technology, University of Dhaka, supplied
[project proposal](../spl3-1442.docx.pdf). The proposal motivates and identifies
the project; it is not used as proof of measured outcomes.

**R4.** TokenWise implementation and attribution sources, inspected
9 October 2026:

- [Extension manifest](../vscode-extension/package.json), [activation](../vscode-extension/src/extension.ts), and [README](../README.md).
- [Workspace setup](../vscode-extension/src/services/automaticSetup.ts) and [background index synchronization](../vscode-extension/src/services/repositoryIndexSync.ts).
- [Repository index](../swe-pruner/swe-pruner/src/swe_pruner/repository/repository_index.py), [AST indexer](../swe-pruner/swe-pruner/src/swe_pruner/repository/python_indexer.py), and [dependency graph](../swe-pruner/swe-pruner/src/swe_pruner/repository/dependency_graph.py).
- [Goal compiler](../swe-pruner/swe-pruner/src/swe_pruner/goal_compiler.py), [lexical retrieval](../swe-pruner/swe-pruner/src/swe_pruner/retrieval/lexical_retriever.py), [workspace pipeline](../swe-pruner/swe-pruner/src/swe_pruner/retrieval/workspace_context.py), and [packer](../swe-pruner/swe-pruner/src/swe_pruner/retrieval/context_builder.py).
- [Neural wrapper](../swe-pruner/swe-pruner/src/swe_pruner/prune_wrapper.py), [model structure](../swe-pruner/swe-pruner/src/swe_pruner/model_structure.py), and [backend serving](../swe-pruner/swe-pruner/src/swe_pruner/online_serving.py).
- [Response guidance](../swe-pruner/swe-pruner/src/swe_pruner/retrieval/response_guidance.py), [conversation selection](../swe-pruner/swe-pruner/src/swe_pruner/conversation_context.py), and [native adapter](../swe-pruner/swe-pruner/src/swe_pruner/antigravity_hook.py).
- [Carbon feature preparation](../carbon-engine/src/carbon_engine/features.py), [training](../carbon-engine/src/carbon_engine/modeling.py), [runtime engine](../swe-pruner/swe-pruner/src/swe_pruner/carbon_model_engine.py), [cross-validation metrics](../swe-pruner/swe-pruner/carbon_artifacts/cv_metrics.json), and [external-reference record](../swe-pruner/swe-pruner/carbon_artifacts/validation_report.json).
- [Third-party acknowledgements](../THIRD_PARTY_NOTICES.md). Model/tokenizer licenses and research authorship are not superseded by TokenWise's application license.

**R5.** TokenWise [test and verification report](../tests.md),
[saved browser results](../evaluation/test-validation/browser-checks.json),
[extension tests](../vscode-extension/tests),
[backend tests](../swe-pruner/swe-pruner/tests), and
[demonstration runner](../demonstration/run_checks.py). Recorded 9 October 2026.

**R6.** TokenWise [comparative study](../comparative_study.md),
[protocol and raw measurement inventory](../evaluation/comparative-study/README.md),
[summary](../evaluation/comparative-study/summary.json),
[source pins and generated tables](../evaluation/comparative-study/tables.md),
[study runner](../scripts/run_comparative_study.py), and
[summary generator](../scripts/summarize_comparative_study.py). Component
measurements recorded 9 October 2026; not a live Antigravity answer-quality study.

**R7.** TokenWise operational instructions:
[short classroom demonstration](../demonstration2.md),
[detailed demonstration](../demonstation.md),
[native comparison protocol](../validation.md),
[teaching application](../demonstration/tokenwise_demo/README.md), and
[development guide](../docs/DEVELOPMENT.md). Historical figures in guides retain
their original scope; this report uses the dated evidence identified above.

**R8.** *DeHalu: Agentic Hallucination Detection and Mitigation in Local
CodeLLMs*, supplied [friend's final report](../Frineds_report/DeHalu_Final_Report.docx).
Used only for academic organization and presentation patterns, not as a source
of TokenWise implementation, identity, figures, results, or original prose.
