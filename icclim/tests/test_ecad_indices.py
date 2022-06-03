from __future__ import annotations

import numpy as np
import pytest

from icclim.ecad.ecad_functions import (
    cfd,
    csdi,
    csu,
    fd,
    gd4,
    hd17,
    prcptot,
    su,
    tn10p,
    tr,
    tx90p,
    wsdi,
)
from icclim.ecad.ecad_indices import EcadIndex
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import Frequency
from icclim.models.index_config import CfVariable, IndexConfig
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.tests.testing_utils import K2C, stub_pr, stub_tas


def test_listing():
    res = EcadIndex.list()
    assert len(res) == len(EcadIndex)


class Test_index_from_string:
    def test_simple(self):
        res = EcadIndex.lookup("SU")
        assert res == EcadIndex.SU

    def test_lowercase(self):
        res = EcadIndex.lookup("tx90p")
        assert res == EcadIndex.TX90P

    def test_error(self):
        with pytest.raises(InvalidIcclimArgumentError):
            EcadIndex.lookup("cacahuête")


@pytest.mark.parametrize("use_dask", [True, False])
def test_tn10p(use_dask):
    tas = stub_tas(use_dask=use_dask)
    conf = IndexConfig(
        frequency=Frequency.MONTH,
        cf_variables=[CfVariable("tas", tas, tas)],
        netcdf_version=NetcdfVersion.NETCDF4,
        window_width=2,
        interpolation=QuantileInterpolation.MEDIAN_UNBIASED,
        save_percentile=True,
        index=EcadIndex.TN10P.climate_index,
    )
    res = tn10p(conf)
    assert res is not None


class Test_SU:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_su_default_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[:5] = 0
        conf = IndexConfig(
            frequency=Frequency.MONTH,
            cf_variables=[CfVariable("tas", tas)],
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.SU.climate_index,
        )
        res = su(conf)
        assert res is not None
        assert res[0][0] == 26  # January

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_su_custom_threshold(self, use_dask):
        tas = stub_tas(use_dask=use_dask)
        tas[:5] = 50 + K2C
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            threshold=40,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.SU.climate_index,
        )
        res = su(conf)
        assert res is not None
        assert res[0][0] == 5  # January


class Test_TR:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_default_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[:5] = 0
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.TR.climate_index,
        )
        res = tr(conf)
        assert res is not None
        assert res[0][0] == 26  # January

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_custom_threshold(self, use_dask):
        tas = stub_tas(use_dask=use_dask)
        tas[:5] = 50 + K2C
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            threshold=40,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.TR.climate_index,
        )
        res = tr(conf)
        assert res is not None
        assert res[0][0] == 5  # January


class Test_prcptot:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_default_threshold(self, use_dask):
        pr = stub_pr(value=2, use_dask=use_dask)
        pr[:10] = 0
        conf = IndexConfig(
            frequency=Frequency.MONTH,
            cf_variables=[CfVariable("pr", pr)],
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.PRCPTOT.climate_index,
        )
        res = prcptot(conf)
        assert res is not None
        np.testing.assert_almost_equal(res[0][0], 42.0, 14)


class Test_csu:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_default_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[10:15] = 0
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.CSU.climate_index,
        )
        res = csu(conf)
        assert res is not None
        assert res[0][0] == 16  # January

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_custom_threshold(self, use_dask):
        tas = stub_tas(use_dask=use_dask)
        tas[:5] = 50 + K2C
        tas[10:20] = 50 + K2C
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            threshold=40,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.CSU.climate_index,
        )
        res = csu(conf)
        assert res is not None
        assert res[0][0] == 10  # January


class Test_gd4:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_default_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[5:15] = 0
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.GD4.climate_index,
        )
        res = gd4(conf)
        assert res is not None
        expected = (26 - 4) * 21
        assert res[0][0] == expected  # 21 days in January above 4 degC (at 26degC)

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_custom_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[5:15] = 0
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            threshold=5,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.GD4.climate_index,
        )
        res = gd4(conf)
        assert res is not None
        expected = (26 - 5) * 21
        assert res[0][0] == expected  # 21 days in January above 4 degC (at 26degC)


class Test_cfd:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_default_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[5:15] = 0
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.CFD.climate_index,
        )
        res = cfd(conf)
        assert res is not None
        assert res[0][0] == 10

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_custom_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[5:10] = 0
        tas[10:15] = 4
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            threshold=5,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.CFD.climate_index,
        )
        res = cfd(conf)
        assert res is not None
        assert res[0][0] == 10


