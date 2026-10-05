# TokenWise: Complete Project Study and Defense Guide

**Project:** TokenWise: Sustainable Context Optimization for Coding Agents  
**Student:** Adnan Bin Wahid, BSSE-1442, Institute of Information Technology, University of Dhaka  
**Supervisor named in the proposal:** Mridha Md. Nafis Fuad  
**Implementation studied:** TokenWise extension 0.6.0, source snapshot inspected on October 5, 2026  
**Purpose:** Understand the entire project, explain its engineering and research foundations, demonstrate it, and answer project-defense questions confidently.

This guide describes TokenWise as a complete system: its requirements, architecture, implementation, research basis, operation, evaluation, distribution, and limitations. It is not a chronological account of repairs, and it does not explain source code line by line. Instead, it explains the reasoning and behavior behind the important parts of the implementation.

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

The project also includes a trained, SEAL-derived energy and carbon-estimation component. In the extension's manual pruning and repository-context workflows, it compares estimated inference impact before and after pruning under the same target-model assumptions. This sustainability component is a scenario estimator, not a meter attached to Antigravity's cloud infrastructure.

An important scope distinction is that the automatic Antigravity launcher currently retrieves context and records activity; it does not call the carbon-estimation endpoint. Automatic context preparation and manual before/after sustainability reporting are therefore related capabilities, but they are not identical execution paths.

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
| Sustainability dashboard | Before/after energy and carbon information in manual result views | Automatic Antigravity retrieval currently does not attach carbon estimates to each activity event. |

The proposal's desired benefits include lower noise, token use, and environmental impact. These are motivations to investigate. The current project establishes functional context retrieval, hard size limits, installation and lifecycle behavior, and particular local measurements. It does not establish universal hallucination reduction, universal speed improvement, or production-quality carbon measurement.

The implementation's operating scope is local, trusted Python repositories. Single-file neural pruning can accept code text, but repository structure is discovered through Python's AST module. Native Windows installation and integration checks are available. macOS/Linux launchers are included, but their presence should not be presented as completed native cross-platform validation. Remote SSH, WSL/dev-container, browser, and virtual-workspace first-run integration are outside the supported workflow.

## 5. Fundamental Concepts

### 5.1 Tokens and token budgets

A token is a unit used by a model's tokenizer. It may represent a whole word, part of a word, punctuation, whitespace, or a code fragment. Token counts are not identical to character counts or line counts. Different models can tokenize the same string differently.

TokenWise uses the local neural model's tokenizer to enforce repository-context budgets. A 4,096-token limit means a limit under that tokenizer. It is not a guaranteed 4,096-token bill from Gemini, Claude, or another agent model. The manual single-file carbon path also has a frontend token-counting implementation, which introduces another distinction explained later.

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
        | saved Python files + user task
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
                        +--> Bounded candidate selection
                        +--> SWE-Pruner-derived neural scoring and line pruning
                        +--> Tiered context packing under a hard token budget
                        |
                        v
          Source-labeled context supplied to the coding agent
                        |
                        v
       Agent explanation, additional investigation, or proposed edits

Separate manual sustainability path:
Original/pruned token counts + target-model assumptions
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
| `Test_project/` | Small Python authentication/payment repository with six tests for demonstrations |
| `docs/` | Proposal, source papers, usage/integration/development/publishing documentation, and evaluation records |
| `README.md` | Normal-user installation and operation instructions |
| `review.md` | Broader review material; descriptions may refer to older snapshots |
| `study.md` | This complete conceptual and defense guide |

Three locations must not be confused: the developer's TokenWise source checkout, the extension-managed backend in IDE user storage, and the user's application repository. Normal users do not need to place their application inside the TokenWise checkout. The managed backend is shared infrastructure; each enabled repository has a small local integration and a link to the central registration.

Generated directories such as virtual environments, package dependencies, compiled output, local activity, backend bundles, and release outputs are not the architectural source of truth. They can be rebuilt or removed according to their ownership rules. The source tree, configuration, training pipeline, and saved model artifacts explain how the product is assembled.

## 8. End-to-End Prompt Lifecycle

Consider the task: **Explain account lockout after failed login attempts and its related tests. Do not modify any files.** The complete automatic path is as follows.

First, the repository has been enabled through the extension. The workspace contains an always-on TokenWise rule, hook configuration, launchers, settings, and a central backend link. If the configured trusted folder is open, background synchronization can already have prepared its repository index.

Second, the Antigravity agent obtains TokenWise context. A supported native hook can do this through the hook protocol; otherwise, the workspace rule asks the agent to execute the local retrieval command. The developer still writes only the ordinary prompt. A command approval may be needed under the IDE's permission policy.

Third, the launcher resolves the managed backend through the central registration. It reuses a healthy matching process or starts one locally. It does not assume that the Python repository is a child of the TokenWise checkout.

