from __future__ import annotations

import json
from pathlib import Path

import pytest

import lstm_for_the_win.cli as cli
import lstm_for_the_win.experiment as experiment
import lstm_for_the_win.handler as handler
from lstm_for_the_win.benchmark import MIN_BENCHMARK_ROWS, _validate as validate_benchmark


def _valid_schema_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    train = [{
        "ID": "1",
        "text": "train review",
        "sentiment": "positive",
        "topic": "smartphone",
        "linguistic_level": "standard",
        "flagprofanity": "0",
        "source": "initial",
        "training_generation": "0",
        "input_timestamp": "2026-08-27T00:00:00+00:00",
    }]
    incoming = [{
        "ID": "2",
        "text": "incoming review",
        "expected_sentiment": "negative",
        "expected_topic": "television",
        "linguistic_level": "informal",
        "flagprofanity": "0",
        "goldtest": "0",
        "input_timestamp": "2026-08-27T00:00:00+00:00",
    }]
    return train, incoming


def test_experiment_schema_validation_branches() -> None:
    train, incoming = _valid_schema_rows()
    experiment.validate_input_schema(train, incoming)

    with pytest.raises(ValueError, match="train.csv"):
        experiment.validate_input_schema([], incoming)
    with pytest.raises(ValueError, match="incoming.csv"):
        experiment.validate_input_schema(train, [])

    partial_train = [{**train[0], "hasemoji": "0"}]
    with pytest.raises(ValueError, match="partial metadata"):
        experiment.validate_input_schema(partial_train, incoming)

    partial_incoming = [{**incoming[0], "hasemoji": "0"}]
    with pytest.raises(ValueError, match="partial metadata"):
        experiment.validate_input_schema(train, partial_incoming)

    overlapping_id = [{**incoming[0], "ID": "1"}]
    with pytest.raises(ValueError, match="disjoint IDs"):
        experiment.validate_input_schema(train, overlapping_id)

    overlapping_text = [{**incoming[0], "text": "train review"}]
    with pytest.raises(ValueError, match="disjoint text"):
        experiment.validate_input_schema(train, overlapping_text)


