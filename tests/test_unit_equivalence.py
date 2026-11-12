"""
Unit-equivalence metamorphic test over the indices of the registries.

The same data given in other units must give the same result: temperatures in K,
degC and degF, precipitation in kg m-2 s-1 and mm/day, eager and chunked. Every ECA&D,
DCSC and generic index whose input is a temperature or a precipitation is checked.
The result of each run is converted to the units of the reference run (degC or mm/day,
eager) and compared, and the output units must be equivalent to the reference ones.
Finally, an index is called twice in one process, because the text of the pint
units changes after the first xclim call.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from packaging.version import Version
from xclim.core.units import convert_units_to

import icclim
from icclim.dcsc.registry import DcscIndexRegistry
from icclim.ecad.registry import EcadIndexRegistry
from icclim.generic.registry import GenericIndicatorRegistry

if TYPE_CHECKING:
    from collections.abc import Callable

BASE = ("1999-01-01", "1999-12-31")
STUDY = ("2000-01-01", "2001-12-31")
TIME = pd.date_range("1999-01-01", "2001-12-31")
NORMAL_TIME = pd.date_range("1999-01-01", periods=365)
N_CELLS = 2

# Units of the input and the one of the reference run.
TEMPERATURE_UNITS = {"degC": lambda c: c, "K": lambda c: c + 273.15}
TEMPERATURE_UNITS["degF"] = lambda c: c * 9 / 5 + 32
PRECIPITATION_UNITS = {"mm/day": lambda p: p, "kg m-2 s-1": lambda p: p / 86400}
STANDARD_VARIABLES = {
    "tg": "tas",
    "tx": "tasmax",
    "tn": "tasmin",
    "pr": "pr",
}


def _reference_data(variable: str, time: pd.DatetimeIndex) -> np.ndarray:
    """Continuous values in degC (temperatures) or mm/day (precipitation)."""
    rng = np.random.default_rng(
        abs(hash(variable)) % 2**32 if False else _SEED[variable]
    )
    n = len(time)
    seasonal = 10 + 10 * np.sin(2 * np.pi * (time.dayofyear.values - 110) / 365)
    mean = seasonal[:, None] + rng.normal(0, 3, (n, N_CELLS))
    if variable == "tas":
        return mean
    if variable == "tasmax":
        return mean + rng.uniform(3, 8, mean.shape)
    if variable == "tasmin":
        return mean - rng.uniform(3, 8, mean.shape)
    wet = rng.random((n, N_CELLS)) > 0.45
    return np.where(wet, rng.gamma(0.8, 7.0, (n, N_CELLS)) + 0.05, 0.0)


_SEED = {"tas": 1, "tasmax": 2, "tasmin": 3, "pr": 4}


def _dataset(
    variables: tuple[str, ...],
    unit_of: dict[str, str],
    time: pd.DatetimeIndex,
    chunked: bool,
) -> xr.Dataset:
    data = {}
    for variable in variables:
        values = _reference_data(variable, time)
        conversion = (PRECIPITATION_UNITS if variable == "pr" else TEMPERATURE_UNITS)[
            unit_of[variable]
        ]
        data[variable] = xr.DataArray(
            conversion(values),
            dims=("time", "x"),
            coords={
                "time": time,
                "x": np.arange(N_CELLS),
                # Some indices (HI) need the latitude of the data.
                "lat": ("x", [42.0, 47.0]),
            },
            name=variable,
            attrs={"units": unit_of[variable]},
        )
    ds = xr.Dataset(data)
    return ds.chunk({"x": 1}) if chunked else ds


def _call(function: Callable, *args, **kwargs):
    accepted = inspect.signature(function).parameters
    return function(
        *args,
        **{key: value for key, value in kwargs.items() if key in accepted},
    )


class Case:
    """One index to check: how to call it and which variables it needs."""

    def __init__(
        self,
        id_,
        variables,
        call,
        needs_base=False,
        needs_normal=False,
        slices_study=True,
    ):
        self.id = id_
        self.variables = variables
        self.call = call
        self.needs_base = needs_base
        self.needs_normal = needs_normal
        self.slices_study = slices_study

    def run(self, unit_of: dict[str, str], chunked: bool) -> xr.DataArray:
        time = TIME
        study = _dataset(self.variables, unit_of, time, chunked)
        kwargs = {"out_file": None, "completeness": "none"}
        if self.needs_base:
            kwargs["base_period_time_range"] = BASE
            if self.slices_study:
                kwargs["time_range"] = STUDY
        if self.needs_normal:
            kwargs["normal"] = _dataset(self.variables, unit_of, NORMAL_TIME, False)
        result = self.call(study, **kwargs)
        name = next(
            v
            for v in result.data_vars
            if "bounds" not in v and not v.endswith("_bnds") and "date" not in v
        )
        return result[name].compute()


def _standard_cases() -> list[Case]:
    cases = []
    for registry_name, registry, module in (
        ("ecad", EcadIndexRegistry, icclim.ecad),
        ("dcsc", DcscIndexRegistry, icclim.dcsc),
    ):
        for index in registry.values():
            names = [v.short_name for v in (index.input_variables or [])]
            if not names or any(n not in STANDARD_VARIABLES for n in names):
                continue
            variables = tuple(STANDARD_VARIABLES[n] for n in names)
            qualifiers = index.qualifiers or []
            function = getattr(module, index.short_name.lower())
            cases.append(
                Case(
                    f"{registry_name}:{index.short_name}",
                    variables,
                    lambda ds, _f=function, **kw: _call(_f, ds, **kw),
                    needs_base="QUANTILE_BASED" in qualifiers
                    or "REFERENCE_PERIOD_INDEX" in qualifiers,
                    needs_normal="NEEDS_NORMAL" in qualifiers,
                    # SPI is computed on the whole series, calibrated on the reference.
                    slices_study=index.short_name not in ("SPI3", "SPI6"),
                )
            )
    return cases


# name -> (variables, extra keyword arguments), per kind of input.
_TEMPERATURE_THRESHOLD = "> 12 degC"
_PRECIPITATION_THRESHOLD = "> 1 mm/day"
GENERIC = {
    "count_occurrences": {"threshold": "{t}"},
    "max_consecutive_occurrence": {"threshold": "{t}"},
    "sum_of_spell_lengths": {"threshold": "{t}", "min_spell_length": 3},
    "excess": {"threshold": "{v}"},
    "deficit": {"threshold": "{v}"},
    "fraction_of_total": {"threshold": "{t}"},
    "maximum": {},
    "minimum": {},
    "average": {},
    "sum": {},
    "standard_deviation": {},
    "max_of_rolling_sum": {"rolling_window_width": 3},
    "min_of_rolling_sum": {"rolling_window_width": 3},
    "max_of_rolling_average": {"rolling_window_width": 3},
    "min_of_rolling_average": {"rolling_window_width": 3},
}
GENERIC_TWO_VARIABLES = (
    "mean_of_difference",
    "difference_of_extremes",
    "mean_of_absolute_one_time_step_difference",
)


def _generic_cases() -> list[Case]:
    cases = []
    registered = {g.name for g in GenericIndicatorRegistry.values()}
    for name, extra in GENERIC.items():
        if name not in registered:
            continue
        function = getattr(icclim, name)
        for variable, threshold, value in (
            ("tas", _TEMPERATURE_THRESHOLD, "12 degC"),
            ("pr", _PRECIPITATION_THRESHOLD, "1 mm/day"),
        ):
            kwargs = {
                k: v.format(t=threshold, v=value) if isinstance(v, str) else v
                for k, v in extra.items()
            }
            cases.append(
                Case(
                    f"generic:{name}:{variable}",
                    (variable,),
                    lambda ds, _f=function, _kw=kwargs, **kw: _call(
                        _f, ds, **_kw, **kw
                    ),
                )
            )
    for name in GENERIC_TWO_VARIABLES:
        if name in registered:
            function = getattr(icclim, name)
            cases.append(
                Case(
                    f"generic:{name}:tasmax-tasmin",
                    ("tasmax", "tasmin"),
                    lambda ds, _f=function, **kw: _call(_f, ds, **kw),
                )
            )
    if "difference_of_means" in registered:
        cases.append(
            Case(
                "generic:difference_of_means:tasmax-tasmin",
                ("tasmax", "tasmin"),
                lambda ds, _f=icclim.difference_of_means, **kw: _call(_f, ds, **kw),
            )
        )
    return cases


CASES = _standard_cases() + _generic_cases()
CASE_IDS = [case.id for case in CASES]

# Failures found by this test on master, kept as strict expected failures: when one is
# fixed the test passes unexpectedly and fails, which says to remove its entry.
_EXCESS = (
    "excess and deficit of a precipitation raise KeyError('units'): the units are lost"
    " before delta_ is added to them (seen with xarray 2026.2 and 2026.9, not with"
    " xarray 2024.11 and 2025.1)"
)
XFAIL = {
    "generic:excess:pr": _EXCESS,
    "generic:deficit:pr": _EXCESS,
}


# Failures that depend on the version of xarray (the lowest set does not have them).
XFAIL_FROM_XARRAY = {"generic:excess:pr", "generic:deficit:pr"}
XARRAY_2026 = Version(xr.__version__) >= Version("2026.1")


def _marked(case_id: str):
    marks = []
    if case_id in XFAIL:
        condition = XARRAY_2026 if case_id in XFAIL_FROM_XARRAY else True
        marks.append(
            pytest.mark.xfail(strict=True, condition=condition, reason=XFAIL[case_id])
        )
    return pytest.param(CASES[CASE_IDS.index(case_id)], id=case_id, marks=marks)


def _unit_combinations(case: Case):
    """Each combination of input units, the first one being the reference."""
    temperature = [v for v in case.variables if v != "pr"]
    precipitation = "pr" in case.variables
    if temperature and precipitation:
        pairs = [("degC", "mm/day"), ("K", "kg m-2 s-1"), ("degF", "mm/day")]
    elif temperature:
        pairs = [(u, None) for u in TEMPERATURE_UNITS]
    else:
        pairs = [(None, u) for u in PRECIPITATION_UNITS]
    for temperature_unit, precipitation_unit in pairs:
        unit_of = dict.fromkeys(temperature, temperature_unit)
        if precipitation:
            unit_of["pr"] = precipitation_unit
        yield unit_of


def _in_reference_units(result: xr.DataArray, reference: xr.DataArray) -> np.ndarray:
    """The values of ``result`` in the units of ``reference``."""
    if result.attrs.get("units") == reference.attrs.get("units"):
        return result.values
    return convert_units_to(result, reference.attrs["units"], context="hydro").values


def _assert_equivalent_units(result: xr.DataArray, reference: xr.DataArray) -> None:
    """The output units can be converted to the reference ones."""
    got, expected = result.attrs.get("units"), reference.attrs.get("units")
    assert got is not None, "the result has no units"
    if got == expected:
        return
    # Raises when the units are not equivalent (precipitation: hydro context).
    convert_units_to(
        xr.DataArray([1.0], attrs={"units": got}), expected, context="hydro"
    )


@pytest.mark.parametrize("case", [_marked(i) for i in CASE_IDS])
def test_same_data_in_other_units_gives_the_same_result(case: Case) -> None:
    combinations = list(_unit_combinations(case))
    reference_units = combinations[0]
    reference = case.run(reference_units, chunked=False)
    problems = []
    for unit_of in combinations:
        for chunked in (False, True):
            if unit_of == reference_units and not chunked:
                continue
            label = f"{unit_of} {'chunked' if chunked else 'eager'}"
            try:
                result = case.run(unit_of, chunked)
                _assert_equivalent_units(result, reference)
                np.testing.assert_allclose(
                    _in_reference_units(result, reference),
                    reference.values,
                    rtol=1e-6,
                    atol=1e-6,
                    equal_nan=True,
                )
            except Exception as error:  # noqa: BLE001
                problems.append(f"{label}: {type(error).__name__}: {str(error)[:120]}")
    assert not problems, " | ".join(problems)


# An index called twice in one process: the text of the pint units changes after the
# first xclim call, which used to break conversions (issue #617).
TWICE = [
    "ecad:TG",
    "ecad:TX90p",
    "ecad:SU",
    "ecad:DTR",
    "ecad:RR1",
    "dcsc:TXND",
    "dcsc:TNCWD",
]


@pytest.mark.parametrize(
    "case_id",
    [
        pytest.param(
            i,
            marks=(
                pytest.mark.xfail(strict=True, reason=XFAIL[i]) if i in XFAIL else []
            ),
        )
        for i in TWICE
    ],
)
def test_an_index_called_twice_in_one_process_gives_the_same_result(
    case_id: str,
) -> None:
    case = CASES[CASE_IDS.index(case_id)]
    combinations = list(_unit_combinations(case))
    first = [case.run(unit_of, chunked=False) for unit_of in combinations]
    second = [case.run(unit_of, chunked=False) for unit_of in combinations]
    for a, b, unit_of in zip(first, second, combinations, strict=True):
        np.testing.assert_array_equal(a.values, b.values, err_msg=str(unit_of))
        assert a.attrs.get("units") == b.attrs.get("units"), unit_of
        np.testing.assert_allclose(
            _in_reference_units(b, first[0]), first[0].values, rtol=1e-6, atol=1e-6
        )
