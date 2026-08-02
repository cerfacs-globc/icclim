from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import ClassVar

import numpy as np
import pytest
import xarray as xr


def _load_tool_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_workload_uses_requested_chunks_for_chunk_sensitive_paths(
    monkeypatch,
) -> None:
    module = _load_tool_module(Path("tools/run_real_data_validation.py"))
    recorded_chunks: list[dict[str, int]] = []

    def fake_open_var(*_args, chunks, **_kwargs):
        recorded_chunks.append(chunks)
        time = xr.date_range("2000-01-01", periods=4, freq="D")
        return xr.DataArray(
            np.ones((4, 1, 1), dtype=np.float32),
            dims=("time", "lat", "lon"),
            coords={"time": time, "lat": [45.0], "lon": [2.0]},
            attrs={"units": "K"},
            name="tas",
        )

    monkeypatch.setattr(module, "_open_var", fake_open_var)

    class FakeIcclim:
        @staticmethod
        def build_threshold(*args, **kwargs):
            return {"args": args, **kwargs}

        @staticmethod
        def average(**_kwargs):
            return xr.Dataset({"average": xr.DataArray([1.0], dims=("time",))})

        @staticmethod
        def sum_of_spell_lengths(**_kwargs):
            return xr.Dataset(
                {"sum_of_spell_lengths": xr.DataArray([1.0], dims=("time",))}
            )

        @staticmethod
        def index(**_kwargs):
            return xr.Dataset({"CSDI": xr.DataArray([1.0], dims=("time",))})

    module._build_workload(
        FakeIcclim,
        "generic_tas_compound_percentile_or_average_yearly",
        chunks=module.ALT_CHUNKS,
    )
    module._build_workload(
        FakeIcclim,
        "generic_tas_spell_bootstrap_yearly",
        chunks=module.ALT_CHUNKS,
    )
    module._build_workload(
        FakeIcclim,
        "csdi_yearly",
        chunks=module.ALT_CHUNKS,
    )

    assert recorded_chunks == [
        module.ALT_CHUNKS,
        module.ALT_CHUNKS,
        module.ALT_CHUNKS,
    ]


@pytest.mark.parametrize(
    ("workload", "method_name"),
    [
        ("generic_tas_compound_percentile_or_count_yearly", "count_occurrences"),
        ("generic_tas_compound_percentile_or_sum_yearly", "sum"),
        ("generic_tas_compound_percentile_or_fraction_yearly", "fraction_of_total"),
        ("wsdi_yearly", "index"),
    ],
)
def test_build_workload_routes_new_workloads(
    monkeypatch,
    workload: str,
    method_name: str,
) -> None:
    module = _load_tool_module(Path("tools/run_real_data_validation.py"))
    called: dict[str, object] = {}

    def fake_open_var(*_args, chunks=module.DEFAULT_CHUNKS, **_kwargs):
        time = xr.date_range("2000-01-01", periods=4, freq="D")
        return xr.DataArray(
            np.ones((4, 1, 1), dtype=np.float32),
            dims=("time", "lat", "lon"),
            coords={"time": time, "lat": [45.0], "lon": [2.0]},
            attrs={"units": "K"},
            name="tas",
        )

    monkeypatch.setattr(module, "_open_var", fake_open_var)

    class FakeIcclim:
        @staticmethod
        def build_threshold(*args, **kwargs):
            return {"args": args, **kwargs}

        @staticmethod
        def count_occurrences(**kwargs):
            called["method"] = "count_occurrences"
            called["kwargs"] = kwargs
            return xr.Dataset(
                {"count_occurrences": xr.DataArray([1.0], dims=("time",))}
            )

        @staticmethod
        def sum(**kwargs):
            called["method"] = "sum"
            called["kwargs"] = kwargs
            return xr.Dataset({"sum": xr.DataArray([1.0], dims=("time",))})

        @staticmethod
        def fraction_of_total(**kwargs):
            called["method"] = "fraction_of_total"
            called["kwargs"] = kwargs
            return xr.Dataset(
                {"fraction_of_total": xr.DataArray([1.0], dims=("time",))}
            )

        @staticmethod
        def index(**kwargs):
            called["method"] = "index"
            called["kwargs"] = kwargs
            return xr.Dataset({"WSDI": xr.DataArray([1.0], dims=("time",))})

    module._build_workload(FakeIcclim, workload, chunks=module.DEFAULT_CHUNKS)

    assert called["method"] == method_name


