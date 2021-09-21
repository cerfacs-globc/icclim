import pytest
from models.netcdf_version import NetcdfVersion

from icclim.eca_indices import Indice, indice_from_string, tn10p
from icclim.models.frequency import Frequency
from icclim.models.indice_config import IndiceConfig
from icclim.tests.unit_tests.stubs import stub_tas


class Test_indice_from_string:
    def test_simple(self):
        res = indice_from_string("SU")
        assert res == Indice.SU

    def test_lowercase(self):
        res = indice_from_string("tx90p")
        assert res == Indice.TX90P

    def test_error(self):
        with pytest.raises(Exception):
            indice_from_string("cacahuête")


def test_tn10p():
    da = stub_tas()
    conf = IndiceConfig(
        ds=da,
        slice_mode=Frequency.MONTH,
        var_name=[""],
        netcdf_version=NetcdfVersion.NETCDF4,
        base_period_time_range=[
            da.time.values[0].astype("M8[D]").astype("O"),
            da.time.values[-1].astype("M8[D]").astype("O"),
        ],
        window_width=2,
        save_percentile=True,
    )
    res = tn10p(conf)
    assert res is not None
