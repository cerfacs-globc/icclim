"""
The percentile thresholds need a base period.

Without ``base_period_time_range`` the percentiles were computed on the whole original
dataset, not on the studied period (``time_range``), so the result depended on how much
data the file held. The ECA&D indices and the generic indicators with a percentile
threshold now raise an ``InvalidIcclimArgumentError`` when no base period is given. The
DCSC indices, the SPI and the generic ``percentile`` are not changed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim import build_threshold
from icclim.exception import InvalidIcclimArgumentError

BASE = ["1981-01-01", "1990-12-31"]


def _dataset() -> xr.Dataset:
    time = pd.date_range("1981-01-01", "2000-12-31")
    rng = np.random.default_rng(4242)

    def variable(base: float, units: str) -> xr.DataArray:
        values = base + rng.random((len(time), 2, 2))
        return xr.DataArray(
            values.astype("float32"),
            dims=("time", "lat", "lon"),
            coords={"time": time},
            attrs={"units": units},
        )

    return xr.Dataset(
        {
            "tasmax": variable(20.0, "degC"),
            "tas": variable(15.0, "degC"),
            "pr": variable(1.0, "mm/day"),
        }
    )


OPTIONS = {"out_file": None, "logs_verbosity": "SILENT"}


@pytest.mark.parametrize(
    ("index_name", "var_name"),
    [
        ("TX90p", "tasmax"),  # day-of-year percentile
        ("WSDI", "tasmax"),  # spell index
        ("R95p", "pr"),  # period percentile
        ("CD", ["tas", "pr"]),  # compound index
    ],
)
def test_an_ecad_percentile_index_without_base_period_raises(
    index_name: str, var_name: str | list[str]
) -> None:
    with pytest.raises(InvalidIcclimArgumentError) as error:
        icclim.index(
            in_files=_dataset(), index_name=index_name, var_name=var_name, **OPTIONS
        )
    message = error.value.args[0]
    assert message.startswith(f"{index_name} is computed with a percentile threshold")
    assert "base_period_time_range" in message
    assert '["1961-01-01", "1990-12-31"]' in message


def test_the_public_function_of_an_ecad_percentile_index_raises() -> None:
    with pytest.raises(InvalidIcclimArgumentError, match="TX90p"):
        icclim.tx90p(_dataset(), var_name="tasmax", **OPTIONS)


@pytest.mark.parametrize(
    "threshold",
    ["> 90 doy_per", build_threshold("> 90 doy_per"), ">= 90 doy_per AND > 10 degC"],
    ids=["string", "threshold", "bounded"],
)
def test_a_generic_percentile_threshold_without_base_period_raises(
    threshold: object,
) -> None:
    with pytest.raises(InvalidIcclimArgumentError) as error:
        icclim.count_occurrences(
            _dataset(), var_name="tasmax", threshold=threshold, **OPTIONS
        )
    message = error.value.args[0]
    assert message.startswith("count_occurrences is computed with a percentile")
    assert "base_period_time_range" in message
    assert "reference_period" in message


def test_the_base_period_is_given_with_base_period_time_range() -> None:
    result = icclim.tx90p(
        _dataset(),
        var_name="tasmax",
        base_period_time_range=BASE,
        slice_mode="year",
        **OPTIONS,
    )
    assert result["TX90p"].sizes["time"] == 20


def test_the_base_period_is_given_to_a_generic_threshold_by_the_index_function() -> (
    None
):
    from_index = icclim.index(
        in_files=_dataset(),
        index_name="count_occurrences",
        var_name="tasmax",
        threshold=build_threshold("> 90 doy_per"),
        base_period_time_range=BASE,
        slice_mode="year",
        **OPTIONS,
    ).count_occurrences
    from_threshold = icclim.count_occurrences(
        _dataset(),
        var_name="tasmax",
        threshold=build_threshold("> 90 doy_per", reference_period=BASE),
        slice_mode="year",
        **OPTIONS,
    ).count_occurrences
    np.testing.assert_array_equal(from_index.values, from_threshold.values)


def test_a_group_with_percentile_indices_needs_the_base_period() -> None:
    with pytest.raises(InvalidIcclimArgumentError, match="percentile threshold"):
        icclim.indices("heat", in_files=_dataset(), var_name="tasmax", **OPTIONS)


# Not changed.


def test_an_index_without_percentile_does_not_need_a_base_period() -> None:
    icclim.su(_dataset(), var_name="tasmax", **OPTIONS)
    icclim.count_occurrences(
        _dataset(), var_name="tasmax", threshold="> 25 degC", **OPTIONS
    )


def test_the_generic_percentile_does_not_need_a_base_period() -> None:
    result = icclim.percentile(
        _dataset(), var_name="tasmax", threshold="> 90 doy_per", **OPTIONS
    )
    assert "percentile" in result


def test_a_dcsc_percentile_index_is_not_changed() -> None:
    result = icclim.dcsc.tx90(_dataset(), var_name="tasmax", **OPTIONS)
    assert "TX90" in result


def test_the_spi_still_raises_its_own_error() -> None:
    with pytest.raises(ValueError, match="reference_period is missing for SPI"):
        icclim.spi3(_dataset(), var_name="pr", **OPTIONS)
