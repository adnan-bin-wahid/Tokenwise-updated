# TokenWise: Complete Project Study and Defense Guide

**Project:** TokenWise: Sustainable Context Optimization for Coding Agents  
**Student:** Adnan Bin Wahid, BSSE-1442, Institute of Information Technology, University of Dhaka  
**Supervisor named in the proposal:** Mridha Md. Nafis Fuad  
**Implementation studied:** TokenWise extension 0.6.8, inspected on October 9, 2026

**Comparison addendum:** Automatic packet comparison, CLI-usage import and the
validation-guide shortcut are included in 0.6.7. Earlier public
0.6.6 assets remain unchanged. The comparison measurements and their
limitations are explained in Section 32.8 below and in the teacher guide.

**Memory addendum (0.6.8):** Related user messages now inform retrieval through
bounded extractive conversation memory. Section 21.5 explains native identity
checks, separately labeled fallback references, constraint selection, outgoing
packet limits, opt-out and the visible selection trace. This adds no LLM call.

**Purpose:** Understand the entire project, explain its engineering and research foundations, demonstrate it, and answer project-defense questions confidently.

This guide describes TokenWise as a complete system: its requirements, architecture, implementation, research basis, operation, evaluation, distribution, and limitations. It is not a chronological account of repairs, and it does not explain source code line by line. Instead, it explains the reasoning and behavior behind the important parts of the implementation.

The implementation descriptions cover 0.6.8, including broad repository overviews, explicit topic exclusions, pruning-input traces, bounded extractive conversation memory, context-strategy comparisons, automatic-result carbon reporting, the single teaching project, outgoing prompt engineering in Section 13.7, and comparison/validation support in Section 32.8. Earlier installers remain unchanged and do not acquire new functionality automatically. Historical performance and carbon-model measurements retain their original dates, fixtures, and evaluation boundaries. A supported experiment or a proposed comparative study is not presented as a completed downstream-quality result.

The project ownership statement must remain precise. I built the TokenWise application and integrated its components into a working developer workflow. That includes the extension, repository-context pipeline, local service integration, sustainability-estimation workflow, installation, configuration, caching, diagnostics, packaging, and testing represented in this repository. The neural checkpoint and the foundational Qwen model are pretrained third-party components; their original training and published benchmark results belong to the cited researchers. Building an application from its requirements is not the same as training every dependency from random initialization. A strong defense can explain both the original system engineering and the properly attributed research it builds on.

## Contents

