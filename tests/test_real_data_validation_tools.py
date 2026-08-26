from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType

import pytest
import xarray as xr

from tools import (
    profile_bootstrap_phases,
    run_real_data_validation,
    summarize_real_data_validation,
)


def test_run_real_data_validation_selected_chunks_switches_with_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ICCLIM_REAL_DATA_CHUNK_PROFILE", raising=False)
    assert (
        run_real_data_validation._selected_chunks()
        == run_real_data_validation.DEFAULT_CHUNKS
    )

    monkeypatch.setenv("ICCLIM_REAL_DATA_CHUNK_PROFILE", "alt")
    assert (
        run_real_data_validation._selected_chunks()
        == run_real_data_validation.ALT_CHUNKS
    )


def test_resolve_import_root_supports_src_and_flat_layouts(tmp_path: Path) -> None:
    src_repo = tmp_path / "src-repo"
    (src_repo / "src" / "icclim").mkdir(parents=True)
    (src_repo / "src" / "icclim" / "__init__.py").write_text("")
    assert run_real_data_validation._resolve_import_root(src_repo) == src_repo / "src"
    assert profile_bootstrap_phases._resolve_import_root(src_repo) == src_repo / "src"

    flat_repo = tmp_path / "flat-repo"
    (flat_repo / "icclim").mkdir(parents=True)
    (flat_repo / "icclim" / "__init__.py").write_text("")
    assert run_real_data_validation._resolve_import_root(flat_repo) == flat_repo
    assert profile_bootstrap_phases._resolve_import_root(flat_repo) == flat_repo


def test_resolve_import_root_raises_for_missing_package(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        run_real_data_validation._resolve_import_root(tmp_path)
    with pytest.raises(FileNotFoundError):
        profile_bootstrap_phases._resolve_import_root(tmp_path)


def test_profile_timed_patch_if_present_records_calls() -> None:
    class Dummy:
        def ping(self):
            return "pong"

    stats: dict[str, dict[str, float]] = {}
    dummy = Dummy()

    with profile_bootstrap_phases._timed_patch_if_present(dummy, "ping", stats):
        assert dummy.ping() == "pong"

    assert stats["ping"]["calls"] == 1.0
    assert stats["ping"]["seconds"] >= 0.0


def test_profile_timed_patch_if_present_noops_when_missing() -> None:
    class Dummy:
        pass

    stats: dict[str, dict[str, float]] = {}
    dummy = Dummy()
    with profile_bootstrap_phases._timed_patch_if_present(dummy, "missing", stats):
        pass
    assert stats == {}


def test_profile_build_workload_rejects_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        profile_bootstrap_phases,
        "_open_var",
        lambda *args, **kwargs: None,
    )
    with pytest.raises(ValueError, match="Unsupported workload"):
        profile_bootstrap_phases._build_workload(
            object(),
            "unknown_workload",
            chunks=profile_bootstrap_phases.DEFAULT_CHUNKS,
        )


def test_run_real_data_validation_build_workload_rejects_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        run_real_data_validation,
        "_open_var",
        lambda *args, **kwargs: None,
    )
    with pytest.raises(ValueError, match="Unknown workload"):
        run_real_data_validation._build_workload(
            object(),
            "unknown_workload",
            chunks=run_real_data_validation.DEFAULT_CHUNKS,
        )


def test_summarize_parse_compare_file_supports_current_vs_master(
    tmp_path: Path,
) -> None:
    compare_path = (
        tmp_path / "current-vs-master-generic_tas_spell_bootstrap_yearly.compare.json"
    )
    compare_path.write_text(
        json.dumps(
            {
                "data_var_comparison": {
                    "sum_of_spell_lengths": {
                        "equal": True,
                        "changed_cells": 0,
                        "max_abs_diff": 0.0,
                    }
                }
            }
        )
    )

    summary = summarize_real_data_validation._parse_compare_file(compare_path)

    assert summary.current_label == "current"
    assert summary.baseline_label == "master"
    assert summary.workload == "generic_tas_spell_bootstrap_yearly"
    assert summary.all_data_vars_equal is True
    assert summary.total_changed_cells == 0
    assert summary.max_abs_diff == 0.0


