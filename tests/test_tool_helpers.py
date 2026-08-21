from __future__ import annotations

import inspect
import json
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest
import xarray as xr

from icclim._core.constants import NEEDS_NORMAL, QUANTILE_BASED, REFERENCE_PERIOD_INDEX
from tools import prototype_cftime_exact_order_stat_quantile as order_quantile_tools
from tools import prototype_cftime_exact_order_stat_count as order_count_tools
from tools import compare_real_data_validation as compare_tools
from tools import analyze_cftime_exact_order_stat_design as order_stat_tools
from tools import debug_real_data_validation as debug_tools
from tools import extract_icclim_funs as extract_tools
from tools import update_logo_version as logo_tools


def test_compare_variable_handles_numeric_and_non_numeric() -> None:
    left = xr.DataArray([1.0, 2.0, float("nan")])
    right = xr.DataArray([1.0, 3.0, float("nan")])
    numeric = compare_tools._compare_variable(left, right)
    assert numeric["equal"] is False
    assert numeric["changed_cells"] == 1
    assert numeric["max_abs_diff"] == 1.0

    non_numeric_left = xr.DataArray(["a", "b"])
    non_numeric_right = xr.DataArray(["a", "b"])
    non_numeric = compare_tools._compare_variable(non_numeric_left, non_numeric_right)
    assert non_numeric == {"equal": True, "changed_cells": 0}


def test_compare_variable_reports_shape_or_dim_mismatch() -> None:
    dims_mismatch = compare_tools._compare_variable(
        xr.DataArray([1, 2], dims=("time",)),
        xr.DataArray([1, 2], dims=("lat",)),
    )
    assert dims_mismatch["equal"] is False
    assert "dims differ" in dims_mismatch["reason"]

    shape_mismatch = compare_tools._compare_variable(
        xr.DataArray([1, 2]),
        xr.DataArray([1, 2, 3]),
    )
    assert shape_mismatch["equal"] is False
    assert "shape differ" in shape_mismatch["reason"]


def test_order_stat_replacement_summary_counts_target_and_substitute_slots() -> None:
    sample_indices = np.asarray(
        [
            [0, 2, 4, -1],
            [1, 3, 5, -1],
        ],
        dtype=np.int64,
    )
    index_year = np.asarray([0, 0, 1, 1, 2, 2], dtype=np.int64)
    index_pos = np.asarray([0, 1, 0, 1, 0, 1], dtype=np.int64)
    substitute_aligned = np.full((3, 3, 2), -1, dtype=np.int64)
    substitute_aligned[0, 1, :] = np.asarray([2, 3])
    substitute_aligned[0, 2, :] = np.asarray([4, -1])
    substitute_aligned[1, 0, :] = np.asarray([0, 1])
    substitute_aligned[1, 2, :] = np.asarray([4, 5])
    substitute_aligned[2, 0, :] = np.asarray([0, -1])
    substitute_aligned[2, 1, :] = np.asarray([2, 3])

    summary = order_stat_tools._summarize_replacement_structure(
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
    )

    assert summary.max_samples_per_doy == 3
    assert summary.min_samples_per_doy == 3
    assert summary.max_target_year_slots_per_doy == 1
    assert summary.min_target_year_slots_per_doy == 1
    assert summary.max_effective_substitute_slots_per_doy == 1
    assert summary.min_effective_substitute_slots_per_doy == 0


def test_order_stat_quantile_matches_simple_adjusted_multiset() -> None:
    base_sorted = np.asarray([1.0, 2.0, 2.0, 5.0], dtype=np.float64)
    removed_sorted = np.asarray([2.0], dtype=np.float64)
    inserted_sorted = np.asarray([3.0], dtype=np.float64)

    quantile = order_quantile_tools._method8_quantile_from_adjusted_sorted(
        base_sorted,
        removed_sorted,
        inserted_sorted,
        0.5,
        1.0 / 3.0,
        1.0 / 3.0,
    )

    np.testing.assert_allclose(quantile, 2.5)


@pytest.mark.parametrize(
    ("case_name", "freq"),
    [
        ("constant", "MS"),
        ("leap_day_cold_spike", "MS"),
        ("reference_overlap_shift", "YS"),
    ],
)
def test_order_stat_threshold_series_prototype_matches_current_builder(
    case_name: str,
    freq: str,
) -> None:
    comparison = order_quantile_tools.compare_order_stat_threshold_series(
        case_name,
        freq,
    )

    assert comparison.changed_doys == 0
    assert comparison.max_abs_diff == 0.0