Fourth, the request is sent to `/prune-workspace` with the task, absolute workspace path, threshold, token budget, and candidate limit. Automatic defaults are 4,096 tokens, threshold 0.45, and six candidates. No active editor file is required.

Fifth, the backend validates the workspace and obtains a repository snapshot. With a live watcher, the current in-memory snapshot avoids a full repository walk per query. Without a live watcher, a conservative content-verified scan protects against stale reuse.

Sixth, the goal compiler interprets the task as an explanation/understanding request. Query identifiers and task vocabulary contribute to lexical search. A relevant anchor can be discovered automatically from the best matches rather than from a manually selected file.

Seventh, lexical matches, exact symbol evidence where available, and dependency relationships identify candidates. In this demo, useful evidence can include `services/auth_service.py`, `models/auth.py`, `tests/test_auth.py`, and supporting helpers. Selection remains budget- and ranking-dependent; a particular output is not promised to include every relevant file.

Eighth, a bounded number of candidates receive neural scoring and pruning. The model considers the goal and the code together. It estimates relevance at the token level, aggregates scores to source lines, and removes less relevant spans. Remaining candidates may contribute interface-only context.

Ninth, the context builder organizes source-labeled excerpts and adds a preamble explaining that they are reference data, may omit lines, and should not be used as direct source replacements. It counts the complete packed text and enforces the configured budget, including headings and separators.

Tenth, the launcher writes a new activity event and returns the context through tool output or hook injection. The extension observes the activity and shows selected files, token count, task, and elapsed preparation time. The agent uses the supplied evidence and can read original files for additional details.

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
| `.tokenwise/conversations/` | Native-hook deduplication state |
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
| **Show Automatic Context** | Inspect the most recently observed prepared context |
| **Remove All Local Data** | Explicitly remove extension-owned data while the extension is still installed |
| **Prune Selected Code** | Manually analyze a selected text region for a task |
| **Prune Current File** | Manually prune a complete editor file |
| **Build Repository Context** | Manually build task-oriented repository context using an active Python file as additional evidence |
| **Check Backend Health** | Verify model/carbon readiness and service/device information |

All names above have the `TokenWise:` prefix in the command palette. Manual workflows remain useful for inspection, comparison, and non-Antigravity VS Code use. The automatic experience relies on the agent integration and does not require these manual pruning commands for every prompt.

### 11.3 What result views communicate

The single-file view compares original and pruned text, token counts, retained line fragments, and any successfully obtained sustainability estimates. The repository view displays a structured goal, selected files, their relations and tiers, source versus packed tokens, and the unified context. Automatic results also include task and preparation time.

The interface provides copy actions, not a button that replaces application source with a pruned excerpt. Elision markers and incomplete blocks make such replacement unsafe. A context optimizer should help the agent reason about source while preserving the original program as the authority.

The status bar is a compact operational indicator. The automatic file/token count describes a particular prepared result. A manual-session carbon accumulator is not a complete meter of all agent requests, all repositories, or the actual electricity used by the IDE.

### 11.4 Settings and defaults

The manual API URL defaults to `http://127.0.0.1:8000`, request timeout to 120 seconds, and threshold to 0.45. Manual repository context defaults to 8,192 tokens. Automatic workspace settings independently default to 4,096 tokens, six candidates, a 40-second backend-start timeout, and a 90-second retrieval timeout.

The optional local goal model is disabled by default. Manual carbon estimation is enabled by default and uses a benchmark-backed Llama-3 8B target, 256 expected output tokens, and an assumed carbon intensity of 475 gCO2/kWh. These are configured scenarios, not automatic detection of the current Antigravity cloud model or region.

Changing a manual extension setting does not necessarily alter the automatic workspace JSON setting. Explain the control boundary clearly when demonstrating a different budget: edit `.agents/tokenwise.json` for the automatic launcher, and use the repository-budget extension setting for the manual command.

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
| `POST /index-workspace` | Start, update, reconcile, or stop a background watcher session | Absolute workspace path, bounded path batches, watcher identity, and sequence values |
| `POST /estimate-carbon` | Predicted phase energy and carbon from workload/model assumptions | Feature values, supported encoded hardware, and loaded artifacts |

Pydantic defines request types and numeric bounds. Invalid schema input is different from a valid request that refers to a nonexistent repository. Model-unavailable conditions use HTTP 503; repository/configuration problems commonly use HTTP 400. The clients expose response errors rather than swallowing them.

### 12.3 Readiness is more than a running port

Another application may already use port 8000. TokenWise checks its service identity and model path before reusing a process. If needed, startup searches a small nearby port range and records the actual port. It does not terminate an unrelated process to take its port.

