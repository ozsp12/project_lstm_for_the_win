# Scientific software architecture

The package separates synthetic data generation, state management, model execution, benchmark evaluation, and artifact production. The separation is methodological: each layer has a defined input and output contract so that changes in one stage do not silently redefine another.

## 1. Synthetic data generation

`agents/generation_core.py` defines the synthetic review configuration, controlled vocabularies, deterministic helpers, label spaces, linguistic strata, and the shared generator implementation. `agents/improved_synthetic_data.py` is the production synthetic review generator. `agents/synthetic_data.py` is retained as a compatibility surface for historical imports; the class name `SyntheticDataAgent` remains part of the code API, while the conceptual component is a deterministic synthetic review generator.

Inputs are `SyntheticDataConfig`, a generation index, and an input timestamp. Outputs are synthetic training or incoming records plus metadata describing linguistic level, profanity, emoji use, spelling-error condition, slang, text length, mixed sentiment, and template family. Generation-level quantities that use jitter are deterministic functions of the configured seed and generation index.

## 2. Data-state management

`handler.py` provides the boundary between model execution and persistent input-state transitions. Initialization creates generation zero. Advancement promotes the subset of the previous incoming batch marked by `goldtest=1`, appends those records to the cumulative training corpus, and generates the next incoming batch.

`goldtest` is a deterministic promotion marker. It does not represent human annotation, independent review, or externally sourced ground truth. Model execution itself does not advance the data state.

`template_metadata.py` materializes or validates persisted template-family metadata used by grouped validation and segmented evaluation.

## 3. Classification

The `classification/` package loads and validates records, constructs validation splits, trains the LSTM, evaluates the incoming batch, and computes classification and calibration metrics.

The validation procedure prefers holding out one complete persisted `template_family` when that holdout preserves all task labels and sufficient fit examples. If no valid grouped holdout exists, it uses a deterministic label-stratified random fallback.

The current LSTM path is:

```text
raw text
  → TextVectorization(max_tokens=20,000, output_sequence_length=96)
  → Embedding(output_dim=48, mask_zero=True)
  → LSTM(48 units)
  → Dropout(0.20)
  → Dense(32, ReLU)
  → Softmax(class_count)
```

The model uses Adam optimization with sparse categorical cross-entropy. Current defaults are batch size 32, up to 20 epochs, and early stopping on validation loss with patience 3 and best-weight restoration. The same architecture is instantiated separately for sentiment and topic classification.

## 4. Baseline

`classification/baseline.py` implements the comparison model:

```text
raw text
  → TF-IDF unigrams and bigrams
  → logistic regression
  → class probabilities
```

The TF-IDF representation uses `ngram_range=(1, 2)`, `min_df=1`, at most 20,000 features, and sublinear term frequency. Logistic regression uses the `lbfgs` solver, `max_iter=500`, and the current model seed as `random_state`.

The baseline is fitted on the same fit split and evaluated on the same incoming records as the LSTM, allowing paired comparison.

## 5. Benchmark evaluation

`benchmark.py` manages the frozen synthetic benchmark. The benchmark is created once from non-promoted incoming records, remains disjoint from the training corpus, and is protected by a provenance manifest and SHA-256 hash. It is evaluated for both implemented classification tasks.

The frozen benchmark provides a stable synthetic reference while the cumulative train/incoming state can change.

## 6. External validation

`external_benchmark.py` manages the immutable Amazon subset of the UCI *Sentiment Labelled Sentences* dataset. It validates provenance, license, row count, label space, and SHA-256 integrity before use.

The external source provides only binary sentiment labels. It therefore supports sentiment evaluation but not product-topic evaluation. The run artifact records both the native three-class model evaluation and the binary-restricted probability evaluation compatible with the external source label space.

## 7. Experiment orchestration

`experiment.py` coordinates one frozen-state execution. It validates input schemas, materializes required metadata, prepares the frozen synthetic benchmark and external benchmark, trains each task, evaluates replicate seeds when requested, constructs the run document, materializes deterministic derived artifacts, and publishes the completed run atomically.

Inputs include the frozen `data/input/` state, run parameters, model seed(s), split seed, and output location. Outputs are one validated run directory and an updated `latest.json` pointer. The orchestration layer does not perform the subsequent data-state transition.

## 8. Canonical artifact generation

`run_artifact.py` builds `run.json`. This document combines provenance, environment metadata, task results, primary-seed predictions, across-seed summaries, uncertainty information, paired classifier comparisons, synthetic benchmark evaluation, and external validation.

Implemented metrics include accuracy, macro precision, macro recall, macro F1, weighted F1, log loss, Brier score, Expected Calibration Error, reliability bins, and confusion matrices. Segmented accuracy includes Wilson 95% confidence intervals. LSTM and baseline predictions are compared using the exact two-sided McNemar test. When multiple model seeds are supplied, comparable metrics are summarized across seeds and Student-t intervals are recorded for the seed-level means.

Segmented evaluation is available for linguistic level, profanity, emoji use, spelling errors, slang, text length, mixed sentiment, `goldtest`, and template family. These outputs describe the framework's available analytical dimensions and do not imply a scientific interpretation of current subgroup results.

## 9. Derived analytical artifacts

`derived_artifacts.py` reads `run.json` and materializes `article_analysis.csv` and the SVG files under `figures/`. These files are deterministic representations of the canonical run document. They must not be edited or treated as independent analytical sources.

The implemented dependency flow is therefore:

```text
synthetic configuration
  → controlled input state
  → validation split
  → LSTM + baseline
  → synthetic benchmark + external validation
  → evaluation and statistical summaries
  → run.json
  → deterministic tabular and visual derivatives
```

Model execution and data-state advancement remain separate operations.