@pytest.mark.parametrize(
    ("case_name", "freq"),
    [
        ("constant", "MS"),
        ("leap_day_cold_spike", "YS"),
    ],
)
def test_order_stat_count_prototype_matches_current_output(
    case_name: str,
    freq: str,
) -> None:
    comparison = order_count_tools.compare_count_prototypes(case_name, freq)

    assert comparison.changed_cells == 0
    assert comparison.max_abs_diff == 0.0


def test_compare_datasets_collects_shared_vars_and_attrs(tmp_path: Path) -> None:
    current = xr.Dataset(
        data_vars={"tas": (("time",), [1.0, 2.0])},
        coords={"time": [0, 1], "lat": 42.0},
        attrs={"history": "new", "title": "same"},
    )
    baseline = xr.Dataset(
        data_vars={"tas": (("time",), [1.0, 2.0])},
        coords={"time": [0, 1], "lat": 42.0},
        attrs={"history": "old", "title": "same"},
    )
    current_path = tmp_path / "current.nc"
    baseline_path = tmp_path / "baseline.nc"
    current.to_netcdf(current_path)
    baseline.to_netcdf(baseline_path)

    result = compare_tools._compare_datasets(current_path, baseline_path)
    assert result["data_var_comparison"]["tas"]["equal"] is True
    assert result["coord_comparison"]["lat"]["equal"] is True
    assert result["dataset_attrs"]["history_equal"] is False
    assert result["dataset_attrs"]["non_history_equal"]["title"] is True


def test_compare_main_writes_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    current = tmp_path / "current.nc"
    baseline = tmp_path / "baseline.nc"
    out = tmp_path / "summary.json"
    xr.Dataset({"tas": (("time",), [1.0])}).to_netcdf(current)
    xr.Dataset({"tas": (("time",), [1.0])}).to_netcdf(baseline)
    monkeypatch.setattr(
        "sys.argv",
        [
            "compare_real_data_validation.py",
            "--current",
            str(current),
            "--baseline",
            str(baseline),
            "--out",
            str(out),
        ],
    )

    compare_tools.main()

    written = json.loads(out.read_text())
    assert written["data_var_comparison"]["tas"]["equal"] is True
    assert '"data_var_comparison"' in capsys.readouterr().out


def test_debug_load_validation_module_errors_when_loader_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        debug_tools.importlib.util,
        "spec_from_file_location",
        lambda *args, **kwargs: None,
    )
    with pytest.raises(RuntimeError, match="Cannot load validation module"):
        debug_tools._load_validation_module()


