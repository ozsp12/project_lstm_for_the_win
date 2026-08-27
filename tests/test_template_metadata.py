from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from lstm_for_the_win.template_metadata import (
    TEMPLATE_FAMILIES,
    _materialize,
    ensure_template_metadata,
    infer_template_family,
)


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_template_family_inference_covers_all_patterns() -> None:
    cases = {
        "I noticed that the battery works well": "noticed",
        "I have been using this phone for a week": "using",
        "The battery is what stood out to me": "stood_out",
        "My main impression of this phone is positive": "main_impression",
        "I did not pay much attention to the camera": "attention",
        "During normal use, the screen works": "context_component",
    }
    assert {infer_template_family(text) for text in cases} == set(TEMPLATE_FAMILIES)
    for text, expected in cases.items():
        assert infer_template_family(text) == expected


def test_template_metadata_is_materialized_once_and_manifest_refreshed(tmp_path: Path) -> None:
    train = [
        {
            "ID": "1", "text": "I noticed that the battery works well", "sentiment": "positive",
        },
        {
            "ID": "2", "text": "My main impression of this phone is average", "sentiment": "neutral",
        },
    ]
    incoming = [
        {
            "ID": "3", "text": "I have been using this phone for a week", "expected_sentiment": "positive",
        },
        {
            "ID": "4", "text": "During normal use, the screen works", "expected_sentiment": "neutral",
        },
    ]
    _write(tmp_path / "train.csv", train)
    _write(tmp_path / "incoming.csv", incoming)
    (tmp_path / "input_manifest.json").write_text(json.dumps({"generation": 0}), encoding="utf-8")

    changed = ensure_template_metadata(tmp_path)
    assert changed == {"train.csv": True, "incoming.csv": True}
    manifest = json.loads((tmp_path / "input_manifest.json").read_text(encoding="utf-8"))
    assert manifest["template_family_metadata"]["materialized"] is True
    assert manifest["record_counts"] == {"incoming.csv": 2, "train.csv": 2}
    assert manifest["incoming_template_family_counts"] == {"context_component": 1, "using": 1}
    assert set(manifest["sha256"]) == {"incoming.csv", "train.csv"}

    assert ensure_template_metadata(tmp_path) == {"train.csv": False, "incoming.csv": False}


def test_materialize_rejects_invalid_explicit_family(tmp_path: Path) -> None:
    path = tmp_path / "train.csv"
    _write(path, [{"ID": "1", "text": "text", "template_family": "unsupported"}])
    with pytest.raises(ValueError):
        _materialize(path)


def test_materialize_rejects_headerless_file(tmp_path: Path) -> None:
    path = tmp_path / "train.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        _materialize(path)