def test_main_writes_chunk_profile_to_summary(monkeypatch, tmp_path: Path) -> None:
    module = _load_tool_module(Path("tools/run_real_data_validation.py"))
    output = xr.Dataset({"value": xr.DataArray([1.0], dims=("time",))})

    monkeypatch.setattr(module, "_warmup", lambda _icclim: None)
    monkeypatch.setattr(module, "_build_workload", lambda *_args, **_kwargs: output)
    monkeypatch.setattr(module, "_git_rev_parse", lambda *_args, **_kwargs: "deadbeef")
    monkeypatch.setattr(
        sys,
        "path",
        [str(tmp_path / "src"), *sys.path],
    )

    fake_icclim = SimpleNamespace(__version__="test-version")
    monkeypatch.setitem(sys.modules, "icclim", fake_icclim)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_real_data_validation.py",
            "--repo",
            str(tmp_path),
            "--workload",
            "generic_tas_spell_bootstrap_yearly",
            "--label",
            "current",
            "--chunk-profile",
            "alt",
            "--out-dir",
            str(tmp_path / "out"),
        ],
    )

    module.main()

    summary_path = (
        tmp_path / "out/current-generic_tas_spell_bootstrap_yearly.summary.json"
    )
    payload = json.loads(summary_path.read_text())
    assert payload["chunk_profile"] == "alt"


def test_main_defaults_to_default_chunk_profile(monkeypatch, tmp_path: Path) -> None:
    module = _load_tool_module(Path("tools/run_real_data_validation.py"))
    output = xr.Dataset({"value": xr.DataArray([1.0], dims=("time",))})
    observed: dict[str, object] = {}

    def fake_build_workload(*_args, **kwargs):
        observed["chunks"] = kwargs["chunks"]
        return output

    monkeypatch.setattr(module, "_warmup", lambda _icclim: None)
    monkeypatch.setattr(module, "_build_workload", fake_build_workload)
    monkeypatch.setattr(module, "_git_rev_parse", lambda *_args, **_kwargs: "deadbeef")
    monkeypatch.setitem(
        sys.modules, "icclim", SimpleNamespace(__version__="test-version")
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_real_data_validation.py",
            "--repo",
            str(tmp_path),
            "--workload",
            "wsdi_yearly",
            "--label",
            "default",
            "--out-dir",
            str(tmp_path / "out"),
        ],
    )

    module.main()

    assert observed["chunks"] == module.DEFAULT_CHUNKS