def test_debug_main_completed_payload(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_icclim = ModuleType("icclim")
    monkeypatch.setitem(__import__("sys").modules, "icclim", fake_icclim)
    fake_validation = SimpleNamespace(
        _warmup=lambda _icclim: None,
        _build_workload=lambda _icclim, _workload: xr.Dataset(
            {"tas": (("time",), [1.0, 2.0])}, coords={"time": [0, 1]}
        ),
    )
    monkeypatch.setattr(debug_tools, "_load_validation_module", lambda: fake_validation)
    monkeypatch.setattr(
        "sys.argv",
        [
            "debug_real_data_validation.py",
            "--repo",
            str(tmp_path),
            "--workload",
            "demo",
        ],
    )

    debug_tools.main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "completed"
    assert payload["data_vars"] == ["tas"]
    assert payload["sizes"]["time"] == 2


def test_debug_main_failed_payload(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_icclim = ModuleType("icclim")
    monkeypatch.setitem(__import__("sys").modules, "icclim", fake_icclim)
    fake_validation = SimpleNamespace(
        _warmup=lambda _icclim: None,
        _build_workload=lambda _icclim, _workload: (_ for _ in ()).throw(
            ValueError("boom")
        ),
    )
    monkeypatch.setattr(debug_tools, "_load_validation_module", lambda: fake_validation)
    monkeypatch.setattr(
        "sys.argv",
        [
            "debug_real_data_validation.py",
            "--repo",
            str(tmp_path),
            "--workload",
            "demo",
        ],
    )

    debug_tools.main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "failed"
    assert payload["error_type"] == "ValueError"
    assert "boom" in payload["error_message"]


def test_logo_run_replaces_version_placeholder(tmp_path: Path) -> None:
    source = tmp_path / "logo.svg"
    dest = tmp_path / "out.svg"
    source.write_text("hello {{icclim.__version__}} world\n")

    logo_tools._run(source, dest)

    assert "{{icclim.__version__}}" not in dest.read_text()


def test_extract_helper_flags_and_arguments() -> None:
    index = SimpleNamespace(
        qualifiers=[NEEDS_NORMAL, QUANTILE_BASED, REFERENCE_PERIOD_INDEX]
    )
    assert extract_tools._is_compared_to_normal(index) is True
    assert extract_tools._is_quantile_based(index) is True
    assert extract_tools._can_have_reference_period(index) is True

    args = extract_tools._get_arguments(["threshold", "user_index"])
    assert "threshold" not in args
    assert "user_index" not in args
    assert "index_name" in args


def test_extract_threshold_and_output_helpers() -> None:
    index = SimpleNamespace(
        output_unit="degC",
        threshold=[
            "> 10 degree_Celsius",
            {"query": "> 90 doy_per", "threshold_min_value": "1 mm/day"},
        ],
    )
    assert extract_tools._get_output_unit_argument(index) == 'out_unit="degC"'
    threshold_arg = extract_tools._get_threshold_argument(index)
    assert "build_threshold" in threshold_arg
    assert "threshold_min_value" in threshold_arg


def test_extract_parameter_declaration_and_signature_building() -> None:
    params = {
        "required": inspect.Parameter(
            "required",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=str,
        ),
        "optional": inspect.Parameter(
            "optional",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation="Literal[start, end]",
            default="yes",
        ),
    }
    signature_args = extract_tools._build_fun_signature_args(params)
    assert "required: str" in signature_args
    assert "optional: Literal['start', 'end'] = \"yes\"" in signature_args


def test_extract_doc_and_threshold_format_helpers(tmp_path: Path) -> None:
    doc = extract_tools._get_params_docstring(
        ["threshold"],
        """
        Summary.

        Parameters
        ----------
        threshold : str
            Threshold description.
        ignored : str
            Ignored.
        """,
    )
    assert "threshold" in doc
    assert "ignored" not in doc

    formatted = extract_tools._format_thresh(
        {"query": "> 90 doy_per", "threshold_min_value": "1 mm/day"}
    )
    assert "build_threshold" in formatted
    assert 'threshold_min_value="1 mm/day"' in formatted

    doc_path = tmp_path / "index.rst"
    doc_path.write_text(
        "before\n.. Generated API comment:Begin\nold\n.. Generated API comment:End\nafter\n"
    )
    extract_tools._generate_doc(doc_path, "\n    replacement\n")
    assert "replacement" in doc_path.read_text()


def test_extract_header_and_all_helpers() -> None:
    header = extract_tools._build_module_header("generic")
    assert "auto-generated" in header
    assert "build_threshold" in header

    all_block = extract_tools._build__all__(["TG", "SU"])
    assert '"tg"' in all_block
    assert '"su"' in all_block


def test_extract_main_routes_to_generators(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[tuple[str, Path]] = []

    monkeypatch.setattr(
        extract_tools, "_generate_ecad_api", lambda path: calls.append(("ecad", path))
    )
    monkeypatch.setattr(
        extract_tools, "_generate_dcsc_api", lambda path: calls.append(("dcsc", path))
    )
    monkeypatch.setattr(
        extract_tools,
        "_generate_generic_api",
        lambda path: calls.append(("generic", path)),
    )
    monkeypatch.setattr(
        extract_tools,
        "_generate_doc",
        lambda path, content: calls.append((content.strip(), path)),
    )
    monkeypatch.setattr(extract_tools, "_get_ecad_doc", lambda: "ecad_doc")
    monkeypatch.setattr(extract_tools, "_get_dcsc_doc", lambda: "dcsc_doc")
    monkeypatch.setattr(extract_tools, "_get_generic_doc", lambda: "generic_doc")
    monkeypatch.setattr("sys.argv", ["extract_icclim_funs.py", str(tmp_path)])

    extract_tools.main()

    assert ("ecad", tmp_path / "_ecad.py") in calls
    assert ("dcsc", tmp_path / "_dcsc.py") in calls
    assert ("generic", tmp_path / "_generic.py") in calls
    assert ("ecad_doc", extract_tools.PATH_TO_ECAD_DOC_FILE) in calls