A healthy HTTP server with `model_loaded: false` cannot provide neural pruning. A server with `carbon_models_loaded: false` cannot provide a valid trained carbon estimate. In a defense, show that the diagnostic contract exposes these separate conditions.

### 12.4 API response interpretation

A workspace result includes its structured goal, source-labeled unified prompt, packed token count, baseline source count for included files, selected-file metadata, anchor, repository fingerprint, and cache diagnostics. These values allow an inspector to connect the result to a snapshot and understand why it has a particular size.

The cache flags distinguish repository-index reuse, prepared retrieval-data reuse, and a complete context-cache hit. They should not be combined into the statement that every cache hit skips all processing. A different task can reuse the index and search data while requiring fresh ranking and pruning.

## 13. Task and Goal Compilation

### 13.1 Why a structured goal exists

A user's natural-language task contains several kinds of information: requested action, target identifiers, symptoms, errors, and desired evidence. Converting this into a structured goal makes retrieval more explicit and reduces dependence on a raw phrase alone.

The goal contains `task_type`, `objective`, `identifiers`, `observed_errors`, `required_context`, `retrieval_questions`, and `clarification_required`. Manual repository commands can also supply the active file, current symbol, selected code, and diagnostics. The automatic path intentionally works without those selections.

### 13.2 Deterministic default behavior

The default compiler uses task vocabulary and templates for understanding, debugging/fixing, refactoring, adding features, testing, and generic repository investigation. It extracts plausible identifiers and error evidence from the supplied task and editor evidence.

This approach is fast, predictable, and available offline without another model server. It avoids a failed optional-LLM request on every ordinary prompt. It is also limited: keyword interpretation is not deep program comprehension, and regex-derived identifiers are not proof that the repository defines a matching symbol.

The goal's required-context and retrieval-question fields communicate intent. They do not mean the system executes a complete autonomous multi-hop planning process for every question. The implemented retriever remains lexical, graph-based, and bounded.

### 13.3 Optional local LLM generation

When enabled, a local OpenAI-compatible chat endpoint can produce structured goal JSON. The client requests deterministic-style output, validates it with the same schema, and uses the deterministic compiler if the request or validation fails. The optional call has its own timeout.

This is an enhancement rather than a dependency of normal installation. Ollama or LM Studio can supply such an endpoint if the user chooses to configure one. No additional model server is required for the default TokenWise experience.

If a user changes this endpoint to a nonlocal service, its privacy implications must be considered. The name 'local goal model' does not magically make an arbitrary URL local. Network destination and what task/editor evidence is sent determine the actual exposure.

### 13.4 Ambiguity and clarification

A vague task such as 'fix the bug' without evidence can set `clarification_required`. That expresses missing information but currently does not stop the backend and force an interactive clarification exchange. The backend can still construct whatever context is available.

This is a useful defense distinction: the project models ambiguity, but it does not yet implement a full clarification policy. A future improvement could ask a targeted question when confidence or evidence is inadequate rather than delivering a weak bundle confidently.

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

`services/auth_service.py` imports authentication models and cryptographic helpers. The helpers import configuration. `tests/test_auth.py` imports the service. These relationships provide a useful explanation chain from lockout behavior to state, token/session behavior, and the test that checks repeated failures.

For a lockout question, the service and test are usually more important than unrelated payment behavior. Graph evidence complements lexical search by revealing dependencies whose filenames or source text may not share the user's exact words.

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

The manual candidate-ranking path can score truncated candidate content and then later prune selected content, creating possible additional model work. The automatic path's reuse avoids repeating the same pruning operation for its pre-pruned candidates. This difference is useful when discussing latency and implementation choices.

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

The wrapper's basic threshold default is 0.5, while the extension/automatic workspace default is 0.45. Repository packing can use a lower threshold for a primary file and a higher one for related files when it performs uncached pruning itself. Pre-pruned automatic candidates already have their excerpt and are reused rather than rescored merely because a later tier label differs.

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

The automatic path can force non-prepruned candidates to the interface tier to keep neural work bounded. File relation labels are descriptive heuristics. A path containing 'test' can receive a 'related test' label; the label alone does not prove that its assertions cover the precise task.

### 20.2 Budgeting the complete artifact

The final budget counts the preamble, file headers, source paths, relation/tier labels, code fences, separators, truncation markers, and content. A budget that counts only retained code would underestimate the actual supplied artifact.

The packer orders the primary file first when appropriate, then other candidates by ranking. It computes remaining space, accounts for block overhead, truncates content using the tokenizer, and verifies the combined text. It tightens when tokenizer decoding or boundary merging creates a discrepancy.

Supported repository budgets range from 256 to 32,768 tokens. The automatic adapter independently checks that the returned packed count is a valid integer and does not exceed the configured budget. Invalid or oversized context is not injected just because the backend returned HTTP success.