class Test_fd:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_default_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[5:15] = 0
        tas[20:25] = 0
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.FD.climate_index,
        )
        res = fd(conf)
        assert res is not None
        assert res[0][0] == 15

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_custom_threshold(self, use_dask):
        tas = stub_tas(tas_value=26 + K2C, use_dask=use_dask)
        tas[5:10] = 0
        tas[10:15] = 4
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            threshold=5,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.FD.climate_index,
        )
        res = fd(conf)
        assert res is not None
        assert res[0][0] == 10


class Test_hd17:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_default_threshold(self, use_dask):
        tas = stub_tas(tas_value=27 + K2C, use_dask=use_dask)
        tas[5:10] = 0
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.HD17.climate_index,
        )
        res = hd17(conf)
        assert res is not None
        assert res[0][0] == 5 * (17 + K2C)

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_custom_threshold(self, use_dask):
        tas = stub_tas(tas_value=27 + K2C, use_dask=use_dask)
        tas[5:10] = 0
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas)],
            frequency=Frequency.MONTH,
            threshold=5,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.HD17.climate_index,
        )
        res = hd17(conf)
        assert res is not None
        assert res[0][0] == 5 * (5 + K2C)


class TestTx90p:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_no_bootstrap_no_overlap(self, use_dask):
        tas = stub_tas(tas_value=27 + K2C, use_dask=use_dask)
        tas[5:10] = 0
        base_tas = tas.sel(time=slice("2042-01-01", "2042-12-31"))
        tas = tas.sel(time=slice("2042-01-01", "2045-12-31"))
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas, base_tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.TX90P.climate_index,
        )
        res, _ = tx90p(conf)
        assert "reference_epoch" not in res.attrs.keys()

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_no_bootstrap_1_year_base(self, use_dask):
        tas = stub_tas(tas_value=27 + K2C, use_dask=use_dask)
        base_tas = tas.sel(
            time=slice("2042-01-01", "2042-12-31"),
        )
        tas = tas.sel(time=slice("2042-01-01", "2045-12-31"))
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas, base_tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.TX90P.climate_index,
        )
        res, _ = tx90p(conf)
        assert "reference_epoch" not in res.attrs.keys()

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_bootstrap_2_years(self, use_dask):
        tas = stub_tas(tas_value=27 + K2C, use_dask=use_dask)
        base_tas = tas.sel(
            time=slice("2042-01-01", "2043-12-31"),
        )
        tas = tas.sel(time=slice("2042-01-01", "2045-12-31"))
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas, base_tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.TX90P.climate_index,
        )
        res, _ = tx90p(conf)
        assert res.attrs["reference_epoch"] == ["2042-01-01", "2043-12-31"]


class TestWsdi:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_wsdi_bootstrap_2_years(self, use_dask):
        tas = stub_tas(tas_value=27 + K2C, use_dask=use_dask)
        base_tas = tas.sel(
            time=slice("2042-01-01", "2043-12-31"),
        )
        tas = tas.sel(time=slice("2042-01-01", "2045-12-31"))
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas, base_tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.TX90P.climate_index,
        )
        res, _ = wsdi(conf)
        assert res.attrs["reference_epoch"] == ["2042-01-01", "2043-12-31"]


class TestCsdi:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_csdi_bootstrap_2_years(self, use_dask):
        tas = stub_tas(tas_value=27 + K2C, use_dask=use_dask)
        base_tas = tas.sel(
            time=slice("2042-01-01", "2043-12-31"),
        )
        tas = tas.sel(time=slice("2042-01-01", "2045-12-31"))
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas, base_tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.TX90P.climate_index,
            save_percentile=True,
        )
        res, per = csdi(conf)
        assert res.attrs["reference_epoch"] == ["2042-01-01", "2043-12-31"]
        assert per.percentiles.values[0] == 10

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_csdi_custom_thresh(self, use_dask):
        tas = stub_tas(tas_value=27 + K2C, use_dask=use_dask)
        base_tas = tas.sel(
            time=slice("2042-01-01", "2043-12-31"),
        )
        tas = tas.sel(time=slice("2042-01-01", "2045-12-31"))
        conf = IndexConfig(
            cf_variables=[CfVariable("tas", tas, base_tas)],
            frequency=Frequency.MONTH,
            netcdf_version=NetcdfVersion.NETCDF4,
            index=EcadIndex.TX90P.climate_index,
            threshold=5,
            save_percentile=True,
        )
        res, per = csdi(conf)
        assert res.attrs["reference_epoch"] == ["2042-01-01", "2043-12-31"]
        assert per.percentiles.values[0] == 5
