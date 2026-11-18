"""
Every threshold and unit written in the generated functions can be parsed.

The generated code is built on one environment and runs on all the supported pint and
xclim versions: a unit symbol that only some of them define (such as "kn" for a knot)
breaks the function at call time (the lowest versions job of the CI runs this).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pint
import pytest
from xclim.core.units import units as xclim_units

import icclim
from icclim._core.model.quantile_interpolation import QuantileInterpolationRegistry
from icclim.dcsc.registry import DcscIndexRegistry
from icclim.ecad.registry import EcadIndexRegistry
from icclim.main import _parse_indicator_config, _parse_threshold
from icclim.threshold.factory import build_threshold

GENERATED_DIR = Path(icclim.__file__).parent / "_generated"


def _generated_threshold_calls() -> list[tuple[str, dict[str, str]]]:
    calls = []
    for path in sorted(GENERATED_DIR.glob("_*.py")):
        tree = ast.parse(path.read_text())
        for function in (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)):
            for call in ast.walk(function):
                if not (
                    isinstance(call, ast.Call)
                    and getattr(call.func, "id", "") == "build_threshold"
                ):
                    continue
                literals = {
                    k.arg: k.value.value
                    for k in call.keywords
                    if k.arg in ("query", "threshold_min_value")
                    and isinstance(k.value, ast.Constant)
                }
                if "query" in literals:
                    calls.append((f"{path.stem[1:]}.{function.name}", literals))
    return calls


CALLS = _generated_threshold_calls()


def test_the_generated_functions_have_thresholds_to_check() -> None:
    assert len(CALLS) > 50
    assert any("threshold_min_value" in literals for _, literals in CALLS)


@pytest.mark.parametrize(
    ("function", "literals"), CALLS, ids=[name for name, _ in CALLS]
)
def test_generated_threshold_is_parsed(function: str, literals: dict[str, str]) -> None:
    build_threshold(**literals)


@pytest.mark.parametrize(
    "min_value",
    sorted(
        {lit["threshold_min_value"] for _, lit in CALLS if "threshold_min_value" in lit}
    ),
)
def test_generated_min_value_units_are_defined_in_pint_and_xclim(
    min_value: str,
) -> None:
    pint.UnitRegistry().Quantity(min_value)
    xclim_units.Quantity(min_value)


@pytest.mark.parametrize(
    "index",
    [*EcadIndexRegistry.values(), *DcscIndexRegistry.values()],
    ids=lambda i: i.short_name,
)
def test_registry_default_threshold_is_parsed(index) -> None:
    config = _parse_indicator_config(index, None, None)
    _parse_threshold(
        config.threshold,
        doy_window_width=5,
        reference_period=["2000-01-01", "2009-12-31"],
        only_leap_years=False,
        interpolation=QuantileInterpolationRegistry.MEDIAN_UNBIASED,
    )