### 20.3 What the budget guarantees and does not guarantee

The budget guarantees bounded packed size under the local tokenizer when a valid result is accepted. It does not guarantee representation of every dependency, retention of every test, optimal allocation among files, or complete semantic correctness.

A long first file can consume most of the available space. Later high-value tests may then be omitted. A future packer could reserve evidence categories, choose at symbol/block granularity, or optimize value per token. The present ordered packing is understandable and bounded but not a globally optimal context-selection solver.

### 20.4 Understanding source versus packed tokens

The workspace result's original-token baseline sums source content for files actually included in the packed result. It is not the token count of the entire repository, and it is not a measured baseline of all file reads Antigravity would otherwise perform.

The packed-token count includes formatting and the preamble. It is therefore possible for a very small interface bundle to have substantial overhead relative to its source baseline. Before/after percentages must be interpreted with these denominators in mind. A displayed or clamped nonnegative saving is not evidence that every task has a positive net benefit.

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
| Complete context | Final packed result and selection | Exact task/goal, fingerprint, root, active file, threshold, budget, and candidate limit |

Index/prepared caches retain a bounded number of repositories, currently eight. Complete contexts retain at most 16 exact requests. Per-file token-count caches retain up to eight tokenizer/text pairs. These limits prevent unbounded growth; eviction means rebuild, not permission to return stale data.

### 22.5 Similar prompts are not identical requests

Search data is query-independent and can safely serve 'explain lockout' and 'explain account locking tests' for the same unchanged snapshot. A completed context is task-dependent and must not be reused merely because the phrases look similar.

The complete-context key includes exact query and structured goal information. It also includes settings that change the output. Editing source or changing the budget invalidates the applicable completed result. This is why cache speed does not require approximate semantic answer reuse.

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

The manual extension requests estimates for original and pruned token counts while keeping expected output, model, hardware, latency, quality features, and carbon intensity unchanged. The difference isolates the modeled input-context effect under that scenario.

If expected output is unchanged, the modeled decode term is unchanged. A 75% input-token reduction therefore need not produce a 75% total energy or carbon reduction. The unchanged decode component remains part of both totals.

The two manual carbon requests can run concurrently. If estimation fails, the extension still presents usable pruning context and reports that the carbon layer was unavailable. It does not replace missing trained artifacts with an untrained hand-written number and label it a valid model prediction.

### 25.5 Tokenizer differences

Single-file pruning reports local neural-tokenizer counts, while its frontend carbon comparison uses a separate token-counting helper based on `gpt-tokenizer`, with a character-based fallback if needed. Repository-context carbon comparisons use the backend's local counts.

Neither automatically guarantees the exact input token count of the user's chosen Antigravity model. The displayed pruning ratio and the carbon-estimation input ratio can therefore have different counting provenance. Honest reporting should name the tokenizer/counting method rather than presenting all token numbers as identical billing units.

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

`Test_project` is a small, readable Python application designed to make repository retrieval observable. It contains ten Python source files organized into configuration, models, services, utilities, tests, and an application entry point. Authentication and payment provide two distinct domains so a prompt can demonstrate whether retrieval focuses on relevant evidence rather than indiscriminately showing the entire application.

It is a demonstration fixture, not a production banking or authentication system. Its simplified storage, password hashing, and mock token/payment behavior should be explained as deliberate teaching/test material.

### 27.2 Authentication state and login flow

`UserAccount` stores an identifier, username, email, password hash, roles, active state, failed-login count, and creation timestamp. `AuthSession` stores a session identifier, user identifier, token, creation time, and revocation state. The service keeps users and sessions in memory and initializes a demo administrator.

When a username is unknown, authentication returns no token and audits the failed lookup. When the account is inactive, authentication returns no token before attempting another password comparison. For an active known account with a wrong password, it increments `failed_login_attempts`.

The lockout threshold is five failed attempts. At the fifth failure, the service sets `is_active` to false, records an error/audit event, and returns no token. A later attempt using the correct password still fails because the inactive-account check occurs first. There is no implemented automatic unlock timer or administrative unlock workflow.

A successful login before lockout resets the failed-attempt count to zero, creates a token with user information, stores an active session, and returns the token. This reset makes failures consecutive with respect to intervening successful login behavior, but the service itself does not implement time-windowed rate limiting.

### 27.3 Session validation and revocation

Validation first verifies the mock token's signature/expiration behavior. It then requires a stored session containing that token and not marked revoked. Revocation changes the selected session's state; validating its token afterward fails.

Existing session validity is not automatically tied to the user's current active state in this demo implementation. Account lockout prevents later authentication, but the demo should not be described as a complete security policy that automatically invalidates every previously created session.

### 27.4 Authentication tests