def test_git_rev_parse_reads_commit_from_subprocess(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_tool_module(Path("tools/run_real_data_validation.py"))
    monkeypatch.setattr(
        module.subprocess,
        "check_output",
        lambda *args, **kwargs: "0123456789abcdef0123456789abcdef01234567\n",
    )

    rev = module._git_rev_parse(tmp_path, "HEAD")

    assert rev == "0123456789abcdef0123456789abcdef01234567"


def test_open_var_and_combined_dataset_use_requested_chunks(monkeypatch) -> None:
    module = _load_tool_module(Path("tools/run_real_data_validation.py"))
    observed: dict[str, object] = {}

    monkeypatch.setattr(module.glob, "glob", lambda _pattern: ["a.nc", "b.nc"])

    def fake_open_mfdataset(files, combine, chunks):
        observed["files"] = files
        observed["combine"] = combine
        observed["chunks"] = chunks
        time = xr.date_range("2000-01-01", periods=2, freq="D")
        return xr.Dataset(
            {
                "tas": xr.DataArray(
                    np.ones((2, 1, 1), dtype=np.float32),
                    dims=("time", "lat", "lon"),
                    coords={"time": time, "lat": [45.0], "lon": [2.0]},
                ),
                "pr": xr.DataArray(
                    np.ones((2, 1, 1), dtype=np.float32),
                    dims=("time", "lat", "lon"),
                    coords={"time": time, "lat": [45.0], "lon": [2.0]},
                ),
            }
        )

    monkeypatch.setattr(module.xr, "open_mfdataset", fake_open_mfdataset)

    tas = module._open_var(module.TAS_GLOB, "tas", chunks=module.ALT_CHUNKS)
    combined = module._open_combined_dataset(chunks=module.ALT_CHUNKS)

    assert observed["combine"] == "by_coords"
    assert observed["chunks"] == module.ALT_CHUNKS
    assert tas.name == "tas"
    assert set(combined.data_vars) == {"tas", "pr"}


def test_warmup_swallows_validation_exceptions() -> None:
    module = _load_tool_module(Path("tools/run_real_data_validation.py"))
    msg = "expected test failure"

    class FakeIcclim:
        @staticmethod
        def index(**_kwargs):
            raise RuntimeError(msg)

    module._warmup(FakeIcclim)


def test_workload_notes_cover_new_chunk_matrix_workloads() -> None:
    module = _load_tool_module(Path("tools/summarize_real_data_validation.py"))

    assert "OR average" in module._workload_notes(
        "generic_tas_compound_percentile_or_average_yearly"
    )
    assert "OR sum" in module._workload_notes(
        "generic_tas_compound_percentile_or_sum_yearly"
    )
    assert module._workload_notes("csdi_yearly") == "standard cold-spell duration index"


def test_summarizer_parses_default_vs_alt_compare_filenames(tmp_path: Path) -> None:
    module = _load_tool_module(Path("tools/summarize_real_data_validation.py"))
    compare_path = tmp_path / "default-vs-alt-csdi_yearly.compare.json"
    compare_path.write_text(
        json.dumps(
            {
                "data_var_comparison": {
                    "CSDI": {
                        "equal": True,
                        "changed_cells": 0,
                        "max_abs_diff": 0.0,
                    }
                }
            }
        )
    )

    summary = module._parse_compare_file(compare_path)

    assert summary.current_label == "default"
    assert summary.baseline_label == "alt"
    assert summary.workload == "csdi_yearly"
    assert summary.all_data_vars_equal is True


def test_summarizer_builds_chunk_profile_table(tmp_path: Path) -> None:
    module = _load_tool_module(Path("tools/summarize_real_data_validation.py"))
    result_dir = tmp_path
    (result_dir / "default-csdi_yearly.summary.json").write_text(
        json.dumps(
            {
                "label": "default",
                "workload": "csdi_yearly",
                "duration_seconds": 10.0,
            }
        )
    )
    (result_dir / "alt-csdi_yearly.summary.json").write_text(
        json.dumps(
            {
                "label": "alt",
                "workload": "csdi_yearly",
                "duration_seconds": 25.0,
            }
        )
    )
    (result_dir / "default-vs-alt-csdi_yearly.compare.json").write_text(
        json.dumps(
            {
                "data_var_comparison": {
                    "CSDI": {
                        "equal": True,
                        "changed_cells": 0,
                        "max_abs_diff": 0.0,
                    }
                }
            }
        )
    )

    summary = module._build_summary_document(result_dir, ["csdi_yearly"])

    assert "## Chunk-profile invariance" in summary
    assert "| csdi_yearly | exact | 0 | 0.0 | 10.00 | 25.00 | +150.0%" in summary


def test_summarizer_historical_note_detects_known_difference() -> None:
    module = _load_tool_module(Path("tools/summarize_real_data_validation.py"))
    comparisons = {
        (
            "current",
            "master",
            "generic_tas_spell_bootstrap_yearly",
        ): module.ComparisonSummary(
            current_label="current",
            baseline_label="master",
            workload="generic_tas_spell_bootstrap_yearly",
            path=Path("a"),
            all_data_vars_equal=True,
            total_changed_cells=0,
            max_abs_diff=0.0,
        ),
        (
            "current",
            "v717",
            "generic_tas_spell_bootstrap_yearly",
        ): module.ComparisonSummary(
            current_label="current",
            baseline_label="v717",
            workload="generic_tas_spell_bootstrap_yearly",
            path=Path("b"),
            all_data_vars_equal=False,
            total_changed_cells=1,
            max_abs_diff=1.0,
        ),
        (
            "master",
            "v717",
            "generic_tas_spell_bootstrap_yearly",
        ): module.ComparisonSummary(
            current_label="master",
            baseline_label="v717",
            workload="generic_tas_spell_bootstrap_yearly",
            path=Path("c"),
            all_data_vars_equal=False,
            total_changed_cells=1,
            max_abs_diff=1.0,
        ),
    }

    note = module._historical_validation_note(
        "generic_tas_spell_bootstrap_yearly",
        comparisons,
    )

    assert note == "historical master/v7.1.7 difference confirmed"


def test_debug_real_data_validation_uses_default_chunks(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_tool_module(Path("tools/debug_real_data_validation.py"))
    observed: dict[str, object] = {}

    class FakeValidationModule:
        DEFAULT_CHUNKS: ClassVar[dict[str, int]] = {
            "time": 365,
            "lat": 24,
            "lon": 32,
        }

        @staticmethod
        def _warmup(_icclim) -> None:
            return None

        @staticmethod
        def _build_workload(_icclim, workload, *, chunks):
            observed["workload"] = workload
            observed["chunks"] = chunks
            return xr.Dataset({"value": xr.DataArray([1.0], dims=("time",))})

    monkeypatch.setattr(module, "_load_validation_module", lambda: FakeValidationModule)
    fake_icclim = SimpleNamespace(__version__="test-version")
    monkeypatch.setitem(sys.modules, "icclim", fake_icclim)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "debug_real_data_validation.py",
            "--repo",
            str(tmp_path),
            "--workload",
            "csdi_yearly",
        ],
    )

    module.main()

    assert observed["workload"] == "csdi_yearly"
    assert observed["chunks"] == FakeValidationModule.DEFAULT_CHUNKS


def test_load_validation_module_reads_neighbor_script() -> None:
    module = _load_tool_module(Path("tools/debug_real_data_validation.py"))

    loaded = module._load_validation_module()

    assert hasattr(loaded, "_build_workload")
    assert hasattr(loaded, "DEFAULT_CHUNKS")
