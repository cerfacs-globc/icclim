"""The reference and exact bootstrap paths use circular windows for the replicates.

icclim computes the nominal percentile of the days of the year with a window that wraps
around the year boundaries (``_circular_percentile_doy``), and so do the compiled
bootstrap kernels. xclim's bootstrap computed the percentiles of the replicates with a
window truncated at the ends of the period, so the reference path
(``ICCLIM_BOOTSTRAP_MODE=default``) and the exact path (``safe``) differed from the
compiled path on the first and on the last days of the year.

Tolerances: the thresholds of the kernel and the circular percentiles are compared with
an absolute tolerance of 1e-6 (float32 rounding of the data, in degrees); they agree to
1e-12 in practice. The counts of the compiled path and of the reference path are
compared with a relative tolerance of 1e-12 (the average of the replicates is summed in
another order); the reference and the exact paths are compared exactly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.bootstrapping import BOOTSTRAP_DIM, build_bootstrap_year_da

import icclim
from icclim import build_threshold
from icclim._core.generic import bootstrap as bs
from icclim._core.generic.bootstrap_primitives import build_bootstrap_prepared_inputs
from icclim._core.generic.threshold.percentile import _circular_percentile_doy

pytestmark = pytest.mark.filterwarnings("ignore")

FIRST_YEAR = 1961
THRESHOLD_TOLERANCE = 1e-6


def _study(n_years: int, dtype: str, calendar: str, n_points: int = 2) -> xr.DataArray:
    start, stop = f"{FIRST_YEAR}-01-01", f"{FIRST_YEAR + n_years - 1}-12-31"
    if calendar == "datetime":
        time = pd.date_range(start, stop, freq="D")
    else:
        time = xr.date_range(start, stop, freq="D", calendar=calendar, use_cftime=True)
    rng = np.random.default_rng(1)
    doy = np.asarray(time.dayofyear)[:, None]
    values = 285 + 8 * np.sin(2 * np.pi * (doy - 100) / 365.25)
    values = values + rng.normal(0, 3, (len(time), n_points))
    return xr.DataArray(
        values.astype(dtype),
        dims=("time", "x"),
        coords={"time": time},
        attrs={"units": "K"},
        name="tasmax",
    ).chunk({"time": 730})


def _base(n_base: int) -> list[str]:
    return [f"{FIRST_YEAR}-01-01", f"{FIRST_YEAR + n_base - 1}-12-31"]


@pytest.mark.parametrize(
    ("dtype", "calendar"), [("float32", "datetime"), ("float64", "noleap")]
)
@pytest.mark.parametrize(
    ("n_base", "window"), [(5, 1), (5, 5), (10, 3), (10, 15), (30, 5)]
)
def test_replicate_thresholds_are_circular(n_base, window, dtype, calendar) -> None:
    study = _study(n_base + 2, dtype, calendar)
    threshold = build_threshold(
        "> 90 doy_per", reference_period=_base(n_base), doy_window_width=window
    )
    prepared = build_bootstrap_prepared_inputs(
        study, threshold, "YS", dtype=getattr(np, dtype)
    )
    idx, arr = prepared.temporal_indexing, prepared.array_inputs
    overlap = study.compute().sel(time=slice(*_base(n_base)))
    groups = overlap.resample(time="YS").groups
    labels = list(groups)
    max_samples = idx.sample_indices_by_day_of_year.shape[1]
    for target in range(0, n_base, max(1, n_base // 3)):
        replicates = build_bootstrap_year_da(overlap, groups, labels[target])
        substitutes = [i for i in range(n_base) if i != target]
        for rep in range(0, len(substitutes), max(1, len(substitutes) // 3)):
            expected = _circular_percentile_doy(
                replicates.isel({BOOTSTRAP_DIM: rep}).isel(x=0),
                window=window,
                alpha=1 / 3,
                beta=1 / 3,
                per=[90.0],
            ).squeeze()
            expected = expected.sortby("dayofyear")
            series = bs._build_bootstrap_threshold_series_for_cell(
                arr.flat_reference_raw,
                idx.sample_indices_by_day_of_year,
                idx.reference_index_year,
                idx.reference_index_position,
                idx.substitute_alignment,
                target,
                substitutes[rep],
                0,
                max_samples,
                0.9,
                1 / 3,
                1 / 3,
                np.nan,
            )
            n_days = int(expected.dayofyear.max())
            got = np.array(
                [
                    bs._adjusted_threshold(series, doy, n_days)
                    for doy in expected.dayofyear.values
                ]
            )
            np.testing.assert_allclose(
                got, expected.values, rtol=0, atol=THRESHOLD_TOLERANCE
            )


def _count(study, mode, slice_mode, n_base, window, monkeypatch) -> np.ndarray:
    if mode == "compiled":
        monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE", raising=False)
    else:
        monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", mode)
    threshold = build_threshold(
        "> 90 doy_per", reference_period=_base(n_base), doy_window_width=window
    )
    result = icclim.index(
        index_name="count_occurrences",
        in_files=study.to_dataset(),
        var_name="tasmax",
        threshold=threshold,
        slice_mode=slice_mode,
        out_file=None,
        logs_verbosity="SILENT",
    ).compute()
    return result.count_occurrences.values


CASES = [
    (5, 1, "year"),
    (5, 5, "year"),
    (5, 5, "month"),
    (10, 3, "year"),
    (10, 15, "month"),
    (30, 5, "year"),
]


@pytest.mark.parametrize(
    ("dtype", "calendar"), [("float32", "datetime"), ("float64", "noleap")]
)
@pytest.mark.parametrize(("n_base", "window", "slice_mode"), CASES)
def test_compiled_default_and_safe_paths_agree(
    monkeypatch, n_base, window, slice_mode, dtype, calendar
) -> None:
    if n_base == 30 and dtype == "float64":
        pytest.skip("the long base is checked in float32 only (duration)")
    # base period first, then years outside of it: in-base and out-of-base years
    study = _study(n_base + 3, dtype, calendar)
    compiled = _count(study, "compiled", slice_mode, n_base, window, monkeypatch)
    default = _count(study, "default", slice_mode, n_base, window, monkeypatch)
    safe = _count(study, "safe", slice_mode, n_base, window, monkeypatch)
    np.testing.assert_array_equal(default, safe)
    # the average of the replicates is summed in another order: 1e-12 relative
    np.testing.assert_allclose(compiled, default, rtol=1e-12, atol=0)
    # in-base years are averages of replicates: some counts are fractional
    in_base = compiled[: 12 * n_base] if slice_mode == "month" else compiled[:n_base]
    if window > 1:
        assert np.any(in_base % 1 != 0)


@pytest.mark.parametrize("window", [1, 5])
def test_paths_agree_on_constant_data_with_spikes(monkeypatch, window) -> None:
    study = _study(7, "float32", "datetime")
    values = np.full(study.shape, 285.0, dtype="float32")
    # spikes on the first and on the last days of the years of the base period, where
    # the windows of the replicates differ if they are not circular
    time = study.indexes["time"]
    for year in (1961, 1962, 1963):
        for month, day in ((1, 1), (1, 2), (12, 30), (12, 31)):
            values[time.get_loc(pd.Timestamp(year, month, day))] = 290.0
    study = study.copy(data=values).chunk({"time": 730})
    compiled = _count(study, "compiled", "year", 4, window, monkeypatch)
    default = _count(study, "default", "year", 4, window, monkeypatch)
    safe = _count(study, "safe", "year", 4, window, monkeypatch)
    np.testing.assert_array_equal(default, safe)
    np.testing.assert_allclose(compiled, default, rtol=1e-12, atol=0)