| Test | What it demonstrates |
| --- | --- |
| `test_successful_login_and_validation` | A valid demo login yields a token and a validated payload with the expected username. |
| `test_account_locks_after_five_failures` | Five wrong-password attempts disable the account and prevent a subsequent correct-password login. |
| `test_revoke_invalidates_session` | Revoking the stored session causes later validation of its token to fail. |

These assertions are excellent evidence for a lockout explanation. They do not cover every authentication edge case. For example, the suite does not directly establish an unlock policy, secure password storage, a successful-login reset after four failures, or distributed persistence.

### 27.5 Payment behavior

`PaymentTransaction` stores transaction identity, user identity, amount, currency, status, gateway reference, error text, retry count, and timestamp. The service creates a pending transaction and attempts a simulated gateway call up to `MAX_PAYMENT_RETRIES`, which is three in the demo configuration.

A positive amount and plausible card length can produce a successful mock reference. A nonpositive amount or invalid card format raises a validation error; the transaction is marked failed and returned without repeating a nonretryable validation failure. A card number ending in `0000` simulates a timeout.

Timeouts are treated as retryable. The service records each failure and sleeps briefly between attempts. On the final timeout it marks the transaction failed and raises `PaymentProcessingError`. This distinction between returned validation failure and raised retry-exhaustion failure is useful task evidence.

### 27.6 Payment tests and repository contrast

The payment tests cover successful processing, invalid card formatting, and exhausted timeout retries. They show why the relevant service, model, configuration, and test should be retrieved together for a retry question.

Ask a lockout question, then a payment-timeout question. The selected context should respond to the different tasks. It may retain some common helper interfaces, but the primary evidence should change. This demonstrates task awareness more clearly than repeatedly running one prompt and pointing only at a token-reduction number.

### 27.7 Demo security qualification

The mock token format is not a production JWT implementation, and the fixed-salt SHA-256 password helper is not a production password-storage recommendation. Payment is simulated rather than a real gateway integration. The configuration includes defaults suitable for a fixture, not production secret management.

These simplifications belong to the demo application, not to the architecture of TokenWise's context retrieval. An examiner can ask about them; the correct answer is to recognize the boundary and explain why a real application would use established security libraries and persistent infrastructure.

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

The result panel escapes task and code text before putting it into HTML and restricts its actionable messages to known copy behavior. Its current content-security policy denies default resource access but allows inline script/style behavior. It is not a nonce-based strict script policy; tightening that policy and adding security-focused UI tests would be useful improvements.

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

This separates a modest distributable extension from the much larger ML runtime download. The release is still more than a thin button wrapper: it contains the implementation required to install and run the local pipeline on another machine.

### 30.3 Public distribution

The current documented release is [TokenWise 0.6.0](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.0). Its normal-user asset is the VSIX, with additional installer/documentation and checksum assets. The project's release workflow is separate from automatically generated GitHub source archives.

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

The following suites were rerun while preparing this guide on October 5, 2026:

| Suite | Result | Meaning |
| --- | --- | --- |
| Extension Node tests | 121 passed, no failures | Command/setup, activity labels, synchronization, ownership, cancellation, and cleanup contracts under the test fixtures |
| Backend Python tests | 69 discovered: 68 passed, 1 skipped, no failures | Adapter, installer, index, cache, budget, and HTTP-contract behavior |
| Demo tests | 6 passed, no failures | Authentication and payment fixture behavior |

The skipped backend test requires creating file symlinks, which this Windows account cannot do. This is a test-coverage qualification, not an unexplained silent pass. The run also emits dependency deprecation warnings; successful assertions do not imply that every library API is future-proof.

Some backend tests intentionally simulate an unavailable neural checkpoint or substitute controlled scoring behavior. Their success must not be described as 68 independent real-model quality benchmarks. Tests exercise the contract they are designed to exercise.

### 31.3 Important regression coverage

Adapter tests verify current user-prompt extraction, ignoring model/tool/injected messages, per-turn deduplication, verification labels, disabled or malformed configuration, backend failure, source discovery without exact symbol names, and rejection of invalid or oversized returned context.

Installer tests cover pinned/cache integrity, partial-download resume and unsupported-range behavior, corruption rejection, stage errors, environment repair, dependency checkpoint reuse, cancellation boundaries, and lock ownership.

Repository/cache tests cover changed content, additions, deletions, directory rename, preserved-timestamp changes, missed-event reconciliation, independent watcher sessions, expired leases, late updates after stop, cached lexical-score equivalence, signature reuse, changed imports/symbols, tokenizer identity, exact-query cache isolation, eviction, and avoiding warm repository walks.

Extension tests additionally exercise trust/remote restrictions, local Antigravity storage handling, settings/rule preservation, rollback, multiroot configuration, background event bursts, in-flight edit preservation, restart reconnection, process identity, JSONC settings cleanup, and a standalone worker surviving removal of the original extension directory.

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
| Packing | Ordered bounded allocation | Important later evidence may not fit. |
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

