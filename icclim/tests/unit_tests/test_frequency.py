import numpy as np
import pandas as pd
import pytest

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import Frequency, month_filter, seasons_resampler
from icclim.tests.unit_tests.test_utils import stub_tas


class Test_build_frequency_over_frequency:
    def test_simple(self):
        freq = Frequency.lookup(Frequency.YEAR)
        assert freq == Frequency.YEAR


class Test_build_frequency_over_string:
    def test_error(self):
        with pytest.raises(InvalidIcclimArgumentError):
            Frequency.lookup("yolo")

    def test_simple(self):
        freq = Frequency.lookup("year")
        assert freq == Frequency.YEAR


class Test_build_frequency_over_list:
    def test_error(self):
        with pytest.raises(InvalidIcclimArgumentError):
            Frequency.lookup(["cacahuêtes"])

    def test_month(self):
        freq = Frequency.lookup(["month", [1, 4, 3]])
        assert freq == Frequency.CUSTOM
        assert freq.panda_freq == "MS"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_season(self):
        freq = Frequency.lookup(["season", [1, 2, 3, 4]])
        assert freq == Frequency.CUSTOM
        assert freq.panda_freq == "MS"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_winter_deprecated(self):
        # deprecated way
        freq = Frequency.lookup(["season", ([11, 12], [3, 4])])
        assert freq == Frequency.CUSTOM
        assert freq.panda_freq == "MS"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_winter(self):
        freq = Frequency.lookup(["season", [11, 12, 1, 2]])
        assert freq == Frequency.CUSTOM
        assert freq.panda_freq == "MS"
        assert freq.accepted_values == []
        assert freq.post_processing is not None


class Test_filter_months:
    def test_simple(self):
        # WHEN
        da = month_filter(stub_tas(), [1, 2, 7])
        # THEN
        months = np.unique(da.time.dt.month)
        assert len(months) == 3
        assert months[0] == 1
        assert months[1] == 2
        assert months[2] == 7


class Test_seasons_resampler:
    def test_simple(self):
        # WHEN
        da_res, time_bds_res = seasons_resampler([4, 5, 6])(stub_tas())
        # THEN
        assert da_res[0] == 91
        assert time_bds_res[0].data[0] == pd.to_datetime("2042-04")
        assert (
            time_bds_res[0].data[1]
            == pd.to_datetime("2042-07") - pd.tseries.offsets.Day()
        )

    def test_winter(self):
        # WHEN
        da_res, time_bds_res = seasons_resampler([11, 12, 1])(stub_tas())
        # THEN
        assert da_res[0] == 31
        assert time_bds_res[0].data[0] == pd.to_datetime("2041-11")
        assert (
            time_bds_res[0].data[1]
            == pd.to_datetime("2042-02") - pd.tseries.offsets.Day()
        )
        assert da_res[1] == 92
        assert time_bds_res[1].data[0] == pd.to_datetime("2042-11")
        assert (
            time_bds_res[1].data[1]
            == pd.to_datetime("2043-02") - pd.tseries.offsets.Day()
        )

    def test_season_with_holes(self):
        # WHEN
        da_res, time_bds_res = seasons_resampler([1, 3, 4])(stub_tas())
        # THEN
        assert da_res[0] == 92
        assert time_bds_res[0].data[0] == pd.to_datetime("2042-01")
        assert (
            time_bds_res[0].data[1]
            == pd.to_datetime("2042-05") - pd.tseries.offsets.Day()
        )
