from __future__ import annotations

import csv
import json
import random
from pathlib import Path

import pytest

from lstm_for_the_win.agents.generation_core import (
    SyntheticDataAgent as ReferenceSyntheticDataAgent,
    SyntheticDataConfig,
    _alpha_code,
    _flags,
    _has_emoji,
    _length_class,
    _text_key,
    _validate_timestamp,
)


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_reference_generator_lifecycle_is_covered(tmp_path: Path) -> None:
    config = SyntheticDataConfig(
        initial_train_rows=1200,
        incoming_rows=1200,
        incoming_rows_jitter=0,
        profanity_fraction_jitter=0,
        goldtest_fraction_jitter=0,
        emoji_fraction_jitter=0,
        validation_fraction_jitter=0,
        vary_counts=False,
    )
    agent = ReferenceSyntheticDataAgent(config)
    manifest_path = agent.initialize(tmp_path, "2026-08-15T12:00:00+00:00")
    first = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert first["generation"] == 0
    assert first["record_counts"] == {"incoming.csv": 1200, "train.csv": 1200}
    assert len(_rows(tmp_path / "train.csv")) == 1200
    assert len(_rows(tmp_path / "incoming.csv")) == 1200

    with pytest.raises(FileExistsError):
        agent.initialize(tmp_path, "2026-08-15T12:00:00+00:00")

    second_path = agent.advance(tmp_path, "2026-08-16T12:00:00+00:00")
    second = json.loads(second_path.read_text(encoding="utf-8"))
    assert second["generation"] == 1
    assert second["record_counts"]["train.csv"] > 1200
    assert second["record_counts"]["incoming.csv"] == 1200


def test_reference_generator_requires_initialization(tmp_path: Path) -> None:
    agent = ReferenceSyntheticDataAgent(
        SyntheticDataConfig(initial_train_rows=1200, incoming_rows=1200, incoming_rows_jitter=0, vary_counts=False)
    )
    with pytest.raises(FileNotFoundError):
        agent.advance(tmp_path, "2026-08-16T12:00:00+00:00")


def test_config_validation_and_generation_helpers(tmp_path: Path) -> None:
    valid = SyntheticDataConfig(initial_train_rows=1200, incoming_rows=1200, incoming_rows_jitter=0, vary_counts=False)
    path = tmp_path / "config.json"
    path.write_text(json.dumps({key: getattr(valid, key) for key in valid.__dataclass_fields__}), encoding="utf-8")
    loaded = SyntheticDataConfig.from_json(path)
    assert loaded == valid
    assert loaded.effective_generation(2)["incoming_rows"] == 1200

    invalid = (
        {"language": "pt"},
        {"synthetic_only": False},
        {"allow_personal_data": True},
        {"initial_train_rows": 1001},
        {"incoming_rows": 1001},
        {"incoming_rows_jitter": -1},
        {"incoming_rows": 1200, "incoming_rows_jitter": 300},
        {"profanity_fraction": 0.0},
        {"emoji_fraction_jitter": -0.1},
    )
    for overrides in invalid:
        kwargs = {"initial_train_rows": 1200, "incoming_rows": 1200, "incoming_rows_jitter": 0, "vary_counts": False, **overrides}
        with pytest.raises(ValueError):
            SyntheticDataConfig(**kwargs).validate()

    assert _validate_timestamp("2026-08-15T12:00:00Z").endswith("Z")
    with pytest.raises(ValueError):
        _validate_timestamp("not-a-date")
    with pytest.raises(ValueError):
        _validate_timestamp("2026-08-15T12:00:00")

    rng = random.Random(42)
    flags = _flags(10, 0.3, rng)
    assert sum(flags) == 3
    assert _length_class("one two") == "short"
    assert _length_class(" ".join(["word"] * 20)) == "medium"
    assert _length_class(" ".join(["word"] * 40)) == "long"
    assert _has_emoji("review 🙂") is True
    assert _has_emoji("review") is False
    assert _alpha_code(1) == "a"
    assert _alpha_code(27) == "aa"
    assert _text_key("Hello,   WORLD!") == "hello world"
