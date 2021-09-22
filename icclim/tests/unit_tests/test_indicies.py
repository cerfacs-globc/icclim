import pytest
from xarray import Dataset

from icclim.eca_indices import Indice, indice_from_string, tn10p
from icclim.models.frequency import Frequency
from icclim.models.indice_config import IndiceConfig
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.tests.unit_tests.test_utils import stub_tas


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


@pytest.mark.parametrize("use_dask", [True, False])
def test_tn10p_interpolation_error(use_dask):
    ds = Dataset()
    ds["tas"] = stub_tas(use_dask=use_dask)
    conf = IndiceConfig(
        ds=ds,
        slice_mode=Frequency.MONTH,
        var_name=["tas"],
        netcdf_version=NetcdfVersion.NETCDF4,
        base_period_time_range=[
            ds.time.values[0].astype("M8[D]").astype("O"),
            ds.time.values[-1].astype("M8[D]").astype("O"),
        ],
        window_width=2,
    )
    with pytest.raises(Exception):
        tn10p(conf)


@pytest.mark.parametrize("use_dask", [True, False])
def test_tn10p(use_dask):
    ds = Dataset()
    ds["tas"] = stub_tas(use_dask=use_dask)
    conf = IndiceConfig(
        ds=ds,
        slice_mode=Frequency.MONTH,
        var_name=["tas"],
        netcdf_version=NetcdfVersion.NETCDF4,
        base_period_time_range=[
            ds.time.values[0].astype("M8[D]").astype("O"),
            ds.time.values[-1].astype("M8[D]").astype("O"),
        ],
        window_width=2,
        interpolation=QuantileInterpolation.MEDIAN_UNBIASED,
    )
    res = tn10p(conf)
    assert res is not None