Fifth, make distribution broader only after support is verified. Add continuous integration, native platform smoke checks, signed/integrity-checked release procedures as appropriate, and public registry publication. Do not claim compatibility based only on the existence of a launcher file.

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

I made context an inspectable artifact rather than a destructive source edit. That design allows both the developer and the agent to recognize omitted material and read original files when needed.

### 35.4 Sustainability pipeline

I implemented benchmark normalization and fusion, feature extraction, phase-specific regression training, artifact saving, runtime prediction, and before/after comparison. I separated original/pruned input effects from fixed expected output and made the energy-to-carbon units explicit.

I report the saved local metrics rather than adopting the source paper's numbers. I recognize proxy target construction and reference assumptions as limitations to address with stronger validation.

### 35.5 Productization and correctness

I implemented central backend registration, recoverable managed installation, arbitrary-workspace integration, background saved-file synchronization, exact cache identities, diagnostics, and ownership-aware uninstall. I added tests for the failure and concurrency cases that could otherwise make a working demo unreliable for another user.

I packaged the extension for VSIX distribution with bundled integrity metadata and separately downloaded weights. Functional tests, isolated integration checks, and performance benchmarks verify different aspects of this complete system.

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

1. Open `Test_project` or another enabled local Python repository. Show that no source file needs to be selected.
2. Start a new Antigravity chat and submit: **Explain account lockout after failed login attempts and its related tests. Do not modify any files.**
3. Show the actual current retrieval command/output or supported hook-injected context, including `[TokenWise automatic context]`.
4. Inspect the new activity timestamp, current query, `status: "ready"`, and `verification: false`. Open the result view to show source files and packed tokens.
5. Confirm the explanation identifies five failures, inactive-state behavior, and the related test assertion. Distinguish source evidence from any extra investigation the agent performs.
6. Submit: **Explain payment gateway timeout retries and the tests that cover exhausted retries. Do not modify any files.**
7. Show that payment service/tests/configuration become the important evidence for the second task.
8. Separately use a manual pruning or repository-context result to demonstrate the sustainability view and explain its assumptions. Do not claim the automatic event already measured carbon.

### 36.4 Performance demonstration without misleading the audience

If demonstrating exact-repeat caching, announce that it is an exact unchanged request. If demonstrating background updates, use a disposable repository rather than altering important project files during the defense. Show the fingerprint change and subsequent source reflection after an acknowledged save.

Present the synthetic search benchmark as a stage measurement. Show total preparation time separately. An examiner should be able to tell which figure includes neural work and which does not.

### 36.5 Closing statement

> TokenWise demonstrates a complete path from task-aware context research to a usable developer extension. The system automatically discovers Python repository evidence, prunes selected content, enforces a hard context budget, and exposes the result in the agent workflow. Its trained sustainability layer provides approximate phase-level inference comparisons with explicit assumptions. I have validated key functional and lifecycle behavior and measured scoped retrieval improvements; my next research step is broader downstream task-quality and net-energy evaluation.

## 37. Detailed Defense Questions and Answers

Use these as reasoning practice, not a script to memorize word for word. A good answer names the mechanism, states the evidence, and acknowledges the boundary.

### 37.1 What problem does your project solve?

TokenWise addresses the difficulty of supplying useful repository context to a coding agent without manual selection or unnecessary source volume. A task can depend on several files, while the developer may not know where they are. The system uses the prompt to retrieve and organize relevant Python evidence, prunes selected content, and enforces a size limit. It also offers approximate manual before/after inference-impact estimates. It does not claim to solve every agent-reasoning or repository-understanding problem.

### 37.2 Why is this not just another chatbot?

TokenWise is an evidence-preparation system, not the final answering model. Antigravity already provides the conversation and agent. My project supplies task-conditioned source context, manages local retrieval infrastructure, and exposes what was selected. The separation lets TokenWise improve the workflow without building a new chat service, authentication system, or cloud-model provider. Its technical work is indexing, retrieval, selection, budgeting, integration, and lifecycle management.

### 37.3 What is your original contribution if you use existing models?

The contribution is a complete integrated developer tool: automatic arbitrary-workspace retrieval, AST/lexical/graph discovery, bounded context construction, Antigravity adapters, trained carbon-estimation integration, background cache maintenance, recoverable installation, diagnostics, safe cleanup, tests, and release packaging. The neural checkpoint is properly attributed. Reusing a pretrained component does not remove the engineering contribution, but I do not claim to have invented or pretrained Qwen or to own the source papers' experiments.

### 37.4 Can you say you built the project from scratch?