1. [How to Study This Guide](#1-how-to-study-this-guide)
2. [What TokenWise Is](#2-what-tokenwise-is)
3. [The Problem and Motivation](#3-the-problem-and-motivation)
4. [Proposal Objectives and Implementation Scope](#4-proposal-objectives-and-implementation-scope)
5. [Fundamental Concepts](#5-fundamental-concepts)
6. [Complete Architecture](#6-complete-architecture)
7. [Repository Organization](#7-repository-organization)
8. [End-to-End Prompt Lifecycle](#8-end-to-end-prompt-lifecycle)
9. [Installation and the Managed Backend](#9-installation-and-the-managed-backend)
10. [Enabling an Arbitrary Python Repository](#10-enabling-an-arbitrary-python-repository)
11. [The Extension and Its User Interface](#11-the-extension-and-its-user-interface)
12. [Backend Service and API Contracts](#12-backend-service-and-api-contracts)
13. [Task and Goal Compilation](#13-task-and-goal-compilation)
14. [Python Repository Indexing](#14-python-repository-indexing)
15. [Dependency Graph and Structural Retrieval](#15-dependency-graph-and-structural-retrieval)
16. [Lexical Retrieval and Candidate Ranking](#16-lexical-retrieval-and-candidate-ranking)
17. [Research Foundation: SWE-Pruner](#17-research-foundation-swe-pruner)
18. [The Deployed Neural Pruner](#18-the-deployed-neural-pruner)
19. [Chunking and Line Selection](#19-chunking-and-line-selection)
20. [Tiered Context and the Hard Token Budget](#20-tiered-context-and-the-hard-token-budget)
21. [Antigravity Integration and Activity Evidence](#21-antigravity-integration-and-activity-evidence)
22. [Background Indexing, Caches, and Freshness](#22-background-indexing-caches-and-freshness)
23. [Research Foundation: SEAL](#23-research-foundation-seal)
24. [Carbon Data Preparation and Model Training](#24-carbon-data-preparation-and-model-training)
25. [Runtime Energy and Carbon Calculations](#25-runtime-energy-and-carbon-calculations)
26. [Worked Numerical Examples](#26-worked-numerical-examples)
27. [The Demonstration Repository](#27-the-demonstration-repository)
28. [Privacy, Security, and Trust](#28-privacy-security-and-trust)
29. [Failure Handling and Uninstall](#29-failure-handling-and-uninstall)
30. [Development, Packaging, and Distribution](#30-development-packaging-and-distribution)
31. [Testing and Verification](#31-testing-and-verification)
32. [Results and Scientific Interpretation](#32-results-and-scientific-interpretation)
33. [Project Contributions and Design Justification](#33-project-contributions-and-design-justification)
34. [Limitations and Improvement Roadmap](#34-limitations-and-improvement-roadmap)
35. [How to Explain the Build Methodology](#35-how-to-explain-the-build-methodology)
36. [Defense Presentation and Live Demonstration](#36-defense-presentation-and-live-demonstration)
37. [Detailed Defense Questions and Answers](#37-detailed-defense-questions-and-answers)
38. [Glossary](#38-glossary)
39. [Final Revision Sheet](#39-final-revision-sheet)
40. [References and Source Map](#40-references-and-source-map)

---

## 1. How to Study This Guide

Read this document in three passes. On the first pass, understand the problem, the architecture, and the normal prompt lifecycle. Your goal is to explain what happens after a user writes a repository question without relying on memorized filenames. On the second pass, study retrieval, neural pruning, cache invalidation, and carbon estimation. Your goal is to explain why each stage exists and what mathematical or engineering assumption it makes. On the third pass, practice the demonstration and defense questions, paying particular attention to evidence and limitations.

For a short presentation, Sections 2, 6, 8, 25, 32, and 36 provide the main story. For technical questions, Sections 13 through 26 contain the deeper mechanisms. For questions about whether the project is genuinely usable, study installation, arbitrary-workspace configuration, background indexing, error handling, cleanup, and release distribution.

Keep four kinds of statements separate throughout the defense:

| Statement type | Meaning | Example |
| --- | --- | --- |
| Implemented behavior | Confirmed by the current source | The packed context has a configurable hard token budget. |
| Local evidence | Tests, saved artifacts, or recorded project measurements | The synthetic watched-retrieval benchmark has sub-millisecond median search overhead. |
| Published research result | A result reported by an external paper | SWE-Pruner reports token reductions on SWE-Bench Verified. |
| Objective or future work | A desirable property not yet established | Improve coding success on a large independent set of real repositories. |

The distinction is not a weakness. It demonstrates that you understand experimental validity and do not confuse a promising design with a measured guarantee. The guide uses the actual implementation as the source of truth when older project documents describe an earlier snapshot.

## 2. What TokenWise Is

TokenWise is a local developer extension and backend that prepares task-relevant, bounded Python repository context for coding agents. The user writes an ordinary prompt in Antigravity. TokenWise identifies relevant source files and tests, reduces unnecessary code content, and supplies an organized context bundle to the agent. The normal automatic workflow does not require the user to choose files, select editor text, or copy a generated prompt manually.

The project also includes a trained, SEAL-derived energy and carbon-estimation component. In direct pruning, repository-context results, fresh automatic results, and context-strategy comparisons, it estimates inference impact under the same target-model assumptions. This sustainability component is a scenario estimator, not a meter attached to Antigravity's cloud infrastructure.

An important scope distinction is that the automatic Antigravity launcher retrieves context and records activity; the extension's automatic monitor then requests carbon estimates separately from the actual local backend. Context can therefore reach the agent before the estimate finishes. The panel reports pending, ready, disabled, or unavailable estimation rather than requiring a successful carbon request before showing useful context. Saved launcher activity is not a physical emissions record, and old/verification activity does not automatically trigger a new estimate.

### A defense-ready explanation

> I built TokenWise to help a coding agent receive the right repository evidence without unnecessary context. It combines task interpretation, Python AST indexing, lexical and dependency-based retrieval, a pretrained task-aware neural pruner, and token-budgeted packing. I integrated this local pipeline with Antigravity and added a separate trained estimation layer to show approximate prompt-level energy and carbon differences. The extension includes managed installation, background updates, diagnostics, and safe cleanup so another developer can use it without my development checkout.

TokenWise does not generate the agent's final answer, fine-tune the user's cloud model, replace Antigravity, or automatically rewrite application source. Its role is to improve the evidence supplied to the agent and make the context preparation process observable.

## 3. The Problem and Motivation

### 3.1 Why repository context is difficult

A coding task usually depends on several connected files. A login question may involve a service, a user model, cryptographic helpers, configuration, and tests. Opening one file can miss the expected behavior. Sending every file can overwhelm the model with unrelated code. The problem is not merely finding a filename; it is deciding how much of each relevant file should be supplied for a particular task.

The user often does not know where the answer lives. Manual selection makes the developer perform retrieval before the agent can help with retrieval. An automatic system can reduce this burden by using the task itself to discover evidence.

### 3.2 Why larger context is not automatically better

A context window is a capacity limit, not a promise that every supplied token contributes equally to reasoning. Irrelevant code competes with relevant evidence for attention and for the available prompt budget. Long observations also increase transmission and processing work. Important behavior can be difficult to notice when surrounded by unrelated helpers, duplicated material, or entire files included for only one useful function.

TokenWise therefore focuses on context quality and bounded size. Its aim is not to make all prompts as short as possible. A tiny prompt that removes a crucial condition is worse than a slightly longer prompt containing the necessary evidence. The design balances coverage, relevance, compression, and source traceability.

### 3.3 The sustainability motivation

LLM inference requires computation, and computation consumes electricity. Reducing avoidable input processing can reduce part of the inference workload under suitable assumptions. However, electricity consumption depends on model size, hardware, batching, token lengths, caching, and implementation. Carbon emissions also depend on the electricity's carbon intensity.

This motivates an estimation layer rather than the claim that every removed token directly causes an identical amount of real carbon reduction. The project makes the relationship inspectable by separating token savings, predicted phase energy, and carbon conversion.

### 3.4 The practical product motivation

A useful extension must do more than produce a good result on the author's computer. It needs understandable installation, a backend that can serve arbitrary repositories, recoverable setup failures, correct cache invalidation, explicit operating boundaries, and cleanup that respects user data. These are central project requirements, not merely presentation polish.

The main research-to-product question is: how can task-aware context optimization become part of an ordinary coding workflow while remaining bounded, explainable, locally runnable, and maintainable?

## 4. Proposal Objectives and Implementation Scope

The [project proposal](docs/TokenWise-Proposal.pdf), especially pages 1-2, defines a three-part pipeline: task-aware skimming, context pruning, and carbon tracking. The present implementation turns that overall idea into an extension, service, retrieval pipeline, and trained estimation workflow.

| Proposal objective | Current implementation | Important qualification |
| --- | --- | --- |
| Goal-hint generation | Structured goal compiler with deterministic task templates and optional local LLM generation | The default is not an additional neural planner; an ambiguous-task flag does not force a clarification conversation. |
| Line-level neural skimming | SWE-Pruner-derived pretrained model scores tokens and selects source lines | The checkpoint was integrated, not pretrained from scratch within this project. |
| Adaptive thresholding | Threshold settings and different context treatments for anchor, related, and interface files | Imports, class headers, and complete syntactic validity are not universally guaranteed. |
| Multi-benchmark feature fusion | Carbon pipeline combines performance data and reasoning-quality benchmark features | The local data preparation and dataset sizes differ from the SEAL paper. |
| Prompt-level carbon estimation | Trained phase predictions plus energy-to-carbon conversion | Estimates are scenario-based, not direct cloud measurements. |
| Phase-specific dual regressors | Separate prefill and decode models, using XGBoost or Ridge according to model-size range | Local metrics must be reported separately from the paper's metrics. |
| Sustainability dashboard | Before/after energy and carbon in direct, repository, and fresh automatic result views; optional per-strategy estimates | Automatic estimates are asynchronous extension-side enrichment, not metering or guaranteed fields in every saved launcher event. |

The proposal's desired benefits include lower noise, token use, and environmental impact. These are motivations to investigate. The current project establishes functional context retrieval, hard size limits, installation and lifecycle behavior, and particular local measurements. It does not establish universal hallucination reduction, universal speed improvement, or production-quality carbon measurement.

The implementation's operating scope is local, trusted Python repositories. Single-file neural pruning can accept code text, but repository structure is discovered through Python's AST module. Native Windows installation and integration checks are available. macOS/Linux launchers are included, but their presence should not be presented as completed native cross-platform validation. Remote SSH, WSL/dev-container, browser, and virtual-workspace first-run integration are outside the supported workflow.

## 5. Fundamental Concepts

### 5.1 Tokens and token budgets

A token is a unit used by a model's tokenizer. It may represent a whole word, part of a word, punctuation, whitespace, or a code fragment. Token counts are not identical to character counts or line counts. Different models can tokenize the same string differently.

TokenWise uses the local neural model's tokenizer to enforce repository-context budgets. A 4,096-token limit means a limit under that tokenizer. It is not a guaranteed 4,096-token bill from Gemini, Claude, or another agent model. Direct pruning now uses the backend's original/retained token counts for its carbon comparison too; the frontend token helper is not the authority for that path.

### 5.2 Retrieval versus pruning

Retrieval selects potentially useful files. Pruning selects useful content within those files. A retriever can find the right service while still returning hundreds of irrelevant lines. A pruner cannot recover a file that retrieval excluded. Combining the two is necessary for repository-scale context optimization.

### 5.3 Abstract syntax trees

An AST represents a program's syntactic structure. Python's parser can identify imports, class definitions, functions, assignments, and calls without executing the program. TokenWise uses that structure to produce repository metadata and interface views.

An AST does not prove runtime behavior. It cannot resolve every dynamic import, monkey patch, reflection operation, or polymorphic call. TokenWise's graph is a useful approximation, not a formally sound whole-program analysis.

### 5.4 Lexical and semantic relevance

Lexical relevance depends on words and identifiers shared by a query and source code. Semantic relevance considers whether the code helps answer the task even without exact word overlap. TokenWise first uses inexpensive lexical and structural signals, then applies a learned neural model to a limited set of candidates.

This is not a vector-database application. The current implementation does not create a persistent embedding index and query it with nearest-neighbor search. Its learned model scores selected query-code pairs at request time.

### 5.5 Prefill and decode

Prefill is the phase in which a language model processes the input prompt and builds internal state, including the key-value cache used during generation. Decode is the phase in which it generates output tokens, typically one step at a time. Reducing input context primarily affects the modeled prefill component when expected output length is held fixed.

### 5.6 Regression, interpolation, and extrapolation

Regression predicts a numeric value from features. Interpolation makes predictions within a range represented by training data; extrapolation makes predictions outside that range. TokenWise's carbon engine chooses between XGBoost and Ridge using a configured model-size interval, but that routing rule does not guarantee that all other request features resemble the training distribution.

### 5.7 Cache invalidation and fingerprints

A cache saves reusable computation. Correctness requires detecting when the saved computation no longer applies. A source-content fingerprint summarizes the repository snapshot used to build search data and context. If content changes, the fingerprint changes and dependent caches must not supply an old context as though it were current.

## 6. Complete Architecture

### 6.1 Runtime architecture

```text
Developer's Python repository
        |
        | saved Python files + user task + eligible bounded same-chat hint
        v
Antigravity / VS Code extension
        |
        +--> Setup, trust checks, configuration, diagnostics, UI
        +--> Background file watcher --> index synchronization
        |
        +--> Antigravity rule/command or supported hook adapter
                        |
                        v
                Local FastAPI backend
                        |
                        +--> Structured goal compilation
                        +--> Cached Python repository index
                        +--> Lexical search + symbol lookup + dependency graph
                        +--> Focused candidate selection / deterministic overview
                        +--> Explicit-topic source views when applicable
                        +--> Bounded neural scoring, retained short bodies, interfaces
                        +--> Tiered context packing under a hard token budget
                        |
                        v
          Source-labeled context supplied to the coding agent
                        |
                        v
       Agent explanation, additional investigation, or proposed edits

Separate sustainability request path in the extension:
Direct source counts / matched repository packets / comparison packets
        + target-model assumptions
        --> trained prefill/decode regressors
        --> predicted joules --> estimated grams CO2
        --> before/after result view
```

### 6.2 Offline and online responsibilities

The carbon research pipeline is primarily offline work. It prepares benchmark data, normalizes features, trains regressors, evaluates them, and saves artifacts. Ordinary extension users load those artifacts; they do not need to download the training benchmarks or retrain models.

The neural pruner is also pretrained before ordinary use. Runtime setup obtains a pinned checkpoint and local tokenizer/configuration assets. It then performs inference locally. The project does not train Qwen during installation or during an Antigravity conversation.

Online operations are goal compilation, index synchronization, retrieval, pruning, context packing, and optional carbon prediction. Here, online means serving a request, not necessarily making an internet call. Core retrieval works locally after dependencies and weights have been installed.

### 6.3 Why the extension and backend are separate

The extension is responsible for editor APIs and user experience. Python provides the AST parser, machine-learning runtime, model loaders, and regression ecosystem. A loopback HTTP boundary allows each part to use its appropriate tools without embedding a large Python ML stack inside the extension host.

The boundary also creates explicit request and response contracts. The extension can show useful errors when the service is unavailable, and the backend can validate inputs independently. A shared backend avoids keeping another large neural-model copy for every enabled repository in the same installation.

## 7. Repository Organization

| Location | Role in the project |
| --- | --- |
| `vscode-extension/` | TypeScript extension, commands, editor integration, result views, setup, background synchronization, and uninstall behavior |
| `swe-pruner/swe-pruner/src/swe_pruner/` | Python service, goal compiler, model wrapper, repository indexing, retrieval, context building, Antigravity adapters, and runtime carbon estimation |
| `swe-pruner/swe-pruner/model/` | Neural-model configuration and tokenizer assets; large checkpoint kept outside Git tracking |
| `swe-pruner/swe-pruner/carbon_artifacts/` | Runtime regression models, feature schema, encoder, registry, metrics, and validation records |
| `carbon-engine/` | Benchmark fetching, merging, feature construction, regression training, and external-reference validation |
| `scripts/` | Setup, model verification, packaging, smoke checks, isolated integration checks, and retrieval benchmarking |
| `demonstration/tokenwise_demo/` | Current single teaching application: account lockout, sessions, invoices/shipping, reports, and twenty tests |
| `demonstration/` | One-project case manifest, standard-library runner, evaluation worksheet, and scoped verification records |
| `Test_project/` | Legacy development fixture with different authentication/payment behavior; not the current packaged teaching project |
| `docs/` | Proposal, source papers, usage/integration/development/publishing documentation, and evaluation records |
| `README.md` | Normal-user installation and operation instructions |
| `review.md` | Broader review material; descriptions may refer to older snapshots |
| `study.md` | This complete conceptual and defense guide |
| `demonstation.md` | Detailed current one-folder teacher walkthrough, prompts, exports, and interpretation |

Three locations must not be confused: the developer's TokenWise source checkout, the extension-managed backend in IDE user storage, and the user's application repository. Normal users do not need to place their application inside the TokenWise checkout. The managed backend is shared infrastructure; each enabled repository has a small local integration and a link to the central registration.

Generated directories such as virtual environments, package dependencies, compiled output, local activity, backend bundles, and release outputs are not the architectural source of truth. They can be rebuilt or removed according to their ownership rules. The source tree, configuration, training pipeline, and saved model artifacts explain how the product is assembled.

## 8. End-to-End Prompt Lifecycle

Consider the task: **Explain account lockout after failed login attempts and its related tests. Do not modify any files.** The complete automatic path is as follows.

First, the repository has been enabled through the extension. The workspace contains an always-on TokenWise rule, hook configuration, launchers, settings, and a central backend link. If the configured trusted folder is open, background synchronization can already have prepared its repository index.

Second, the Antigravity agent obtains TokenWise context. A supported native hook can do this through the hook protocol; otherwise, the workspace rule asks the agent to execute the local retrieval command. The developer still writes only the ordinary prompt. A command approval may be needed under the IDE's permission policy.

Third, the launcher resolves the managed backend through the central registration. It reuses a healthy matching process or starts one locally. It does not assume that the Python repository is a child of the TokenWise checkout.

Fourth, the request is sent to `/prune-workspace` with the task, absolute workspace path, threshold, token budget, and candidate limit. A recognized native follow-up can also include a bounded same-topic user hint. Automatic defaults are 4,096 tokens, threshold 0.45, and six candidates. No active editor file is required. A project-overview request takes a separate representative-coverage route instead of using generic prompt words as source identifiers.

Fifth, the backend validates the workspace and obtains a repository snapshot. With a live watcher, the current in-memory snapshot avoids a full repository walk per query. Without a live watcher, a conservative content-verified scan protects against stale reuse.

Sixth, the goal compiler interprets the task as an explanation/understanding request. Query identifiers and task vocabulary contribute to lexical search. A relevant anchor can be discovered automatically from the best matches rather than from a manually selected file.

Seventh, lexical matches, exact symbol evidence where available, and dependency relationships identify candidates. In the current demo, useful lockout evidence includes `security/auth_service.py`, `security/models.py`, `security/settings.py`, and `tests/test_auth.py`. Short configuration dependencies receive reserved candidate positions so constants are less likely to be crowded out by callers. Explicit topic contrasts can remove independent excluded units from query-specific reference views. Selection remains budget- and ranking-dependent; a particular output is not promised to include every relevant file.

Eighth, a bounded number of candidates receive neural scoring and pruning. The model considers the goal and the code together. It estimates relevance at the token level, aggregates scores to source lines, and removes less relevant spans. Eligible short task-matched candidates not already pre-pruned can retain their source; remaining candidates may contribute interfaces. An overview uses deterministic excerpts rather than neural line decisions. Per-file method labels expose these different treatments.

Ninth, the context builder organizes source-labeled excerpts and adds a preamble explaining that they are reference data, may omit lines, and should not be used as direct source replacements. It counts the complete packed text and enforces the configured budget, including headings and separators.

Tenth, the launcher writes a new activity event and returns the context through tool output or hook injection. The extension observes the activity and shows selected files, source/retained/packed token counts, task, input trace, warnings, and elapsed preparation time. For a fresh non-verification automatic result, it separately requests before/after carbon using the matched formatted baseline and actual backend URL. A late response cannot replace a newer result. The agent uses the supplied evidence and can read original files for additional details.

Finally, the agent produces its explanation. That final reasoning and cloud-model response belong to Antigravity, not TokenWise. TokenWise does not assert that its excerpt is all the evidence the agent will ever need. The rule explicitly allows ordinary file tools for further investigation.

## 9. Installation and the Managed Backend

### 9.1 Normal-user installation

A normal user installs the released VSIX, opens a trusted local Python repository, and runs **TokenWise: Enable Automatic Context**. On a new machine, the extension offers a managed backend installation. Git, Node.js, extension compilation, and F5 are not normal-user requirements.

The current managed runtime requires a 64-bit Python 3.12 interpreter. The installer creates a private virtual environment rather than replacing the application's own environment or installing ML packages into the user's global Python. The documented planning allowance is approximately 10 GB of disk space; 8 GB RAM is a practical starting recommendation, not a performance guarantee.

Setup needs network access to obtain dependencies and about 1.35 GB of pretrained weights. Retrieval can operate offline afterward. Antigravity's own model access still depends on its own service and account. TokenWise does not require a separate inference API key for its local pruner.

### 9.2 The seven visible setup steps

| Step | What it establishes | Recovery behavior |
| --- | --- | --- |
| 1. Prerequisites | Correct Python version/bitness and integrity of bundled backend files | Wrong interpreter or damaged bundle produces a specific error before a valid installation is claimed. |
| 2. Backend files | Verified backend source and assets copied into private storage | Correct storage permissions or disk capacity and retry. |
| 3. Environment | A usable private Python environment | An unusable private environment can be recreated without treating it as the user's project environment. |
| 4. Dependencies | Packaging tools, CPU PyTorch, and backend packages | Checkpoints are revalidated and successful substeps reused; broken checks cause repair rather than blind skipping. |
| 5. Model | Pinned weights downloaded or reused and SHA-256 verified | Partial downloads resume when valid byte-range responses are available; invalid weights are not accepted. |
| 6. Verification | Backend imports, tokenizer, expected model files, and carbon artifacts are usable | Errors identify the failed verification rather than claiming the service is ready. |
| 7. Registration | Verified installation exposed through central registration and user settings | Installed assets remain available if registration needs to be retried. |

The installer groups several dependency substeps under visible step 4. It stores their completion against the bundle fingerprint. On retry, it checks that the environment and package versions still work. A previous completion record is evidence to inspect, not unconditional permission to skip validation.

### 9.3 Model identity and integrity

The backend bundle specifies the upstream checkpoint repository `ayanami-kitasan/code-pruner`, a pinned revision `863cee3198c715c9df1faa422a3490e0832bb734`, the expected file size of 1,345,834,856 bytes, and SHA-256 `373b77f5262c3298b803303d49ea38949d3e92f08dc3bbb90b03f490413adae9`.

The hash identifies the exact bytes accepted by the installer. Pinning a revision avoids silently changing the runtime model when a repository's default branch changes. Integrity validation catches corruption or an incorrect local copy. It does not, by itself, establish that the upstream model is scientifically ideal or remove the need to respect its licensing and provenance.

Downloads use HTTPS, check the final response protocol, validate range offsets and total size, and verify the finished file. If the server ignores a resume request and returns a whole-file response, the installer restarts the partial file instead of appending incorrect bytes. A complete verified cache entry can be reused; a complete verified partial download can be recovered.

### 9.4 Storage and upgrades

Managed installations use version-and-bundle-fingerprint-specific directories under the extension's user storage. The model cache and package cache support reuse across attempts. Repositories resolve a central installation registration rather than each embedding a version-specific backend path.

On a managed update, a verified owned backend can be stopped after installation succeeds, and background synchronization reconnects to the new registration. A checkout backend is treated differently: it is not deleted or automatically terminated as though it were extension-owned. This distinction protects development environments and unrelated work.

The initial download and private ML environment are substantial usability costs. The project makes these costs visible and recoverable; it does not eliminate them. Future acceleration or smaller models would need their own relevance and quality evaluation.

## 10. Enabling an Arbitrary Python Repository

### 10.1 The central-backend design

An enabled repository contains a small `.tokenwise/backend-link.json` file pointing to the profile's central registration. That registration identifies the actual installation, Python executable, and runtime directory. Workspace launchers use it to run the installed backend adapter.

This allows a project such as `E:\Projects\demo-python` or `C:\Projects\my-app` to use TokenWise without being copied inside its source checkout. Multiple enabled repositories in an IDE profile can share the same installed ML runtime.

### 10.2 Files created or updated

| Workspace location | Purpose |
| --- | --- |
| `.agents/tokenwise.json` | Automatic retrieval settings, including budget, threshold, limits, and startup policy |
| `.agents/hooks.json` | TokenWise handler merged into existing hook configuration |
| `.agents/rules/tokenwise*.md` | Always-on rule defining retrieval behavior and the fallback command |
| `.agents/tokenwise/` | Platform-specific launchers and setup ownership manifest |
| `.tokenwise/backend-link.json` | Local link to the central backend registration |
| `.tokenwise/latest.json` | Most recent retrieval activity and prepared context |
| `.tokenwise/conversations/` | Native-hook deduplication and bounded same-topic earlier-user state, scoped by workspace/conversation identity |
| `.gitignore` | Generated rule to exclude local TokenWise runtime data where necessary |

Setup changes integration/configuration files, not application source. The runtime directory can contain source excerpts and task text, so excluding `.tokenwise/` from accidental Git publication is important.

### 10.3 Preserving existing work

Configuration is not implemented as an indiscriminate overwrite. Existing hook entries and unrelated handlers are retained. Existing settings are merged with defaults, with automatic retrieval enabled. If a rule filename belongs to user content, setup can select another TokenWise rule filename. Customized launchers are not silently replaced.

The ownership manifest records hashes of generated rules and launchers. Later setup and cleanup use those hashes to distinguish unchanged generated content from user modifications. JSON must be valid before writes proceed. Invalid settings or malformed JSON produce an actionable failure instead of replacing the file with defaults.

Writes are planned using snapshots, checked for concurrent changes, and applied atomically per file. If a later write fails, the attempt restores only bytes still matching what that attempt wrote. A concurrent user edit is not rolled back just to make setup appear transactional.

### 10.4 Trust and path safety

First-run setup requires a trusted local workspace and local extension host. It rejects unsupported remote or virtual workspace situations. Path checks keep writes within the designated directory and reject symlinks/junctions that could redirect integration writes elsewhere.

The local IDE storage path is resolved through editor-aware helpers. A local Antigravity `vscode-userdata` storage URI is not automatically the same as a remote repository. The meaningful check is whether the path can be treated as the expected local native storage, not whether every URI happens to use the literal `file` scheme.

## 11. The Extension and Its User Interface

### 11.1 Activation responsibilities

The extension activates after editor startup. It initializes lifecycle tracking, the pruning service, result panel, backend management, repository-index synchronization, automatic activity monitoring, status display, and commands. These components cooperate but have distinct responsibilities.

Backend management handles installation, registration, startup, update prompts, and diagnostics. Repository synchronization handles saved-file events and index leases. Automatic activity monitoring observes the result of a prompt-related retrieval. The result panel displays data; it is not the engine performing retrieval.

### 11.2 Commands and their purpose

| Command | When it is useful |
| --- | --- |
| **Enable Automatic Context** | First-time workspace configuration or repair of its backend link |
| **Set Up Backend** | Install, repair, or update the managed runtime independently of workspace configuration |
| **Start Backend** | Warm the model and select the actual running backend endpoint |
| **Diagnose Setup** | Inspect registration, installation, backend health, and workspace configuration |
| **Open Setup Guide** | Read bundled instructions without needing the development checkout |
| **Open Demonstration Guide** | Open the bundled current one-project teacher walkthrough |
| **Demonstrate Pruning Inputs** | Inspect no-anchor repository discovery, exact selected source, or an explicitly supplied user-history replay |
| **Compare Context Strategies** | Export unpruned all-Python/manual-selection packets and unbiased automatic context for the same snapshot/task |
| **Configure Automatic Comparison** (0.6.7) | Enable/disable local comparison for fresh automatic packets or retry the latest snapshot |
| **Import Antigravity Usage Comparison** (0.6.7) | Compare two independent successful CLI usage logs separately from packet counts |
| **Open Validation Guide** (0.6.7) | Open the bundled classroom quick route, fixed tasks and with/without rubrics |
| **Show Automatic Context** | Inspect the most recently observed prepared context |
| **Remove All Local Data** | Explicitly remove extension-owned data while the extension is still installed |
| **Prune Selected Code** | Manually analyze a selected text region for a task |
| **Prune Current File** | Manually prune a complete editor file |
| **Build Repository Context** | Manually build task-oriented repository context using an active Python file as additional evidence |
| **Check Backend Health** | Verify model/carbon readiness and service/device information |

All names above have the `TokenWise:` prefix in the command palette. Manual workflows remain useful for inspection, comparison, and non-Antigravity VS Code use. The automatic experience relies on the agent integration and does not require these manual pruning commands for every prompt.

### 11.3 What result views communicate

The single-file view compares original and pruned text, backend-native counts, model-input count, document relevance, line scores, decision-mask fragments, and sustainability estimates when available. A captured input trace identifies entire-file versus excerpt scope, the first source line, the task, and requested threshold. The repository view displays the structured goal, excluded topics, selected files, relations, tiers, pruning methods, applied thresholds, retained source, formatting overhead, packed context, and warnings. Automatic results also include task and preparation time. Copy and JSON-export controls make controlled runs inspectable outside the panel.

The decision mask precedes final excerpt formatting. A line can be kept by threshold or by preservation/gap bridging, and a formatter can retain a small removed span for readability. The displayed line table is limited to its first 200 lines; the JSON export carries the available complete scores. Do not describe the mask as a guaranteed executable-source transformation or proof that every printed line independently passed the threshold.

The interface provides copy actions, not a button that replaces application source with a pruned excerpt. Elision markers and incomplete blocks make such replacement unsafe. A context optimizer should help the agent reason about source while preserving the original program as the authority.

The status bar is a compact operational indicator. The automatic file/token count describes a particular prepared result. A manual-session carbon accumulator is not a complete meter of all agent requests, all repositories, or the actual electricity used by the IDE.

### 11.4 Settings and defaults

The manual API URL defaults to `http://127.0.0.1:8000`, request timeout to 120 seconds, and threshold to 0.45. Manual repository context defaults to 8,192 tokens. Automatic workspace settings independently default to 4,096 tokens, six candidates, a 40-second backend-start timeout, and a 90-second retrieval timeout.

The optional local goal model is disabled by default. Carbon estimation is enabled by default and uses a benchmark-backed Llama-3 8B target, 256 expected output tokens, and an assumed carbon intensity of 475 gCO2/kWh. Optional model-size and latency overrides left unset or saved as zero use automatic registry features; blank GPU overrides are omitted. Valid zero benchmark scores remain real overrides. These are configured scenarios, not automatic detection of the current Antigravity cloud model or region.

Changing a manual extension setting does not necessarily alter the automatic workspace JSON setting. Explain the control boundary clearly when demonstrating a different budget: edit `.agents/tokenwise.json` for the automatic launcher, and use the repository-budget extension setting for the manual command.

The 0.6.6 response-guidance addition follows the same boundary. Automatic retrieval uses the default-on JSON boolean `response_guidance`; manual repository/demo/comparison requests use `tokenWise.enableResponseGuidance`. These switches control outgoing instructions, not the neural model's input format or the optional local goal model. Direct selected-source pruning does not add this response-guidance packet.

## 12. Backend Service and API Contracts

### 12.1 FastAPI service lifecycle

The backend is a Python FastAPI application served by Uvicorn. Startup resolves the model directory, validates expected assets, and loads the neural model locally. Carbon artifacts are initialized separately. An asynchronous reconciliation task periodically checks watched repositories.

If the neural model is missing or fails to load, the service can still expose health information. Pruning endpoints then return a model-unavailable error instead of pretending a random or untrained model is usable. Likewise, unavailable carbon artifacts do not disable all pruning functionality.

CPU thread settings are bounded. The default is four CPU threads, configurable within a maximum of eight through `TOKENWISE_CPU_THREADS`. Neural requests are serialized with an inference lock to avoid unsafe concurrent model operations and excessive CPU oversubscription. Blocking work is moved to worker threads so the HTTP event loop is not used as the direct computation loop.

### 12.2 Main endpoints

| Endpoint | Responsibility | Important validation |
| --- | --- | --- |
| `GET /health` | Service identity, neural/carbon readiness, device, model path, PID, and indexing capability | Clients should inspect readiness fields, not just successful HTTP status. |
| `POST /prune` | Query-conditioned pruning of submitted code text | Nonempty query/code and threshold bounds through request schema |
| `POST /prune-workspace` | Goal-driven repository retrieval, pruning, and packing | Python language, existing workspace, nonblank task, active-file containment, budget and candidate bounds |
| `POST /compare-workspace` | All-indexed-Python/manual-selection/automatic packet comparison for one snapshot | Saved selection containment, at most 200 indexed files/2 MiB of source, and unchanged fingerprint; editor/history hints are removed from the automatic branch |
| `POST /compare-prepared-workspace` (0.6.7) | All-Python baseline versus an exact already-prepared packet, without a second pruning pass | Saved-file reconciliation, snapshot equality, packet-count validation and baseline size limits |
| `POST /index-workspace` | Start, update, reconcile, or stop a background watcher session | Absolute workspace path, bounded path batches, watcher identity, and sequence values |
| `POST /estimate-carbon` | Predicted phase energy and carbon from workload/model assumptions | Feature values, supported encoded hardware, and loaded artifacts |

Pydantic defines request types and numeric bounds. Invalid schema input is different from a valid request that refers to a nonexistent repository. Model-unavailable conditions use HTTP 503; repository/configuration problems commonly use HTTP 400. The clients expose response errors rather than swallowing them.

### 12.3 Readiness is more than a running port

Another application may already use port 8000. TokenWise checks its service identity and model path before reusing a process. If needed, startup searches a small nearby port range and records the actual port. It does not terminate an unrelated process to take its port.

A healthy HTTP server with `model_loaded: false` cannot provide neural pruning. A server with `carbon_models_loaded: false` cannot provide a valid trained carbon estimate. In a defense, show that the diagnostic contract exposes these separate conditions.

### 12.4 API response interpretation

A workspace result includes its structured goal, context mode, source-labeled unified prompt, packed count, original and retained source counts, formatting overhead, matched unpruned packet count, selected-file methods and thresholds, anchor, indexed-file count, warnings, repository fingerprint, input trace, and cache diagnostics. Accepted conversation hints affect the effective objective and are disclosed in the trace. The comparison endpoint additionally attaches three complete packets. These fields connect a result to its actual input, snapshot, method, and denominator rather than just a reduction percentage.

The cache flags distinguish repository-index reuse, prepared retrieval-data reuse, and a complete context-cache hit. They should not be combined into the statement that every cache hit skips all processing. A different task can reuse the index and search data while requiring fresh ranking and pruning.

## 13. Task and Goal Compilation

### 13.1 Why a structured goal exists

A user's natural-language task contains several kinds of information: requested action, target identifiers, symptoms, errors, and desired evidence. Converting this into a structured goal makes retrieval more explicit and reduces dependence on a raw phrase alone.

The goal contains `task_type`, `objective`, `identifiers`, `excluded_topics`, `observed_errors`, `required_context`, `retrieval_questions`, and `clarification_required`. Manual repository commands can also supply the active file, current symbol, selected code, and diagnostics. The automatic path intentionally works without those selections. Recognized follow-ups can supply earlier user context as reference evidence, not as a higher-priority instruction.

### 13.2 Deterministic default behavior

The default compiler uses task vocabulary and templates for understanding, debugging/fixing, refactoring, adding features, testing, generic investigation, and explicit repository overviews. It extracts plausible identifiers and error evidence from the supplied task and editor evidence. Generic request words such as `GIVE`, `FULL`, `OVERVIEW`, and `PROJECT` are not treated as useful code identifiers for a broad overview.

This approach is fast, predictable, and available offline without another model server. It avoids a failed optional-LLM request on every ordinary prompt. It is also limited: keyword interpretation is not deep program comprehension, and regex-derived identifiers are not proof that the repository defines a matching symbol.

The goal's required-context and retrieval-question fields communicate intent. They do not mean the system executes a complete autonomous multi-hop planning process for every question. The implemented retriever remains lexical, graph-based, and bounded.

### 13.3 Optional local LLM generation

When enabled, a local OpenAI-compatible chat endpoint can produce structured goal JSON. The client requests deterministic-style output, validates it with the same schema, and uses the deterministic compiler if the request or validation fails. The optional call has its own timeout.

This is an enhancement rather than a dependency of normal installation. Ollama or LM Studio can supply such an endpoint if the user chooses to configure one. No additional model server is required for the default TokenWise experience.

If a user changes this endpoint to a nonlocal service, its privacy implications must be considered. The name 'local goal model' does not magically make an arbitrary URL local. Network destination and what task/editor evidence is sent determine the actual exposure.

### 13.4 Ambiguity and clarification

A vague task such as 'fix the bug' without evidence can set `clarification_required`. That expresses missing information but currently does not stop the backend and force an interactive clarification exchange. The backend can still construct whatever context is available.

This is a useful defense distinction: the project models ambiguity and can include a warning/instruction to clarify, but it does not implement a full enforced clarification dialogue. The fallback rule asks for clarification when a same-chat reference has no identifiable subject. These measures are not a guarantee that the agent will resolve every ambiguous prompt correctly.

### 13.5 Broad requests and explicit exclusions

A task such as 'Give me the full overview of my project' becomes `repository_overview`. It seeks documentation, entry points, core behavior, models, configuration, and tests rather than only the nearest dependency neighborhood. This is distinct from explaining one class or function.

For 'Explain session expiry, not invoice pricing,' the contrast parser separates positive query terms from `excluded_topics`. Recognized contrasts include ', not', 'but not', 'rather than', and 'excluding'. Ordinary code negation such as 'not revoked' and instructions such as 'do not modify files' are not general exclusion rules. This distinction prevents unwanted invoice terms from becoming positive retrieval targets while preserving the meaning of the user's real task.

Focused repository retrieval builds AST-based reference views that can omit independently excluded declarations, methods, unused excluded imports, and separate display statements. It protects helpers required by the positive topic, reports warnings when those helpers must remain, and falls back safely if a view cannot be isolated. It does not edit application files, mutate their authoritative source text, or apply arbitrary line deletion. Exact selected-source pruning still receives the captured file/excerpt; it is not silently replaced with a repository scope-filtered view.

### 13.6 Earlier user context in the effective task

The API accepts `conversation_history` with at most 32 user strings, each bounded to 2000 characters, or a legacy `context_hint` of at most 4000 characters. The selector identifies a related topic segment and chooses at most eight references and 4000 characters. History contributes to goal compilation, lexical retrieval and pruning for related explicit tasks as well as recognized follow-ups. The trace separates current query, effective objective, selected reference text and provenance; Section 21.5 explains transport, selection and packet bounds.

### 13.7 Outgoing response guidance and prompt engineering

This is an implemented feature in **0.6.6**; older installers do not contain it. Its role is to improve the instructions accompanying retrieved evidence; whether it improves downstream answers must be established through an experiment. The release includes both this study and the teacher rehearsal.

#### Three different uses of prompting

TokenWise now has three distinct instruction-related stages. First, goal compilation converts developer intent into a retrieval objective. Its deterministic templates already express what kinds of behavior to inspect, while the optional local-model path asks for validated structured JSON. Second, the neural pruner conditions source relevance on that objective. This is the pretrained model's established input convention, not a new outgoing agent prompt. Third, response guidance instructs the downstream agent how to answer using the selected evidence. The new feature implements this third stage without altering either earlier stage's model input.

Calling these all 'prompt engineering' without distinguishing their purpose would obscure the system. The specific outgoing techniques are **task-aware instruction templates**, **evidence grounding**, **constraint preservation**, and **instruction/reference separation**. They are not fine-tuning, a new trained model, hidden-chain-of-thought prompting, or a guarantee of correctness.

#### How the outgoing stage works

After the structured goal is available, repository retrieval builds its normal preamble. A deterministic helper chooses one of six response profiles from `task_type`, appends a complete guidance block before source excerpts, and then passes that combined preamble into the normal token-budgeted packer. Overview mode explicitly chooses the overview profile. Unknown categories fall back to generic guidance. Repository text and arbitrary task-type strings are not interpolated into the template instructions.

| Profile | Intended answer behavior |
| --- | --- |
| `generic_task` | Explain relevant behavior and boundaries; separate evidence from assumptions |
| `bug_fix` | Separate observed symptoms from hypotheses; explain a proposed fix and validation |
| `refactor` | Identify affected interfaces and behavior to preserve; disclose validation and risks |
| `feature_addition` | Use existing interfaces/patterns; explain integration without inventing requirements |
| `test_generation` | Connect cases to behavior/boundaries; separate existing tests from proposed tests |
| `repository_overview` | Cover purpose, entry points, components, data flow, and tests; disclose gaps or scaffolding |

Full profiles share instructions to follow the latest user request and its constraints, cite files/symbols for repository claims, inspect originals when excerpts omit required evidence, and never invent behavior or claim tests passed without execution. The latest user request remains authoritative: 'Do not modify any files' is not changed into permission to fix something merely because a debugging profile was selected. Likewise, the agent should respect a user-requested response format instead of treating these profiles as a mandatory replacement format.

The automatic preamble labels source text as reference data. Code remains in source-labeled fenced blocks. The Windows and portable always-on rules describe the guidance as optional assistance that cannot override the user's constraints; source comments are not instructions. This boundary reduces ambiguity but is not proof of an unbreakable prompt-injection defense. The final agent and its platform still enforce permissions and higher-priority policies.

#### Concrete example

For `Explain session expiry and its related tests. Do not modify any files.`, the user task is preserved while TokenWise supplies retrieved excerpts and an explanation-oriented profile. A useful answer should establish expiry and revocation from `security/models.py`, `security/auth_service.py`, `security/settings.py`, and discovered related tests rather than inventing session persistence, renewal, encryption, or successful execution. Which files actually fit the packet depends on retrieval and its budget. The template itself does not hard-code the demo's 300-second duration or any other application facts.

The guidance tells the agent what evidence standard to use; it does not tell it which factual conclusion to reach. If the expiry constant or test body is missing, it asks the agent to inspect originals or disclose the gap. It cannot make absent evidence appear, nor can it make a tiny scaffold behave like a full application.

#### Cost, budget, and integrity

This helper requires no additional LLM call. It constructs text from fixed strings and counts it with the same tokenizer used by the context packer. It does not change the neural checkpoint, add a remote API dependency, or promise zero extra cost: the added instructions take downstream input tokens and counting work.

The guidance fragment is limited to the smaller of **160 TokenWise tokens** and **one quarter of the configured packet budget**. The helper also requires at least 96 tokens outside the combined preamble before accepting a guidance variant; this is a packing allowance, not a guarantee that every file or relevant function can fit. It first tries the full profile, then a compact common instruction with the profile identified in its heading. If neither complete variant fits, it omits guidance rather than chopping an instruction mid-sentence. The compact form carries common constraints, not the full profile's task-specific sentence. The final packer remains responsible for enforcing the complete packet budget, including separators, labels, fences, and source.

The unpruned matched baseline for ordinary before/after carbon reporting contains the **same guidance** as the pruned packet. Otherwise the comparison could accidentally attribute a difference in instructions to source pruning. Guidance tokens are context overhead, not retained source tokens; source reduction and complete packet counts retain different meanings. The optional all-Python/selected/TokenWise comparator still preserves the original unpruned baseline packets and discloses guidance only on its TokenWise branch. That is a comparison of whole strategies, not an isolated experiment on the guidance alone.

Complete-result cache identity includes guidance version and enabled state. Therefore an unguided request cannot accidentally receive a cached guided packet, and changes to a future template must increment its version. Query-independent AST, lexical, and graph data remain reusable. Regression tests compare model-call counts with guidance enabled and disabled so the new stage cannot silently introduce another neural pass.

#### Trace and user controls

Every current workspace result carries a `response_guidance` trace:

| Field | Meaning |
| --- | --- |
| `version` | Template contract version, currently `1` |
| `profile` | Selected supported task category |
| `enabled` | Whether the request opted into guidance |
| `status` | `applied`, `disabled`, or `omitted_budget` |
| `format` | `full`, `compact`, or `null` when omitted/disabled |
| `tokens` | Tokenizer count for the guidance fragment, zero when absent |
| `text` | Exact emitted guidance text, empty when absent |

The repository result panel shows version, profile, status, format, and fragment tokens; complete context and JSON exports provide the text and counts. Older reports remain usable and show `not reported` rather than pretending they contain the feature. Automatic activity parsing validates new optional metadata while preserving compatibility with older records.

Automatic Antigravity retrieval uses `"response_guidance": true` in the repository's `.agents/tokenwise.json`; a boolean `false` disables it. The default is true even for an older settings file that omits the key. Manual **Build Repository Context**, repository/history demonstrations, and **Compare Context Strategies** independently use `tokenWise.enableResponseGuidance` in editor settings. Direct `/prune` and selected-source commands still produce raw excerpts and line decisions, not guided outgoing repository packets. Disabling response guidance does not disable retrieval, earlier-user hints, source-reference labels, or the existing Antigravity rule.

Normal users install the 0.6.8 VSIX, reload, update the Python backend through **Set Up Backend**, and refresh workspace rules through **Enable Automatic Context**. A developer source-build trial instead requires `npm run prepare-backend`, `npm run compile`, and F5 from `vscode-extension`, followed by the same backend/setup refresh. Compile alone updates TypeScript, not an already installed/running Python service. See the [README rehearsal](README.md#response-guidance) and [demonstration](demonstation.md#response-guidance).

#### How to establish whether answers are better

The on/off switches make the feature inspectable, but repeating two prompts is not sufficient proof. To isolate its effect, export one current packet and form a paired condition by removing only the exact emitted guidance block. Keep the original task, source excerpts, headers, context snapshot, agent model, requested answer constraints, available tools, and expected-output assumptions the same. Verify that the copied guided and unguided packets otherwise contain identical evidence. Start a fresh chat for each trial, avoid an active TokenWise rule injecting a second guided packet, and alternate or randomize condition order. Record any additional file reads: if the agent obtains different evidence through tools, that is a workflow outcome rather than a pure fixed-evidence comparison.

Score multiple repeated tasks against executable or manually verified ground truth: factual correctness, relevant file/symbol citations, boundary-condition coverage, disclosure of missing evidence, unsupported claims, user-constraint compliance, latency, and input/output tokens. A session explanation can be checked against the exact `now < expires_at` boundary, revocation behavior, and real tests. A refactoring task needs preservation checks, while a feature task needs requirement and integration checks. Do not compare only stylistic detail or the largest reduction percentage.

When testing the two settings directly with the same budget, the extra guidance may reduce available source space, so record any evidence changes. That test evaluates the practical combined workflow. It is distinct from the fixed-excerpt instruction ablation above. No downstream Antigravity answer-quality study is claimed as complete merely because transport and budgeting tests pass.

#### Verification recorded for this addition

On October 7, 2026, source verification completed with **174 extension tests passed**, **119 backend tests discovered: 118 passed and one Windows symlink-privilege skip**, and **20 demonstration application tests passed plus its application check**. The backend suite includes 13 new response-guidance tests. The bundled real tokenizer was loaded offline to check all full profile limits and focused/overview packet counts at 256, 512, and 4,096 tokens with guidance on and off. The generated development bundle contains the new backend module.

HTTP and neural-call regressions use a reference pruner/test double; they validate delivery, profiles, budgets, metadata, and cache behavior rather than measuring pretrained relevance accuracy. No new Antigravity cloud answer-quality trial or measured energy experiment was performed. These are source-addition checks, not replacements for the historical 0.6.5 release verification numbers elsewhere in this guide.

#### A defensible presentation statement

> I implemented a task-aware prompt-engineering layer at the point where TokenWise sends repository context to Antigravity. It combines evidence-grounding instructions, user-constraint preservation, and separate instruction/reference blocks. The versioned guidance is bounded, inspectable, switchable, and adds no model call. I designed it to improve answer reliability; a controlled guided-versus-unguided study is needed to quantify that benefit.

## 14. Python Repository Indexing

### 14.1 Discovery without executing the repository

The indexer walks the workspace for Python source files, accepting the `.py` suffix case-insensitively. It excludes common development and generated directories, including `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`, build outputs, editor folders, cache folders, `.agents`, and `.tokenwise`.

The indexer reads source as data and parses it; it does not import and run arbitrary application modules. This makes indexing usable on repositories that cannot currently install dependencies or start successfully. It also avoids triggering application side effects merely to discover definitions.

The exclusion set is fixed in the current implementation. There is no general `.gitignore` parser or dedicated `.tokenwiseignore` engine controlling indexing. Adding `/.tokenwise/` to a repository's Git ignore file is about publication hygiene; it is not proof that all other Git-ignored source is excluded from retrieval. There is also no explicit general source-file-size cap at this boundary.

### 14.2 Metadata collected

Each indexed file can provide source text, content hash, AST-derived definitions, imports, call names, line locations, lexical counts, path/symbol terms, interface text, and cached token counts. Classes include names, bases, method-name metadata, and locations. Functions contribute definition metadata and symbol locations.

Ordinary function handling and async-function handling are not fully uniform. The definition visitor does not register async functions in the same way as ordinary `FunctionDef` nodes, while interface construction can retain async signatures. This matters in async-heavy repositories and is an example of a concrete language-coverage limitation rather than a generic claim that AST analysis covers all Python equally.

### 14.3 Stable reads and syntax errors

Files may change while being read. The index uses filesystem metadata and repeated consistency checks to reduce the chance of mixing bytes and metadata from different versions. It computes a SHA-256 content identity for the accepted text.

Unchanged files retain parsed and derived metadata. A syntax-invalid file can remain lexically searchable from its text even when AST definitions, graph evidence, or generated interfaces are unavailable. The index therefore does not treat a temporary syntax error as proof that the file has no useful evidence.

Path resolution rejects escapes outside the workspace. A symlink to an external file should not make arbitrary source outside the selected repository become part of its context. This containment behavior should be understood separately from the stronger symlink rejection used for setup and cleanup writes.

### 14.4 Interface extraction

An interface view is a compact structural representation built with AST operations. It can keep imports, top-level assignments, annotated assignments, classes, relevant class assignments, function/method signatures, decorators as represented by the AST transformation, and placeholder bodies. It does not retain the full implementation of every function.

This view helps expose what a transitive dependency offers without paying for all its internal details. However, top-level assignments can contain meaningful values, and a signature-only view is not guaranteed to conceal secrets or preserve every runtime contract. It is a structural compression method, not a privacy filter or formal API specification.

## 15. Dependency Graph and Structural Retrieval

### 15.1 Nodes, edges, and direction

Files are graph nodes. Imports and approximate call relationships create edges from a file to files it appears to use. A reverse adjacency structure supports finding dependents: files that import or call into another file.

This reverse direction is important for tests. A service may not import its tests, but a test often imports the service. Traversing only outgoing dependencies would miss that useful evidence. TokenWise can traverse both outgoing and incoming relationships.

### 15.2 Two-hop expansion

Breadth-first search explores nearby files and records shortest graph distance, with a maximum of two hops in the current retrieval design. A first-hop neighbor might be a directly imported model or a test importing the anchor. A second-hop neighbor might be the configuration imported by a cryptographic helper.

The graph is not traversed without bounds. Candidate limits and later ranking control how much discovered evidence can enter the final bundle. Being two hops away does not guarantee inclusion, and being more than two hops away does not make a file intrinsically irrelevant.

### 15.3 Example: authentication evidence

In `demonstration/tokenwise_demo`, `security/auth_service.py` imports account/password definitions from `security/models.py` and threshold/duration constants from `security/settings.py`. `tests/test_auth.py` imports the service and asserts the failure count, lockout interval, and expiry boundary. `app.py` imports these components and the independent workflows. These relationships connect implementation, constants, state, callers, and tests.

For a lockout question, the service, settings, and tests are usually more important than unrelated invoice/shipping behavior. Graph evidence complements lexical search by revealing dependencies whose filenames or source text may not share the user's exact words.

### 15.4 Approximation limits

Module resolution uses simplified mappings and suffix matching. Call resolution relies on names rather than a complete Python type and import resolver. Aliases, relative imports, package `__init__` behavior, same-named functions, dynamic imports, runtime dispatch, and inheritance can produce incomplete or incorrect edges.

Accordingly, the correct defense statement is 'the graph helps retrieve structurally related evidence,' not 'the graph proves the complete runtime dependency set.' Supporting tests and manual source inspection remain essential for validating behavior.

## 16. Lexical Retrieval and Candidate Ranking

### 16.1 Term normalization

The lexical retriever normalizes code and task vocabulary so camelCase, snake_case, and common plural variations can contribute matching terms. It uses stop-word handling to reduce uninformative query words. Terms can come from content, paths, and symbols.

Path and symbol evidence are especially useful in code retrieval. A file named `auth_service.py` or a class named `AuthService` can be more informative than a repeated generic word in a long file. This is why the scoring design does not use body occurrence counts alone.

### 16.2 The implemented scoring idea

For a query term `t`, a simplified statement of the implemented weight is:

```text
weight(t) = ln(1 + N / (1 + df(t)))
evidence(file, t) = min(content_count(file, t), 4)
                  + 5 * path_count(file, t)
                  + 3 * symbol_count(file, t)
lexical_score(file) = sum(weight(t) * evidence(file, t))
```

Here, `N` is the number of indexed files, and `df(t)` is the content-document frequency of the term. The content cap reduces the effect of repetitive words. The path and symbol boosts provide source-structure information. Ties are resolved deterministically using file paths.

This is a custom TF/IDF-like scoring method. It should not be called BM25, because the implementation does not use the full BM25 length normalization and saturation formula. Precise algorithm naming matters in a technical defense.

### 16.3 Automatic anchor discovery

Automatic retrieval does not need an active editor. The system can choose an anchor from strong task matches. When evidence is weak, it has conventional entry-point fallbacks such as `app.py`, `main.py`, or `__main__.py`, and deterministic fallback ordering.

The anchor is a retrieval starting point, not a certificate that the file is the answer. Exact identifier matches and the top lexical matches also seed discovery so the graph does not depend entirely on one initial file.

### 16.4 Hybrid ranking and candidate bounds

Candidates come from the anchor, identifier evidence, strong lexical matches, and graph expansion. Neural scoring is bounded to avoid running the expensive model over an entire repository. The automatic path pre-prunes at most three selected neural candidates and can reuse their returned document score and excerpt.

A hybrid score combines normalized lexical evidence with neural probability, using the stronger signal rather than pretending the two values have identical origins. Other candidates can contribute interfaces. The automatic default candidate limit is six, while the manual API default is eight. These are maximum candidate controls, not promises that six or eight files fit the final prompt.

The manual candidate-ranking path can score truncated candidate content and then later prune selected content, creating possible additional model work. The automatic path's reuse avoids repeating the same pruning operation for its pre-pruned candidates. Up to two short configuration dependencies are reserved after the initial priority candidates, within the overall limit. Eligible matched bodies of at most 512 local tokens can remain intact when not already pre-pruned; this packing shortcut does not mean every small candidate avoids an earlier neural pass. These distinctions matter when discussing latency and implementation choices.

### 16.6 Dedicated overview retrieval

Overview retrieval reads at most two supported root documentation/package files, preferring one README and then available configuration. Each document read is limited to 64 KiB with stable-read/containment checks and warnings for clipping or concurrent changes. Its document fingerprint joins the complete-context cache key, so a README/package edit can invalidate an overview even when no Python file changed.

Python files are grouped into representative roles: entry point, core logic, tests, data model, API, configuration, storage, utility, module, and package interface. Deterministic role coverage and structural prominence select candidates independently of the open editor. Small implementations of at most 1,600 characters can remain intact; larger ones generally use cached interfaces. A bounded repository map lists component counts and up to 24 paths. The overview packer shares remaining space among later components rather than allowing a README to consume the entire budget.

This route does not perform neural line pruning and its method is `overview_excerpt`. The serving contract still requires the installed pruner runtime and its tokenizer. Coverage warnings identify omitted indexed Python files; initializer-only scaffolds receive an explicit warning rather than an invented application overview. Documentation, candidates, and budget remain bounded, so 'overview' never means a guaranteed complete audit of every project asset.

### 16.5 Retrieval failure modes

A lexically unfamiliar task may miss the right file. A generic query may choose an unhelpful anchor. A dynamic dependency may be absent from the graph. Candidate caps may discard useful evidence in a large repository. A first file can consume much of the packing budget.

These are reasons to measure retrieval recall and downstream task success. A low token count alone cannot establish that context quality is good. TokenWise exposes sources and allows the agent to read additional originals so the initial bundle is not treated as an infallible closed-world answer.

## 17. Research Foundation: SWE-Pruner

### 17.1 What the paper contributes

The [SWE-Pruner paper](docs/papers/SWE-Pruner.pdf), titled *SWE-Pruner: Self-Adaptive Context Pruning for Coding Agents*, proposes task-conditioned filtering of the code observations received by a coding agent. The central idea is a goal hint: the pruner is told what the agent is trying to learn or accomplish, so relevance can change from task to task even for the same source file.

This is more specific than generic summarization. A summary might describe a service broadly; a goal-conditioned pruner can preserve the exact failure check, return behavior, or test assertion needed for the current task. The output remains selected source evidence, rather than only a newly generated natural-language description.

The paper's agent setup inserts pruning into file/tool observations, such as code returned by file-reading commands. TokenWise instead primarily builds an initial repository-context bundle for a user task. Both are task-conditioned context optimization, but they operate at different integration boundaries. The project should not be described as an exact reproduction of the paper's entire agent harness.

### 17.2 Research model and training approach

The paper uses a Qwen3-Reranker-0.6B backbone and combines features from early, middle, and late transformer layers. Its model has token-compression and document-relevance objectives. A CRF component models dependencies between keep/drop labels so neighboring decisions need not be treated as wholly independent.

The training data are generated through a teacher-student process. The paper describes extracting 200,000 snippets from 195,370 files across 5,945 repositories and retaining 61,184 final examples. Teacher and judge models create and evaluate task-conditioned selections across tasks including explanation, debugging, refactoring, optimization, locating code, feature addition, completion, and relevant-part extraction. These figures describe the researchers' training dataset, not a dataset TokenWise generated locally. See the paper's methodology and appendices.

The reported training combines a sequence-length-normalized CRF negative log-likelihood with a relevance-regression loss:

```text
L_compress = mean(CRF_negative_log_likelihood_i / sequence_length_i)
L_rerank   = mean((predicted_document_score - teacher_score)^2)
L_total    = (1 - lambda) * L_compress + lambda * L_rerank
lambda     = 0.05
```

The paper reports specialized multi-GPU training, optimization settings, and selective transformer-layer tuning. TokenWise's ordinary backend installation does none of this training. It loads a supplied pretrained checkpoint and its configuration.

### 17.3 Published results and their limits

On SWE-Bench Verified, the paper's Table 1 reports a Claude Sonnet 4.5 configuration increasing success from 70.6% to 72.0% while reducing reported tokens from 0.911 million to 0.701 million, a 23.1% reduction. Its GLM-4.6 configuration increases success from 55.4% to 56.6% while reducing tokens from 0.791 million to 0.488 million, a 38.3% reduction. These are external benchmark results under the paper's agent and model configurations, not TokenWise's measured success rate. [SWE-Pruner, page 7, Table 1](docs/papers/SWE-Pruner.pdf).

The paper also examines long-code question answering and code completion. Some compressed settings improve efficiency while losing quality on particular metrics. For example, its long-code-completion table does not support the claim that pruning always improves exact match. This is evidence that compression is a tradeoff requiring task-specific validation, not an unconditional improvement. [SWE-Pruner, page 8, Table 4](docs/papers/SWE-Pruner.pdf).

The paper's latency table reports average time to first token (TTFT) and depends on its measurement hardware and input size. It reports approximately 44.70 ms at 64 tokens and 102.00 ms at 8,192 tokens. This table is not an end-to-end repository-request benchmark. The general narrative about very low latency should not be turned into a promise that TokenWise's CPU repository requests complete in under 100 ms. [SWE-Pruner, page 20, Table 6](docs/papers/SWE-Pruner.pdf).

Its AST-validity analysis also matters: pruning does not make every output valid executable code. One reported Function RAG comparison falls from 92.3% AST correctness to 87.3% with SWE-Pruner. Even the paper does not establish universal preservation of complete program syntax. [SWE-Pruner, page 21, Table 8](docs/papers/SWE-Pruner.pdf).

### 17.4 What TokenWise takes from the research

TokenWise uses the goal-conditioned neural-skimming idea, the pretrained model architecture/checkpoint, and token-to-line relevance selection. It contributes a practical repository discovery pipeline around that capability, a hard final context budget, editor integration, cache and lifecycle management, and a sustainability-estimation workflow.

The research establishes why this design is worth exploring. The project's own tests establish whether its integration behaves correctly. Independent downstream agent experiments would be needed to establish that TokenWise reproduces the paper's quality or token-saving outcomes.

## 18. The Deployed Neural Pruner

### 18.1 Input and task conditioning

The pruner receives a query/goal and code text. It constructs a model input containing instructions, task evidence, code, and the delimiters expected by the checkpoint. The same file can therefore produce different retained lines for 'explain lockout' and 'explain session revocation.'

The neural model is a relevance model. It does not generate a rewritten implementation, synthesize tests, or answer the user question directly. It produces signals used to select useful evidence.

### 18.2 Backbone and feature fusion

The local backbone configuration corresponds to Qwen3-Reranker-0.6B with 28 transformer layers and a 1,024-dimensional hidden representation. The selected layer positions are approximately one-quarter, one-half, and the final layer: layers 7, 14, and 28.

Those representations are concatenated, giving a 3,072-dimensional fused input. An attention-based fusion block with eight heads, residual behavior, normalization, and dropout combines information across the selected representations. Earlier layers can retain more local/token information; later layers can provide more contextual relevance. That is the rationale for multi-layer fusion, not proof that every selected layer is optimal for every code task.

The token compression head applies normalization, a 256-dimensional bottleneck, nonlinear activation, dropout, and a two-output classification layer. Its two emissions correspond to prune/keep evidence. The architecture contains CRF transition parameters and decoding/loss methods from the upstream implementation.

### 18.3 A crucial inference distinction

The paper describes CRF/Viterbi decoding in its inference account. The deployed TokenWise wrapper does not call the Viterbi decoder for its live line selection. Instead, the model forward path returns the difference between keep and prune emissions, and the wrapper applies a sigmoid:

```text
token_keep_probability = sigmoid(keep_emission - prune_emission)
```

For two local class emissions, this is equivalent to the keep-class probability from a two-class softmax. The wrapper then aggregates these probabilities to lines and applies a threshold. Consequently, the existence of a CRF class in the code is not evidence that live TokenWise inference uses the full sequence-decoding procedure described in the paper.

This detail is important if an examiner asks whether your implementation exactly matches SWE-Pruner. The answer is that it uses a SWE-Pruner-derived checkpoint and architecture but has a specific deployed scoring and thresholding procedure that must be evaluated on its own.

### 18.4 Document relevance head

The document-scoring path uses the final hidden representation and a yes/no relevance construction. It obtains a log-probability for the positive answer and converts that log-probability back into a probability. The resulting score lies in the expected probability range and can participate in candidate ranking.

The score estimates relevance according to the learned model. It is not an uncertainty certificate, an exact probability of task success, or proof that all necessary behavior is present. Lexical and structural evidence remain useful alongside it.

### 18.5 Local loading and hardware behavior

The runtime has local backbone configuration and tokenizer files and uses offline loading flags after setup. The model can be constructed from local configuration and loaded from the verified checkpoint without downloading another copy of the foundational backbone during inference initialization.

The model runs in evaluation mode without gradient computation. The CPU path uses float32 behavior and avoids incompatible mixed-dtype/autocast assumptions. A configured checkout runtime can select supported CUDA use, but the normal managed installation installs CPU-oriented dependencies and does not require a GPU.

The underlying backbone configuration contains a larger theoretical positional limit, but the current pruning wrapper uses an 8,192-token working window. Claim the deployed limit, not the maximum number found in a lower-level model configuration file.

## 19. Chunking and Line Selection

### 19.1 Why code must be chunked

A repository file can be longer than the pruner's model window. The available space for code is less than 8,192 tokens because instructions, query, prefix, and suffix also consume tokens. The wrapper calculates available code space and splits long code into overlapping chunks.

The default overlap is 50 tokens. Overlap reduces abrupt boundary effects by giving a token near a split some surrounding information in more than one chunk. It adds duplicated computation, so it is a quality/efficiency tradeoff rather than free coverage.

The wrapper maps chunk results back to absolute code-token positions and averages scores where overlapping chunks cover the same source positions. It uses the maximum document-relevance score across chunks. A maximum chunk score can make a file appear relevant because one region is useful; it does not imply uniform relevance throughout the file.

If the query and formatting leave fewer than approximately 100 tokens of code space, the wrapper returns the original code with an error indication rather than pretending meaningful pruning occurred. Extremely large task text is therefore not an unlimited supported input. Client paths differ in how they surface pruning failures and how repository packing falls back.

### 19.2 Mapping tokens back to source lines

The tokenizer supplies character offsets. The wrapper maps each code token to source lines it overlaps, handling both LF and CRLF line endings. A token spanning a line boundary contributes to the relevant overlapping lines. Line score is the mean of the contributing token probabilities:

```text
line_score(line) = sum(keep_probability of overlapping tokens)
                   / number_of_overlapping_tokens
keep_line        = line_score >= threshold
```

This makes a line's relevance less sensitive to the number of token fragments it contains than a raw probability sum would be. It still relies on tokenizer alignment and model scores; it is not a parser enforcing syntactic closure.

### 19.3 Thresholds and retained structure

The wrapper's basic threshold default is 0.5, while the extension/automatic workspace default is 0.45. Direct selected-source pruning uses the requested threshold. Focused repository pruning uses `max(0.10, requested - 0.15)` for the anchor and `min(0.85, requested + 0.15)` for related neural candidates. At requested 0.45, these are 0.30 and 0.60. Automatic pre-pruning already uses these adjusted thresholds; packing reuses the result rather than rescoring it. Per-file `effective_threshold` records the applied value, and non-neural methods have no applied neural threshold.

A lower threshold generally keeps more lines; a higher threshold generally removes more. It does not follow that the higher threshold is better. Excessive pruning may remove an exception, configuration dependency, or test assertion that determines the correct answer.

The optional first-fragment preservation keeps the first line, not every import statement. Small removed spans may be retained when an elision marker would be longer. One-line gaps may be bridged, and blank-line output is simplified. These heuristics improve readability but do not guarantee complete class/function blocks or import closure.

### 19.4 Output semantics

Removed spans can be represented using markers such as `(filtered N lines)`. This informs the agent that content is missing. Such markers can make the excerpt invalid Python, and a retained function body without its full surrounding structure is not a compilable source replacement.

The output is a reading artifact. The original repository remains the program. This is why the agent rule instructs the model to read originals before editing and why the UI offers copying context rather than applying the excerpt to a file.

### 19.5 Token accounting

`origin_token_cnt` and `left_token_cnt` count original and retained code text with the local tokenizer. A reported model-input count includes task/instruction overhead for a constructed input, but it is not a full measurement of total multi-chunk computation. Overlap and repeated chunk inference can increase actual processing beyond that simple count.

For performance and sustainability research, measure the complete pruning operation separately. A text token count is useful, but it does not substitute for wall-clock timing or local power measurement.

## 20. Tiered Context and the Hard Token Budget

### 20.1 Why use tiers

Not all related files need equally detailed treatment. The anchor is often central evidence; a directly related dependency or test may need an implementation excerpt; a farther helper may only need its interface. Tiers express this allocation of detail.

| Tier | Intended role | Context treatment |
| --- | --- | --- |
| 1 | Primary/active anchor | Light pruning when the context builder performs a fresh pass |
| 2 | Direct or strongly relevant evidence | More aggressive pruning, or reuse of an already pruned result |
| 3 | Transitive or lower-priority context | Interface representation rather than full implementation |

The automatic path generally gives non-prepruned candidates interfaces to keep neural work bounded, with eligible short task-matched bodies retained instead. Overview excerpts follow their own deterministic route. File metadata names `neural_lines`, `short_source_retained`, `signature_interface`, `overview_excerpt`, or a fallback; an explicit scope filter adds a `scope_filter+` prefix and omitted-unit names. These methods must not all be described as neural compression. Relation labels remain heuristics: a path containing 'test' can be labeled 'related test' without proving its assertions cover the precise task.

### 20.2 Budgeting the complete artifact

The final budget counts the preamble, file headers, source paths, relation/tier labels, code fences, separators, truncation markers, and content. A budget that counts only retained code would underestimate the actual supplied artifact.

Focused packing orders the primary file first when appropriate, then other candidates by ranking. Overview packing uses a fair-share content allowance for remaining components. Both compute remaining space, account for block overhead, truncate content using the tokenizer, and verify the combined text. The packer tightens when tokenizer decoding or boundary merging creates a discrepancy, and uses longer fences when source contains Markdown code fences.

Supported repository budgets range from 256 to 32,768 tokens. The automatic adapter independently checks that the returned packed count is a valid integer and does not exceed the configured budget. Invalid or oversized context is not injected just because the backend returned HTTP success.

### 20.3 What the budget guarantees and does not guarantee

The budget guarantees bounded packed size under the local tokenizer when a valid result is accepted. It does not guarantee representation of every dependency, retention of every test, optimal allocation among files, or complete semantic correctness.

A long first file in focused mode can consume most of the available space. Later high-value tests may then be omitted. Overview mode already reserves a fair share across components, and candidate selection already reserves some configuration positions, but neither is a globally optimal evidence-allocation solver. Symbol/block selection or stronger test/contract reservations remain possible improvements.

### 20.4 Understanding source versus packed tokens

The workspace result's original-token baseline sums source content for files actually included in the packed result. It is not the token count of the entire repository, and it is not a measured baseline of all file reads Antigravity would otherwise perform.

The result separates four measurements:

| Field | Meaning |
| --- | --- |
| `original_tokens` | Original source for included files, before query-specific scope filtering; not the whole repository |
| `retained_source_tokens` | Sum of per-file retained excerpt counts, separate from outer packet formatting |
| `pruned_tokens` | Complete final packet, including preamble, headers, fences, markers, and separators |
| `raw_context_tokens` | Same included files, relations, tiers, and formatting with original unpruned source; matched repository-carbon baseline |

`context_overhead_tokens` reports the nonnegative difference between packed and summed excerpt counts. Tokenizer boundary effects mean separately counted components are not a universal exact additive decomposition. Retained excerpt text itself can include elision/truncation markers.

Source reduction compares original and retained excerpt counts: `(original - retained) / original * 100` for a nonzero original. It does not subtract the complete formatted packet from bare source. For the tiny 17-token source/117-token packet example, unchanged retained source means 0% source reduction and 100 tokens of reported overhead, not -588.24% reduction. A genuine retained-source increase is labeled as an increase; signed energy/carbon changes are not clamped into fictitious savings. Whole-repository savings require the separately constructed all-Python comparison, and actual agent savings require complete downstream trajectories.

## 21. Antigravity Integration and Activity Evidence

### 21.1 Native hook adapter

The hook adapter accepts a JSON payload from a supported `PreInvocation` mechanism. It reads recent transcript records from the end rather than loading an unbounded transcript into memory. Its reverse reader has a bounded inspection region and tolerates a partially written trailing record.

It looks for explicit user inputs or supported standard user-role records, skipping model/tool records and messages beginning with TokenWise's injected-context marker. This avoids interpreting the system's own injected text as a new user request and repeatedly retrieving for it.

The hook verifies workspace association where provided, compiles a per-turn identity using conversation/record information and the query, and uses per-conversation state to avoid duplicate injection for intermediate steps in the same user turn. The same words in a later explicit user turn are still a new turn; simple string equality is not the whole identity rule.

Once context is prepared, the adapter returns an `injectSteps` structure with a `userMessage`. That keeps the context at user-message priority rather than elevating repository text into a system instruction. Errors produce diagnostics and an empty hook response so the agent can continue normal discovery.

### 21.2 Workspace-rule command fallback

When native hook injection is unavailable, the always-on rule tells the agent to invoke the local context launcher before investigating the repository. On Windows, task text is encoded as UTF-8/Base64 for the launcher rather than inserted as arbitrary executable shell syntax. A portable launcher provides the corresponding alternative on supported local setups.

The command returns the bounded context as tool output. This is the path that makes 'one ordinary prompt, no manual selection' usable on builds with rules and command tools. It remains agent-driven: the agent must follow the rule and receive permission to run the local command.

This fallback is not guaranteed interception before the very first model call. At least part of agent orchestration may already have occurred before it decides to call the tool. The project should not claim access to an undocumented universal extension API that rewrites every Antigravity prompt.

### 21.3 Activity records

Retrieval records include a new event ID, UTC timestamp, transport, status, task text, verification label, and, on success, result and elapsed time. States include `retrieving`, `ready`, and `error`. Native-hook conversation records are stored separately to manage duplicate invocation.

Writes use temporary files and replacement so the extension does not normally read a half-written JSON object. The extension validates activity before showing it and watches `.tokenwise/latest.json` for new results.

The UI distinguishes fresh activity, previous activity, and explicit verification. An old ready result loaded when the folder opens is labeled as a last result rather than a new prompt event. Verification output is labeled as a test and is not used to create the illusion that Antigravity consumed the context.

### 21.4 A four-level evidence ladder

1. **Configured:** the rule, launchers, settings, and link exist.
2. **Prepared:** a new ready event contains bounded context for the current task.
3. **Delivered:** the current agent invocation has the actual context in hook injection or tool output.
4. **Used effectively:** the agent's answer or change is grounded in the evidence and succeeds according to a task evaluation.

Only the last level establishes downstream usefulness for that task. Status-bar success establishes preparation, not all four levels. For the defense, show both the current retrieval output and the agent's grounded explanation.

### 21.5 Bounded same-chat references, not permanent memory

Version 0.6.8 uses bounded, extractive user memory. Candidate state is capped at 32 turns of 2000 characters each. For native bootstrap, the existing reverse reader scans at most a 16 MiB transcript tail and collects at most 64 earlier qualifying turns before candidate normalization. Recovery accepts records with the matching conversation ID, or unlabeled records only when the transcript path is verifiably scoped to that conversation. Otherwise it uses only that chat's existing state. Workspace and conversation identity remain separate; no other chat's latest activity is used. Assistant/model replies, tool output and injected snippets are excluded.

The selector uses the repository's term normalizer, topic overlap and expanded follow-up cues. It segments topic changes and selects the related segment, prioritizing the topic anchor and recognized active requirements before filling remaining slots with recent related turns. Up to eight selected messages share a 4000-character hint allowance. Recognized newer edit/test/format/exclusion constraints remove superseded clauses; the latest request takes precedence. The summary is an extract from selected user text, not a model-generated semantic summary. Explicit unrelated subjects do not inherit old requirements. Lexical English heuristics can miss synonyms, arbitrary coreference and unrecognized conflicts, so this is not perfect general chat understanding.

Updated fallback rules pass the latest query and earlier user strings separately: Windows uses encoded JSON history and the portable launcher accepts a JSON stdin envelope. The trace says `agent_supplied_user_turns`; TokenWise cannot independently verify those messages against private IDE chat storage. It must not label this native capture. Missing referents still require clarification. Existing workspaces must run Enable Automatic Context again after installing the matching backend so owned rules/launchers receive the new transport; customized integration files are preserved.

The input trace exposes selected candidate positions/text/reasons, considered and omitted counts, truncation, extractive summary/requirements and exact outgoing-reference status. Candidate positions are indices within the bounded window, not absolute transcript message numbers. The outgoing JSON-quoted reference is separate from repository facts and states that the latest request wins. It uses at most 384 tokenizer tokens and one quarter of the packet budget, with evidence space reserved; it may be compact or omitted even when a hint informed retrieval. Its overhead counts toward the complete packed context and matched carbon baseline. Set `conversation_memory` to false in `.agents/tokenwise.json` to disable automatic history transport/use. State and exports can contain user requirements and need privacy review before sharing.

### 21.6 Controlled input demonstrations and provenance

**TokenWise: Demonstrate Pruning Inputs** exposes three controlled modes. Repository mode submits the task and folder without editor hints. Selected mode captures either the whole Python file or the exact highlighted excerpt, including unsaved editor text and its starting source line, and sends that text directly to `/prune`. Conversation mode asks the demonstrator to supply an earlier user task, then submits a follow-up for repository retrieval. It labels an accepted hint as `supplied_replay`; it does not secretly capture live Antigravity chat.

Input traces disclose current/effective task, scope, requested threshold, history provenance, and indexed-file count where applicable. Native history can be labeled `native_scoped_user_turns`; ordinary API hints use `supplied_user_context`; an absent hint is `none`. Per-file method/applied-threshold data explain the actual repository treatment, while direct results show neural line scores and decision masks. JSON exports let an examiner inspect these facts rather than infer the pruning process from an answer alone.

The separate **Compare Context Strategies** command constructs literal context baselines, not three different neural input modes. It compares all indexed Python, unpruned saved selection, and automatic retrieval with selection/history hints removed. All-Python exports exclude fixed ignored directories and non-Python documents. They reject more than 200 indexed files or 2 MiB of source, invalid/unsaved selections, and changed snapshots rather than silently truncating a baseline. A direct selected-source neural run and an unpruned selected comparison packet are therefore different experiments.

## 22. Background Indexing, Caches, and Freshness

### 22.1 Why background work matters

Parsing unchanged files less often is useful, but walking a large repository on every request still costs time. The project therefore prepares a configured workspace index in the background and applies saved-file deltas. Different tasks reuse source-derived search information instead of rebuilding it for every query.

Only configured, trusted local workspaces with the expected profile backend link participate. Merely opening an unrelated folder does not install dependencies, download weights, or start indexing it automatically. `enabled: false` stops automatic retrieval/indexing, and `auto_start_backend: false` prevents an offline backend from being started just for warm-up.

### 22.2 Events, batching, and ordering

The extension watches Python file creation, change, and deletion and handles rename/deletion events for affected paths or subtrees. It groups bursts using a 150 ms debounce and sends at most 512 relative paths per update.

Each pending path has a revision. If a path changes again while a request is in flight, acknowledgment of the earlier revision does not delete the newer pending change. This prevents a common asynchronous-event bug: losing a second edit because the first request finished later.

A per-window watcher ID and increasing sequence number tell the backend which session owns an update and whether it is current. Stop/release sequencing prevents a late update from reactivating a closed watcher. Multiple windows can hold independent leases; closing one does not necessarily mean no other live watcher remains.

### 22.3 Leases and reconciliation

Heartbeats occur every 30 seconds and renew a 90-second watcher lease. The backend checks reconciliation every 15 seconds and performs a due full content-verified scan at approximately 120-second intervals. Reconciliation catches missed events, including some changes that preserve file size and timestamps.

If no watcher is alive, retrieval returns to a conservative scan-before-request behavior. If a watcher expired and becomes active again, the backend rechecks before trusting delta-only maintenance. This trades some fallback latency for correctness rather than assuming that a previously indexed repository never changes.

### 22.4 Cache layers

| Cache | Reuses | Invalidation or identity |
| --- | --- | --- |
| Repository index | Source snapshots, ASTs, per-file metadata | Changed accepted content, additions, removals, and reconciliation |
| Prepared retrieval data | Lexical counts/postings, graph, symbol locations, interfaces | Repository fingerprint |
| Per-file token counts | Counting for original/interface/pruned text | Tokenizer object identity and exact text |
| Complete context | Final packed result and selection | Exact task/goal, history hint, fingerprints, root, active file, threshold, budget, candidate limit, guidance version and enabled state |

Index/prepared caches retain a bounded number of repositories, currently eight. Complete contexts retain at most 16 exact requests. Per-file token-count caches retain up to eight tokenizer/text pairs. These limits prevent unbounded growth; eviction means rebuild, not permission to return stale data.

### 22.5 Similar prompts are not identical requests

Search data is query-independent and can safely serve 'explain lockout' and 'explain account locking tests' for the same unchanged snapshot. A completed context is task-dependent and must not be reused merely because the phrases look similar.

The complete-context key includes exact query, structured goal, accepted history hint, and settings that change the output. Overviews also include the bounded project-document fingerprint. Editing source/documentation, changing the hint, or changing the budget invalidates the applicable completed result. This is why cache speed does not require approximate semantic answer reuse.

### 22.6 Concurrency and snapshots

Per-repository locks and copy-on-write snapshots keep in-flight readers associated with a coherent accepted version while updates construct newer state. Unchanged metadata can be retained without forcing every file to be parsed again. A scan in one repository should not block all unrelated repository-index activity through a single global repository lock.

Neural inference still has a global serialization lock. Background repository work and model work therefore have different concurrency constraints. Eliminating repository walks does not eliminate neural execution time or queueing behind another pruning request.

### 22.7 Remaining freshness limits

The index represents saved files on disk, not arbitrary unsaved editor buffers. A saved edit becomes visible after its update completes. A missed event can remain unseen until reconciliation. Caches are in memory and do not persist a warm index across process restart.

The implementation reuses per-file features but can rebuild prepared graph/search structures for a changed repository fingerprint; it is not a fully incremental dynamic-graph engine updating only one graph edge at a time. This is an important distinction when explaining the speed design precisely.

## 23. Research Foundation: SEAL

### 23.1 The paper's purpose

The [SEAL paper](docs/papers/SEAL-Carbon-Estimation.pdf), *SEALing the Gap: A Reference Framework for LLM Inference Carbon Estimation via Multi-Benchmark Driven Embodiment*, addresses inference carbon estimation when direct instrumentation of every model/hardware combination is unavailable. It combines benchmark-driven features and learned energy predictors, then converts energy to emissions using carbon intensity.

Its reference-framework idea is valuable because closed model services often do not expose their exact inference hardware or energy. However, an estimator under such uncertainty remains conditional on features and assumptions. It cannot create missing physical knowledge simply by using a sophisticated regressor.

### 23.2 Separate phases and benchmark fusion

The paper treats prefill and decode separately and combines performance benchmark information with model-quality benchmark information. Input/output lengths, latency, model size, GPU category, and reasoning-quality indicators help describe a workload and model configuration.

The paper reports LLM-Perf and Open LLM benchmark sources, a merge by normalized model identity and precision, and comparison of multiple regression families. It finds XGBoost useful for its interpolation experiments and Ridge useful for its extrapolation experiments. TokenWise adopts that phase-separated, benchmark-derived approach with its own pipeline and artifacts. [SEAL, pages 2-4](docs/papers/SEAL-Carbon-Estimation.pdf).

### 23.3 Published data and metrics are not local metrics

SEAL reports benchmark counts of 3,173 and 2,045 rows with 3,042 merged rows, and uses a 10-fold evaluation configuration. TokenWise's saved preparation record and 5-fold training configuration differ. A faithful defense must identify this as a SEAL-derived implementation, not a numerically exact reproduction.

The paper's Table I reports, for its settings, XGBoost decode MAPE of 6.98% and prefill MAPE of 5.36%, with Ridge errors of 31.58% and 24.85% respectively. Those values cannot be substituted for the project's saved carbon-model errors. [SEAL, page 4, Table I](docs/papers/SEAL-Carbon-Estimation.pdf).

The paper's external examples use 38 input and 64 output tokens with published energy references for Llama-2 7B and 13B, and report an average relative error of 17.76%. TokenWise also has a two-reference validation artifact but produces different predictions and an average error of approximately 17.46%. Matching the general experimental idea is not the same as reproducing every prediction. [SEAL, page 4, Table II](docs/papers/SEAL-Carbon-Estimation.pdf).

### 23.4 What quality features mean

MMLU-Pro and BBH scores describe aspects of model benchmark performance. They are predictive covariates in the regression approach, not energy units and not a direct measurement of how much reasoning a particular prompt requires.

A statistical correlation can help prediction without establishing causality. Saying 'the model has this benchmark score, therefore this prompt physically consumes this exact energy' would be an unjustified interpretation. The project uses these values as features and reports their provenance or fallback assumptions where available.

## 24. Carbon Data Preparation and Model Training

### 24.1 Training pipeline versus runtime pipeline

The `carbon-engine` directory implements benchmark acquisition, normalization, merging, feature extraction, training, and reference validation. The serving backend contains the runtime artifact loader and prediction API. Normal users consume the saved models; researchers or developers can rerun preparation/training to produce new artifacts.

Training scripts existing in a repository demonstrate an implemented procedure. Saved reports demonstrate a recorded outcome of that procedure. They do not mean that every model was retrained while this guide was written. This guide reports the artifacts in the studied snapshot.

### 24.2 Data sources and normalization

The pipeline can use benchmark CSV data already present locally or obtain benchmark data from the configured external source. It normalizes varying column names and values so model identity, precision, hardware, token lengths, timing, energy, and benchmark scores can be compared.

Model identifiers are normalized by operations such as lowercasing and handling organization prefixes. Precision representations are made more consistent before merging. An inner join on normalized model name and precision yields rows where both performance and quality evidence are available.

This is not a lossless universal benchmark database. Inconsistent naming can drop a match; overly broad normalization can merge distinct variants. GPU normalization and precision interpretation need careful tests as new benchmark formats appear.

### 24.3 The saved local preparation record

The project's saved data-verification and merge records describe 1,612 Open LLM rows, 34,128 raw performance rows across 48 CSV files, 12,822 normalized performance rows, 3,407 joined rows, and 101 rows remaining after the recorded deduplication. The recorded missing-data drop count is zero for that run.

The field named `deduped_rows` is the remaining-row count, not a statement that only 101 rows were removed. That small final dataset is significant when interpreting generalization and error metrics.

The deduplication key includes model, precision, input/output token counts, and GPU, but not every possible runtime framework or quantization detail. Meaningfully different operating configurations can therefore be collapsed. Improving provenance and retaining those distinctions is important scientific future work.

### 24.4 Feature vector

The runtime and training artifact schema explicitly contains eight ordered features:

| Feature | Interpretation | Expected form |
| --- | --- | --- |
| `n_input_tokens` | Prompt/input length in the modeled workload | Positive token count |
| `n_output_tokens` | Generated/expected output length | Positive token count |
| `model_size_b` | Model-size feature | Billions of parameters or an explicit assumption |
| `latency_per_input_token_ms` | Input-processing timing feature | Milliseconds per input token |
| `latency_per_output_token_ms` | Output-generation timing feature | Milliseconds per output token |
| `gpu_encoded` | Saved category encoding for supported GPU | Integer category from artifact encoder |
| `mmlu_pro_score` | Normalized model benchmark score | Value on a 0-1 scale |
| `bbh_score` | Normalized model benchmark score | Value on a 0-1 scale |

Feature order is part of the model contract. Rearranging columns without retraining or updating the schema can produce meaningless predictions even though the vector has the right length.

The saved hardware encoder maps A100 80 GB, A10G, and T4 to explicit numeric categories. Unsupported categories should be rejected rather than silently assigned an invented code. Encoding is categorical identification, not a claim that category numbers have physical spacing.

### 24.5 Units and target construction

The preparation logic converts timing assumed to be seconds into per-token milliseconds and energy assumed to be kWh into joules:

```text
latency_per_token_ms = 1000 * latency_seconds / token_count
energy_joules       = 3,600,000 * energy_kwh
```

Unit assumptions must be checked against the actual benchmark schema. A column already in milliseconds or joules must not receive the same conversion again. Structured schema handling improves consistency, but it does not remove the need for source-specific unit validation.

Where measured phase energy is absent, the pipeline can synthesize a target using GPU design power and reported latency:

```text
proxy_energy_joules = GPU_TDP_watts * latency_seconds
```

This is a major qualification. TDP is not a live measurement of power utilization, and the duration may have its own benchmark meaning. The training corpus cannot be described as entirely measured physical energy ground truth. The exact measured-versus-proxy proportion needs a dedicated provenance audit; it is not inferred here.

### 24.6 Training models and routing interval

The project trains four artifacts: XGBoost prefill, XGBoost decode, Ridge prefill, and Ridge decode. XGBoost uses 100 trees, maximum depth 3, learning rate 0.3, squared-error objective, and a fixed seed. Ridge uses alpha 1 and the local feature setup without a standard-scaler pipeline.

The local model-size interpolation interval is 7B-111B inclusive. XGBoost handles requests routed inside that interval; Ridge handles requests outside it. The paper's described interval and local routing bounds should not be treated as identical by default.

XGBoost can learn nonlinear feature interactions but tree ensembles generally have limited extrapolation behavior. Ridge is a regularized linear model and can extend a trend beyond observed values, but linear extension can also be wrong. Choosing the appropriate family is a modeling decision, not a guarantee of reliable predictions for unseen architectures.

### 24.7 Cross-validation and artifact saving

The training script uses five-fold shuffled cross-validation with a fixed random seed. It computes held-out predictions and records MAPE, MAE, RMSE, and R-squared, then fits final models on the applicable local partition.

Random row folds may place very similar configurations of the same model in both training and validation. That can make metrics optimistic for generalization to a genuinely new model family. Grouped evaluation by model/family and independent hardware measurements would provide stronger evidence.

XGBoost models are saved as JSON; Ridge models are serialized with joblib/pickle. The runtime also loads a feature schema, hardware encoder, routing bounds, and model registry. Pickle-based artifacts must remain trusted bundled assets because loading arbitrary pickle files can execute code.

## 25. Runtime Energy and Carbon Calculations

### 25.1 Resolving model and hardware assumptions

A carbon request identifies the target model and workload. Explicit feature overrides take precedence when provided; otherwise, the runtime uses the saved model registry and defined fallbacks. The result can expose feature-source information so a user knows whether values came from a known benchmark configuration or assumptions.

The default scenario is a benchmark-backed Llama-3 8B target inside the interpolation interval. It is not a detector for Gemini's exact model size, hardware, batching, or datacenter location. Values for closed models stored as registry fallbacks must be described as implementation assumptions, not externally verified secret model specifications.

### 25.2 Reference-workload normalization

The serving estimator uses a reference workload of 256 input tokens and 128 output tokens. It resolves model, hardware, latency, and benchmark-quality features and predicts reference phase energies using that normalized workload. It then scales phase energy to the request's input/output lengths:

```text
E_prefill = max(0, E_prefill_reference) * actual_input_tokens / 256
E_decode  = max(0, E_decode_reference)  * actual_output_tokens / 128
E_total   = E_prefill + E_decode
```

This gives a consistent before/after comparison and avoids using the changing request token count twice in a regression and a separate scaling factor. It also makes the runtime's linear scaling assumption explicit. The underlying regressors are multifeature models, but request-length scaling at this serving boundary is linear by phase.

Real transformer prefill, KV-cache growth, batching, prompt caching, and decode cost can have more complex behavior. The implementation is a reference-normalized indicator, not a full hardware simulator.

### 25.3 Converting energy to carbon

One kilowatt-hour equals 3.6 million joules. Carbon intensity is expressed in grams of CO2 per kilowatt-hour. The runtime computes:

```text
energy_kwh = E_total_joules / 3,600,000
CO2_grams  = energy_kwh * carbon_intensity_g_per_kwh
```

The default intensity of 475 gCO2/kWh is an assumed configurable scenario value. It is not a live regional-grid lookup. Carbon intensity can vary by place and time; a carefully sourced value makes the estimate more meaningful but does not eliminate uncertainty in the energy model.

The output uses an operational electricity-to-CO2 conversion. Without additional factors and data, it is not a complete lifecycle CO2-equivalent inventory including equipment manufacture, training, network infrastructure, or all greenhouse gases.

### 25.4 Fair before/after comparison

The extension keeps expected output, model, hardware, latency, quality features, and carbon intensity unchanged across a comparison. Direct pruning compares backend-native original and retained excerpt counts with a `source-only` baseline. Repository and fresh automatic results compare `raw_context_tokens` with the complete final packet using a `formatted-context` baseline: the same included files and formatting without pruning. The strategy-comparison view estimates each of its three actual complete packets. These denominators answer different questions and are labeled rather than silently mixed.

If expected output is unchanged, the modeled decode term is unchanged. A 75% input-token reduction therefore need not produce a 75% total energy or carbon reduction. The unchanged decode component remains part of both totals.

Carbon requests for the compared inputs can run concurrently. Fresh automatic estimates use the actual loopback backend URL recorded with the activity, have a capped estimate timeout, and update the result asynchronously. Event identity/current-result checks prevent a stale estimate from overwriting a newer result. Disabled, pending, ready, and unavailable states distinguish intentional configuration, work in progress, success, and failure. Old backend responses without a matched baseline require an update/new prompt rather than a fabricated count.

If estimation fails, usable context remains available with the specific setting/backend error. Optional zero model-size/latency overrides mean registry features, not invalid API values; a valid benchmark score of zero is preserved. Negative/nonfinite overrides and nonpositive expected-output/intensity settings fail clearly. Tiny CO2 values retain sufficient display precision. Before-minus-after differences retain their sign, so an increase is shown as an increase. No untrained hand-written fallback is labeled as a trained prediction.

### 25.5 Tokenizer differences

Direct single-file carbon now uses the backend's `origin_token_cnt` and `left_token_cnt`, the same provenance as its pruning result. Repository and strategy comparisons also use backend/local-tokenizer counts. Direct clients validate counts and do not replace empty/invalid counts with a frontend estimate to manufacture a positive baseline. If no retained source exists, source-only carbon is reported unavailable while the context result remains inspectable.

These counts still do not automatically equal the tokenizer or billing count of the user's chosen Antigravity model. Distinguish local source-excerpt counts, complete local context packets, and complete downstream prompts/conversations. Comparisons are reproducible under the local tokenizer without pretending to measure hidden provider accounting.

### 25.6 What the estimate excludes

The current estimate does not meter local neural-pruning energy, indexing, package/model downloads, training, embodied hardware emissions, network transfer, datacenter overhead, or the entire agent conversation. It also does not predict how pruning changes future output length or the number of agent rounds.

Consequently, estimated avoided cloud-input energy is not yet net environmental ROI. A complete evaluation would compare avoided agent energy against the added TokenWise workload over a defined boundary. Keeping the backend warm may help latency, but an always-running process also has an energy cost that this estimate does not include.

## 26. Worked Numerical Examples

All numbers in this section are explicitly illustrative calculations, not measurements of a real TokenWise request or predictions produced by the saved model. Their purpose is to explain the mechanics.

### 26.1 Lexical scoring example

Suppose there are ten indexed files and the term 'lockout' appears in the body of two files. Its weight is:

```text
weight = ln(1 + 10 / (1 + 2))
       = ln(4.3333)
       = approximately 1.4663
```

For one candidate, suppose capped content frequency is 4, path frequency is 1, and symbol frequency is 1. Its evidence for that term is `4 + 5 + 3 = 12`, contributing approximately `17.596` to the lexical score. Other query terms add their own contributions.

This example explains why a useful filename or symbol can outweigh repetitive prose. It does not mean every file's actual score is on a universal 0-1 scale; normalization for hybrid use happens separately.

### 26.2 Token-to-line example

Suppose a line has three overlapping token probabilities: 0.9, 0.8, and 0.1. Its mean is 0.6. At threshold 0.45, it is retained. Another line with probabilities 0.1, 0.2, and 0.3 has mean 0.2 and is removed unless a readability/preservation heuristic changes the final presentation.

If the retained line depends on a removed earlier condition, the excerpt can become semantically incomplete. The numeric threshold alone does not know that every enclosing block must be retained. This explains why source labels and permission to inspect originals matter.

### 26.3 Chunk-capacity example

Suppose instruction/query overhead occupies 400 tokens of the 8,192-token working window. Approximately 7,792 tokens remain for code in that constructed chunk. With a 50-token overlap, a simple successive chunk stride would be approximately 7,742 code tokens, subject to the actual wrapper's input construction.

A 15,000-token file requires multiple chunk evaluations. Overlapping tokens are processed more than once, and the result must map back to the original positions. A single reported source token count is therefore not the total neural computation performed.

### 26.4 Packing example

Suppose the budget is 4,096 tokens, and the preamble uses 100. File A's formatted excerpt occupies 2,600; file B occupies 900. Around 496 tokens remain before accounting for every separator and boundary effect. A third file requiring 700 cannot simply be appended.

The packer can truncate it to available space or stop if its block overhead cannot fit. The output remains bounded. If the third file contains the decisive test, this demonstrates a coverage issue that a better allocation policy could address; budget compliance and evidence completeness are different properties.

### 26.5 Energy and carbon example

Assume a fictional model has reference prefill energy of 256 J for 256 input tokens and reference decode energy of 128 J for 128 output tokens. Assume input is reduced from 4,096 to 1,024 tokens, expected output remains 256, and carbon intensity is 475 gCO2/kWh.

```text
Before prefill = 256 * 4096 / 256 = 4096 J
After prefill  = 256 * 1024 / 256 = 1024 J
Decode both   = 128 * 256 / 128   = 256 J

Before total  = 4096 + 256 = 4352 J
After total   = 1024 + 256 = 1280 J
Energy saved  = 4352 - 1280 = 3072 J

Before CO2    = 4352 / 3,600,000 * 475 = 0.574222 g
After CO2     = 1280 / 3,600,000 * 475 = 0.168889 g
CO2 difference                         = 0.405333 g

Input reduction = (4096 - 1024) / 4096 = 75%
Total modeled energy reduction = 3072 / 4352 = approximately 70.59%
```

The total percentage is smaller because decode is unchanged. These invented reference energies are chosen for easy arithmetic and must not appear in a results slide as measurements from the trained estimator.

### 26.6 Net-impact boundary example

Suppose an independent measurement later finds that local pruning consumes some additional energy. That energy must be compared with the modeled or measured avoided agent energy using a consistent carbon boundary and relevant electricity intensities.

The current project does not have that physical net-impact measurement. The correct interpretation of its sustainability view is 'estimated request-level inference difference under these assumptions,' not 'proven net carbon savings for the entire workflow.'

## 27. The Demonstration Repository

### 27.1 Why a separate test application exists

The current packaged teaching application is `demonstration/tokenwise_demo`. Open that folder itself in Antigravity; opening the whole TokenWise checkout changes the repository being evaluated. The application contains eleven Python files, twenty standard-library tests, and no required third-party application dependencies. The parent `demonstration/run_checks.py` is an additional runner, not a second project.

Four earlier teaching repositories were consolidated into this one application. The legacy `Test_project` remains a development fixture with different semantics and must not supply the expected numbers for the current teacher presentation. Historical results for those earlier fixtures retain their original scope.

| Current module | Role and reason it is useful for evaluation |
| --- | --- |
| `app.py` | Deterministic integration example linking the components |
| `security/models.py` | `Account`, `Session`, and the teaching-only digest helper; exact-class pruning input |
| `security/settings.py` | Lockout threshold/duration and session duration; cross-file configuration evidence |
| `security/auth_service.py` | Account lockout and timed reset |
| `workflows.py` | Session, invoice, and shipping functions in one mixed-topic input |
| `reports.py` | Activity counts and CSV export, independent from authentication internals |
| `tests/test_auth.py` | Five authentication boundary tests |
| `tests/test_workflows.py` | Ten session/invoice/shipping tests |
| `tests/test_models.py` | Two default/digest tests |
| `tests/test_reports.py` | Three count/CSV tests |

The eleventh Python file is `security/__init__.py`. This is a teaching fixture, not production authentication or commerce software. Its multiple domains provide both positive evidence and distractors while keeping the source small enough for controlled all-code comparison.

### 27.2 Authentication state and login flow

`Account` is a dataclass with `username`, `digest`, `failed_attempts` defaulting to zero, and `locked_until` defaulting to zero. `AuthService.authenticate(account, password, now)` accepts an explicit integer clock, so tests are deterministic and do not sleep or depend on the computer's current time. It returns a Boolean rather than creating a token.

When `now < locked_until`, authentication returns false immediately, including for the correct password. At or after an existing deadline, it clears the deadline and failure count before checking the supplied password. The exact lockout deadline is therefore an allowed reset boundary, not one more blocked second.

The configuration is `LOCKOUT_THRESHOLD = 3` and `LOCKOUT_SECONDS = 60`. A wrong password increments failures; reaching the threshold sets `locked_until = now + 60`. A valid password before lockout clears failures and returns true. A wrong password at an expired deadline starts a fresh count rather than carrying the old three failures forward.

For three wrong attempts at time 100, the deadline is 160. Correct authentication at 159 is false; at 160 it is true and resets account state. This is deliberately different from the legacy fixture's permanent inactive-account behavior. There is no user database, network login endpoint, background unlock scheduler, or production rate-limiting policy in this example.

### 27.3 Session validation and revocation

`Session` is a dataclass with `username`, `expires_at`, and `revoked = False`. `issue_session(username, now)` rejects an empty username and constructs a session ending at `now + SESSION_SECONDS`, where the constant is 300. It is a separate workflow, not an implicit side effect of `authenticate`.

`session_is_valid(session, now)` requires both `not session.revoked` and `now < session.expires_at`. A session issued at 100 is valid at 399 but invalid at 400. `revoke_session` marks it revoked, causing validation to fail even before expiration. These helpers do not implement JWTs, signed tokens, persistent session storage, or automatic account-lockout invalidation.

For an exact `Session` class question, select all of `security/models.py` or highlight that class and run direct pruning. The selected file also contains `Account` and a digest helper, making task-conditioned line selection visible. Inspect the decorator/import as well as fields: omitting `@dataclass` may leave useful field evidence while losing initialization/equality semantics. A high reduction percentage does not prove a complete class explanation.

### 27.4 Authentication tests

| Test | What it demonstrates |
| --- | --- |
| `test_lockout_threshold` | Two failures leave the account unlocked; the third creates the configured deadline. |
| `test_correct_password_rejected_during_lockout` | Correct credentials are rejected before the deadline without erasing the existing failure count. |
| `test_expiry_boundary` | Authentication is rejected one unit before the deadline and accepted at the deadline, clearing failures/deadline. |
| `test_success_resets_failures_before_lockout` | A successful login interrupts an earlier failure count. |
| `test_wrong_password_after_expiry_starts_a_new_count` | Wrong credentials after expiry begin a fresh count of one. |

These assertions define the lockout grading facts before an agent answer is evaluated. They establish fixture behavior, not security guarantees for a distributed real login service. The service, constants, and tests together provide stronger evidence than any one selected file alone.

### 27.5 Invoice and shipping behavior

`invoice_total(subtotal_cents, tax_percent, shipping_cents)` accepts nonnegative subtotal/shipping and an integer tax percentage from 0 through 100. It calculates rounded tax as `(subtotal_cents * tax_percent + 50) // 100`, then adds subtotal and shipping. The example `10000, 15, 500` produces 12000 cents; `10, 15, 0` produces 12 cents, showing half-up rounding. A zero invoice is valid. Invalid amounts raise `ValueError`.

`shipping_days(zone, express=False)` maps local/regional/international to 2/4/10 days, rejects an unknown zone, and returns one day for a valid express shipment. Invoice and shipping share `workflows.py` with sessions. This lets the same input reveal different relevance masks when the task changes, and provides an explicit distractor for 'session expiry, not invoice pricing.'

The current example does not contact a payment gateway or implement timeout/retry processing. Those behaviors belong to the legacy application and should not be described as features of `tokenwise_demo`.

### 27.6 Workflow, model, and reporting tests

The ten workflow tests cover session expiry, revocation, required username, invoice calculation, invalid values, rounding, tax/shipping bounds, zero amounts, shipping modes, and unknown zones. The two model tests check account/session defaults and a deterministic, password-sensitive digest.

`activity_summary` counts actions and returns keys in sorted order; `export_activity` writes an `actor,action` CSV header and the corresponding values. Three report tests cover populated counts/CSV, empty input, and sorted multi-action counts. Reports are independent of account state and password checking, so they provide another unrelated component for broad versus focused retrieval.

Run `python demonstration/run_checks.py` from the checkout, or `python -m unittest discover -s tests -v` and `python app.py` inside the application folder. The deterministic entry point shows deadline 160, rejected/accepted authentication around that deadline, session deadline 400 and its boundary/revocation, invoice total 12000, regional shipping four days, and one invoice/one login activity.

The test total is 5 authentication + 10 workflows + 2 models + 3 reports = 20. Ask lockout, session, invoice, reporting, and overview questions using the same application. Task awareness means the selected evidence responds to those different needs; it does not mean every request must remove a fixed percentage.

### 27.7 Demo security qualification

The teaching digest is an unsalted SHA-256 demonstration, explicitly marked as not production password storage. Integer clocks, in-memory dataclasses, simple invoice arithmetic, and small CSV reports make boundary behavior easy to test; they do not establish a production security/commerce design. There is no real payment integration or secret-management system.

These simplifications belong to the application fixture, not to TokenWise's retrieval architecture. Explain their teaching purpose and distinguish fixture tests from model/agent effectiveness. The current [teacher walkthrough](demonstation.md) provides exact prompts, selection coordinates, history controls, comparison steps, exports, expected facts, and troubleshooting; **TokenWise: Open Demonstration Guide** opens its packaged copy.

## 28. Privacy, Security, and Trust

### 28.1 Local processing boundary

Repository indexing and neural pruning are local in the normal managed workflow. The automatic adapter sends requests to a loopback backend rather than a hosted TokenWise service. Runtime model loading uses local assets after installation.

This does not mean the complete agent workflow is offline. Supplying selected repository excerpts to Antigravity's agent can send them to whatever model service Antigravity uses. TokenWise reduces the material supplied; it does not independently guarantee the privacy policy of that downstream service.

Installation also contacts dependency and model hosts. Optional goal-model configuration can add another endpoint. State the exact processing boundary instead of saying that no project text can ever leave the machine.

### 28.2 Workspace trust and executable integration

The extension does not support unrestricted activation/setup in untrusted workspaces. A workspace rule and launcher affect agent behavior and execute local tooling, so consent and trusted-local checks matter. The backend installation path is application/profile-managed rather than blindly taken from arbitrary repository settings.

Generated rules ask the agent to respect command permissions. The project does not need unrestricted terminal execution or administrative access as a normal installation requirement. A user may still need to approve the specific local command under the IDE's policy.

### 28.3 Source as data, not instructions

The context preamble and agent rule identify repository excerpts as reference material. Instructions inside comments, strings, or source files should not gain authority over the agent simply because retrieval included them. Hook context uses user-message priority, not a fabricated system-message role.

These measures reduce confusion but are not a formal prompt-injection defense. A model can still be influenced by malicious source text. Robust source trust labeling, adversarial tests, and stronger agent-side boundaries are possible future work.

### 28.4 Local HTTP security boundary

The managed server binds to `127.0.0.1`, and background synchronization checks that its endpoint is local. The automatic Python client disables machine proxy forwarding for loopback requests. Model-path and service-identity checks avoid adopting an unrelated server as the correct runtime.

The backend is not designed as an authenticated multi-user internet service. Its repository APIs accept local workspace paths, and it does not implement a comprehensive authorization allowlist for every process on the machine. A loopback bind reduces exposure but does not make local callers impossible. Do not expose the service to a public interface without a separate security design.

### 28.5 Secrets and exclusions

There is no implemented general secret scanner or complete `.gitignore`-aware exclusion layer. Python configuration files and top-level assignments can contain values that enter retrieval or interface context. Fixed directory exclusions are not a guarantee that sensitive source is omitted.

A production-hardening roadmap should add configurable ignore rules, file-size policies, and secret-risk handling before making stronger privacy claims. Source-code minimization is beneficial, but relevance and sensitivity are different classification problems.

### 28.6 Webview and artifact security

The result panel escapes task and code text before putting it into HTML and handles known copy/export actions rather than executing supplied source as commands. Its current content-security policy denies default resource access but allows inline script/style behavior. It is not a nonce-based strict script policy; tightening that policy and adding security-focused UI tests would be useful improvements.

Runtime Ridge artifacts are serialized objects and must come from trusted packaged data. Neural weights use safetensors with pinned integrity verification. These formats and checks have different threat models; a safe weight format does not make an arbitrary pickle safe.

### 28.7 Local retention

Activity files store the task and returned excerpts. Conversation state and runtime logs also remain on disk. The generated ignore rule prevents accidental Git inclusion but does not encrypt the files or implement an automatic short retention policy.

Users should understand these local records. Cleanup removes recognized owned records, while customized/unrecognized data is preserved and reported. Future options could disable detailed activity retention or redact sensitive content from logs.

## 29. Failure Handling and Uninstall

### 29.1 Graceful retrieval failure

An unavailable backend should not make the coding agent unusable. The native adapter returns no injection on failure and writes a visible error event where possible. The command fallback returns a failed command status, and the rule tells the agent to continue ordinary repository discovery while acknowledging the failure.

This avoids a false-success state in which an old context is quietly substituted for a new request. It also makes TokenWise an enhancement to the workflow rather than a single point of failure for all coding assistance.

### 29.2 Typical failures and diagnosis

| Failure | What to inspect | Correct recovery principle |
| --- | --- | --- |
| Python prerequisite failure | Detected version, bitness, and configured executable | Install/select the required interpreter; do not destroy the application's existing Python environment. |
| Dependency download failure | Numbered setup stage and output log | Fix network/proxy/disk issue and retry with checkpoints/caches retained. |
| Model mismatch/corruption | Pinned size/hash check | Replace or redownload invalid bytes; never load them to claim setup completion. |
| Malformed workspace JSON | Named configuration file | Correct the JSON; setup preserves the original rather than overwriting it. |
| Port already occupied | Actual runtime registration and health | Use a free nearby port and keep unrelated processes running. |
| Model not loaded | Health readiness and backend log | Repair assets/runtime and restart the appropriate owned backend. |
| No current chat retrieval | Rule loading, command approval, event timestamp | Start a new chat and verify actual current tool output. |
| Missing watcher support | Index output and backend version | Update the backend; conservative retrieval can still continue. |
| Carbon artifacts unavailable | Carbon readiness and error output | Keep context result and report missing estimation rather than inventing values. |
| Invalid carbon settings | Named expected-output/intensity/override setting in the result error | Unset optional size/latency overrides or use zero for registry features; repair invalid values without discarding context. |
| Overview contains only initializers | Coverage warning, root documentation, and opened folder | Check whether the repository is a scaffold or the wrong folder; do not invent missing application behavior. |
| Comparison refuses an export | Saved selection, repository fingerprint, file/byte limits | Save and retry an unchanged bounded fixture; do not call a truncated packet an all-code baseline. |

Startup locks and per-conversation locks reduce duplicate work. Stale hook locks can be recovered according to age. An installer lock after a crash requires verifying that no setup is still running before removing only the owned stale lock. Lock recovery is not permission to delete another process's lock.

### 29.3 Ownership-aware removal

Cleanup is based on recorded ownership, not on deleting anything whose filename happens to contain 'tokenwise.' It tracks extension profiles, managed storage, configured repositories, installation registration, and generated-file hashes.

It removes recognized generated integration, context/conversation records, managed environments and caches, and TokenWise preferences. It merges hook removal without discarding unrelated handlers. It restores or carefully removes the generated ignore entry without treating all user edits as disposable.

Rules or launchers modified by a user are preserved and reported. Existing backend checkouts, Python itself, unrelated settings, application code, and unrecognized files are not supposed to be deleted. Safe cleanup can legitimately leave those files because preserving user data takes priority over the cosmetic claim that no matching word remains anywhere.

### 29.4 Process identity before termination

A PID can be reused by the operating system. Cleanup therefore must not terminate a process only because its number appears in a JSON record. It checks that a backend belongs to the managed installation/private interpreter and that an installer corresponds to the expected script/storage arguments.

If ownership cannot be verified, the process and associated storage can be retained with a warning. This is safer than stopping an unrelated Python process and then deleting files it may be using.

### 29.5 Uninstall worker

The extension declares an editor uninstall hook that runs without needing the VS Code API. Before extension files disappear, it copies the required cleanup code and JSONC parser into an isolated temporary worker directory, writes a cleanup plan, and starts a hidden detached Node process.

The worker can finish deleting a large managed environment even after the editor removes the original extension directory. On clean completion it removes its own temporary files. If cleanup encounters warnings or preserved content, it leaves a report for diagnosis rather than hiding the incomplete outcome.

Uninstall completion can depend on the editor finishing removal and restarting. It is not a synchronous universal guarantee that every byte is gone immediately after clicking the button. **Remove All Local Data** provides an explicit, inspectable cleanup path while the extension is installed.

## 30. Development, Packaging, and Distribution

### 30.1 Developer workflow

The developer works on TypeScript extension source and Python backend source. Compiling the extension does not reload an already-running Python backend. Pressing F5 launches an extension development host; it is a testing workflow, not the installation procedure friends should follow.

The [development guide](docs/DEVELOPMENT.md) contains source setup and test commands. From a prepared Windows checkout, the following backend test command uses the repository's virtual environment:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location).Path 'swe-pruner\swe-pruner\src'
.\.venv\Scripts\python.exe -m unittest discover -s swe-pruner/swe-pruner/tests -v
```

Run extension commands from `vscode-extension`:

```powershell
npm test
npm run prepare-backend
npm run compile
```

The first command compiles through the npm pretest hook and runs Node tests. Preparing the backend generates the allowlisted bundle. Source changes require the relevant component to be rebuilt/restarted; 'Start Backend' can reuse a healthy process and is not a universal hot-reload command.

### 30.2 Package construction

`npm run package` prepares backend assets, compiles extension code, creates a VSIX, and produces release assets. The backend bundle includes selected source files, tokenizer/configuration assets, runtime carbon artifacts, licenses/notices, the installer, and needed adapter/control scripts.

Large neural weights, development virtual environments, user `.tokenwise` activity, developer tests, and research PDFs are excluded from the normal extension runtime bundle. A manifest records each bundled file's expected path, size, and SHA-256 so installation can validate what it received.

The package also includes the single application's twenty teaching tests, its manifest/runner, the user and teacher guides, and the PNG at `resources/icon.png` registered in the extension manifest. Teaching fixture tests are packaged evidence, unlike the extension/backend developer unit suites. Demo preparation validates the case manifest, regenerates only its owned example resource directory, and rejects redirected paths so removed older project folders cannot leak into the installer. Runtime `.agents`, `.tokenwise`, caches, and saved demonstration results are excluded.

This separates a modest distributable extension from the much larger ML runtime download. The release is still more than a thin button wrapper: it contains the implementation required to install and run the local pipeline on another machine.

### 30.3 Public distribution

The 0.6.8 distribution is [TokenWise 0.6.8](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.8), dated October 9, 2026. Its assets are `tokenwise-vscode-0.6.8.vsix`, `TokenWise-0.6.8.zip`, and `SHA256SUMS.txt`. The ZIP includes the installer, one teaching project, `study.md`, `demonstation.md`, `demonstration2.md`, `validation.md`, usage/operational documentation, notices, and internal checksums. Normal users install the VSIX through **Extensions > ... > Install from VSIX...**, reload, set up/update the matching backend, and enable their trusted Python folder again to refresh owned integration. They do not need Node.js, a source clone, or F5.

The release publisher verifies an explicit file allowlist and hashes, checks that the annotated tag and remote `main` match the release commit, creates a draft, uploads three assets, and verifies GitHub sizes/digests before publication. The final 0.6.5 VSIX, ZIP, and checksums were also downloaded without authentication and checked against the local build. The installer was inspected for the icon, guide, one-project inventory, and backend integrity. These checks establish distribution integrity, not general agent quality. Earlier public assets/tags remain unchanged; a future update requires a new version. GitHub's automatically generated source archives are not the normal-user installer.

A GitHub Pages web application would not replace this extension. A static website cannot simply install an editor backend, inspect arbitrary local repositories, or integrate with Antigravity's workspace agent. A website could host documentation and demonstrations, but the usable product remains an extension plus local service.

The current release should be described as a Windows-tested beta distributed through GitHub Releases, not a completed Visual Studio Marketplace/Open VSX listing. Public registry publication, publisher credentials, and additional native platform testing are separate release gates.

### 30.4 Licensing and attribution

TokenWise's project license does not erase upstream licenses. Packaging must carry appropriate backend/model notices and credit the research sources. Read [third-party notices](docs/THIRD-PARTY-NOTICES.md) and the bundled backend/model documentation when preparing a release or academic report.

The contribution narrative is strongest when it identifies what was engineered and what was reused. Established libraries are not evidence against a from-requirements project build; falsely claiming their authorship would be.

## 31. Testing and Verification

### 31.1 Why multiple levels are needed

A mocked test can prove ordering, validation, and cleanup decisions without loading a large model. It cannot prove the real checkpoint loads or produces meaningful context. A real-model smoke test can prove runtime compatibility on a fixture, but it does not establish general downstream agent quality. A cloud-agent task evaluation answers still another question.

TokenWise therefore has several forms of evidence rather than treating one test command as proof of the entire research hypothesis.

### 31.2 Current unit-test results

The 0.6.8 source/release checks on October 9, 2026 report the following suites. These are functional checks, not downstream agent-quality measurements. The 0.6.7 record remains historical: 191 extension passes, 121 backend passes and one skip, and twenty application passes. The October 7 record for 0.6.6 reports 174 extension passes, 118 backend passes and one skip; 0.6.5 reports 167 extension passes, 105 backend passes and one skip. Each teaching application check passed twenty tests.

| Suite | Result | Meaning |
| --- | --- | --- |
| Extension Node tests | 193 passed, no failures | Setup/lifecycle, synchronization, carbon states/counts, bounded memory traces, automatic comparisons, CLI-usage imports, response guidance, bundled classroom guides, packaging, and icon contracts |
| Backend Python tests | 142 discovered: 141 passed, 1 skipped, no failures | Adapter, installer, index/cache, overview/focused retrieval, exclusions, conversation selection/identity/supersession, real-tokenizer budgets, response templates, and HTTP/comparison contracts |
| Current demo tests | 20 passed, no failures; deterministic app output passed | Lockout/session boundaries, invoice/shipping, model defaults, and activity reports |

The skipped backend test requires creating file symlinks, which this Windows account cannot do. This is a test-coverage qualification, not an unexplained silent pass. The run also emits dependency deprecation warnings; successful assertions do not imply that every library API is future-proof.

Some backend tests intentionally simulate an unavailable neural checkpoint or substitute controlled scoring behavior. Their success must not be described as independent real-model quality benchmarks. Tests exercise the contract they are designed to exercise. The current [demo verification record](demonstration/VERIFICATION.md) separately preserves historical integrations and explicitly states that a fresh real-weight/live-cloud rehearsal was not performed for the consolidated fixture during its release checks.

### 31.3 Important regression coverage

Adapter tests verify current user-prompt extraction, ignoring model/tool/injected messages, per-turn deduplication, verification labels, disabled or malformed configuration, backend failure, source discovery without exact symbol names, and rejection of invalid or oversized returned context.

Installer tests cover pinned/cache integrity, partial-download resume and unsupported-range behavior, corruption rejection, stage errors, environment repair, dependency checkpoint reuse, cancellation boundaries, and lock ownership.

Repository/cache tests cover changed content, additions, deletions, directory rename, preserved-timestamp changes, missed-event reconciliation, independent watcher sessions, expired leases, late updates after stop, cached lexical-score equivalence, signature reuse, changed imports/symbols, tokenizer identity, exact-query cache isolation, eviction, and avoiding warm repository walks.

Extension tests additionally exercise trust/remote restrictions, local Antigravity storage handling, settings/rule preservation, rollback, multiroot configuration, background event bursts, in-flight edit preservation, restart reconnection, process identity, JSONC settings cleanup, and a standalone worker surviving removal of the original extension directory.

Newer regression coverage includes overview role coverage and initializer-only warnings, README/package invalidation, tiny-source overhead accounting, matched carbon packets, late-estimate rejection, zero/invalid scenario overrides, same-chat bounds and new-chat isolation, explicit topic exclusions with protected helpers, selected-file/excerpt traces and line coordinates, unbiased comparison inputs and snapshot limits, regenerated single-project packaging, bundled guide access, and the manifest's square PNG icon. Passing these contracts does not demonstrate that every relevant fact survives real neural pruning.

### 31.4 Recorded integration verification

The repository's [development documentation](docs/DEVELOPMENT.md) records a separate native managed-install verifier. It creates an isolated environment, installs actual CPU dependencies, deliberately fails the model step, retries using checksum-verifiable local weights, verifies dependency-step reuse, loads the real neural model, and performs loopback HTTP retrieval/cache/edit checks.

This is stronger than a pure mocked installer test. It does not include downloading the complete 1.35 GB checkpoint over the internet during that verifier, and it does not call Antigravity's cloud model. Those boundaries should be stated when presenting it.

An isolated Windows uninstall verifier uses separate IDE/user-data locations and an owned harmless process to check the native removal path without uninstalling the user's real extension. Portable context verification uses temporary external repositories so the arbitrary-workspace path can be checked without writing real project activity.

### 31.5 What remains experimentally unproven

There is not yet a large TokenWise-specific controlled experiment showing coding success, hallucination reduction, or average total latency across many real repositories and Antigravity tasks. Nor is there a complete local-plus-cloud physical-energy measurement proving net emissions reduction.

A research evaluation should freeze tasks, repositories, model version, settings, and baselines; compare success and total token/time/cost outcomes; repeat runs; and report failures as well as improvements. Functional verification and research effectiveness complement one another but cannot substitute for one another.

## 32. Results and Scientific Interpretation

### 32.1 Retrieval-overhead benchmark

The synthetic benchmark creates 1,000 small generated Python files and runs 50 distinct queries. A recorded Windows run on October 5, 2026 measured:

| Operation | Recorded value |
| --- | ---: |
| Cold index/search preparation | 5,795.48 ms |
| Warm watched query median | 0.559 ms |
| Warm watched query p95 | 0.810 ms |
| One-file edit plus prepared-search refresh | 16.876 ms |
| AST reparses for that one-file edit | 1 |
| No-watcher verified-scan query median | 328.978 ms |
| No-watcher verified-scan query p95 | 374.629 ms |

These measurements concern index, lexical, and graph work on a synthetic fixture. They exclude model loading, neural pruning, HTTP overhead, and Antigravity's cloud response. The useful conclusion is that background maintenance greatly reduces repeated repository/search overhead in that setting. The invalid conclusion would be that the full agent answers in 0.559 ms.

The benchmark also asserts zero walks/parses for warm watched requests and exactly one reparse for a one-file edit. Those operation counts explain the architectural effect more directly than a timing number alone. See [benchmark script](scripts/benchmark_retrieval.py) and [development record](docs/DEVELOPMENT.md).

### 32.2 Real neural latency boundary

A previously recorded isolated native CPU verification had one real first neural retrieval taking approximately 24.19 seconds on a two-file fixture after service startup. This is a single environment/task observation, not a broad latency distribution, and it excludes Antigravity's cloud answer.

The contrast with the sub-millisecond cached-search benchmark is intentional: after repository work is optimized, neural inference can dominate. A smaller context budget alone does not necessarily reduce all upstream scoring work proportionally. Measure stages before deciding which optimization will help users most.

### 32.3 Local carbon cross-validation metrics

The following values come from the project's [saved cross-validation artifact](swe-pruner/swe-pruner/carbon_artifacts/cv_metrics.json), not from the SEAL paper:

| Artifact | MAPE | MAE (J) | RMSE (J) | R-squared |
| --- | ---: | ---: | ---: | ---: |
| XGBoost prefill/interpolation | 13.83% | 16.85 | 32.35 | 0.879 |
| XGBoost decode/interpolation | 22.41% | 409.60 | 1,008.76 | 0.246 |
| Ridge prefill/extrapolation | 22.08% | 2.78 | 4.25 | 0.993 |
| Ridge decode/extrapolation | 46.59% | 109.63 | 149.42 | 0.901 |

The interpolation decoder's R-squared of 0.246 indicates limited explained variation in that validation setting. The Ridge decoder's 46.59% MAPE indicates substantial average proportional error. These are reasons to label output approximate and improve training/data validation, not to hide the weaker models behind the strongest metric.

The models use different applicable partitions, so raw MAE values cannot be treated as a controlled head-to-head comparison on identical samples without further analysis. A high R-squared and a high MAPE can coexist because the metrics emphasize different aspects of error.

### 32.4 Understanding the metrics

```text
MAE  = mean(abs(prediction - actual))
RMSE = sqrt(mean((prediction - actual)^2))
MAPE = 100 * mean(abs(prediction - actual) / abs(actual))
R2   = 1 - sum((actual - prediction)^2) / sum((actual - mean(actual))^2)
```

MAE expresses average error in the target's units. RMSE gives larger mistakes extra weight. MAPE expresses proportional error and is sensitive to near-zero true values. R-squared compares squared errors with the variance around a mean baseline; it is not 'percent physically accurate' and is not a substitute for calibration or external validation.

### 32.5 External-reference results

The saved [validation report](swe-pruner/swe-pruner/carbon_artifacts/validation_report.json) contains:

| Reference | Published empirical value | Local predicted value | Relative error |
| --- | ---: | ---: | ---: |
| Llama-2 7B, 38 input/64 output tokens | 349.96 J | 365.72 J | 4.50% |
| Llama-2 13B, 38 input/64 output tokens | 602.27 J | 419.12 J | 30.41% |
| Average of the two errors | -- | -- | 17.46% |

The reference script supplies assumptions including phase-latency and quality features. This is a comparison with two published reference points, not an independent new hardware measurement campaign. The average masks the much larger 13B error. Both the per-sample errors and the small sample count should be visible in a defense.

### 32.6 A claim table for presentation slides

| Safe claim | Why it is supported | Claim to avoid |
| --- | --- | --- |
| Automatic local Python context retrieval works on demonstrated tasks. | Actual prompt/tool output and functional integration tests | It always retrieves every necessary file. |
| The supplied artifact is bounded by a local-tokenizer budget. | Packer and adapter checks plus budget tests | The agent's entire conversation or billing is bounded by that number. |
| Warm background indexing reduces repository/search overhead. | Synthetic operation/timing benchmark | Every full prompt is sub-millisecond or under 100 ms. |
| The estimator provides approximate before/after scenario values. | Trained artifacts, formula, and reports | It meters Gemini/Antigravity's actual carbon footprint. |
| I built an integrated, distributable developer system. | Extension, backend, retrieval, setup, lifecycle, packaging, and tests | I invented Qwen or trained the upstream neural checkpoint from scratch. |
| Published papers motivate the design. | Referenced methods and benchmark results | Their success/error values are TokenWise's own measurements. |

### 32.7 Comparative-study support and remaining work

The practical teacher-facing protocol is [validation.md](validation.md), with a
native Antigravity with/without workflow study, three source-grounded tasks and
predefined six-item answer rubrics. Its eighteen-run pilot and blank worksheet
are a plan, not completed cloud-agent measurements. A native baseline is distinct
from supplying all code as a hypothetical context-only baseline.

The current implementation supports a comparative study, but a completed comparative answer-quality dataset is not implied by the commands or tests. **Compare Context Strategies** exports all indexed Python, unpruned saved selection, and automatic TokenWise packets for one task/snapshot. **Demonstrate Pruning Inputs** separately exposes repository discovery, exact selected-source neural pruning, and a supplied-history replay. These two commands investigate different questions: what context is supplied, and what inputs influence its preparation.

An initial study can use six tasks in `tokenwise_demo`: lockout/tests, session expiry/revocation, the `Session` class, invoice calculation/tests, shipping/tests, and a whole-project overview. Keep task wording, source snapshot, agent model/settings, and carbon scenario fixed. Export the packets and define required facts from source/tests before examining answers. For the lockout task, those facts include three failures, sixty seconds, correct-password rejection before the deadline, acceptance/reset at the deadline, and a new count after an expired wrong-password attempt.

Use fresh isolated chats and one packet/question per condition. In a context-only experiment, disallow additional repository reads, browsing, terminals, and retrieval tools; reject or separately classify a run that uses them. A project-connected Antigravity agent can otherwise recover missing evidence, obscuring the effect of the packet. If tool access cannot be controlled, label the result a tool-assisted workflow comparison and count additional reads/rounds instead of claiming a context-only comparison.

Report complete packet tokens, source retention, required-fact coverage, incorrect/unsupported assertions, context preparation time, total response time, manual selection effort, and estimated scenario carbon. Record cold startup separately from warm operation; report total prompt/history/output tokens where observable. Three repetitions per task/strategy would produce 54 initial answer trials, with rotated strategy order and reported variability. This is a proposed pilot protocol, not a table of outcomes already obtained. One deliberately small teaching project cannot establish general performance across real repositories.

History belongs in a separate controlled experiment: compare the same recognized follow-up with and without the specified earlier user topic, then test an explicit topic switch and a fresh chat. Label supplied replay versus actual native/fallback behavior. Do not describe history as an interchangeable source baseline or persistent cross-chat memory. Carbon comparisons remain configured downstream predictions, not measured net savings including local pruning. Optional graph/neural/cache ablations would need their own explicit configurations and results; the current UI does not automatically run or grade those research ablations.

### 32.8 Automatic comparisons and reported Antigravity usage (0.6.7)

The October 9 source implementation adds two distinct measurement paths. Keeping
them distinct is essential: preparing a packet is observable locally, but it does
not reveal every request that Antigravity's IDE agent sends to a cloud model.

**Automatic prepared-packet comparison.** A developer enables
`tokenWise.autoCompareAutomaticContext` using **TokenWise: Configure Automatic
Comparison**. After a fresh, non-verification automatic result arrives, the
extension sends its exact prepared context, current task and workspace to
`POST /compare-prepared-workspace` on the recorded loopback backend. The backend
reconciles saved Python files, rejects a changed repository fingerprint, validates
the packet's tokenizer count, and constructs an unpruned all-indexed-Python
baseline. It does not run the neural pruner again or use a selected editor file.
Study exports are bounded to 200 Python files and 2 MiB of Python source; an
oversized baseline is rejected rather than misleadingly truncated.

The result contains both complete packets, source and packet token counts,
task-plus-packet counts, file lists, the Python snapshot fingerprint, notes and
the explicit measurement scope `prepared_packets`. The frontend shows absolute
token differences and percentage reductions or increases. A zero baseline has
no meaningful percentage; small repositories can legitimately expand because of
formatting and response guidance. Carbon estimates are calculated under the
same configured inference scenario and remain predictions. Overview packets can
include project documents that the Python-only baseline excludes, so the
comparison is not claimed to contain identical categories of evidence.

This analysis is asynchronous and opt-in. A failed comparison does not remove
the already prepared context, and event identity prevents an old result from
replacing a newer prompt's panel. The same configuration command provides
disable and retry actions. Export records preserve packets for inspection;
TokenWise does not inject the all-code baseline into the actual agent conversation.
The exported comparison is not persisted back into the adapter's `latest.json`;
that file continues to represent the adapter's original preparation event.

**Reported CLI-usage comparison.** Antigravity's
[official headless CLI](https://www.antigravity.google/docs/cli/headless/)
can produce JSON usage envelopes and stream-JSON completed tool events.
**TokenWise: Import Antigravity Usage Comparison** reads two user-selected logs
locally and creates a separately labeled `imported_antigravity_cli_usage` report.
It retains input, output, cache-read, thinking and total counters as reported;
it never adds per-step values to already cumulative terminal totals. Completed
tool transitions are deduplicated by step index. Answers, durations, reported
model identity and observed tool parameters are available for evaluation and
JSON export. Tool output bodies are not included in the imported tool summary.

Both runs must be successful, fresh single-turn conversations with usable
reported usage. Failed, zero-usage, resumed, mixed-conversation or oversized logs
are rejected. The importer also rejects using the same conversation twice or
different models when both model identities are reported. If a model identity
is missing, equality is explicitly unverified. Plain JSON envelopes lack tool
traces; stream logs show observed calls, not every file or instruction visible
to the model. Terminal commands may read many files, and system instructions,
rules, history or subagents can supply context outside the observed trace.

The without/with labels are assigned by the experimenter. The logs alone do not
verify identical task wording, settings, evidence, or TokenWise consumption.
Keep those controls explicit, use independent conversations, rotate condition
order, and inspect tool-assisted contamination. CLI telemetry cannot be relabeled
as telemetry from a prior IDE chat. The extension does not intercept private
IDE storage, automatically send paid A/B requests, or automatically grade answer
quality. A context-only all-code-versus-pruned experiment and an unrestricted
native-agent workflow comparison answer different questions. Neither is a
completed superiority study just because the measurement interface exists.

These features are included in 0.6.7, not functionality added to the older
published 0.6.6 installer. **Open Validation Guide** opens the bundled quick route
and evaluation protocol. The runnable procedure is in the
[teacher guide](demonstation.md#automatic-comparison-067).

## 33. Project Contributions and Design Justification

### 33.1 System contribution

The project's contribution is the complete developer-facing system joining repository discovery, goal-conditioned neural context selection, bounded packaging, editor/agent integration, and sustainability interpretation. These pieces have different constraints, and connecting them reliably is substantive software engineering.

The system does not merely invoke a model with selected text. It discovers evidence without manual selection, manages a shared runtime across arbitrary workspaces, retains and updates reusable search data, exposes sources and activity, handles failures, and packages a recoverable installation for other users.

### 33.2 Why combine inexpensive and learned retrieval

Running a transformer over every source file would be expensive. Pure string matching would be fast but miss task-conditioned relevance. AST/graph evidence supplies structure, lexical search supplies cheap task matching, and bounded neural scoring supplies a learned query-code signal.

This staged design controls compute and explains candidate origins. Its weakness is that early-stage misses cannot be recovered automatically by a later pruner. That tradeoff should be tested with retrieval recall and agent-task quality, not concealed by a high compression ratio.

### 33.3 Why signatures instead of summaries for distant dependencies

An AST-derived interface can preserve exact function names and argument structure without asking a generative model to invent an explanation. It is comparatively cheap and reusable across tasks. It also reduces dependence on another LLM call.

The cost is that behavior inside the omitted body can matter. A transitive helper's signature does not explain its validation, error handling, or side effects. The agent can inspect originals when it needs more detail.

### 33.4 Why an explicit final budget

Candidate count alone is not a size bound: six huge files can still overwhelm context. Line thresholds alone are not a size bound: many lines may all score above the threshold. An independent final token packer provides a clear operational guarantee even when upstream relevance scores retain a lot of material.

This separation is a strong engineering property. Retrieval decides what appears useful; pruning reduces content; packing enforces the actual output constraint. None of those responsibilities has to pretend it solves the others completely.

### 33.5 Why cache data before caching answers

Most prompts share the same repository structure but not the same goal. Caching term counts, interfaces, and graphs helps every new task while avoiding semantic answer reuse. Exact completed-context caching remains useful for repeated unchanged requests, but it is deliberately more restrictive.

The design also recognizes event ordering, watcher expiration, and conservative reconciliation. These make the speed improvement credible without accepting stale evidence as the price of faster responses.

### 33.6 Complexity intuition

Cold preparation reads/parses source across the accepted repository and constructs metadata. Its cost grows with source size and file count. Graph traversal is bounded to a small neighborhood and has ordinary graph-search cost over the visited nodes/edges. Cached lexical lookup uses prepared term information rather than rebuilding every file's term counts for each query.

A content delta reparses affected files, although prepared graph/search refresh can still involve wider metadata work. Neural cost grows with selected content, chunk count, and the model's attention/computation characteristics. Final token counting and packing also consume time, but a bounded candidate set keeps them manageable.

The overall response includes all stages plus agent time. Improving one asymptotic or measured component does not automatically dominate the total. This is why stage-specific profiling is more informative than saying the whole extension is 'fast' without a measurement boundary.

### 33.7 What makes it a strong project

TokenWise has a clear problem, a traceable research basis, a multi-component architecture, nontrivial algorithms, explicit runtime constraints, reproducible test tooling, and an actual distribution path. It is demonstrable through real repository questions and explainable through concrete data flows and formulas.

It is not necessary to call it the best extension in the world. A stronger claim is that it is a coherent, useful research-informed engineering project with visible limitations and a credible improvement plan. Being able to explain weak carbon metrics or an agent integration boundary often demonstrates more understanding than presenting only attractive numbers.

## 34. Limitations and Improvement Roadmap

### 34.1 Current limitations

| Area | Current boundary | Consequence |
| --- | --- | --- |
| Language | Python AST repository indexing | Do not claim general Java/JavaScript/TypeScript repository support. |
| Workspace | Trusted local folders | Remote/virtual first-run workflows are not supported. |
| Agent integration | Native adapter where supported; rule/command fallback otherwise | No universal guarantee of pre-first-model-call interception. |
| Source freshness | Saved disk files and asynchronous updates | Unsaved edits and missed events have visibility delays. |
| Static analysis | Approximate import/call graph and uneven async-definition metadata | Some relationships/symbols can be missed or misidentified. |
| Privacy filters | Fixed exclusions; no complete ignore/secret layer | Sensitive relevant source may be included. |
| Pruning | Learned line relevance, not syntax-preserving transformation | Excerpts can omit necessary structure or be invalid Python. |
| Packing | Focused ordered allocation; overview fair-share allocation | Important evidence may still be absent despite size compliance. |
| Conversation | Bounded recognized same-topic references or supplied replay | Not general conversational reasoning or permanent cross-chat memory. |
| Comparison tools | Packet/input export, not automatic answer grading | A comparative dataset and independent scoring still need to be collected. |
| Performance | Large local model and serialized inference | CPU inference can dominate latency despite fast search. |
| Carbon evidence | Small local prepared data, proxy targets, imperfect errors | Estimates have significant uncertainty. |
| Environmental boundary | Request-level inference scenario | Not measured net lifecycle savings. |
| Platform confidence | Windows native checks | Portable code is not proof of native macOS/Linux readiness. |
| Research evaluation | Functional evidence and selected measurements | Broad agent-success improvements remain to be measured. |

### 34.2 Highest-priority next work

First, create an independent real-task evaluation set. Use multiple Python repositories and tasks covering debugging, explanation, test discovery, refactoring, and feature work. Measure retrieval coverage, selected-evidence usefulness, task success, total input/output tokens, full latency, and failures against clear baselines.

Second, profile and improve the neural stage. Compare fewer scoring candidates, shorter candidate windows, selective symbol/block pruning, alternative smaller models, and supported accelerated runtimes. Any new fast mode must be labeled and evaluated; it should not silently pretend to be equivalent to the current neural pipeline.

Third, harden source selection and local API security. Add configurable ignore/size policies, secret-risk handling, explicit authorized-workspace enforcement where appropriate, and adversarial prompt/source tests. Tighten Webview script policy and increase async/import resolution coverage.

Fourth, strengthen sustainability validation. Preserve measured-versus-proxy provenance, audit units and deduplication, use grouped splits, add more independent hardware/reference samples, report uncertainty, and measure local pruning overhead. This would turn the dashboard from a rough indicator toward a better-validated decision aid.

Fifth, make distribution broader only after support is verified. Extend automated build checks, native platform smoke checks, artifact signing where appropriate, and public registry publication. The current draft-first release process already checks hashes, remote commit/tag identity, and uploaded digests. Do not claim native compatibility based only on the existence of a launcher file.

### 34.3 Future research questions

How much context can be removed before task success falls? Is file-level retrieval or symbol-level retrieval better for different task types? Does a minimum allocation for tests improve correctness? Can a goal hint remain useful across a long multi-turn task without carrying stale evidence? At what repository size does background-index memory become a problem? When does local pruning energy exceed avoided downstream energy?

These are measurable questions. They give the project a research agenda beyond cosmetic feature additions.

## 35. How to Explain the Build Methodology

Use the following logical construction sequence to explain how the project was made. This describes the implemented design process and component relationships, not an invented diary or claim that upstream research training was performed locally.

### 35.1 Requirements and boundaries

I started from the need to reduce unnecessary repository context while keeping relevant evidence available. I defined the target experience as an ordinary Antigravity prompt with automatic local Python discovery, no manual file selection, and a bounded output. I also separated prompt-level sustainability estimation from direct energy measurement.

This requirement set determines the architecture: an editor component, a local service, a retrieval pipeline, a neural pruner, a final packer, and a trained estimation layer. It also determines the support boundary and evaluation plan.

### 35.2 Research-informed component selection

I used SWE-Pruner as the neural-skimming foundation and SEAL as the energy-estimation reference approach. I selected established runtime tools such as Python AST parsing, PyTorch/Transformers, FastAPI, TypeScript editor APIs, XGBoost, and Ridge rather than claiming to implement every foundational library.

The engineering contribution is how these components satisfy the project's requirements, including adapting their runtime boundaries and exposing their assumptions honestly.

### 35.3 Repository intelligence and context construction

I implemented source discovery, metadata collection, lexical evidence, dependency expansion, ranking, interface extraction, and bounded packing around the task. I connected those stages so retrieval can operate without an active editor file and return source-labeled evidence.

I distinguish focused retrieval from deterministic repository overviews, preserve appropriate short evidence/configuration, interpret explicit topic contrasts without editing source, and expose applied methods/thresholds. I also implemented bounded same-chat user-reference handling and controlled input/packet exports so the pruning process can be inspected and compared.

I made context an inspectable artifact rather than a destructive source edit. That design allows both the developer and the agent to recognize omitted material and read original files when needed.

### 35.4 Sustainability pipeline

I implemented benchmark normalization and fusion, feature extraction, phase-specific regression training, artifact saving, runtime prediction, and before/after comparison. I separated original/pruned input effects from fixed expected output and made the energy-to-carbon units explicit. Direct pruning uses backend-native counts; repository results use matched formatted packets; fresh automatic results receive asynchronous estimates without delaying context delivery or replacing a newer result.

I report the saved local metrics rather than adopting the source paper's numbers. I recognize proxy target construction and reference assumptions as limitations to address with stronger validation.

### 35.5 Productization and correctness

I implemented central backend registration, recoverable managed installation, arbitrary-workspace integration, background saved-file synchronization, exact cache identities, diagnostics, and ownership-aware uninstall. I added tests for the failure and concurrency cases that could otherwise make a working demo unreliable for another user.

I packaged version 0.6.8 with inspectable bounded conversation memory, outgoing response guidance, automatic packet comparison, independent CLI-usage import, its icon, one runnable teaching application, twenty application tests, bundled study/validation/short demonstration guides, integrity metadata, and separately downloaded weights. Functional tests, isolated integration checks, performance benchmarks, and public-download checks verify different aspects of this complete system. The real-model/agent results recorded for older fixtures are not relabeled as current single-project experiments.

### 35.6 Evaluation and reflection

I evaluate implementation correctness separately from research effectiveness. Passing tests demonstrates important behavior; benchmark timing demonstrates a scoped performance effect; carbon metrics quantify a particular estimator's errors. Large-scale agent success and net physical emissions are still questions requiring independent experiments.

This is a rigorous build narrative: requirements, design, implementation, verification, deployment, and reflection. It does not need fictional personal dates, unsupported benchmark claims, or borrowed model authorship.

## 36. Defense Presentation and Live Demonstration

### 36.1 Suggested 12-15 minute presentation

| Time | Topic | What to communicate |
| --- | --- | --- |
| 0-2 minutes | Problem and objective | Too little context misses evidence; too much creates cost/noise. Define the one-prompt experience. |
| 2-4 minutes | Architecture | Show extension, local backend, repository intelligence, neural selection, hard budget, and separate carbon path. |
| 4-7 minutes | Technical method | Explain goals, lexical/graph retrieval, line scores, tiers, and exact cache invalidation. |
| 7-9 minutes | Sustainability | Explain phase regressors, reference normalization, units, assumptions, and local metrics. |
| 9-12 minutes | Live demonstration | Show two different tasks, current tool output, selected evidence, and no manual selection. |
| 12-15 minutes | Evidence and contribution | Present tests, scoped performance results, original integration work, limitations, and next evaluation steps. |

### 36.2 Pre-defense preparation

Install and verify the backend before the presentation. A live 1.35 GB download is not an effective demonstration. Open a trusted local Python repository and confirm the current TokenWise rule, backend readiness, and index output. Warm the backend to avoid confusing installation/model-start time with the task demonstration.

Keep the current model/artifact configuration and test output available. Prepare screenshots or a recording of the exact successful flow in case internet-dependent Antigravity access is unavailable. Clearly identify a recording as a recording rather than treating it as live evidence.

Do not change or delete integration merely to make the demo dramatic. The natural demonstration is that a prepared extension makes ordinary repository prompts easier.

### 36.3 Demonstration sequence

1. Open `demonstration/tokenwise_demo` itself, configure the trusted folder, and warm the matching backend. Show that no source file needs to be selected. Run its twenty tests and deterministic entry point before the presentation.
2. Start a new Antigravity chat and submit: **Explain account lockout after failed login attempts, the expiry boundary, and its related tests. Do not modify any files.**
3. Show the actual current retrieval command/output or supported hook-injected context, including `[TokenWise automatic context]`.
4. Inspect the new activity timestamp, current query, `status: "ready"`, and `verification: false`. Open the view to show actual files, input trace, methods/applied thresholds, retained source, overhead, packed tokens, and warnings.
5. Confirm three failures, sixty seconds, rejection before the deadline, acceptance at the deadline, and the relevant tests. Distinguish supplied evidence from extra agent investigation.
6. Submit: **Explain session expiry and revocation, not invoice pricing. Do not modify any files.** Show the changed evidence, excluded topic, 300-second duration, and expiry/revocation tests.
7. Run **Demonstrate Pruning Inputs** for no-anchor discovery, the whole `security/models.py` or an exact `Session` excerpt, and a supplied earlier-user replay. Inspect masks/scope/provenance; label the replay rather than treating it as a live chat result.
8. Show a same-chat follow-up, an explicit topic switch, and a new-chat control. Native hints and fallback resolved queries must be described according to their actual trace, not assumed to be identical.
9. Show **Compare Context Strategies** for the same lockout task/snapshot. Its all-Python/selected baselines are unpruned; the selected file does not anchor automatic retrieval. Export packets without claiming the command grades their answers.
10. Inspect the automatic or controlled result's carbon section. Explain its source-only/matched-packet baseline, model/output/intensity assumptions, and ready/pending/disabled/error state. These are predictions, not measured Antigravity emissions. Use [the complete walkthrough](demonstation.md) for exact rehearsal steps and exports.

### 36.4 Performance demonstration without misleading the audience

If demonstrating exact-repeat caching, announce that it is an exact unchanged request. If demonstrating background updates, use a disposable repository rather than altering important project files during the defense. Show the fingerprint change and subsequent source reflection after an acknowledged save.

Present the synthetic search benchmark as a stage measurement. Show total preparation time separately. An examiner should be able to tell which figure includes neural work and which does not.

### 36.5 Closing statement

> TokenWise demonstrates a complete path from task-aware context research to a usable developer extension. The system automatically discovers Python repository evidence, prunes selected content, enforces a hard context budget, and exposes the result in the agent workflow. Its trained sustainability layer provides approximate phase-level inference comparisons with explicit assumptions. I have validated key functional and lifecycle behavior and measured scoped retrieval improvements; my next research step is broader downstream task-quality and net-energy evaluation.

## 37. Detailed Defense Questions and Answers

Use these as reasoning practice, not a script to memorize word for word. A good answer names the mechanism, states the evidence, and acknowledges the boundary.

### 37.1 What problem does your project solve?

TokenWise addresses the difficulty of supplying useful repository context to a coding agent without manual selection or unnecessary source volume. A task can depend on several files, while the developer may not know where they are. The system uses the prompt to retrieve and organize relevant Python evidence, prunes selected content, and enforces a size limit. It also exposes approximate inference-impact comparisons in direct, repository, automatic, and controlled-comparison views. It does not claim to solve every agent-reasoning or repository-understanding problem.

### 37.2 Why is this not just another chatbot?

TokenWise is an evidence-preparation system, not the final answering model. Antigravity already provides the conversation and agent. My project supplies task-conditioned source context, manages local retrieval infrastructure, and exposes what was selected. The separation lets TokenWise improve the workflow without building a new chat service, authentication system, or cloud-model provider. Its technical work is indexing, retrieval, selection, budgeting, integration, and lifecycle management.

### 37.3 What is your original contribution if you use existing models?

The contribution is a complete integrated developer tool: automatic arbitrary-workspace retrieval, AST/lexical/graph discovery, bounded context construction, Antigravity adapters, trained carbon-estimation integration, background cache maintenance, recoverable installation, diagnostics, safe cleanup, tests, and release packaging. The neural checkpoint is properly attributed. Reusing a pretrained component does not remove the engineering contribution, but I do not claim to have invented or pretrained Qwen or to own the source papers' experiments.

### 37.4 Can you say you built the project from scratch?

I can explain the complete TokenWise system from its requirements through architecture, implementation, validation, and distribution. 'From scratch' in application engineering does not mean writing the operating system, editor, parser, or ML framework. For precision, I say I built the project using established libraries and integrated pretrained research components. I distinguish my system work from the original neural training and published research contributions.

### 37.5 What are the three main conceptual stages?

The proposal describes task-aware skimming, context pruning, and carbon tracking. In focused retrieval, these expand into goal compilation, source indexing, lexical/structural candidate discovery, applicable source filtering, bounded neural processing, and final packing. Overviews use deterministic representative excerpts. The extension estimates carbon separately, including asynchronous fresh automatic-result enrichment. A context can be delivered even if carbon is disabled or unavailable; it is not physical tracking of every agent request.

### 37.6 Why did you choose Python repository support first?

Python provides an established AST parser in the standard library and a clear environment for building the initial indexing and graph pipeline. It also matches the demo and relevant software-engineering research setting. A language-specific first version allows explicit behavior and tests. Supporting another language requires an appropriate parser, import resolver, symbol/interface handling, watcher rules, and evaluation; accepting arbitrary code text in a pruner is not equivalent to full repository support.

### 37.7 What happens if no file is open in the editor?

Automatic retrieval still works because the user task and workspace are sufficient inputs. The retriever discovers an anchor using lexical evidence, identifier evidence, and entry-point fallbacks. It then expands and ranks candidates. Manual repository context can use an active file as extra evidence, but the automatic Antigravity path intentionally removes that requirement. The anchor is a starting hypothesis, not guaranteed proof of the correct answer location.

### 37.8 Is this retrieval-augmented generation?

It is a retrieval-assisted agent workflow: source evidence is retrieved and supplied to the model, which then reasons or generates. However, the retrieval implementation is not the common persistent-embedding/vector-database pattern. It uses Python metadata, lexical counts, dependency relationships, and bounded query-code neural scoring. Saying that distinction explicitly is more informative than applying the label RAG without describing the actual algorithm.

### 37.9 Why not send the entire repository?

Repositories can be too large, and most files are irrelevant to one task. Sending everything increases processing and distracts from useful evidence. TokenWise seeks relevant files and content, then enforces a hard size limit. The risk is missing evidence, so the agent retains permission to read originals and perform additional investigation. The correct target is sufficient evidence per token, not maximal repository coverage or minimal tokens regardless of correctness.

### 37.10 Why not use only keyword search?

Keyword search is inexpensive and often useful for identifiers, but related files can use different vocabulary. A test imports a service even if its text does not match the user's phrase exactly. Graph expansion adds structural relationships, and the neural model evaluates selected query-code relevance. Combining signals makes discovery richer while bounding compute. The design still needs recall evaluation because an early-stage miss cannot be repaired by pruning a different file.

### 37.11 Is your lexical retriever BM25?

No. It is a custom TF/IDF-like score with content-frequency capping, path and symbol boosts, and an inverse-frequency-style query-term weight. It does not implement the full BM25 length-normalization and saturation formula. I name the method according to its source rather than calling every lexical ranking system BM25. A later BM25 comparison would be an experimental alternative, not the current implementation's identity.

### 37.12 What information does the AST provide?

It identifies syntactic definitions and relationships without running the application. TokenWise extracts imports, classes, functions, approximate call names, locations, and compact interfaces. That supports symbol lookup and graph retrieval even when application dependencies are unavailable. The AST does not resolve all dynamic behavior, and async definitions are not fully uniform in the current metadata visitor. It is a structural aid, not formal verification or complete runtime analysis.

### 37.13 How do you find tests if services do not import them?

The graph includes reverse relationships as well as outgoing dependencies. Tests often import the service, so incoming edges reveal relevant dependents. Lexical matches and test-path evidence can also help. A 'related test' label is still heuristic, and candidate/budget limits can exclude useful tests. I demonstrate the current lockout test and explain why broader test-discovery accuracy should be measured independently.

### 37.14 Why use two graph hops?

One hop gives direct neighbors; two hops can expose supporting configuration or helpers without expanding across the entire repository. It is a practical bound balancing evidence breadth and noise. Two is not a theoretical guarantee of complete task coverage. Some tasks require farther relationships, so the agent can read more and future evaluation can compare task-specific hop limits or symbol-level expansion.

### 37.15 How does the system handle broken Python syntax?

The file can remain lexically indexable from its source text, while AST definitions, graph evidence, and interface extraction may be unavailable. That is useful because a developer may ask for help precisely when a file is temporarily broken. It would be misleading to say every syntax-invalid file is completely excluded or completely understood. The available evidence changes, and the agent may need direct source inspection.

### 37.16 What is a goal hint?

A goal hint states what the agent needs from code for the task. It can include action, identifiers, observed errors, and desired evidence. The pruner uses it to distinguish task-relevant lines from unrelated implementation. TokenWise's default goal comes from deterministic compilation, with optional validated local-LLM generation. The hint is not a perfect plan or proof that all extracted identifiers exist; it is structured retrieval and scoring guidance.

### 37.17 Why is the optional local LLM disabled by default?

The default pipeline should work without requiring another model service, extra installation, or a failed network request. Deterministic goals are quick and explainable. A local model can improve natural-language structuring in some cases, but it adds compute, latency, configuration, and potential errors. The fallback preserves usability. I would evaluate its contribution through an ablation rather than assuming an extra model always makes retrieval better.

### 37.18 Does the system ask clarification questions automatically?

Not as a complete enforced workflow. The structured goal can mark `clarification_required`, and repository context can warn the agent to clarify; the fallback rule also requests clarification when a same-chat subject is missing. The backend can still produce context. These instructions and warnings are not a guaranteed interactive policy that resolves every ambiguity before retrieval.

### 37.19 How does the neural model choose lines?

It scores the task and code jointly. The live wrapper converts keep/prune emission differences into token keep probabilities, maps tokens to source lines using character offsets, averages probabilities per line, and applies a threshold. Readability/preservation heuristics affect the final excerpt. The output is selected source evidence, not generated replacement code. Necessary block structure can still be missing, so original files remain authoritative.

### 37.20 Do you use Viterbi decoding in live inference?

The architecture includes CRF-related methods and the paper describes Viterbi decoding, but the deployed wrapper's line selection uses sigmoid-transformed emission differences followed by line averaging and thresholds. It does not invoke the Viterbi decoder for that live path. This is an example of why I separate the paper's method from the exact served implementation rather than assuming class names prove a particular algorithm is active.

### 37.21 What is the purpose of multi-layer fusion?

It combines early, middle, and late transformer representations so the scoring head can use different levels of code information. The local configuration selects layers 7, 14, and 28 from a 28-layer backbone and combines their features through an attention-based fusion component. That is an architectural rationale; proving that those layers outperform alternatives for TokenWise requires an ablation, which the current project does not independently report.

### 37.22 What does the relevance probability mean?

It is the model's learned signal that a document or token is useful for the supplied goal. It is not calibrated evidence that the final agent answer will be correct with that probability. Nor does a highly relevant file necessarily contain all the required information. The system combines this signal with lexical/structural evidence and exposes source excerpts, leaving room for verification and further reading.

### 37.23 What happens with a file longer than the model window?

The wrapper reserves space for task/instructions and splits code into overlapping chunks within an 8,192-token working limit. It maps scores back to original token positions and averages overlap scores. Multiple chunks add model work, and the strongest chunk relevance contributes to document scoring. Extremely large query overhead can leave too little code space for useful pruning. Chunking is a bounded strategy, not unlimited-context inference.

### 37.24 What happens when you change the threshold?

A lower threshold usually retains more lines and a higher threshold removes more. Neither guarantees improved quality. Direct pruning uses the requested threshold; focused repository neural passes apply a lower anchor/higher related threshold and expose the actual values. Already pre-pruned candidates are reused. Short-source/interface/overview methods have no applied neural threshold. I choose thresholds using task-quality/token tradeoffs rather than only maximizing compression.

### 37.25 Is the pruned code valid Python?

Not necessarily. It is context for reading, with omitted spans and elision markers, not a syntactically closed source transformation. The paper also reports less-than-perfect AST correctness. The extension therefore offers copying context rather than replacing original files, and the agent rule says to inspect originals before edits. If executable-source preservation becomes a requirement, it needs a separate block/AST-aware design and tests.

### 37.26 How do you guarantee the context size?

The final packer counts the complete supplied artifact using the local tokenizer, including preamble, headers, fences, separators, and markers. It truncates content to remaining space and verifies the combined count. The automatic adapter rejects an invalid or oversized returned count. This guarantees the accepted bundle's configured local-tokenizer bound, not the agent's total conversation size or exact downstream billing-token count.

### 37.27 Does the budget guarantee all necessary files are included?

No. Size and coverage are different properties. Focused packing can spend much of the budget on a primary file. Overview fair-share packing and configuration candidate reservations improve specific allocation cases, but ranking and retrieval remain imperfect and tests can be absent. The output is initial evidence, not guaranteed completeness; stronger symbol/block or test/contract allocation needs evaluation.

### 37.28 How is 'original tokens' defined in repository results?

It sums original source tokens for included files, not the whole repository or every possible agent read. Source reduction uses retained excerpt counts, while packed tokens include outer formatting. `raw_context_tokens` is the matched unpruned packet for repository carbon. Literal all-indexed-Python comparison is a separately constructed baseline. These denominators are not interchangeable, and real agent savings require observing complete trajectories.

### 37.29 Can TokenWise enforce every Antigravity prompt before the model sees it?

Not universally. It has a native-hook adapter for supported builds and an always-on rule/command fallback. The fallback depends on the agent following the rule and having command permission, so it is not guaranteed interception before the first model call. The user experience can still be one ordinary prompt with automatic retrieval, but the integration guarantee must match the actual editor mechanism.

### 37.30 How do you prove the agent used the context?

I separate configuration, preparation, delivery, and effective use. A ready activity event proves preparation. Current hook injection or actual tool output proves delivery. A grounded explanation or successful change demonstrates use for the task. A status bar alone is not sufficient. In the demo I show the current task/timestamp, the context output, and an answer correctly explaining the retrieved service and test behavior.

### 37.31 Why do verification and old results have different labels?

A verifier can prepare real context without invoking Antigravity's cloud model. An old event can be loaded when a folder opens without any new prompt. Treating either as fresh agent use would create misleading evidence. The monitor labels verification as a test and historical ready data as a last result. This supports honest diagnostics and makes the demonstration's evidence easier to audit.

### 37.32 How do you avoid retrieving repeatedly for one user turn?

The native hook finds an explicit user record, derives a turn identity including conversation/record information and query, and stores per-conversation completed state. Intermediate steps for the same turn do not re-inject context. The injected marker is excluded when scanning user-like messages. A later user turn repeating the same words can still be new because identity is not based only on query-string equality.

### 37.33 Why is background indexing faster than reusing ASTs alone?

AST reuse avoids reparsing unchanged files, but repeated repository walking and metadata checks still cost time. A live configured watcher lets retrieval reuse the maintained snapshot without scanning everything per query. Saved-file deltas update affected content, and periodic reconciliation catches missed events. The benchmark demonstrates the repository/search overhead effect separately from neural inference, which can remain the dominant runtime cost.

### 37.34 How do you avoid stale context after an edit?

Accepted source content changes the repository fingerprint. Prepared retrieval data and exact context caches are tied to that fingerprint. Updates reparse changed files, retain unchanged metadata, and refresh dependent structures. Events carry ordering/revision information, and reconciliation handles missed events. There is still asynchronous visibility delay and no unsaved-buffer guarantee; I describe correctness relative to the accepted saved-file snapshot.

### 37.35 What if a second edit happens while the first update is running?

The pending-path map stores a revision for each edit. Completion of the first request removes only entries still at the revision it sent. A newer edit remains pending and is sent in another batch. Without this check, a late acknowledgment could erase newer work. The tests exercise this race, showing that performance engineering includes ordering correctness, not merely caching values.

### 37.36 What if file watcher events are missed or the editor closes?

The backend reconciles content approximately every two minutes and uses 30-second heartbeats with a 90-second watcher lease. When no watcher remains alive, retrieval reverts to content verification before each request. Stop sequences prevent late requests from reactivating closed sessions. This makes the fallback slower but safer. Missed events can remain unseen until reconciliation, so the system does not promise instantaneous global freshness.

### 37.37 Can similar prompts share a cached complete result?

Not merely because they are similar. They can share query-independent search metadata for the same repository snapshot. Complete context keys include exact query, goal, settings, workspace/active-file information, and fingerprint. A changed task or source must not receive an unrelated old bundle. This separation provides much of the speed benefit without approximate semantic-result reuse that could silently introduce incorrect evidence.

### 37.38 Are your performance numbers end-to-end?

The sub-millisecond warm number is a synthetic watched index/lexical/graph measurement, not neural or cloud-agent time. Cold preparation, delta maintenance, neural execution, HTTP, and final agent response have different costs. A recorded real CPU neural request took approximately 24.19 seconds on one fixture. I report boundaries explicitly and would measure full p50/p95 task latency over many real cases before claiming a broad user-facing speedup.

### 37.39 What does the SEAL-derived layer predict?

It predicts prefill and decode energy from benchmark-derived model/workload features, then converts energy to carbon using an assumed intensity. The runtime uses normalized reference phase predictions scaled to actual token lengths. It does not access a physical power meter in Antigravity's datacenter. It is a scenario-based estimator intended to make input-context effects inspectable, with local error metrics and uncertainty limitations.

### 37.40 Why use separate prefill and decode models?

The phases perform different work, and reducing input while holding expected output fixed should not be treated as an identical reduction in generated-output cost. Separate predictions expose that distinction. In the current serving normalization, input reduction changes the scaled prefill term while unchanged output keeps decode constant. The approach is still approximate because real cache, batching, and hardware behavior can couple the phases more intricately.

### 37.41 Why XGBoost inside the range and Ridge outside?

This follows the SEAL-inspired distinction between learning nonlinear patterns in represented data and extending trends beyond it. The local routing interval is 7B-111B. XGBoost learns tree-based interactions; Ridge provides a regularized linear model. Neither guarantees accurate unseen workloads, and model-size range alone does not describe all out-of-distribution features. The project therefore reports errors and needs grouped/external validation rather than relying on routing as proof.

### 37.42 Did you use exactly the SEAL dataset and evaluation?

No. The pipeline is SEAL-derived, but saved local row counts, normalization/deduplication, model routing bounds, cross-validation folds, and predictions differ. The local prepared record ends with 101 deduplicated rows and uses five folds, while the paper reports other counts and ten folds. I report local metrics from the artifacts and paper metrics only as attributed research results. That is more precise than calling it an exact reproduction.

### 37.43 Are all training energy targets measured?

No. When benchmark phase energy is unavailable, the preparation logic can use GPU TDP multiplied by latency as a proxy. TDP is design power, not measured utilization. Unit assumptions and measured-versus-proxy provenance need careful auditing. I therefore cannot describe the whole training corpus as meter-grade ground truth. Stronger future validation would preserve provenance and compare against independent physical measurements.

### 37.44 What are MMLU-Pro and BBH doing in an energy model?

They are model-quality benchmark covariates in the multi-benchmark approach. They can correlate with properties of model families and support statistical prediction. They are not energy measurements or per-prompt reasoning meters. Their inclusion does not prove a causal law that higher benchmark quality directly causes a particular energy value. I preserve their scale and provenance and evaluate whether they improve predictions rather than asserting causality.

### 37.45 How do you calculate carbon from joules?

I divide joules by 3,600,000 to obtain kilowatt-hours, then multiply by carbon intensity in grams CO2 per kilowatt-hour. For example, the same predicted energy yields different emissions under different assumed electricity intensities. The default value is a configured scenario, not a live grid measurement. This formula covers operational electricity conversion within the stated boundary, not total lifecycle or embodied emissions.

### 37.46 Does 50% fewer input tokens mean 50% less carbon?

Not necessarily. In the current comparison, decode energy remains when output length is held fixed, so total reduction is smaller than input/prefill reduction. Real hardware behavior may also be nonlinear and cached prompts can have different costs. The 75%-input example in this guide produces approximately 70.59% total modeled reduction with invented reference energies. It illustrates the equation and is not a trained-model measurement.

### 37.47 Is this Antigravity's actual carbon footprint?

No. The target model, hardware, latency, output length, and carbon intensity are configured or registry-derived assumptions. The default Llama-3 scenario is not automatic identification of Gemini's hidden infrastructure. Local pruning energy and the full conversation are excluded. The dashboard is an approximate comparison aid. Actual footprint claims require suitable physical/provider evidence and a defined measurement boundary.

### 37.48 What do the weak carbon metrics tell you?

They show that the estimator's accuracy is uneven. XGBoost decode R-squared is approximately 0.246, and Ridge decode MAPE is approximately 46.59%. Those values justify cautious labeling and better data/evaluation, not a claim of precise measurement. A two-reference average error also cannot prove broad generalization. I present the errors openly and prioritize provenance, grouped validation, more independent samples, and uncertainty reporting.

### 37.49 Can high R-squared and high MAPE both be true?

Yes. R-squared evaluates squared residuals relative to overall target variance; MAPE evaluates proportional errors for individual values and is sensitive to small denominators. A model can track large-scale variation while making large percentage errors on some samples. Metrics also come from different model partitions here. I interpret several metrics together rather than translating one high R-squared into a percentage-accuracy claim.

### 37.50 Is the project guaranteed to be environmentally beneficial?

Not yet at a measured net-system level. Avoided downstream context processing must be compared with local pruning/indexing, startup/download, and other relevant energy costs under a consistent boundary. The current estimator excludes those added costs. It supports an approximate prompt-level scenario difference, while net environmental ROI remains an experimental question. A useful sustainability project should make that distinction rather than assuming every compression operation is green.

### 37.51 How does your friend's repository find the backend?

The workspace contains a link to the IDE profile's central installation registration. That registration names the private Python executable, installed backend root, and runtime directory. Launchers resolve it rather than navigating up a fixed number of directories from the user's project. Thus multiple unrelated local repositories can share one managed installation. A moved repository or different IDE profile may need to be enabled again to create a valid local link.

### 37.52 Why not distribute a GitHub Pages application instead?

A static website cannot replace the editor APIs, private ML runtime, and local filesystem integration required here. GitHub Releases can distribute the VSIX and documentation. A website could explain the project or show recordings, but the usable experience remains an extension and local backend. Public marketplace distribution is another installation channel, not a transformation into a browser application.

### 37.53 What makes installation recoverable?

The setup exposes numbered stages, structured errors, recovery hints, dependency checkpoints tied to bundle identity, package caches, verified model caches, and valid partial-download resume. It checks completed steps before reuse and does not claim completion after a failed stage. The user can fix a cause and retry rather than deleting everything. This is particularly important because a private ML environment and large weights make complete restarts expensive.

### 37.54 Why not delete everything named TokenWise on uninstall?

Names alone do not prove ownership. A user may customize a generated rule, have an existing checkout, or create unrelated notes. Cleanup uses profile links, manifests, hashes, constrained paths, and verified process identity. It removes recognized owned data while preserving and reporting customized/unavailable items. A trustworthy uninstall prioritizes protecting user files over the cosmetic promise that every matching filename disappears immediately.

### 37.55 What prevents cleanup from killing the wrong process?

It does not rely only on a saved PID, because operating systems reuse process IDs. It checks the managed interpreter/installation and expected backend or installer command identity. Unverified processes are not stopped, and storage can be retained with warnings. Tests exercise reused or foreign PID cases. This is an important lifecycle safety property when a system owns a large local service.

### 37.56 Does local processing mean there are no security concerns?

No. Local workspace launchers execute code, loopback APIs need appropriate boundaries, source can contain secrets or prompt injections, and activity files retain excerpts. The downstream agent can transmit selected source to its provider. TokenWise uses trust checks, path containment, escaping, pinned assets, and ownership controls, but it lacks a complete secret/ignore layer and authenticated multi-user service design. Local reduces some exposure; it does not imply zero risk.

### 37.57 What is the account-lockout behavior in your demo?

The current `tokenwise_demo` accumulates three failures and sets a sixty-second deadline. A correct password is rejected before it; at the deadline, expired lockout state clears before password checking. Success clears failures, while a wrong password at expiry starts a fresh count. Five authentication tests establish the threshold and boundaries. This is not the legacy fixture's five-failure permanent disablement, and it does not automatically revoke existing sessions.

### 37.58 Why put sessions and invoice calculations in the same file?

`workflows.py` is a mixed-topic neural input. The same code can yield different useful lines for session expiry versus invoice pricing; explicit 'session expiry, not invoice pricing' also exercises repository source filtering. The tests define exact expiry, revocation, rounding, validation, and shipping facts. This lets me evaluate whether the retained evidence is sufficient, not only small. No real payment gateway/retry workflow exists in this current fixture.

### 37.59 What would a fair research comparison look like?

Use fixed tasks/snapshots and identical agent/model/settings. The current comparison command supplies all-indexed-Python, unpruned saved selection, and unbiased TokenWise packets; it does not grade answers. For a context-only trial, use isolated fresh chats without extra tools and score against predefined source/test facts. If tools are allowed, classify it as a workflow experiment and count extra reads/rounds. Repeat conditions, report token/time/quality/failure outcomes and variability, and test history separately. Graph/neural/cache ablations need explicit benchmark configurations. Carbon needs independent energy/local-overhead evidence for net claims; functional tests alone do not prove research superiority.

### 37.60 What is the most important next improvement?

The most important next step is proving downstream usefulness across independent real tasks while profiling the neural bottleneck. That evidence guides whether to improve candidate recall, context allocation, or model speed. In parallel, carbon provenance and validation need strengthening. Adding features without evaluation can make the tool larger without making it more useful. The current system gives a clear architecture and instrumentation from which to conduct those experiments.

### 37.61 Does conversation history really influence pruning?

For related explicit requests and recognized follow-ups, selected scoped user references enter the effective goal and lexical retrieval before evidence selection. Controlled replay supplies text explicitly; updated fallback passes separately labeled agent-supplied user references. Inspect selected messages, effective objective and outgoing memory status, not only the final answer. Neither route implies general cross-chat memory, complete transcript ingestion, perfect semantic matching or reuse of assistant claims as facts.

### 37.62 Why does an overview have a pruning result without neural line masks?

An overview asks for architecture/coverage, not relevance to one declaration. The deterministic route uses bounded root documents, role-diverse Python components, short bodies or interfaces, a repository map, and fair-share packing. Its label is `overview_excerpt`, not `neural_lines`. It still uses the local tokenizer and budget. This avoids mistaking a package initializer for a complete project and honestly reports missing coverage.

### 37.63 Why was a tiny repository previously showing negative reduction?

Subtracting a 117-token formatted packet from 17 tokens of bare source mixes denominators. Current source reduction compares original and retained excerpts, reporting zero when those seventeen source tokens remain and reporting formatting overhead separately. Carbon compares matched packets instead. A real retained-text or carbon increase is still possible and must be labeled as an increase, not hidden as a saving.

### 37.64 Why can excluded invoice-related code sometimes remain?

The scope filter removes independent excluded units, not every line containing a negative-topic word. A helper can be required by the requested behavior, and the implementation protects such dependencies with warnings. Shared logic, unresolved syntax, and bounded retrieval limit what can be isolated. Original files are untouched; the filter operates on query-specific reference views and is not a universal semantic or secret-removal guarantee.

### 37.65 Can I say I used prompt engineering to get better Antigravity answers?

I can say that I implemented task-aware outgoing prompting **designed to improve** grounded answer quality in 0.6.6. It has real templates, budget-aware insertion, versioned result traces, on/off settings, cache isolation, automatic transport, and regression tests. I should not yet say it has been proven to produce better answers or that I changed Antigravity's system prompt. Older installers remain unchanged. Section 13.7 explains the techniques and the controlled experiment required to establish a measured improvement.

## 38. Glossary

| Term | Meaning in this project |
| --- | --- |
| Agent | A model-driven coding system that can reason and use tools, here supplied by Antigravity |
| Anchor | Primary file used as an initial context/retrieval reference |
| AST | Parsed syntax structure used to derive Python metadata without running application code |
| BBH | Big-Bench Hard; a benchmark score used as a model-quality feature |
| Benchmark | A defined dataset or workload used for systematic evaluation |
| Cache fingerprint | Content-derived repository identity connecting reusable data to a snapshot |
| Candidate | File considered for ranking and eventual context inclusion |
| Carbon intensity | Grams of CO2 associated with one kWh of assumed electricity |
| Chunk | Bounded part of code processed within the neural model's working window |
| Context budget | Maximum packed text size under the specified tokenizer |
| Context strategy | All-indexed-Python, unpruned selected source, or automatic TokenWise packet in a controlled comparison |
| Context wall | The practical difficulty/cost of using very large or noisy model context |
| CRF | Conditional random field, a sequence-labeling component present in the upstream architecture |
| Decode | Output-token generation phase of LLM inference |
| Dependency graph | Approximate file relationships from imports and call-name evidence |
| Document score | Learned relevance signal for a task-code pair |
| Effective threshold | Actually applied per-file neural threshold, distinct from requested repository threshold |
| Excluded topic | Explicit contrasting subject omitted when independent of the requested evidence |
| Extrapolation | Prediction outside a specified represented feature range |
| Feature schema | Ordered definition of inputs expected by a trained regression model |
| Goal hint | Task-conditioned description guiding retrieval and pruning |
| GPU encoder | Mapping from supported hardware categories to saved numeric codes |
| Heartbeat | Periodic signal renewing a watcher lease |
| History replay | Earlier user context supplied by the demonstrator, not evidence of live chat capture |
| Input trace | Current/effective task, source scope, thresholds, and history provenance for an inspectable run |
| Interface view | AST-derived compact signatures and structural context with bodies omitted |
| Interpolation | Prediction inside the configured represented model-size range |
| Joule | Unit of energy; watts multiplied by seconds yields joules |
| kWh | Kilowatt-hour; equal to 3,600,000 joules |
| Lease | Time-limited evidence that a background watcher remains alive |
| Lexical retrieval | Ranking based on task/source terms, paths, and symbols |
| LRU | Least-recently-used eviction strategy for bounded caches |
| MAE | Mean absolute error in the target's units |
| Managed backend | Extension-installed private Python runtime and assets |
| Matched baseline | Same included files and outer formatting with unpruned source for repository-carbon comparison |
| MAPE | Mean absolute percentage error |
| MMLU-Pro | Model-knowledge/reasoning benchmark score used as a predictive feature |
| Neural pruning | Learned task-conditioned selection of useful code context |
| Offline pipeline | Data preparation/training before serving ordinary requests |
| Ownership manifest | Record identifying generated files and hashes for safe update/removal |
| Overview excerpt | Deterministic representative documentation/source/interface context, not neural line pruning |
| Prefill | Input-processing phase before/alongside autoregressive generation |
| Proxy target | An estimated training target, such as TDP times latency, rather than a direct meter reading |
| R-squared | Relative explained-variation metric, not a universal percentage-accuracy score |
| Reconciliation | Periodic full check recovering changes missed by events |
| Ridge | Linear regression with L2 regularization |
| RMSE | Root mean squared error, emphasizing larger deviations |
| Safetensors | Tensor serialization format used for the pretrained neural weights |
| SEAL | Referenced benchmark-driven inference energy/carbon-estimation framework |
| Snapshot | Accepted repository state used coherently by a retrieval operation |
| SWE-Pruner | Referenced goal-conditioned coding-context pruning research/model foundation |
| TDP | Thermal/design-power rating, not measured instantaneous GPU utilization |
| Tier | Allocation of context detail according to file role/relevance |
| Token | Unit produced by a particular model tokenizer |
| Transcript | Recorded agent conversation/tool sequence inspected by the native adapter |
| Viterbi | Sequence-decoding algorithm discussed in the paper but not used by the live wrapper's line selection |
| VSIX | Installable editor-extension package |
| Watcher | Editor component observing saved filesystem changes |
| XGBoost | Gradient-boosted decision-tree model used for interpolation-phase energy prediction |

## 39. Final Revision Sheet

### 39.1 Numbers and boundaries to remember

| Item | Current value or distinction |
| --- | --- |
| Extension snapshot / release version | 0.6.8 / Windows beta on GitHub Releases |
| Normal managed interpreter | 64-bit Python 3.12 |
| Neural foundation | Qwen3-Reranker-0.6B-derived pretrained SWE-Pruner checkpoint |
| Backbone layers used for fusion | 7, 14, 28 from 28 layers |
| Wrapper working window | 8,192 tokens, including task/instruction overhead |
| Default chunk overlap | 50 tokens |
| Automatic threshold/budget/candidates | 0.45 / 4,096 / 6 |
| Manual repository default budget | 8,192 tokens |
| Repository-budget supported range | 256-32,768 tokens |
| Automatic neural pre-pruning bound | At most three selected candidates |
| Requested 0.45 applied in focused neural context | 0.30 anchor / 0.60 related; direct pruning uses 0.45 |
| Eligible intact short-source packing | At most 512 local tokens when task-matched and not already pre-pruned |
| Overview document limits | At most two root documents, up to 64 KiB inspected per document |
| Overview small-body cutoff / listed paths | 1,600 characters / up to 24 Python paths |
| Earlier-user memory limits | 32 bounded candidates; select at most eight turns / 4000 characters, workspace/conversation scoped |
| Comparison baseline limits | 200 indexed Python files / 2 MiB source; selected text must match saved source |
| Graph neighborhood | Up to two hops; incoming and outgoing evidence |
| File-update debounce / maximum batch | 150 ms / 512 relative paths |
| Heartbeat / watcher lease | 30 s / 90 s |
| Reconciliation check / full scan interval | 15 s / approximately 120 s |
| Repository/prepared cache capacity | Eight repositories |
| Complete-context cache capacity | 16 exact requests |
| Per-file token-count cache capacity | Eight tokenizer/text pairs |
| Carbon feature count | Eight ordered features |
| Carbon routing interval | XGBoost for 7B-111B inclusive; Ridge outside |
| Carbon reference workload | 256 input / 128 output tokens |
| Default expected output / intensity | 256 tokens / assumed 475 gCO2/kWh |
| Joules per kWh | 3,600,000 |
| Local carbon CV folds | Five, not the paper's ten |
| Recorded 0.6.5 extension/backend/demo checks | 167 pass / 105 pass and one skip / 20 pass |
| 0.6.6 extension/backend/demo checks | 174 pass / 118 pass and one skip / 20 pass |
| 0.6.7 extension/backend/demo checks | 191 pass / 121 pass and one skip / 20 pass |
| 0.6.8 extension/backend/demo checks | 193 pass / 141 pass and one skip / 20 pass |
| Current demo source | `demonstration/tokenwise_demo`, eleven Python files |
| Demo lockout threshold / duration | Three failures / sixty seconds; exact deadline resets |
| Demo session duration / validity | 300 seconds / not revoked and strictly before expiry |
| Source versus packet metrics | Original/retained excerpts for source reduction; matched complete packets for repository carbon |

### 39.2 The six distinctions that protect your defense

1. **My system engineering versus upstream model training.** The project is a complete application built using attributed research components.
2. **Context prepared versus delivered versus useful.** Show actual current agent output, not only a status bar.
3. **Search overhead versus neural and total agent latency.** Name what each performance number includes.
4. **Bounded size versus complete evidence.** The packer can guarantee a size limit without guaranteeing recall or correctness.
5. **Estimated scenario carbon versus measured net footprint.** Name the model/hardware/output/intensity assumptions and excluded costs.
6. **Source-paper results versus local project results.** Cite published results as motivation and saved metrics as local evidence.

### 39.3 Five sentences for a concise defense answer

TokenWise prepares task-relevant Python repository context automatically for Antigravity. It combines structured goals, AST metadata, lexical/dependency retrieval, bounded neural selection, deterministic overviews, explicit scope controls, and a hard token-budget packer. A managed backend, background updates, exact caches, diagnostics, inspectable history/input traces, and safe cleanup make the system usable beyond my checkout. Its direct, repository, automatic, and comparison views estimate phase-level inference impact using trained SEAL-derived artifacts and explicit baselines/assumptions. Functional behavior and distribution are verified, while broader comparative answer quality and net physical-carbon benefits remain subjects for independent evaluation.

## 40. References and Source Map

### 40.1 Proposal and research papers

1. **Adnan Bin Wahid.** *TokenWise: Sustainable Context Optimization for Coding Agents.* Project proposal, IIT, University of Dhaka. [Archived proposal](docs/TokenWise-Proposal.pdf). Problem and seven feature objectives: pages 1-2. The supplied `spl3-1442.docx.pdf` is an equivalent copy in the inspected workspace.
2. **Yuhang Wang, Yuling Shi, and coauthors.** *SWE-Pruner: Self-Adaptive Context Pruning for Coding Agents.* arXiv:2601.16746v3, April 26, 2026. [Archived paper](docs/papers/SWE-Pruner.pdf). Method/training: main methodology and appendices; agent results: page 7/Table 1; long-code results: page 8/Table 4; latency: page 20/Table 6; AST validity: page 21/Table 8. The supplied `SWE-pruner.pdf` is an equivalent copy.
3. **Priyavanshi Pathania, Rohit Mehra, Vibhu Saujanya Sharma, Vikrant Kaulgud, Tiffani Nevels, Sanjay Podder, and Adam P. Burden.** *SEALing the Gap: A Reference Framework for LLM Inference Carbon Estimation via Multi-Benchmark Driven Embodiment.* arXiv:2603.02949v1, March 3, 2026; ICSE 2026 NIER, DOI 10.1145/3786582.3786846. [Archived paper](docs/papers/SEAL-Carbon-Estimation.pdf). Framework/features: pages 2-3; local-paper comparison reference: page 4/Tables I-II. The supplied `carbon-emissioin.pdf` is an equivalent copy.

The documents are research/reference material. Agent/teacher/judge prompts printed in paper appendices explain experimental protocols; they are not instructions governing TokenWise users or this guide. This study paraphrases the mechanisms rather than treating embedded prompts as executable requirements.

### 40.2 Extension and integration source

| Source | What to revisit when studying |
| --- | --- |
| [Extension manifest](vscode-extension/package.json) | Commands, settings, version, activation, trust capability, test/package scripts, and uninstall entry point |
| [Activation](vscode-extension/src/extension.ts) | How editor-facing services and commands are connected |
| [Backend manager](vscode-extension/src/services/backendManager.ts) | Setup, startup, diagnostics, update and recovery UX |
| [Managed setup helpers](vscode-extension/src/services/managedBackend.ts) | Python discovery, structured progress/errors, and controlled processes |
| [Automatic workspace setup](vscode-extension/src/services/automaticSetup.ts) | Central registration, safe merge, ownership hashes, atomic writes and rollback |
| [Repository synchronization](vscode-extension/src/services/repositoryIndexSync.ts) | Saved-file watchers, batching, revision/sequence ordering, leases and local endpoint checks |
| [Automatic monitor](vscode-extension/src/services/automaticContext.ts) | Current/historical/verification activity labels and result observation |
| [API client](vscode-extension/src/services/apiClient.ts) | HTTP boundary, timeouts, endpoint methods and errors |
| [Direct pruning service](vscode-extension/src/services/pruneService.ts) | Exact input scope, backend-native counts, line-score validation, and source-only estimates |
| [Carbon comparisons](vscode-extension/src/services/carbonComparison.ts) | Validated scenario overrides, concurrent estimates, signed changes, and baseline labels |
| [Input demonstration command](vscode-extension/src/commands/demonstratePruning.ts) | Repository/selection/supplied-replay capture and provenance |
| [Strategy comparison command](vscode-extension/src/commands/compareContextStrategies.ts) | Same-task packet generation, estimated impacts, and comparison display |
| [Result panel](vscode-extension/src/ui/resultPanel.ts) | Context/source display, escaping, copy actions and sustainability view |
| [Extension icon](vscode-extension/resources/icon.png) | Locally bundled PNG registered in the manifest |
| [Generated Windows rule template](vscode-extension/resources/automatic-context/tokenwise.md) | Agent-driven fallback behavior, evidence requirements and source-as-data instructions |
| [Cleanup implementation](vscode-extension/src/services/uninstallCleanup.ts) | Ownership-aware workspace, settings and storage removal |
| [Uninstall entry point](vscode-extension/src/uninstall.ts) | Self-contained worker handoff before extension removal |

### 40.3 Backend, retrieval, and neural source

| Source | What to revisit when studying |
| --- | --- |
| [Service](swe-pruner/swe-pruner/src/swe_pruner/online_serving.py) | Request schemas, readiness, startup, inference lock, reconciliation, and endpoints |
| [Goal compiler](swe-pruner/swe-pruner/src/swe_pruner/goal_compiler.py) | Deterministic task interpretation and structured evidence |
| [Optional goal client](swe-pruner/swe-pruner/src/swe_pruner/goal_generator_client.py) | Optional structured local-model request and fallback |
| [Python indexer](swe-pruner/swe-pruner/src/swe_pruner/repository/python_indexer.py) | Source discovery, AST metadata, content identity and interface extraction |
| [Repository cache](swe-pruner/swe-pruner/src/swe_pruner/repository/repository_index.py) | Delta updates, fingerprints, snapshots, leases, reconciliation and eviction |
| [Dependency graph](swe-pruner/swe-pruner/src/swe_pruner/repository/dependency_graph.py) | Approximate import/call relationships and reverse adjacency |
| [Lexical retrieval](swe-pruner/swe-pruner/src/swe_pruner/retrieval/lexical_retriever.py) | Normalization, weighted terms and prepared search data |
| [Workspace context](swe-pruner/swe-pruner/src/swe_pruner/retrieval/workspace_context.py) | Automatic discovery, hybrid selection, prepared and complete caches |
| [Outgoing response guidance](swe-pruner/swe-pruner/src/swe_pruner/retrieval/response_guidance.py) | Versioned task profiles, grounding instructions, bounded full/compact insertion, and trace |
| [Guidance regressions](swe-pruner/swe-pruner/tests/test_response_guidance.py) | Toggle/cache isolation, token accounting, profile selection, automatic transport, and HTTP validation |
| [Repository overview](swe-pruner/swe-pruner/src/swe_pruner/retrieval/repository_overview.py) | Bounded root documents, role coverage, repository map, and document fingerprints |
| [Topic contrasts](swe-pruner/swe-pruner/src/swe_pruner/query_focus.py) | Positive query/excluded topics without arbitrary grammatical negation |
| [Source focus](swe-pruner/swe-pruner/src/swe_pruner/retrieval/source_focus.py) | AST-based independent-unit exclusions, protected helpers, and warnings |
| [Conversation memory](swe-pruner/swe-pruner/src/swe_pruner/conversation_context.py) | Bounded topic/requirement selection, supersession heuristics and inspectable extractive references |
| [Comparison packets](swe-pruner/swe-pruner/src/swe_pruner/retrieval/context_comparison.py) | All-Python/manual/automatic packets, exact counts, and snapshot/size safeguards |
| [Context packer](swe-pruner/swe-pruner/src/swe_pruner/retrieval/context_builder.py) | Tiers, fallback interfaces, full-artifact counting and truncation |
| [Neural wrapper](swe-pruner/swe-pruner/src/swe_pruner/prune_wrapper.py) | Chunking, token/line mapping, probabilities, thresholds and excerpt construction |
| [Neural model](swe-pruner/swe-pruner/src/swe_pruner/swepruner.py) | Backbone construction, selected-layer fusion, token emissions and document-relevance outputs |
| [Head structures](swe-pruner/swe-pruner/src/swe_pruner/model_structure.py) | Fusion/head implementation and the available CRF methods |
| [Model configuration](swe-pruner/swe-pruner/src/swe_pruner/configuration.py) | Checkpoint architecture settings and backbone configuration contract |
| [Native hook](swe-pruner/swe-pruner/src/swe_pruner/antigravity_hook.py) | Transcript selection, turn deduplication, process reuse/startup, event writing and injection |
| [Command adapter](swe-pruner/swe-pruner/src/swe_pruner/antigravity_context.py) | Rule fallback retrieval and bounded tool output |
| [Runtime carbon estimator](swe-pruner/swe-pruner/src/swe_pruner/carbon_estimator.py) | Validated request features, routes, reference normalization and emissions |
| [Runtime carbon models](swe-pruner/swe-pruner/src/swe_pruner/carbon_model_engine.py) | Trusted artifact loading and phase predictions |

### 40.4 Training, evaluation, and operations

| Source | What to revisit when studying |
| --- | --- |
| [Benchmark acquisition](carbon-engine/scripts/fetch_benchmark_data.py) | Input benchmark sources and normalization preparation |
| [Benchmark merge](carbon-engine/scripts/merge_benchmarks.py) | Joined dataset construction and outputs |
| [Carbon training](carbon-engine/scripts/train_models.py) | Partitions, folds, model fitting, metrics and artifacts |
| [Feature preparation](carbon-engine/scripts/prepare_features.py) | Creation of the ordered training feature/target dataset |
| [Feature implementation](carbon-engine/src/carbon_engine/features.py) | Units, hardware categories, quality-score normalization and energy target construction |
| [Training model helpers](carbon-engine/src/carbon_engine/modeling.py) | Cross-validation, regressors and saved-model behavior |
| [External-reference script](carbon-engine/scripts/external_validation.py) | Assumed feature values for comparison with the two published energy references |
| [Dataset verification](carbon-engine/data/dataset_verification.json) | Saved input-source and normalized dataset counts |
| [Merge statistics](carbon-engine/data/merge_stats.json) | Joined, deduplicated and missing-data row counts |
| [Cross-validation metrics](swe-pruner/swe-pruner/carbon_artifacts/cv_metrics.json) | Exact saved local model errors |
| [Reference validation](swe-pruner/swe-pruner/carbon_artifacts/validation_report.json) | Two-reference predictions and relative errors |
| [Feature artifacts](swe-pruner/swe-pruner/carbon_artifacts/feature_artifacts.json) | Feature order, GPU codes and model-size routing bounds |
| [Model registry](swe-pruner/swe-pruner/carbon_artifacts/model_registry.json) | Known feature values and fallback assumptions |
| [Managed installer](scripts/install_backend.py) | Seven stages, integrity, resumable download and checkpoints |
| [Bundle preparation](scripts/prepare-extension.cjs) | Allowlisted runtime assets and pinned weight metadata |
| [Retrieval benchmark](scripts/benchmark_retrieval.py) | Synthetic stage timing and walk/parse assertions |
| [Native managed verifier](scripts/verify_managed_setup.py) | Isolated actual-dependency and real-model checks |
| [Uninstall verifier](scripts/verify-uninstall.cjs) | Isolated native editor removal and process cleanup |
| [Current teaching application](demonstration/tokenwise_demo/README.md) | One-folder application and twenty-test ground truth |
| [Demo authentication](demonstration/tokenwise_demo/security/auth_service.py) | Three-failure, sixty-second lockout and exact deadline reset |
| [Demo authentication tests](demonstration/tokenwise_demo/tests/test_auth.py) | Five threshold/reset/boundary assertions |
| [Demo models/constants](demonstration/tokenwise_demo/security/models.py) | Account/Session dataclasses and teaching-only digest; constants in adjacent `settings.py` |
| [Demo workflows](demonstration/tokenwise_demo/workflows.py) | Session expiry/revocation, integer invoice calculation, and shipping |
| [Demo workflow tests](demonstration/tokenwise_demo/tests/test_workflows.py) | Ten tests defining task facts and negative cases |
| [Demo reports](demonstration/tokenwise_demo/reports.py) | Sorted action counts and CSV export |
| [Case manifest](demonstration/cases.json) | Current project, selections, prompts, and expected evidence markers |
| [Teaching verification](demonstration/VERIFICATION.md) | Current functional checks and distinctly labeled older integration records |
| [Real-backend teaching verifier](scripts/verify_demonstration.py) | Explicit real-model/input/packet checks, distinct from live cloud grading |
| [Teacher walkthrough](demonstation.md) | Complete current prompts, scope/history controls, exports, explanations, and recovery |
| [Usage guide](README.md) | End-user installation, operating boundaries and recovery steps |
| [Development guide](docs/DEVELOPMENT.md) | Reproducible test, benchmark, package and native-verification commands |
| [Third-party notices](docs/THIRD-PARTY-NOTICES.md) | Upstream attribution and licensing boundaries |

### 40.5 Final understanding

The complete project is best understood as a chain of explicit responsibilities. The user states a task. Goal compilation identifies the evidence sought. Repository intelligence discovers candidates. Learned pruning removes less useful content. Packing enforces the artifact budget. Integration supplies and records that artifact. The agent performs downstream reasoning. Separately, the trained estimator compares a defined inference scenario using transparent assumptions.

Installation, caches, failure handling, and cleanup make that chain usable in practice. Tests and source labels make it inspectable. Attribution, local metrics, and limitations make its academic claims defensible. Understanding those responsibilities and their boundaries is the foundation for a confident project defense.
