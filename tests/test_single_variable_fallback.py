"""
The only data variable of a dataset as the input of an index (issue #696).

A direct ``icclim.index`` call (and the single-input functions built on it) uses the
only data variable when no variable has the expected name, with a warning.
``icclim.indices`` never does: an index whose variable is missing fails, or is skipped
with ``ignore_error=True``.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim.exception import InvalidIcclimArgumentError

FALLBACK_WARNING = "Using the only data variable"
BASE = ["2000-01-01", "2000-12-31"]


def _tasmax(name: str = "tasmax") -> xr.Dataset:
    time = pd.date_range("2000-01-01", periods=730, freq="D")
    values = (270 + np.arange(730) % 30).astype("float64").reshape(730, 1, 1)
    da = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [10.0], "lon": [20.0]},
        attrs={"units": "K"},
    )
    return xr.Dataset({name: da})


def _cmip6_like(tmp_path) -> xr.Dataset:
    """A single data variable with the bounds read as coordinates, as CMIP6 files."""
    ds = _tasmax()
    ds = ds.assign_coords(
        lat_bnds=(("lat", "bnds"), [[9.5, 10.5]]),
        lon_bnds=(("lon", "bnds"), [[19.5, 20.5]]),
    )
    time_bnds = np.stack(
        [ds.time.values, ds.time.values + np.timedelta64(1, "D")], axis=1
    )
    ds["time_bnds"] = (("time", "bnds"), time_bnds)
    ds.time.attrs["bounds"] = "time_bnds"
    ds.lat.attrs["bounds"] = "lat_bnds"
    ds.lon.attrs["bounds"] = "lon_bnds"
    path = tmp_path / "cmip6_like.nc"
    ds.to_netcdf(path)
    opened = xr.open_dataset(path, decode_coords="all")
    assert list(opened.data_vars) == ["tasmax"]
    return opened


def _skip_messages(caught: list[warnings.WarningMessage]) -> list[str]:
    return [str(w.message) for w in caught if "Could not compute" in str(w.message)]


def _fallback_messages(caught: list[warnings.WarningMessage]) -> list[str]:
    return [str(w.message) for w in caught if FALLBACK_WARNING in str(w.message)]


def test_indices_do_not_compute_an_index_from_the_only_variable() -> None:
    ds = _tasmax()
    with pytest.raises(InvalidIcclimArgumentError, match="TNn needs the following"):
        icclim.indices(["TXx", "TNn"], in_files=ds)


def test_indices_ignore_error_skips_the_index_with_a_missing_variable() -> None:
    ds = _tasmax()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        res = icclim.indices(["TXx", "TNn"], in_files=ds, ignore_error=True)
    assert list(res.data_vars) == ["TXx"]
    skipped = _skip_messages(caught)
    assert len(skipped) == 1
    assert skipped[0].startswith("Could not compute TNn,")
    assert "No variable found for TNn: name it tasmin" in skipped[0]
    assert _fallback_messages(caught) == []


def test_indices_error_message_names_the_expected_variable() -> None:
    with pytest.raises(InvalidIcclimArgumentError) as error:
        icclim.indices(["TNn"], in_files=_tasmax())
    message = error.value.args[0]
    assert "needs the following variable(s) [tn]" in message
    assert "name it tasmin" in message
    assert "`var_name`" in message


def test_indices_cmip6_like_dataset_with_bounds_as_coordinates(tmp_path) -> None:
    ds = _cmip6_like(tmp_path)
    group = ["TXx", "TN90p", "TNx", "TR", "TG90p"]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        res = icclim.indices(
            group, in_files=ds, ignore_error=True, base_period_time_range=BASE
        )
    assert list(res.data_vars) == ["TXx"]
    skipped = _skip_messages(caught)
    assert len(skipped) == 4
    for name in ("TN90p", "TNx", "TR", "TG90p"):
        assert (
            len([m for m in skipped if m.startswith(f"Could not compute {name},")]) == 1
        )
    assert _fallback_messages(caught) == []
    with pytest.raises(InvalidIcclimArgumentError, match="TN90p needs the following"):
        icclim.indices(group, in_files=ds, base_period_time_range=BASE)


def test_indices_with_explicit_var_name_still_work() -> None:
    ds = _tasmax("foo")
    res = icclim.indices(["TXx", "SU"], in_files=ds, var_name="foo")
    assert sorted(res.data_vars) == ["SU", "TXx"]


def test_indices_find_the_variables_by_their_standard_names() -> None:
    ds = _tasmax()
    ds["tasmin"] = ds["tasmax"] - 10
    res = icclim.indices(["TXx", "TNn"], in_files=ds)
    assert sorted(res.data_vars) == ["TNn", "TXx"]


def test_index_uses_the_only_variable_with_a_warning() -> None:
    ds = _tasmax("foo")
    with pytest.warns(
        UserWarning, match="Using the only data variable 'foo' as the input of TXx"
    ) as caught:
        res = icclim.index(index_name="TXx", in_files=ds, slice_mode="year")
    assert len(_fallback_messages(caught.list)) == 1
    assert "Pass `var_name`" in _fallback_messages(caught.list)[0]
    assert float(res["TXx"].isel(time=0).squeeze()) == pytest.approx(25.85)


def test_index_keeps_the_fallback_for_an_index_needing_another_variable() -> None:
    ds = _tasmax()
    with pytest.warns(UserWarning, match="Using the only data variable 'tasmax'"):
        res = icclim.index(index_name="TNn", in_files=ds, slice_mode="year")
    assert "TNn" in res.data_vars


def test_index_with_a_standard_name_or_var_name_does_not_warn() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        icclim.index(index_name="TXx", in_files=_tasmax(), slice_mode="year")
        icclim.index(
            index_name="TXx", in_files=_tasmax("foo"), var_name="foo", slice_mode="year"
        )
    assert _fallback_messages(caught) == []


def test_ecad_function_uses_the_only_variable_with_a_warning() -> None:
    ds = _tasmax("foo")
    with pytest.warns(
        UserWarning, match="Using the only data variable 'foo' as the input of TXx"
    ):
        res = icclim.ecad.txx(in_files=ds, slice_mode="year")
    assert "TXx" in res.data_vars


def test_indices_on_an_unnamed_dataarray_need_a_variable_name() -> None:
    unnamed = _tasmax()["tasmax"].rename(None)
    with pytest.raises(InvalidIcclimArgumentError, match="No variable found for TXx"):
        icclim.indices(["TXx"], in_files=unnamed)
    res = icclim.indices(["TXx"], in_files=unnamed, var_name="tasmax")
    assert list(res.data_vars) == ["TXx"]
