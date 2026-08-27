# Synthetic generation configuration

`config/synthetic_data.json` defines the reproducible inputs to the synthetic review generator. These values describe the intended generation process; some quantities can vary deterministically by generation when jitter is enabled.

## Configuration parameters

| Parameter | Methodological role |
|---|---|
| `seed` | Base seed from which deterministic generation-level random choices are derived. |
| `initial_train_rows` | Number of records created for the initial cumulative training corpus. The implementation requires a multiple of the sentiment × topic × linguistic-level strata. |
| `incoming_rows` | Central size of the unseen incoming batch. |
| `incoming_rows_jitter` | Allowed deterministic variation around the configured incoming size when `vary_counts=true`. Realized sizes remain compatible with the generator strata. |
| `profanity_fraction` | Target fraction of records generated under the profanity condition. |
| `profanity_fraction_jitter` | Deterministic generation-level variation around the configured profanity fraction. |
| `emoji_fraction` | Target fraction of generated records containing emoji. |
| `emoji_fraction_jitter` | Deterministic generation-level variation around the configured emoji fraction. |
| `spelling_error_fraction` | Target fraction of records generated with the spelling-error condition. |
| `slang_fraction` | Target fraction of records generated with controlled slang. |
| `mixed_sentiment_fraction` | Target fraction of records containing mixed-sentiment structure. |
| `goldtest_fraction` | Target fraction of incoming records marked for deterministic promotion at the next state transition. It does not represent human-reviewed ground truth. |
| `goldtest_fraction_jitter` | Deterministic variation around the configured promotion-marker fraction. |
| `validation_fraction` | Requested fraction of the training corpus used by the validation-split procedure. |
| `validation_fraction_jitter` | Deterministic generation-level variation around the requested validation fraction. |
| `vary_counts` | Enables deterministic generation-to-generation variation for quantities that have an associated jitter. |
| `synthetic_only` | Safety and provenance constraint requiring generated rather than externally sourced records. |
| `allow_personal_data` | Must remain `false`; the generator is designed to avoid personal-data ingestion. |

The current file also records generator identity/version and language. The implementation currently supports English.

## Linguistic-level distribution

`linguistic_level` is not a free probability vector in the current JSON configuration. The generator defines five levels — `limited`, `informal`, `standard`, `advanced`, and `technical` — and structures corpus sizes over the Cartesian strata formed by three sentiment classes, four topic classes, and five linguistic levels. This is why configured corpus sizes must be multiples of 60.

The realized incoming manifest records the actual counts by linguistic level. Documentation should therefore distinguish the structural generator design from a user-specified distribution parameter.

## Template families

Template families are also generator-defined rather than configured as a JSON probability vector. The current production generator materializes six structural families: `noticed`, `using`, `stood_out`, `context_component`, `main_impression`, and `attention`.

Each generated record stores its `template_family`. The persisted field is used by the validation procedure to prefer whole-family holdout and is also available for segmented evaluation. `input_manifest.json` records the realized counts by family.

## Configured, effective, and recorded values

The framework distinguishes three levels of generation information:

1. **Configuration parameters** are the stable values in `synthetic_data.json`, such as `incoming_rows=1800`, `emoji_fraction=0.18`, or `goldtest_fraction=0.20`.
2. **Effective generation parameters** are deterministic generation-specific values derived from the base seed, generation index, and configured jitter. Examples include the realized incoming size and the effective profanity, emoji, promotion, and validation fractions.
3. **Recorded metadata** describe what was actually materialized in the generated records, such as counts by linguistic level, emoji condition, profanity, text length, mixed sentiment, slang, spelling-error condition, promotion marker, and template family.

`data/input/input_manifest.json` records both the original configuration and the effective generation values, together with observed counts and file hashes. This separation makes the intended parameters, deterministic generation realization, and resulting dataset state independently auditable.

No configuration value should be changed merely to alter current evaluation results.