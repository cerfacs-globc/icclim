"""
Combined percentile thresholds and the bootstrap (issue #724, interim step).

For the years inside the base period, each threshold is averaged over the bootstrap
replicates and the masks are then combined, instead of combining the masks of each
replicate. icclim warns once per call when this happens. The xfail tests document
the target: the counts paired per replicate.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim import build_threshold
from icclim._core.generic.indicator import COMBINED_PERCENTILE_BOOTSTRAP_WARNING

BASE = ("2000-01-01", "2002-12-31")
MARK = "issues/724"


def _ds(end: str = "2005-12-31") -> xr.Dataset:
    time = pd.date_range("2000-01-01", end)
    rng = np.random.default_rng(1)
    base = 285 + rng.normal(0, 3, len(time))
    rain = rng.gamma(0.5, 6.0, len(time)) / 86400

    def da(values, units):
        return xr.DataArray(
            values.astype("float32").reshape(-1, 1, 1),
            dims=("time", "lat", "lon"),
            coords={"time": time, "lat": [1.0], "lon": [2.0]},
            attrs={"units": units},
        )

    return xr.Dataset(
        {
            "tasmax": da(base, "K"),
            "tas": da(base, "K"),
            "pr": da(rain, "kg m-2 s-1"),
        }
    )


def _thr(query: str):
    return build_threshold(query, reference_period=BASE)


def _count_724(call) -> int:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        call()
    return len([w for w in caught if MARK in str(w.message)])


def _generic(threshold, ds=None, **kwargs):
    return icclim.index(
        index_name="count_occurrences",
        in_files=_ds() if ds is None else ds,
        var_name="tasmax",
        slice_mode="year",
        threshold=threshold,
        **kwargs,
    )


def test_warning_text_points_to_the_issue():
    assert "not paired per replicate" in COMBINED_PERCENTILE_BOOTSTRAP_WARNING
    assert "can differ from combining the thresholds per bootstrap replicate" in (
        COMBINED_PERCENTILE_BOOTSTRAP_WARNING
    )
    assert "ATBD" not in COMBINED_PERCENTILE_BOOTSTRAP_WARNING
    assert "outside the base period are not affected" in (
        COMBINED_PERCENTILE_BOOTSTRAP_WARNING
    )
    assert "https://github.com/cerfacs-globc/icclim/issues/724" in (
        COMBINED_PERCENTILE_BOOTSTRAP_WARNING
    )


def test_bounded_threshold_warns_once():
    count = _count_724(lambda: _generic(_thr("> 90 doy_per") & _thr("< 99 doy_per")))
    assert count == 1


def test_percentile_with_basic_threshold_warns_once():
    count = _count_724(
        lambda: _generic(_thr("> 90 doy_per") & build_threshold("> 20 degC"))
    )
    assert count == 1


@pytest.mark.parametrize("index_name", ["CD", "CW", "WD", "WW"])
def test_multi_variable_indices_warn_once(index_name):
    count = _count_724(
        lambda: icclim.index(
            index_name=index_name,
            in_files=_ds(),
            slice_mode="year",
            base_period_time_range=list(BASE),
        )
    )
    assert count == 1


def test_warning_reaches_the_caller_with_user_warning_category():
    with pytest.warns(UserWarning, match=MARK) as caught:
        _generic(_thr("> 90 doy_per") & _thr("< 99 doy_per"))
    assert caught[0].filename == __file__


def test_indices_warns_once_for_several_combined_indices():
    count = _count_724(
        lambda: icclim.indices(
            ["CD", "CW"],
            in_files=_ds(),
            ignore_error=True,
            slice_mode="year",
            base_period_time_range=list(BASE),
        )
    )
    assert count == 1


def test_indices_with_standard_percentile_index_does_not_warn():
    count = _count_724(
        lambda: icclim.indices(
            ["TX90p"],
            in_files=_ds(),
            ignore_error=True,
            slice_mode="year",
            base_period_time_range=list(BASE),
        )
    )
    assert count == 0


def test_single_threshold_does_not_warn():
    assert _count_724(lambda: _generic(_thr("> 90 doy_per"))) == 0


def test_standard_single_threshold_index_does_not_warn():
    count = _count_724(
        lambda: icclim.index(
            index_name="TX90p",
            in_files=_ds(),
            var_name="tasmax",
            slice_mode="year",
            base_period_time_range=list(BASE),
        )
    )
    assert count == 0


def test_bounded_basic_thresholds_do_not_warn():
    count = _count_724(
        lambda: _generic(build_threshold(">= 20 degC") & build_threshold("< 30 degC"))
    )
    assert count == 0


def test_no_bootstrap_when_study_equals_the_base_period_does_not_warn():
    ds = _ds("2002-12-31")
    assert (
        _count_724(lambda: _generic(_thr("> 90 doy_per") & _thr("< 99 doy_per"), ds))
        == 0
    )


def test_bootstrap_disabled_does_not_warn():
    count = _count_724(
        lambda: _generic(_thr("> 90 doy_per") & _thr("< 99 doy_per"), bootstrap=False)
    )
    assert count == 0


def test_user_filter_silences_the_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("ignore")
        _generic(_thr("> 90 doy_per") & _thr("< 99 doy_per"))
    assert not caught


# --- target of the fix (option A): documented, expected to fail for now ------------

STUDY_YEARS = range(2000, 2012)
ORACLE_BASE = ("2000-01-01", "2004-12-31")


def _oracle_data():
    time = pd.date_range("2000-01-01", "2011-12-31")
    rng = np.random.default_rng(3)
    doy = time.day_of_year.to_numpy()
    values = 285 + 10 * np.sin(2 * np.pi * (doy - 110) / 365.25)
    values = values + rng.normal(0, 3, len(time))
    da = xr.DataArray(
        values.reshape(-1, 1, 1).astype("float32"),
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0], "lon": [2.0]},
        attrs={"units": "K"},
        name="tasmax",
    )
    keep = ~((time.month == 2) & (time.day == 29))
    years = {
        y: values[(time.year == y) & keep].astype("float32").astype("float64")
        for y in STUDY_YEARS
    }
    return da, years


def _percentile_per_day(sample_years, q, half=2):
    arr = np.stack(sample_years)
    pooled = np.empty((365, arr.shape[0] * (2 * half + 1)))
    for day in range(365):
        idx = [(day + offset) % 365 for offset in range(-half, half + 1)]
        pooled[day] = arr[:, idx].ravel()
    return np.quantile(pooled, q / 100, axis=1, method="median_unbiased")


def _brute_force(years, year, spec):
    """Mean over the bootstrap replicates of the count of (a_k AND b_k)."""
    base_years = list(range(2000, 2005))
    counts = []
    for other in (y for y in base_years if y != year):
        sample = [years[other if y == year else y] for y in base_years]
        mask = np.ones(365, dtype=bool)
        for operator, q in spec:
            thr = _percentile_per_day(sample, q)
            mask &= (years[year] > thr) if operator == ">" else (years[year] < thr)
        counts.append(mask.sum())
    return float(np.mean(counts))


def _icclim_counts(threshold):
    da, _ = _oracle_data()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = icclim.count_occurrences(
            in_files=da.to_dataset(),
            var_name="tasmax",
            threshold=threshold,
            slice_mode="year",
            ignore_Feb29th=True,
        )
    return np.asarray(res["count_occurrences"].values, dtype="float64").ravel()


@pytest.mark.xfail(strict=True, reason="#724")
def test_impossible_bounded_threshold_is_zero_in_base_years():
    def thr(query):
        return build_threshold(query, reference_period=ORACLE_BASE)

    got = _icclim_counts(thr("> 90 doy_per") & thr("< 90 doy_per"))
    np.testing.assert_array_equal(got[:5], np.zeros(5))


@pytest.mark.xfail(strict=True, reason="#724")
def test_compound_count_is_the_mean_over_replicates_of_the_paired_masks():
    def thr(query):
        return build_threshold(query, reference_period=ORACLE_BASE)

    _, years = _oracle_data()
    got = _icclim_counts(thr("> 90 doy_per") & thr("< 99 doy_per"))
    expected = np.array(
        [_brute_force(years, y, [(">", 90), ("<", 99)]) for y in range(2000, 2005)]
    )
    np.testing.assert_allclose(got[:5], expected)
