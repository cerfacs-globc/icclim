from icclim.models.frequency import (
    Frequency,
    build_frequency,
    month_resampler,
    seasons_resampler,
    winter_resampler,
)
import pandas as pd
import pytest
import xarray
import numpy as np


class Test_build_frequency_over_frequency:
    def test_simple(self):
        freq = build_frequency(Frequency.YEAR)
        assert freq == Frequency.YEAR


class Test_build_frequency_over_string:
    def test_error(self):
        with pytest.raises(Exception) as exc:
            build_frequency("yolo")

    def test_simple(self):
        freq = build_frequency("year")
        assert freq == Frequency.YEAR


class Test_build_frequency_over_list:
    def test_error(self):
        with pytest.raises(Exception) as exc:  # TODO use a more specific exception
            build_frequency(["cacahuêtes"])

    def test_month(self):
        freq = build_frequency(["month", [1, 4, 3]])
        assert isinstance(freq, Frequency)
        assert freq.panda_freq == "MS"
        assert freq.accepted_values == []
        assert freq.resampler is not None

    def test_season(self):
        freq = build_frequency(["season", [1, 2, 3, 4]])
        assert isinstance(freq, Frequency)
        assert freq.panda_freq == "MS"
        assert freq.accepted_values == []
        assert freq.resampler is not None


class Test_month_resampler:
    def test_simple(self):
        # WHEN
        da = month_resampler([1, 2, 7])(STUB_DA)
        # THEN
        months = np.unique(da.time.dt.month)
        assert len(months) == 3
        assert months[0] == 1
        assert months[1] == 2
        assert months[2] == 7


class Test_winter_resampler:
    def test_simple(self):
        # WHEN
        da = winter_resampler(10, 3)(STUB_DA)
        # THEN
        months = np.unique(da.time.dt.month)
        assert len(months) == 6
        assert months[0] == 1
        assert months[1] == 2
        assert months[2] == 3
        assert months[3] == 10
        assert months[4] == 11
        assert months[5] == 12


class Test_winter_resampler:
    def test_simple(self):
        # WHEN
        da = seasons_resampler(4, 9)(STUB_DA)
        # THEN
        months = np.unique(da.time.dt.month)
        assert len(months) == 6
        assert months[0] == 4
        assert months[1] == 5
        assert months[2] == 6
        assert months[3] == 7
        assert months[4] == 8
        assert months[5] == 9


STUB_DA = xarray.DataArray(
    data=np.zeros(366 * 5),
    dims=["time"],
    coords=dict(time=pd.date_range("2042-01-01", periods=366 * 5),),
)

