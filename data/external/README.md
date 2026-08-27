# External evaluation data

`data/external/` contains independently sourced benchmarks used only for out-of-source evaluation. These data are outside the synthetic generation process, outside the deterministic promotion mechanism, and outside model training.

## Current benchmark

The current source is the Amazon subset of the UCI *Sentiment Labelled Sentences* dataset.

| Property | Value |
|---|---|
| Dataset | Sentiment Labelled Sentences |
| Source subset | Amazon cell-phone review sentences |
| DOI | `10.24432/C57604` |
| License | CC BY 4.0 |
| Observations | 1,000 |
| Available task | Sentiment classification |
| Source labels | `negative`, `positive` |
| Stored file | `uci_sentiment_labelled_sentences/amazon_cells_labelled.tsv` |

The model sentiment space contains `negative`, `neutral`, and `positive`, whereas this external source is binary. The framework therefore records both the native three-class model evaluation against the available labels and a source-compatible binary-restricted evaluation obtained by restricting and renormalizing model probabilities to `negative` and `positive`. The source has no compatible product-topic labels, so it is not used for topic evaluation.

## Immutability and provenance

The benchmark is treated as immutable because it provides an evaluation source independent of the synthetic generator and changing train/incoming state. `uci_sentiment_labelled_sentences/manifest.json` records the DOI, source URL, source archive member, license, task, label space, row count, immutable status, and SHA-256 hash. The loader validates the stored data against this manifest before use.

External data must never be promoted into `data/input/train.csv` or used to construct synthetic generations.