def test_experiment_file_seed_and_previous_run_branches(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        experiment.read_csv(tmp_path / "missing.csv")

    assert experiment.previous_run_id(tmp_path) is None
    latest = tmp_path / "latest.json"
    latest.write_text("{broken", encoding="utf-8")
    assert experiment.previous_run_id(tmp_path) is None
    latest.write_text(json.dumps({"run_id": 123}), encoding="utf-8")
    assert experiment.previous_run_id(tmp_path) is None
    latest.write_text(json.dumps({"run_id": "bad run"}), encoding="utf-8")
    assert experiment.previous_run_id(tmp_path) is None
    latest.write_text(json.dumps({"run_id": "valid-run_1"}), encoding="utf-8")
    assert experiment.previous_run_id(tmp_path) == "valid-run_1"

    assert experiment.parse_replicate_seeds(None, 42) == [42]
    assert experiment.parse_replicate_seeds("43,,42,43", 42) == [42, 43]
    assert experiment.parse_replicate_seeds([44, 45], 42) == [42, 44, 45]
    with pytest.raises(ValueError, match="non-negative"):
        experiment.parse_replicate_seeds([-1], 42)


def test_experiment_runtime_metadata_and_early_failures(tmp_path: Path) -> None:
    metadata = experiment.environment_versions()
    assert metadata["operating_system"]
    assert metadata["machine"]
    assert metadata["python_implementation"]
    assert metadata["runner_os"]
    assert metadata["runner_arch"]

    runner = experiment.ExperimentRunner()
    with pytest.raises(ValueError, match="run_id"):
        runner.train_and_publish(tmp_path / "input", tmp_path / "output", run_id="bad run")
    with pytest.raises(ValueError, match="epochs"):
        runner.train_and_publish(tmp_path / "input", tmp_path / "output", run_id="ok", epochs=0)
    with pytest.raises(ValueError, match="patience"):
        runner.train_and_publish(tmp_path / "input", tmp_path / "output", run_id="ok", patience=-1)

    existing_root = tmp_path / "existing-output"
    (existing_root / "already-there").mkdir(parents=True)
    with pytest.raises(FileExistsError):
        runner.train_and_publish(tmp_path / "input", existing_root, run_id="already-there")


def test_handler_generation_modes_and_delegation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[tuple[object, ...]] = []

    class FakeConfig:
        @classmethod
        def from_json(cls, path: str | Path) -> str:
            calls.append(("config", Path(path)))
            return "config"

    class FakeAgent:
        def __init__(self, config: str) -> None:
            calls.append(("agent", config))

        def initialize(self, input_dir: str | Path, timestamp: str, *, overwrite: bool) -> Path:
            calls.append(("initialize", Path(input_dir), timestamp, overwrite))
            return Path(input_dir) / "input_manifest.json"

        def advance(self, input_dir: str | Path, timestamp: str) -> Path:
            calls.append(("advance", Path(input_dir), timestamp))
            return Path(input_dir) / "input_manifest.json"

    monkeypatch.setattr(handler, "SyntheticDataConfig", FakeConfig)
    monkeypatch.setattr(handler, "SyntheticDataAgent", FakeAgent)
    monkeypatch.setattr(handler, "default_timestamp", lambda: "default-ts")
    monkeypatch.setattr(handler, "ensure_template_metadata", lambda path: calls.append(("metadata", Path(path))))

    pipeline_handler = handler.PipelineHandler()
    manifest = pipeline_handler.generate_inputs("config.json", tmp_path, mode="initialize", overwrite=True)
    assert manifest == tmp_path / "input_manifest.json"
    assert ("initialize", tmp_path, "default-ts", True) in calls

    manifest = pipeline_handler.generate_inputs(
        "config.json", tmp_path, mode="advance", input_timestamp="explicit-ts"
    )
    assert manifest == tmp_path / "input_manifest.json"
    assert ("advance", tmp_path, "explicit-ts") in calls

    with pytest.raises(ValueError, match="overwrite"):
        pipeline_handler.generate_inputs("config.json", tmp_path, mode="advance", overwrite=True)
    with pytest.raises(ValueError, match="mode must"):
        pipeline_handler.generate_inputs("config.json", tmp_path, mode="invalid")

    class FakeRunner:
        def train_and_publish(self, *args: object, **kwargs: object) -> Path:
            calls.append(("train", args, kwargs))
            return tmp_path / "published"

    delegated = handler.PipelineHandler(runner=FakeRunner()).train_and_publish(
        "input", "output", run_id="run", epochs=2, replicate_seeds=[42, 43]
    )
    assert delegated == tmp_path / "published"
    assert any(call[0] == "train" for call in calls)

    monkeypatch.setattr(cli, "main", lambda argv=None: 7)
    assert handler.main(["--help"]) == 7


def _benchmark_rows() -> list[dict[str, str]]:
    return [
        {"ID": str(index), "text": f"benchmark-{index}", "goldtest": "0"}
        for index in range(1, MIN_BENCHMARK_ROWS + 1)
    ]


def test_benchmark_validation_branches() -> None:
    rows = _benchmark_rows()
    validate_benchmark(rows, [])

    with pytest.raises(ValueError, match="at least"):
        validate_benchmark(rows[:-1], [])

    duplicate_id = [dict(row) for row in rows]
    duplicate_id[1]["ID"] = duplicate_id[0]["ID"]
    with pytest.raises(ValueError, match="unique"):
        validate_benchmark(duplicate_id, [])

    duplicate_text = [dict(row) for row in rows]
    duplicate_text[1]["text"] = duplicate_text[0]["text"]
    with pytest.raises(ValueError, match="unique"):
        validate_benchmark(duplicate_text, [])

    promotable = [dict(row) for row in rows]
    promotable[0]["goldtest"] = "1"
    with pytest.raises(ValueError, match="never promoted"):
        validate_benchmark(promotable, [])

    with pytest.raises(ValueError, match="disjoint"):
        validate_benchmark(rows, [{"ID": rows[0]["ID"], "text": "different"}])
    with pytest.raises(ValueError, match="disjoint"):
        validate_benchmark(rows, [{"ID": "different", "text": rows[0]["text"]}])
