from __future__ import annotations

import pandas as pd

from icclim._core.generic.threshold.percentile import (
    _build_single_bootstrap_reference,
)
from tests.testing_utils import stub_tas


def test_build_single_bootstrap_reference__common_year_target_from_leap_donor() -> None:
    tas = stub_tas()
    groups = tas.resample(time="YS").groups

    boot_ref = _build_single_bootstrap_reference(
        tas,
        groups,
        pd.Timestamp("2045-01-01"),
        pd.Timestamp("2044-01-01"),
    )

    target_time = tas.sel(time=slice("2045-01-01", "2045-12-31")).time
    replaced_time = boot_ref.sel(time=slice("2045-01-01", "2045-12-31")).time

    assert boot_ref.sizes["time"] == tas.sizes["time"]
    assert replaced_time.equals(target_time)
    assert len(replaced_time) == 365
    assert boot_ref.indexes["time"].is_unique


def test_build_single_bootstrap_reference__leap_year_target_from_common_donor() -> None:
    tas = stub_tas()
    groups = tas.resample(time="YS").groups

    boot_ref = _build_single_bootstrap_reference(
        tas,
        groups,
        pd.Timestamp("2044-01-01"),
        pd.Timestamp("2045-01-01"),
    )

    target_time = tas.sel(time=slice("2044-01-01", "2044-12-31")).time
    replaced_time = boot_ref.sel(time=slice("2044-01-01", "2044-12-31")).time

    assert boot_ref.sizes["time"] == tas.sizes["time"]
    assert replaced_time.equals(target_time)
    assert len(replaced_time) == 366
    assert boot_ref.indexes["time"].is_unique