I can explain the complete TokenWise system from its requirements through architecture, implementation, validation, and distribution. 'From scratch' in application engineering does not mean writing the operating system, editor, parser, or ML framework. For precision, I say I built the project using established libraries and integrated pretrained research components. I distinguish my system work from the original neural training and published research contributions.

### 37.5 What are the three main conceptual stages?

The proposal describes task-aware skimming, context pruning, and carbon tracking. In the implemented retrieval workflow, these expand into goal compilation, source indexing, lexical/structural candidate discovery, bounded neural processing, and final packing. The carbon stage is a separate trained estimation path in manual extension results. Separating conceptual stages from actual execution paths prevents the misleading claim that every automatic prompt currently receives a carbon estimate.

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

Not as a complete enforced workflow. The structured goal can mark `clarification_required` for insufficient evidence, but the backend can still produce context. A future policy could use that flag or confidence signals to ask a targeted question before retrieval. I distinguish the implemented ambiguity representation from a finished interactive clarification system so the demonstration does not promise behavior that is absent.

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

A lower threshold usually retains more lines and a higher threshold removes more. Neither guarantees improved quality. The implementation also uses tier-related treatment and reuse of already pruned automatic candidates, so a final tier label does not always imply a new model pass at a different threshold. I would choose thresholds using task-quality/token tradeoff experiments rather than only maximizing the compression percentage.

### 37.25 Is the pruned code valid Python?

Not necessarily. It is context for reading, with omitted spans and elision markers, not a syntactically closed source transformation. The paper also reports less-than-perfect AST correctness. The extension therefore offers copying context rather than replacing original files, and the agent rule says to inspect originals before edits. If executable-source preservation becomes a requirement, it needs a separate block/AST-aware design and tests.

### 37.26 How do you guarantee the context size?

The final packer counts the complete supplied artifact using the local tokenizer, including preamble, headers, fences, separators, and markers. It truncates content to remaining space and verifies the combined count. The automatic adapter rejects an invalid or oversized returned count. This guarantees the accepted bundle's configured local-tokenizer bound, not the agent's total conversation size or exact downstream billing-token count.

### 37.27 Does the budget guarantee all necessary files are included?

No. Size and coverage are different properties. The ordered packer can spend much of the budget on a primary file, leaving insufficient space for another useful dependency or test. Candidate ranking and retrieval are also imperfect. The current output is an initial evidence bundle. A future allocation strategy could reserve space for tests and contracts or optimize evidence value per token.

### 37.28 How is 'original tokens' defined in repository results?

It sums original source tokens for included files, not the entire repository and not every file the agent would otherwise read. Packed tokens include context formatting. This denominator matters when reporting reductions. I do not compare a packed bundle with a fictional all-repository baseline unless that baseline is explicitly constructed for an experiment. Real agent-token savings require observing the complete baseline and optimized trajectories.

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

A known active user with a wrong password accumulates failures. At five, the account becomes inactive. Later correct-password authentication still fails because inactive status is checked before password handling. Successful login before lockout resets the count. The test asserts five failures, inactive state, and rejection of the later correct password. There is no automatic unlock timer, and previously existing sessions are not automatically invalidated by checking user activity in this demo.

### 37.58 Why does payment timeout behave differently from invalid input?

Timeout is retryable, so the service attempts up to three times and raises `PaymentProcessingError` after final exhaustion. Invalid card or amount input is treated as nonretryable; it marks the transaction failed and returns it. The tests distinguish success, invalid-card failure, and retry exhaustion. This gives retrieval meaningful behavior to explain and illustrates why configuration and tests can be as important as the service body.

### 37.59 What would a fair research comparison look like?

Use fixed repositories/tasks and the same agent/model/settings for a no-TokenWise baseline and TokenWise runs. Compare success, needed-evidence recall, full input/output tokens, cost, wall-clock distributions, additional file reads, and failures. Repeat tasks and report uncertainty. Ablations can remove graph retrieval, neural pruning, or caching. Carbon evaluation needs independent energy evidence and local-overhead measurement. Functional test counts alone cannot establish research superiority.

### 37.60 What is the most important next improvement?

