from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import dask.array as da
import pytest

from tools import benchmark_non_bootstrap, run_real_data_validation


def test_parse_selection_supports_all_and_rejects_unknown() -> None:
    assert benchmark_non_bootstrap._parse_selection("all", ("a", "b")) == (
        "a",
        "b",
    )
    assert benchmark_non_bootstrap._parse_selection("b,a", ("a", "b")) == (
        "b",
        "a",
    )
    with pytest.raises(ValueError, match="unknown"):
        benchmark_non_bootstrap._parse_selection("unknown", ("a", "b"))


def test_scheduler_recorder_counts_graphs() -> None:
    recorder = benchmark_non_bootstrap.SchedulerRecorder()
    with recorder:
        da.arange(12, chunks=3).sum().compute()

    assert len(recorder.graph_sizes) == 1
    assert recorder.graph_sizes[0] > 0


@pytest.mark.parametrize(
    "workload",
    [
        "generic_tas_sum_yearly",
        "generic_tas_rolling_sum_5day_yearly",
        "generic_tas_rolling_mean_5day_yearly",
        "generic_tas_max_date_event_monthly",
        "generic_tas_min_date_event_monthly",
        "generic_tas_consecutive_date_event_monthly",
        "generic_tas_reference_diff_daily",
        "generic_tas_reference_diff_monthly",
    ],
)
def test_real_data_runner_accepts_non_bootstrap_workloads(
    monkeypatch: pytest.MonkeyPatch,
    workload: str,
) -> None:
    class FakeIcclim:
        def __getattr__(self, name):
            return lambda **kwargs: {"operation": name, "kwargs": kwargs}

    monkeypatch.setattr(
        run_real_data_validation,
        "_open_var",
        lambda *args, **kwargs: object(),
    )

    result = run_real_data_validation._build_workload(
        FakeIcclim(),
        workload,
        chunks=run_real_data_validation.DEFAULT_CHUNKS,
    )

    assert "operation" in result


@pytest.mark.slow
def test_non_bootstrap_subprocess_memory_regression(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    output = tmp_path / "benchmark.json"
    completed = subprocess.run(  # noqa: S603
        [
            sys.executable,
            str(repo / "tools" / "benchmark_non_bootstrap.py"),
            "--repo",
            str(repo),
            "--out",
            str(output),
            "--workloads",
            "baseline_count",
            "--layouts",
            "single",
            "--chunk-modes",
            "user",
            "--years",
            "2",
            "--lat-size",
            "64",
            "--lon-size",
            "64",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output.read_text())
    result = payload["results"][0]
    assert result["status"] == "ok", result.get("traceback")
    assert result["task_count"] > 0
    assert result["scheduler_calls"] >= 1
    assert result["wall_seconds"] > 0
    assert result["peak_rss_bytes"] < 1024**3
