"""
The warnings raised inside one ``icclim.index`` call reach the user (issue #717).

``icclim.index`` records the warnings of its computation for the provenance. They are
shown to the user once, with their category, except the few noisy ones listed in
``icclim.main._UNSHOWN_WARNINGS``.
"""

from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
import icclim.main as icclim_main

BASE = ["2000-01-01", "2000-12-31"]
INNER = "a warning raised by the computation"
NOISE = "Variable does not have a `standard_name` attribute."


def _ds() -> xr.Dataset:
    time = pd.date_range("2000-01-01", periods=730, freq="D")
    values = (270 + np.arange(730) % 30).astype("float64").reshape(730, 1, 1)
    da = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [10.0], "lon": [20.0]},
        attrs={"units": "K"},
    )
    return xr.Dataset({"tasmax": da})


@pytest.fixture
def inner_warnings(monkeypatch):
    """Make the computation raise the given warnings (repeating each twice)."""
    original = icclim_main._run_index_workflow
    to_raise: list[tuple[type[Warning], str]] = []

    def patched(*args, **kwargs):
        for category, message in to_raise:
            warnings.warn(message, category, stacklevel=1)
            warnings.warn(message, category, stacklevel=1)
        return original(*args, **kwargs)

    monkeypatch.setattr(icclim_main, "_run_index_workflow", patched)
    return to_raise


def _recorded(call) -> list[warnings.WarningMessage]:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        call()
    return caught


def _su(**kwargs):
    return icclim.index(index_name="SU", in_files=_ds(), slice_mode="year", **kwargs)


def test_inner_warning_reaches_user_once_with_category(inner_warnings):
    inner_warnings.append((DeprecationWarning, INNER))
    caught = [w for w in _recorded(_su) if INNER in str(w.message)]
    assert len(caught) == 1
    assert caught[0].category is DeprecationWarning


def test_inner_warning_is_also_in_provenance(inner_warnings, tmp_path):
    inner_warnings.append((UserWarning, INNER))
    out = tmp_path / "out.nc"
    with pytest.warns(UserWarning, match=INNER):
        _su(out_file=str(out))
    prov = json.loads((tmp_path / "out.prov.json").read_text())
    assert any(INNER in w["message"] for w in prov["warnings"])


def test_unshown_warning_is_recorded_but_not_shown(inner_warnings, tmp_path):
    inner_warnings.append((UserWarning, NOISE))
    out = tmp_path / "out.nc"
    caught = _recorded(lambda: _su(out_file=str(out)))
    assert not [w for w in caught if NOISE in str(w.message)]
    prov = json.loads((tmp_path / "out.prov.json").read_text())
    assert any(NOISE in w["message"] for w in prov["warnings"])


def test_user_filter_silences_reemitted_warning(inner_warnings):
    inner_warnings.append((UserWarning, INNER))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("ignore")
        _su()
    assert not caught


def test_single_variable_fallback_warning_once():
    ds = _ds().rename({"tasmax": "foo"})
    caught = _recorded(
        lambda: icclim.index(index_name="TXx", in_files=ds, slice_mode="year")
    )
    assert (
        len([w for w in caught if "Using the only data variable" in str(w.message)])
        == 1
    )


def test_indices_ignore_error_one_skip_warning_per_index():
    caught = _recorded(
        lambda: icclim.indices(
            "heat", in_files=_ds(), ignore_error=True, slice_mode="year"
        )
    )
    skipped = [str(w.message) for w in caught if "is skipped" in str(w.message)]
    assert skipped
    assert len(skipped) == len(set(skipped))


def test_indices_shows_inner_warning_once(inner_warnings):
    inner_warnings.append((UserWarning, INNER))
    caught = _recorded(
        lambda: icclim.indices(
            ["SU"], in_files=_ds(), ignore_error=True, slice_mode="year"
        )
    )
    assert len([w for w in caught if INNER in str(w.message)]) == 1
