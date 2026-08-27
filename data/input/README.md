# Synthetic input state

`data/input/` contains the synthetic state used for training, current-state evaluation, and the frozen synthetic benchmark. The generator produces controlled review text together with metadata that can be used for stratified evaluation.

`train.csv` stores training labels as `sentiment` and `topic`. `incoming.csv` and `benchmark.csv` store the corresponding evaluation labels as `expected_sentiment` and `expected_topic`. The underlying label spaces are the same: sentiment uses `negative`, `neutral`, and `positive`; topic uses `smartphone`, `television`, `refrigerator`, and `washing_machine`.

## Conceptual schema

| Variable | Methodological meaning |
|---|---|
| `ID` | Unique monotonically increasing record identifier used to preserve row-level traceability across data states and predictions. |
| `text` | Synthetic product-review text used as the classifier input. Text is generated from controlled lexical and structural components. |
| `sentiment` / `expected_sentiment` | Target sentiment class. The `expected_` name indicates that the record belongs to an evaluation dataset rather than the current training corpus. |
| `topic` / `expected_topic` | Target product category. The `expected_` name has the same evaluation-state meaning as for sentiment. |
| `linguistic_level` | Controlled linguistic stratum: `limited`, `informal`, `standard`, `advanced`, or `technical`. It supports evaluation of performance across different language profiles. |
| `flagprofanity` | Binary indicator that the generated review includes the controlled profanity condition. It supports subgroup evaluation and does not encode sentiment. |
| `hasemoji` | Binary indicator for the controlled presence of emoji in the generated text. |
| `hasspellingerror` | Binary indicator for an intentionally introduced spelling-error condition. |
| `hasslang` | Binary indicator for controlled slang usage. |
| `length_class` | Coarse text-length category: `short`, `medium`, or `long`. It supports performance analysis by review length. |
| `mixed_sentiment` | Binary indicator that the generated review contains mixed-sentiment structure rather than a single uniformly expressed polarity. |
| `goldtest` | Deterministic selection marker used on incoming records to define the subset eligible for promotion at the next data-state transition. It is not human annotation, independent validation, or externally produced ground truth. |
| `template_family` | Persisted structural family of the generated sentence pattern. Current families are `noticed`, `using`, `stood_out`, `context_component`, `main_impression`, and `attention`. The field supports grouped validation and segmented analysis. |
| `input_timestamp` | Timezone-aware timestamp associated with the creation of the input state, used for provenance and traceability. |

Training records additionally contain `source`, which distinguishes initial records from records promoted from an earlier incoming batch, and `training_generation`, which records the generation in which a record entered the cumulative training corpus.

## Dataset roles

### `train.csv`

The training corpus is cumulative. Model fitting uses this file after an internal validation split is created. Training and incoming records must have disjoint IDs and text. When the controlled data state advances, selected incoming records may be added to this corpus.

### `incoming.csv`

The incoming dataset is the current unseen batch for the frozen model state. It is evaluated before any of its records are promoted. Segmented metrics can be computed over the metadata fields above.

### `benchmark.csv`

The benchmark is a frozen synthetic evaluation set created from non-promoted incoming records. It remains disjoint from `train.csv` and is never included in the promotion mechanism. Its stable composition provides a fixed reference while the train/incoming state may evolve.

## Manifests

`input_manifest.json` records the configured generation parameters, generation index, realized or effective generation parameters, row counts, metadata distributions, last issued ID, promotion count, and SHA-256 hashes for `train.csv` and `incoming.csv`.

`benchmark_manifest.json` records the frozen benchmark's source generation, generator version, number of rows, immutable status, schema version, and SHA-256 hash. These manifests are integrity and provenance records; they are not model inputs.