"""Completeness masking must never hide results computed from complete data.

The completeness policy (strict by default since 7.2.0) masks output periods
whose source data is incomplete. Data without any missing value is complete by
definition, so the default must return exactly what ``allow_missing_periods=True``
returns, whatever the way inputs are given to the index.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

STUDY = ("2002-01-01", "2003-12-31")
REFERENCE = ("2000-01-01", "2001-12-31")


def _daily_tas() -> xr.DataArray:
    time = pd.date_range("2000-01-01", "2003-12-31", freq="D")
    rng = np.random.default_rng(7)
    seasonal = 10 + 8 * np.sin(2 * np.pi * np.arange(time.size) / 365.25)
    values = seasonal[:, None] + rng.normal(0, 2, (time.size, 3))
    return xr.DataArray(
        values,
        dims=("time", "station"),
        coords={"time": time, "station": [0, 1, 2]},
        name="tas",
        attrs={"units": "degC", "standard_name": "air_temperature"},
    )


def _study_and_reference() -> tuple[xr.DataArray, xr.DataArray]:
    tas = _daily_tas()
    return tas.sel(time=slice(*STUDY)), tas.sel(time=slice(*REFERENCE))


def _non_overlapping_inputs(tas: xr.DataArray) -> dict:
    study = tas.sel(time=slice(*STUDY))
    reference = tas.sel(time=slice(*REFERENCE))
    return {"study": study, "reference": reference}


@pytest.mark.parametrize("slice_mode", ["month", "year", "day"])
def test_difference_to_a_reference_on_another_period_is_not_masked(
    slice_mode: str,
) -> None:
    study, reference = _study_and_reference()
    kwargs = {
        "in_files": {"study": study, "reference": reference},
        "slice_mode": slice_mode,
        "sampling_method": "groupby_ref_and_resample_study",
        "out_file": None,
    }

    default = icclim.difference_of_means(**kwargs).difference_of_means.compute()
    unmasked = icclim.difference_of_means(
        **kwargs, allow_missing_periods=True
    ).difference_of_means.compute()

    study_periods = default.sel(time=slice(*STUDY))
    assert study_periods.notnull().all()
    xr.testing.assert_equal(default, unmasked)


def test_difference_to_a_reference_matches_independent_computation() -> None:
    study, reference = _study_and_reference()

    result = icclim.difference_of_means(
        in_files={"study": study, "reference": reference},
        slice_mode="month",
        sampling_method="groupby_ref_and_resample_study",
        out_file=None,
    ).difference_of_means.compute()

    normal = reference.groupby("time.month").mean("time")
    monthly = study.resample(time="MS").mean("time")
    expected = monthly.groupby("time.month") - normal
    got = result.sel(time=slice(*STUDY))
    np.testing.assert_allclose(
        got.transpose("time", "station").values,
        expected.transpose("time", "station").values,
        rtol=1e-6,
    )


@pytest.mark.parametrize(
    "index_name",
    ["sum", "average", "count_occurrences", "maximum", "minimum"],
)
@pytest.mark.parametrize("slice_mode", ["month", "year"])
def test_complete_data_is_never_masked_by_default(
    index_name: str, slice_mode: str
) -> None:
    tas = _daily_tas()
    kwargs = {
        "index_name": index_name,
        "in_files": tas.to_dataset(),
        "var_name": "tas",
        "slice_mode": slice_mode,
        "out_file": None,
    }
    if index_name == "count_occurrences":
        kwargs["threshold"] = ">= 10 degC"

    default = icclim.index(**kwargs)
    unmasked = icclim.index(**kwargs, allow_missing_periods=True)

    name = next(iter(default.data_vars))
    assert default[name].notnull().all()
    xr.testing.assert_equal(default[name].compute(), unmasked[name].compute())