def test_summarize_parse_compare_file_supports_master_vs_v717(tmp_path: Path) -> None:
    compare_path = (
        tmp_path / "master-vs-v717-generic_tas_spell_bootstrap_yearly.compare.json"
    )
    compare_path.write_text(
        json.dumps(
            {
                "data_var_comparison": {
                    "sum_of_spell_lengths": {
                        "equal": False,
                        "changed_cells": 1,
                        "max_abs_diff": 1.0,
                    }
                }
            }
        )
    )

    summary = summarize_real_data_validation._parse_compare_file(compare_path)

    assert summary.current_label == "master"
    assert summary.baseline_label == "v717"
    assert summary.workload == "generic_tas_spell_bootstrap_yearly"
    assert summary.all_data_vars_equal is False
    assert summary.total_changed_cells == 1
    assert summary.max_abs_diff == 1.0


def test_summarize_notes_cover_new_compound_workloads() -> None:
    note = summarize_real_data_validation._workload_notes(
        "generic_tas_compound_percentile_or_fraction_yearly"
    )
    assert "compound percentile OR" in note
    assert "bootstrap leaf masks" in note


def test_summarize_notes_cover_new_cftime_and_filtered_average_workloads() -> None:
    assert "cftime monthly" in summarize_real_data_validation._workload_notes(
        "tx90p_cftime_monthly"
    )
    assert "drier regional subset" in summarize_real_data_validation._workload_notes(
        "generic_pr_average_bootstrap_dry_yearly"
    )


