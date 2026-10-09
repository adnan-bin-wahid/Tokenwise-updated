# One TokenWise Demonstration Project

Open **[tokenwise_demo](tokenwise_demo/README.md)** itself in Antigravity. Keep
this same workspace open for the entire presentation. Do not open the TokenWise
checkout or the `demonstration` parent as the retrieval workspace.

The complete, ordered teacher script is **[demonstation.md](../demonstation.md)**.
The 0.6.5 extension also opens it with **TokenWise: Open Demonstration Guide**.

For the teacher's validation and comparison request, follow the current-source
[validation protocol](../validation.md): real native with/without runs, fixed
tasks, predefined answer rubrics and a blank results worksheet. That guide and
these comparison additions are included in 0.6.7, not the existing 0.6.6 assets.

The application contains account lockout, sessions, invoices, shipping, and
activity reports. All features work; unrelated features serve as pruning controls,
not filler. Eleven Python files and twenty deterministic tests provide the
ground truth for the three teacher scenarios:

1. Repository discovery with no selected file.
2. Neural pruning of an entire file or an exact highlighted excerpt.
3. Earlier same-topic user intent resolving a referring follow-up.

The same folder also demonstrates project overviews, thresholds, budgeted context,
copy/export controls, token accounting, approximate carbon estimates, topic
exclusions, indexing/cache freshness, and optional all-code/selected/automatic
packet comparisons. No second application or `baseline_lab` is necessary.

From the TokenWise checkout or extracted bundle root:

```powershell
py -3.12 demonstration/run_checks.py
```

From the open `tokenwise_demo` folder:

```powershell
py -3.12 app.py
py -3.12 -m unittest discover -s tests -v
```

The demo app needs no pip packages, server, account, clock mocking, or network.
The extension backend is a separate installation and does require its pretrained
model and dependencies. Check [verification notes](VERIFICATION.md) and use the
[blank evidence worksheet](results-template.md) for actual presentation results.

Get the project, validation protocol, prompt-engineering rehearsal, and study from the [0.6.7 release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.7).
The already-published 0.6.4 ZIP
contains the previous four-project layout; it has not been silently replaced.
Generated exports under `results/`, `.agents`, `.tokenwise`, and Python caches
are not demonstration source and must not be shipped as classroom evidence.
