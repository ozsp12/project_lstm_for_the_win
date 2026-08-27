# Data architecture

The `data/` directory separates controlled synthetic input state, independently sourced evaluation data, and validated run artifacts. The intended scientific flow is:

```text
input state → model execution → canonical artifact → deterministic derived artifacts
```

This separation prevents evaluation sources and derived files from silently entering the training state.

## `data/input/`

This directory contains the controlled synthetic state used by the framework.

`train.csv` is the cumulative training corpus. It can grow between generations when a deterministic subset of the previous incoming batch is promoted. `incoming.csv` is the current batch of observations that has not been incorporated into the current training state; it is used to evaluate the model trained from the frozen current corpus.

`benchmark.csv` is a frozen synthetic benchmark. It is initialized from non-promoted incoming records, remains disjoint from the training corpus, and must never be promoted into training. Its purpose is to provide a stable longitudinal reference while the train/incoming state can evolve.

`input_manifest.json` records the synthetic configuration, generation number, realized generation parameters, record counts, distribution summaries, and SHA-256 hashes of the current input files. `benchmark_manifest.json` records the benchmark origin, source generation, row count, generator version, immutable status, and hash.

The conceptual schemas and analytical metadata are documented in [`input/README.md`](input/README.md).

## `data/external/`

This directory contains benchmarks obtained from external sources. External data do not participate in synthetic generation, deterministic promotion, or model training.

The current external benchmark is the Amazon subset of the UCI *Sentiment Labelled Sentences* dataset. It provides 1,000 binary sentiment observations and is treated as immutable evaluation data. Provenance, label-space differences, DOI, license, and integrity rules are documented in [`external/README.md`](external/README.md).

## `data/output/`

This directory contains artifacts produced by a validated execution. Each run directory is centered on `run.json`, the canonical representation of the input provenance, task results, benchmark evaluations, uncertainty information, predictions, and runtime metadata.

`article_analysis.csv` and the files in `figures/` are generated deterministically from `run.json`. They provide tabular and visual representations for inspection and downstream use; they are not independent analytical sources.

Among generated run artifacts, the retention policy keeps only the latest fully validated run directory. `latest.json` points to that directory. `README.md` is static documentation and is not part of run retention. See [`output/README.md`](output/README.md) for the full contract.