class _FakeIcclim:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def build_threshold(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    def index(self, **kwargs):
        self.calls.append(("index", kwargs))
        return {"method": "index", "kwargs": kwargs}

    def indices(self, **kwargs):
        self.calls.append(("indices", kwargs))
        return {"method": "indices", "kwargs": kwargs}

    def count_occurrences(self, **kwargs):
        self.calls.append(("count_occurrences", kwargs))
        return {"method": "count_occurrences", "kwargs": kwargs}

    def average(self, **kwargs):
        self.calls.append(("average", kwargs))
        return {"method": "average", "kwargs": kwargs}

    def sum(self, **kwargs):
        self.calls.append(("sum", kwargs))
        return {"method": "sum", "kwargs": kwargs}

    def fraction_of_total(self, **kwargs):
        self.calls.append(("fraction_of_total", kwargs))
        return {"method": "fraction_of_total", "kwargs": kwargs}

    def sum_of_spell_lengths(self, **kwargs):
        self.calls.append(("sum_of_spell_lengths", kwargs))
        return {"method": "sum_of_spell_lengths", "kwargs": kwargs}


@pytest.mark.parametrize(
    ("workload", "expected_method", "expected_key"),
    [
        ("tg_monthly", "index", "index_name"),
        ("tg_djf_seasonal", "index", "slice_mode"),
        ("rr1_yearly", "index", "var_name"),
        ("su_tasmax_yearly", "index", "time_range"),
        ("prcptot_yearly", "index", "slice_mode"),
        ("generic_tas_count_date_event_monthly", "count_occurrences", "date_event"),
        ("generic_tas_bounded_count_yearly", "count_occurrences", "threshold"),
        ("generic_tas_bounded_average_yearly", "average", "threshold"),
        ("generic_tas_bounded_sum_yearly", "sum", "threshold"),
        ("generic_tas_bounded_fraction_yearly", "fraction_of_total", "threshold"),
        ("generic_tas_bounded_or_count_yearly", "count_occurrences", "threshold"),
        ("generic_tas_bounded_or_average_yearly", "average", "threshold"),
        ("generic_tas_bounded_or_sum_yearly", "sum", "threshold"),
        ("generic_tas_bounded_or_fraction_yearly", "fraction_of_total", "threshold"),
        (
            "generic_tas_compound_percentile_count_yearly",
            "count_occurrences",
            "threshold",
        ),
        ("generic_tas_compound_percentile_average_yearly", "average", "threshold"),
        ("generic_tas_compound_percentile_sum_yearly", "sum", "threshold"),
        (
            "generic_tas_compound_percentile_fraction_yearly",
            "fraction_of_total",
            "threshold",
        ),
        (
            "generic_tas_compound_percentile_or_count_yearly",
            "count_occurrences",
            "threshold",
        ),
        ("generic_tas_compound_percentile_or_average_yearly", "average", "threshold"),
        ("generic_tas_compound_percentile_or_sum_yearly", "sum", "threshold"),
        (
            "generic_tas_compound_percentile_or_fraction_yearly",
            "fraction_of_total",
            "threshold",
        ),
        ("generic_pr_fraction_bootstrap_yearly", "fraction_of_total", "threshold"),
        ("generic_pr_count_bootstrap_yearly", "count_occurrences", "threshold"),
        ("generic_pr_sum_bootstrap_yearly", "sum", "threshold"),
        ("generic_pr_average_bootstrap_yearly", "average", "threshold"),
        ("generic_pr_average_bootstrap_monthly", "average", "threshold"),
        ("generic_pr_average_bootstrap_dry_yearly", "average", "threshold"),
        ("generic_pr_average_bootstrap_99_yearly", "average", "threshold"),
        ("generic_tas_fraction_bootstrap_yearly", "fraction_of_total", "threshold"),
        ("generic_tas_sum_bootstrap_yearly", "sum", "threshold"),
        ("generic_tas_average_bootstrap_yearly", "average", "threshold"),
        (
            "generic_tas_spell_bootstrap_yearly",
            "sum_of_spell_lengths",
            "min_spell_length",
        ),
        ("wsdi_yearly", "index", "index_name"),
        ("csdi_yearly", "index", "index_name"),
        ("tg90p_save_thresholds_monthly", "index", "save_thresholds"),
        ("tx90p_cftime_yearly", "index", "index_name"),
        ("tx90p_cftime_monthly", "index", "index_name"),
        ("combined_cd_yearly", "index", "index_name"),
        ("indices_mixed_yearly", "indices", "index_group"),
        ("indices_mixed_with_cd_yearly", "indices", "index_group"),
    ],
)
def test_run_real_data_validation_build_workload_routes_expected_call(
    monkeypatch: pytest.MonkeyPatch,
    workload: str,
    expected_method: str,
    expected_key: str,
) -> None:
    fake = _FakeIcclim()
    monkeypatch.setattr(
        run_real_data_validation,
        "_open_var",
        lambda *args, **kwargs: {"source": "var", "args": args, "kwargs": kwargs},
    )
    monkeypatch.setattr(
        run_real_data_validation,
        "_open_combined_dataset",
        lambda *args, **kwargs: {"source": "combined", "kwargs": kwargs},
    )
    monkeypatch.setattr(
        run_real_data_validation,
        "_as_cftime_gregorian",
        lambda da: da,
    )

    result = run_real_data_validation._build_workload(
        fake,
        workload,
        chunks=run_real_data_validation.DEFAULT_CHUNKS,
    )

    assert result["method"] == expected_method
    assert expected_key in result["kwargs"]


def test_run_real_data_validation_converts_time_to_cftime_gregorian() -> None:
    time = xr.date_range("2000-01-01", periods=3, freq="D")
    tas = xr.DataArray(
        [1.0, 2.0, 3.0],
        dims=["time"],
        coords={"time": time},
        name="tas",
    )

    converted = run_real_data_validation._as_cftime_gregorian(tas)

    assert converted.time.dtype == object
    assert converted.indexes["time"][0].calendar == "standard"


def test_summarize_format_helpers_cover_pending_and_numeric_paths() -> None:
    assert summarize_real_data_validation._format_seconds(None) == "pending"
    assert summarize_real_data_validation._format_seconds(1.234) == "1.23"
    assert summarize_real_data_validation._format_ratio(None, 1.0) == "pending"
    assert summarize_real_data_validation._format_ratio(2.0, 4.0) == "2.00x"
    assert summarize_real_data_validation._format_percent_change(None, 1.0) == "pending"
    assert summarize_real_data_validation._format_percent_change(6.0, 4.0) == "+50.0%"


def test_summarize_validation_and_history_notes_cover_main_branches() -> None:
    exact = summarize_real_data_validation.ComparisonSummary(
        current_label="current",
        baseline_label="master",
        workload="generic_tas_spell_bootstrap_yearly",
        path=Path("dummy"),
        all_data_vars_equal=True,
        total_changed_cells=0,
        max_abs_diff=0.0,
    )
    different = summarize_real_data_validation.ComparisonSummary(
        current_label="current",
        baseline_label="v717",
        workload="generic_tas_spell_bootstrap_yearly",
        path=Path("dummy"),
        all_data_vars_equal=False,
        total_changed_cells=1,
        max_abs_diff=1.0,
    )
    master_v717 = summarize_real_data_validation.ComparisonSummary(
        current_label="master",
        baseline_label="v717",
        workload="generic_tas_spell_bootstrap_yearly",
        path=Path("dummy"),
        all_data_vars_equal=False,
        total_changed_cells=1,
        max_abs_diff=1.0,
    )

    assert summarize_real_data_validation._format_validation_status(None) == (
        "pending",
        "pending",
        "pending",
    )
    assert summarize_real_data_validation._format_validation_status(exact) == (
        "exact",
        "0",
        "0.0",
    )
    assert summarize_real_data_validation._format_validation_status(different) == (
        "differs",
        "1",
        "1",
    )
    assert (
        summarize_real_data_validation._historical_validation_note(
            "generic_tas_spell_bootstrap_yearly",
            {
                ("current", "master", "generic_tas_spell_bootstrap_yearly"): exact,
                ("current", "v717", "generic_tas_spell_bootstrap_yearly"): different,
                ("master", "v717", "generic_tas_spell_bootstrap_yearly"): master_v717,
            },
        )
        == "historical master/v7.1.7 difference confirmed"
    )


def test_summarize_parse_summary_file_and_compare_filename_errors(
    tmp_path: Path,
) -> None:
    summary_path = tmp_path / "current-wsdi_yearly.summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "workload": "wsdi_yearly",
                "label": "current",
                "duration_seconds": 12.5,
            }
        )
    )
    summary = summarize_real_data_validation._parse_summary_file(summary_path)
    assert summary.workload == "wsdi_yearly"
    assert summary.label == "current"
    assert summary.duration_seconds == 12.5
    assert (
        summarize_real_data_validation._remove_suffix(
            "current.summary.json",
            ".summary.json",
        )
        == "current"
    )

    unknown_compare = tmp_path / "unknown.compare.json"
    unknown_compare.write_text(json.dumps({"data_var_comparison": {}}))
    with pytest.raises(ValueError, match="Unsupported compare filename"):
        summarize_real_data_validation._parse_compare_file(unknown_compare)


