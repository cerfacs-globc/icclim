from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import ClassVar

import numpy as np
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
