"""
End of support of ``user_index`` is announced with a FutureWarning (issue #719).

``icclim.index(user_index=...)`` and the generated ``icclim.custom_index`` warn once per
call, at the line of the caller's code. The computation does not change.
"""

from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim.main import USER_INDEX_END_OF_SUPPORT_WARNING

USER_INDEX = {
    "index_name": "my_index",
    "calc_operation": "nb_events",
    "logical_operation": "gt",
    "thresh": "20 degC",
}


def _ds() -> xr.Dataset:
    time = pd.date_range("2000-01-01", "2001-12-31")
    values = (285 + 10 * np.sin(np.arange(len(time)) / 58)).astype("float32")
    da = xr.DataArray(
        values.reshape(-1, 1, 1),
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0], "lon": [2.0]},
        attrs={"units": "K"},
    )
    return xr.Dataset({"tasmax": da})


def _recorded(call):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = call()
    return result, [w for w in caught if "7.6.0" in str(w.message)]


def _index(**kwargs):
    return icclim.index(
        user_index=USER_INDEX,
        in_files=_ds(),
        var_name="tasmax",
        slice_mode="year",
        **kwargs,
    )


def _custom_index():
    return icclim.custom_index(
        user_index=USER_INDEX, in_files=_ds(), var_name="tasmax", slice_mode="year"
    )


def test_warning_text_gives_the_dates_and_the_migration():
    text = USER_INDEX_END_OF_SUPPORT_WARNING
    assert "7.6.0" in text
    assert "7.1.8" in text
    assert "icclim.index" in text
    assert "icclim.generic" in text
    assert "custom_indices_recipes" in text


@pytest.mark.parametrize("call", [_index, _custom_index], ids=["index", "custom_index"])
def test_future_warning_once_at_the_callers_line(call):
    _, caught = _recorded(call)
    assert len(caught) == 1
    assert caught[0].category is FutureWarning
    assert caught[0].filename == __file__


def test_user_indice_spelling_still_works_with_one_warning():
    _, caught = _recorded(
        lambda: icclim.index(
            user_indice=USER_INDEX, in_files=_ds(), var_name="tasmax", slice_mode="year"
        )
    )
    assert len(caught) == 1
    assert caught[0].category is FutureWarning
    assert caught[0].filename == __file__


def test_result_is_identical_through_both_entry_points():
    direct, _ = _recorded(_index)
    wrapper, _ = _recorded(_custom_index)
    xr.testing.assert_identical(
        direct.drop_attrs(deep=False).my_index, wrapper.drop_attrs(deep=False).my_index
    )
    assert int(direct.my_index.sum()) > 0


def test_user_filter_silences_the_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("ignore")
        _index()
    assert not caught


def test_warning_is_recorded_in_the_provenance(tmp_path):
    out = tmp_path / "out.nc"
    with pytest.warns(FutureWarning, match="7.6.0"):
        _index(out_file=str(out))
    prov = json.loads((tmp_path / "out.prov.json").read_text())
    entries = [w for w in prov["warnings"] if "7.6.0" in w["message"]]
    assert len(entries) == 1
    assert entries[0]["category"] == "FutureWarning"


def test_no_warning_without_user_index():
    ds = _ds()
    _, standard = _recorded(
        lambda: icclim.index(index_name="SU", in_files=ds, var_name="tasmax")
    )
    _, group = _recorded(
        lambda: icclim.indices("tasmax", in_files=ds, ignore_error=True)
    )
    _, generic = _recorded(
        lambda: icclim.count_occurrences(
            in_files=ds, var_name="tasmax", threshold="> 20 degC"
        )
    )
    _, wrapper = _recorded(lambda: icclim.su(in_files=ds, var_name="tasmax"))
    assert standard == []
    assert group == []
    assert generic == []
    assert wrapper == []