def test_summarize_loaders_tables_and_main_cover_summary_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "current-generic_tas_spell_bootstrap_yearly.summary.json").write_text(
        json.dumps(
            {
                "workload": "generic_tas_spell_bootstrap_yearly",
                "label": "current",
                "duration_seconds": 80.0,
            }
        )
    )
    (
        tmp_path / "baseline-master-generic_tas_spell_bootstrap_yearly.summary.json"
    ).write_text(
        json.dumps(
            {
                "workload": "generic_tas_spell_bootstrap_yearly",
                "label": "baseline-master",
                "duration_seconds": 100.0,
            }
        )
    )
    (
        tmp_path / "baseline717-generic_tas_spell_bootstrap_yearly.summary.json"
    ).write_text(
        json.dumps(
            {
                "workload": "generic_tas_spell_bootstrap_yearly",
                "label": "baseline717",
                "duration_seconds": 110.0,
            }
        )
    )
    (
        tmp_path / "current-vs-master-generic_tas_spell_bootstrap_yearly.compare.json"
    ).write_text(
        json.dumps(
            {
                "data_var_comparison": {
                    "sum_of_spell_lengths": {
                        "equal": True,
                        "changed_cells": 0,
                        "max_abs_diff": 0.0,
                    }
                }
            }
        )
    )

    runs = summarize_real_data_validation._load_run_summaries(tmp_path)
    comparisons = summarize_real_data_validation._load_compare_summaries(tmp_path)
    validation_table = summarize_real_data_validation._build_validation_table(
        ["generic_tas_spell_bootstrap_yearly"],
        comparisons,
    )
    performance_table = summarize_real_data_validation._build_performance_table(
        ["generic_tas_spell_bootstrap_yearly"],
        runs,
    )
    summary_document = summarize_real_data_validation._build_summary_document(
        tmp_path,
        ["generic_tas_spell_bootstrap_yearly"],
    )

    assert ("current", "generic_tas_spell_bootstrap_yearly") in runs
    assert ("current", "master", "generic_tas_spell_bootstrap_yearly") in comparisons
    assert "generic_tas_spell_bootstrap_yearly" in validation_table
    assert "generic_tas_spell_bootstrap_yearly" in performance_table
    assert "# Real-data bootstrap validation summary" in summary_document

    out_path = tmp_path / "summary.md"
    monkeypatch.setattr(
        summarize_real_data_validation,
        "_build_summary_document",
        lambda result_dir, expected_workloads: "summary-body",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "summarize_real_data_validation.py",
            "--result-dir",
            str(tmp_path),
            "--out",
            str(out_path),
            "--expected-workload",
            "wsdi_yearly",
        ],
    )
    summarize_real_data_validation.main()
    assert out_path.read_text() == "summary-body"


