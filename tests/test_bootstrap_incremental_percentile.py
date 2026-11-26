"""The incremental replicate percentiles give exactly the values of the old kernel.

``ICCLIM_BOOTSTRAP_PERCENTILE=reference`` selects the kernel that selects the
percentile of every replicate from scratch. The default kernel sorts the sample of a
day once and removes/inserts the values of the replaced year. Both must give the
same values bit for bit: ``assert_array_equal`` is used everywhere.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim import build_threshold
from icclim._core.generic import bootstrap as bs
from icclim._core.generic.bootstrap_primitives import build_bootstrap_prepared_inputs

pytestmark = pytest.mark.filterwarnings("ignore")

FIRST_YEAR = 1961


def _study(
    calendar: str,
    n_years: int,
    dtype: str,
    nan_fraction: float,
    seed: int = 3,
    first_year: int = FIRST_YEAR,
) -> xr.DataArray:
    last_day = 30 if calendar == "360_day" else 31
    start, stop = f"{first_year}-01-01", f"{first_year + n_years - 1}-12-{last_day}"
    if calendar == "datetime":
        time = pd.date_range(start, stop, freq="D")
    else:
        time = xr.date_range(start, stop, freq="D", calendar=calendar, use_cftime=True)
    rng = np.random.default_rng(seed)
    doy = np.asarray(time.dayofyear)[:, None, None]
    values = 285 + 8 * np.sin(2 * np.pi * (doy - 100) / 365.25)
    values = values + rng.normal(0, 3, (len(time), 3, 2))
    if nan_fraction:
        values[rng.random(values.shape) < nan_fraction] = np.nan
    return xr.DataArray(
        values.astype(dtype),
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0, 2.0, 3.0], "lon": [1.0, 2.0]},
        attrs={"units": "K"},
        name="tasmax",
    ).chunk({"time": 730})


def _base(n_base: int, calendar: str) -> list[str]:
    last_day = 30 if calendar == "360_day" else 31
    return [f"{FIRST_YEAR}-01-01", f"{FIRST_YEAR + n_base - 1}-12-{last_day}"]


def _count(study, threshold, monkeypatch, *, reference: bool) -> np.ndarray:
    if reference:
        monkeypatch.setenv("ICCLIM_BOOTSTRAP_PERCENTILE", "reference")
    else:
        monkeypatch.delenv("ICCLIM_BOOTSTRAP_PERCENTILE", raising=False)
    result = bs.compute_doy_percentile_bootstrap_count(study, threshold, "YS")
    assert result is not None
    return result.values


CASES = [
    ("datetime", "float32", 0.0),
    ("datetime", "float32", 0.05),
    ("noleap", "float64", 0.0),
    ("360_day", "float64", 0.03),
    ("all_leap", "float64", 0.0),
    ("standard", "float64", 0.05),
]


def _grid():
    """Every window and base length, spread over the calendars and the dtypes."""
    cases = []
    for case_i, (calendar, dtype, nan_fraction) in enumerate(CASES):
        for n_base in (2, 3, 7, 8, 10, 30):
            for window in (1, 3, 5, 7, 15):
                # the longest bases are costly: two calendars only, three windows
                if n_base == 30 and (case_i % 3 != 0 or window in (3, 7)):
                    continue
                cases.append((calendar, dtype, nan_fraction, n_base, window))
    return cases


@pytest.mark.parametrize(
    ("calendar", "dtype", "nan_fraction", "n_base", "window"),
    _grid(),
)
def test_count_kernel_is_identical_to_reference(
    monkeypatch, calendar, dtype, nan_fraction, n_base, window
) -> None:
    study = _study(calendar, n_base + 2, dtype, nan_fraction)
    operator = ">" if (n_base + window) % 2 else "<="
    threshold = build_threshold(
        f"{operator} 90 doy_per",
        reference_period=_base(n_base, calendar),
        doy_window_width=window,
    )
    expected = _count(study, threshold, monkeypatch, reference=True)
    got = _count(study, threshold, monkeypatch, reference=False)
    np.testing.assert_array_equal(got, expected)


@pytest.mark.parametrize("calendar", ["datetime", "noleap"])
def test_count_kernel_with_years_before_and_after_the_base(
    monkeypatch, calendar
) -> None:
    study = _study(calendar, 12, "float32", 0.02, first_year=FIRST_YEAR - 2)
    threshold = build_threshold(
        "> 80 doy_per",
        reference_period=_base(5, calendar),
        doy_window_width=5,
    )
    expected = _count(study, threshold, monkeypatch, reference=True)
    got = _count(study, threshold, monkeypatch, reference=False)
    np.testing.assert_array_equal(got, expected)


@pytest.mark.parametrize("window", [1, 5])
def test_index_with_ignore_feb29th_is_identical(monkeypatch, window) -> None:
    study = _study("datetime", 8, "float32", 0.0).to_dataset()
    kwargs = {
        "index_name": "TX90p",
        "in_files": study,
        "var_name": "tasmax",
        "base_period_time_range": _base(5, "datetime"),
        "slice_mode": "year",
        "doy_window_width": window,
        "ignore_Feb29th": True,
    }
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_PERCENTILE", "reference")
    expected = icclim.index(**kwargs).TX90p.load()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_PERCENTILE")
    got = icclim.index(**kwargs).TX90p.load()
    np.testing.assert_array_equal(got.values, expected.values)


@pytest.mark.parametrize(
    ("calendar", "dtype"), [("datetime", "float32"), ("noleap", "float64")]
)
@pytest.mark.parametrize("window", [1, 5, 15])
def test_replicate_threshold_bank_is_identical_to_series_builder(
    calendar, dtype, window
) -> None:
    study = _study(calendar, 9, dtype, 0.05)
    threshold = build_threshold(
        "> 90 doy_per",
        reference_period=_base(6, calendar),
        doy_window_width=window,
    )
    prepared = build_bootstrap_prepared_inputs(
        study, threshold, "YS", dtype=getattr(np, dtype)
    )
    idx, arr = prepared.temporal_indexing, prepared.array_inputs
    reference = arr.flat_reference_raw
    n_ref_years = idx.substitute_alignment.shape[1]
    max_samples = idx.sample_indices_by_day_of_year.shape[1]
    n_days = idx.sample_indices_by_day_of_year.shape[0]
    quantile = float(threshold.percentile_coord().item()) / 100.0
    alpha = float(threshold.interpolation.alpha)
    beta = float(threshold.interpolation.beta)
    for cell in range(reference.shape[1]):
        for target in range(n_ref_years):
            bank = np.full((n_ref_years, n_days), np.nan)
            bs._build_replicate_threshold_bank(
                reference,
                idx.sample_indices_by_day_of_year,
                idx.reference_index_year,
                idx.reference_index_position,
                idx.substitute_alignment,
                target,
                cell,
                max_samples,
                quantile,
                alpha,
                beta,
                np.nan,
                bank,
            )
            for substitute in range(n_ref_years):
                if substitute == target:
                    continue
                expected = bs._build_bootstrap_threshold_series_for_cell(
                    reference,
                    idx.sample_indices_by_day_of_year,
                    idx.reference_index_year,
                    idx.reference_index_position,
                    idx.substitute_alignment,
                    target,
                    substitute,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    np.nan,
                )
                np.testing.assert_array_equal(bank[substitute], expected)


def test_environment_variable_selects_the_reference_kernel(monkeypatch) -> None:
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_PERCENTILE", raising=False)
    assert bs._select_count_kernel() is bs._bootstrap_count_kernel
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_PERCENTILE", "reference")
    assert bs._select_count_kernel() is bs._bootstrap_count_kernel_reference