The most important next step is proving downstream usefulness across independent real tasks while profiling the neural bottleneck. That evidence guides whether to improve candidate recall, context allocation, or model speed. In parallel, carbon provenance and validation need strengthening. Adding features without evaluation can make the tool larger without making it more useful. The current system gives a clear architecture and instrumentation from which to conduct those experiments.

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
| Context wall | The practical difficulty/cost of using very large or noisy model context |
| CRF | Conditional random field, a sequence-labeling component present in the upstream architecture |
| Decode | Output-token generation phase of LLM inference |
| Dependency graph | Approximate file relationships from imports and call-name evidence |
| Document score | Learned relevance signal for a task-code pair |
| Extrapolation | Prediction outside a specified represented feature range |
| Feature schema | Ordered definition of inputs expected by a trained regression model |
| Goal hint | Task-conditioned description guiding retrieval and pruning |
| GPU encoder | Mapping from supported hardware categories to saved numeric codes |
| Heartbeat | Periodic signal renewing a watcher lease |
| Interface view | AST-derived compact signatures and structural context with bodies omitted |
| Interpolation | Prediction inside the configured represented model-size range |
| Joule | Unit of energy; watts multiplied by seconds yields joules |
| kWh | Kilowatt-hour; equal to 3,600,000 joules |
| Lease | Time-limited evidence that a background watcher remains alive |
| Lexical retrieval | Ranking based on task/source terms, paths, and symbols |
| LRU | Least-recently-used eviction strategy for bounded caches |
| MAE | Mean absolute error in the target's units |
| Managed backend | Extension-installed private Python runtime and assets |
| MAPE | Mean absolute percentage error |
| MMLU-Pro | Model-knowledge/reasoning benchmark score used as a predictive feature |
| Neural pruning | Learned task-conditioned selection of useful code context |
| Offline pipeline | Data preparation/training before serving ordinary requests |
| Ownership manifest | Record identifying generated files and hashes for safe update/removal |
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
| Extension snapshot | 0.6.0 |
| Normal managed interpreter | 64-bit Python 3.12 |
| Neural foundation | Qwen3-Reranker-0.6B-derived pretrained SWE-Pruner checkpoint |
| Backbone layers used for fusion | 7, 14, 28 from 28 layers |
| Wrapper working window | 8,192 tokens, including task/instruction overhead |
| Default chunk overlap | 50 tokens |
| Automatic threshold/budget/candidates | 0.45 / 4,096 / 6 |
| Manual repository default budget | 8,192 tokens |
| Repository-budget supported range | 256-32,768 tokens |
| Automatic neural pre-pruning bound | At most three selected candidates |
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
| Extension/backend/demo tests in this run | 121 pass / 68 pass and one skip / 6 pass |
| Demo lockout / payment attempts | Five failures / three gateway attempts |

### 39.2 The six distinctions that protect your defense

1. **My system engineering versus upstream model training.** The project is a complete application built using attributed research components.
2. **Context prepared versus delivered versus useful.** Show actual current agent output, not only a status bar.
3. **Search overhead versus neural and total agent latency.** Name what each performance number includes.
4. **Bounded size versus complete evidence.** The packer can guarantee a size limit without guaranteeing recall or correctness.
5. **Estimated scenario carbon versus measured net footprint.** Name the model/hardware/output/intensity assumptions and excluded costs.
6. **Source-paper results versus local project results.** Cite published results as motivation and saved metrics as local evidence.

### 39.3 Five sentences for a concise defense answer

TokenWise prepares task-relevant Python repository context automatically for Antigravity. It combines structured goals, AST metadata, lexical and dependency retrieval, pretrained neural line selection, and a hard token-budget packer. A central managed backend, background saved-file updates, exact caches, diagnostics, and safe cleanup make the system usable beyond my checkout. Its separate manual sustainability view estimates phase-level inference impact using trained SEAL-derived artifacts and explicit assumptions. Functional behavior is tested, while broader downstream quality and net physical-carbon benefits remain subjects for independent evaluation.

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
| [Result panel](vscode-extension/src/ui/resultPanel.ts) | Context/source display, escaping, copy actions and sustainability view |
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
| [Demo authentication](Test_project/services/auth_service.py) | Five-failure lockout, session creation, validation and revocation |
| [Demo authentication tests](Test_project/tests/test_auth.py) | Assertions supporting the lockout explanation |
| [Demo payments](Test_project/services/payment_service.py) | Retryable timeout versus nonretryable validation behavior |
| [Demo payment tests](Test_project/tests/test_payment.py) | Success, invalid input and retry-exhaustion coverage |
| [Usage guide](README.md) | End-user installation, operating boundaries and recovery steps |
| [Development guide](docs/DEVELOPMENT.md) | Reproducible test, benchmark, package and native-verification commands |
| [Third-party notices](docs/THIRD-PARTY-NOTICES.md) | Upstream attribution and licensing boundaries |

### 40.5 Final understanding

The complete project is best understood as a chain of explicit responsibilities. The user states a task. Goal compilation identifies the evidence sought. Repository intelligence discovers candidates. Learned pruning removes less useful content. Packing enforces the artifact budget. Integration supplies and records that artifact. The agent performs downstream reasoning. Separately, the trained estimator compares a defined inference scenario using transparent assumptions.

Installation, caches, failure handling, and cleanup make that chain usable in practice. Tests and source labels make it inspectable. Attribution, local metrics, and limitations make its academic claims defensible. Understanding those responsibilities and their boundaries is the foundation for a confident project defense.
