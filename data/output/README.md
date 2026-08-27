# Validated run artifacts

`data/output/` stores the artifacts of the latest fully validated model execution. The directory is organized around a single canonical run document and deterministic representations derived from it.

```text
data/output/
├── README.md
├── latest.json
└── <timestamp>_github-<workflow_run_id>/
    ├── run.json
    ├── article_analysis.csv
    └── figures/
```

## Canonical artifact

`run.json` is the source of truth for an execution. It records run provenance, input-state hashes and generation, software and environment metadata, deterministic settings, task configuration, model and baseline metrics, statistical comparisons, segmented evaluations, benchmark results, external validation, and row-level prediction information.

Any downstream interpretation of a run should be traceable back to this JSON document.

## Derived analytical artifacts

`article_analysis.csv` is a tabular representation generated from `run.json`. It exists to make run information easier to inspect and consume in table-oriented tools. It does not perform an independent analysis and must not diverge from the canonical JSON.

Files under `figures/` are also generated deterministically from `run.json`. The validation workflow removes these derived files, regenerates them from the canonical artifact, and verifies that their hashes are unchanged.

**Derived artifacts must never become independent sources of truth.** Changes to a derived file must be reproducible from the corresponding canonical `run.json`; derived files must not be manually edited to redefine run results.

## `latest.json`

`latest.json` contains the identifier of the current validated run directory. It is a pointer, not an analytical artifact.

## Retention policy

Among generated executions, only the latest fully validated run directory is retained. A previous run is removed only after its replacement has passed the implemented contract, deterministic-artifact, test, and coverage validations. `README.md` is static documentation and `latest.json` is the stable pointer to the retained run.