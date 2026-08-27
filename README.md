# LSTM for the Win

Reproducible framework for controlled product-review classification with Long Short-Term Memory (LSTM) models.

**Project page:** https://ozsp12.github.io/en/projects/lstm_ftw/

## Project overview

This project studies two supervised text-classification problems on product reviews: sentiment classification and product-topic classification. The framework combines a deterministic synthetic review generator, a cumulative training corpus, an unseen incoming batch, leakage-aware validation, an LSTM classifier, a TF-IDF logistic-regression baseline, a frozen synthetic benchmark, an external real-world sentiment benchmark, statistical evaluation, and a canonical run artifact.

Synthetic data are used to control linguistic properties such as writing level, profanity, emoji use, spelling errors, slang, text length, mixed sentiment, and template family. The data state can evolve through an explicit deterministic promotion mechanism, but this mechanism should be understood as controlled state evolution rather than as empirical evidence of continual-learning performance.

Reproducibility is enforced through frozen input state during model execution, recorded seeds, deterministic TensorFlow operations, immutable benchmarks, hashes and manifests, environment metadata, hash-locked dependencies, and deterministic regeneration of analytical artifacts.

## Scientific objective

The framework is designed to support reproducible comparison of classifiers under controlled linguistic variation and controlled changes in the input distribution. It separates data generation, model fitting, benchmark evaluation, statistical comparison, artifact creation, and data-state transition so that each stage can be inspected independently.

## Classification tasks

The sentiment task uses the labels `negative`, `neutral`, and `positive`. The topic task uses `smartphone`, `television`, `refrigerator`, and `washing_machine`. Both tasks are trained from the same review corpus but use task-specific target labels.

## Conceptual architecture

```text
Configuration
    ↓
Synthetic Review Generator
    ↓
Train / Incoming / Frozen Benchmark
    ↓
Validation Split
    ↓
LSTM and TF-IDF Logistic Regression
    ↓
Evaluation
    ↓
External Validation
    ↓
run.json
    ↓
Deterministic Derived Analytical Artifacts
```

The data-state transition is separate from model execution:

```text
incoming
    ↓
deterministic promotion subset
    ↓
cumulative train
    ↓
next incoming generation
```

`goldtest` is the deterministic marker used to select records for promotion. It is not a human annotation, independent review, or externally produced ground truth.

## Data lifecycle

`data/input/train.csv` is the cumulative training corpus. `data/input/incoming.csv` is the current unseen batch evaluated by the current model state. `data/input/benchmark.csv` is a frozen synthetic benchmark that remains outside training. External benchmark data are stored separately under `data/external/`.

Model execution uses a frozen committed input state. Data advancement is an explicit operation performed after the evaluated state is complete. Detailed data contracts are documented in [`data/README.md`](data/README.md) and [`data/input/README.md`](data/input/README.md).

## Models

The neural classifier follows:

```text
raw text → TextVectorization → Embedding → LSTM → Dropout → Dense/ReLU → Softmax
```

The comparison baseline follows:

```text
raw text → TF-IDF unigrams/bigrams → logistic regression → class probabilities
```

Exact model and baseline parameters are documented in [`src/lstm_for_the_win/README.md`](src/lstm_for_the_win/README.md).

## Evaluation framework

The implemented evaluation includes accuracy, macro precision, macro recall, macro F1, weighted F1, log loss, Brier score, Expected Calibration Error, reliability bins, confusion matrices, Wilson confidence intervals for segmented accuracy, and exact two-sided McNemar comparison between paired LSTM and baseline predictions. Production runs can aggregate comparable metrics across multiple model seeds.

Segmented evaluation can use linguistic level, profanity, emoji use, spelling errors, slang, text length, mixed sentiment, `goldtest`, and template family. These facilities define the analysis framework; the documentation does not assign scientific interpretation to current subgroup results.

## Data and artifact organization

```text
data/input/     controlled synthetic input state and frozen synthetic benchmark
data/external/  immutable independently sourced benchmark data
data/output/    latest validated run and deterministic derivatives
```

`run.json` is the canonical source of truth for a run. `article_analysis.csv` and files under `figures/` are deterministic representations derived from that JSON and must not become independent sources of truth.

## Reproducibility

The runtime uses Python 3.12 and TensorFlow 2.20. Dependencies are installed from a hash-locked environment. TensorFlow operation determinism and process seeds are enforced, model and split seeds are recorded, benchmark integrity is checked with hashes, and the canonical artifact records software and platform metadata. Coverage measurement includes statements and branches with an overall gate of at least 90%.

## Repository structure

Implementation details are distributed across the local documentation:

- [`config/README.md`](config/README.md): synthetic-generation configuration and effective parameters;
- [`data/README.md`](data/README.md): data roles and artifact contracts;
- [`src/lstm_for_the_win/README.md`](src/lstm_for_the_win/README.md): scientific software architecture.

## Installation and execution

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-lock.txt
python -m pip install -e . --no-deps --no-build-isolation
python -m pip check
lstm-pipeline train --run-id local --epochs 20 --replicate-seeds "42,1337,2026"
```

Synthetic input generation and controlled state advancement are exposed through the same `lstm-pipeline` command-line interface. Configuration details are documented under `config/`.

## Licensing and citation

Repository software is licensed under the MIT License. External dataset licensing and attribution are documented in `DATA_LICENSES.md`. Citation metadata are provided in `CITATION.cff`.