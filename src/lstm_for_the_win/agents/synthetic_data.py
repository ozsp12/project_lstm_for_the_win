"""Stable compatibility surface for synthetic-generation primitives.

The production generator lives in :mod:`improved_synthetic_data`. Shared
configuration, vocabularies, deterministic helpers and the legacy reference
agent live in :mod:`generation_core`. This module preserves the historical
import path without keeping a second implementation here.
"""

from .generation_core import (
    ASSESSMENTS,
    CONTEXTS,
    DETAILS,
    EMOJIS,
    FOLLOWUPS,
    LENGTH_CLASSES,
    LINGUISTIC_LEVELS,
    PROFANITY_CLAUSES,
    SENTIMENTS,
    SLANG_OPENERS,
    SLANG_TAILS,
    STYLE_FIELDS,
    TECHNICAL_OPENERS,
    TOPICS,
    TOPIC_LANGUAGE,
    SyntheticDataAgent,
    SyntheticDataConfig,
    _alpha_code,
    _flags,
    _has_emoji,
    _length_class,
    _read_csv,
    _text_key,
    _validate_timestamp,
    _write_csv,
)

__all__ = ["SyntheticDataAgent", "SyntheticDataConfig"]