@pytest.mark.parametrize(
    ("workload", "expected_method"),
    [
        ("generic_tas_compound_percentile_or_count_yearly", "count_occurrences"),
        ("generic_tas_compound_percentile_or_average_yearly", "average"),
        ("generic_tas_compound_percentile_or_sum_yearly", "sum"),
        ("generic_tas_compound_percentile_or_fraction_yearly", "fraction_of_total"),
        ("generic_tas_spell_bootstrap_yearly", "sum_of_spell_lengths"),
        ("wsdi_yearly", "index"),
        ("csdi_yearly", "index"),
    ],
)
def test_profile_build_workload_routes_expected_call(
    monkeypatch: pytest.MonkeyPatch,
    workload: str,
    expected_method: str,
) -> None:
    fake = _FakeIcclim()
    monkeypatch.setattr(
        profile_bootstrap_phases,
        "_open_var",
        lambda *args, **kwargs: {"source": "var", "kwargs": kwargs},
    )

    result = profile_bootstrap_phases._build_workload(
        fake,
        workload,
        chunks=profile_bootstrap_phases.DEFAULT_CHUNKS,
    )

    assert result["method"] == expected_method


def test_run_real_data_validation_main_writes_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_icclim = ModuleType("icclim")
    fake_icclim.__version__ = "9.9.9"
    result_ds = xr.Dataset({"foo": xr.DataArray([1, 2], dims=["time"])})

    monkeypatch.setitem(sys.modules, "icclim", fake_icclim)
    monkeypatch.setattr(
        run_real_data_validation,
        "_resolve_import_root",
        lambda repo: repo,
    )
    monkeypatch.setattr(run_real_data_validation, "_warmup", lambda icclim: None)
    monkeypatch.setattr(
        run_real_data_validation,
        "_build_workload",
        lambda icclim, workload, *, chunks: result_ds,
    )
    monkeypatch.setattr(
        run_real_data_validation,
        "_git_rev_parse",
        lambda repo, ref: "deadbeef",
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
            "current",
            "--out-dir",
            str(tmp_path),
        ],
    )

    run_real_data_validation.main()

    payload = json.loads((tmp_path / "current-wsdi_yearly.summary.json").read_text())
    assert payload["label"] == "current"
    assert payload["workload"] == "wsdi_yearly"
    assert payload["head_commit"] == "deadbeef"
    assert payload["chunk_profile"] == "default"


def test_profile_main_writes_profile_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_icclim = ModuleType("icclim")
    fake_core = ModuleType("icclim._core")
    fake_generic = ModuleType("icclim._core.generic")
    fake_bootstrap = ModuleType("icclim._core.generic.bootstrap")
    fake_primitives = ModuleType("icclim._core.generic.bootstrap_primitives")
    fake_functions = ModuleType("icclim._core.generic.functions")
    result_ds = xr.Dataset({"foo": xr.DataArray([1, 2], dims=["time"])})

    fake_bootstrap.build_bootstrap_temporal_indexing = lambda *args, **kwargs: None
    fake_bootstrap.build_bootstrap_array_inputs = lambda *args, **kwargs: None
    fake_primitives.build_bootstrap_reference_sample = lambda *args, **kwargs: None
    fake_primitives.build_bootstrap_prepared_inputs = lambda *args, **kwargs: None
    fake_functions.reset_bootstrap_profile = lambda: None
    fake_functions.get_bootstrap_profile = lambda: {"bootstrap_family": "test"}
    monkeypatch.setitem(sys.modules, "icclim", fake_icclim)
    monkeypatch.setitem(sys.modules, "icclim._core", fake_core)
    monkeypatch.setitem(sys.modules, "icclim._core.generic", fake_generic)
    monkeypatch.setitem(sys.modules, "icclim._core.generic.bootstrap", fake_bootstrap)
    monkeypatch.setitem(
        sys.modules,
        "icclim._core.generic.bootstrap_primitives",
        fake_primitives,
    )
    monkeypatch.setitem(sys.modules, "icclim._core.generic.functions", fake_functions)
    monkeypatch.setattr(
        profile_bootstrap_phases,
        "_resolve_import_root",
        lambda repo: repo,
    )
    monkeypatch.setattr(profile_bootstrap_phases, "_warmup", lambda icclim: None)
    monkeypatch.setattr(
        profile_bootstrap_phases,
        "_build_workload",
        lambda icclim, workload, *, chunks: result_ds,
    )
    out_path = tmp_path / "profile.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "profile_bootstrap_phases.py",
            "--repo",
            str(tmp_path),
            "--workload",
            "wsdi_yearly",
            "--chunk-profile",
            "default",
            "--out",
            str(out_path),
        ],
    )

    profile_bootstrap_phases.main()

    payload = json.loads(out_path.read_text())
    assert payload["workload"] == "wsdi_yearly"
    assert payload["chunk_profile"] == "default"
    assert payload["bootstrap_profile"] == {"bootstrap_family": "test"}
