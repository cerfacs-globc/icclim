from __future__ import annotations

import os
import shutil
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.utils import PercentileDataArray

from icclim.ecad.ecad_indices import EcadIndex
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.pre_processing.input_parsing import (
    InFileDictionary,
    guess_var_names,
    read_dataset,
    update_to_standard_coords,
)


def test_update_to_standard_coords():
    # GIVEN
    ds = xr.Dataset(
        {
            "pouet": xr.DataArray(
                data=np.full(10, 42).reshape((10, 1, 1)),
                coords=dict(
                    latitude=[42],
                    longitude=[42],
                    t=pd.date_range("2042-01-01", periods=10, freq="D"),
                ),
                dims=["t", "latitude", "longitude"],
                name="pr",
                attrs={"units": "kg m-2 d-1"},
            )
        }
    )
    # WHEN
    res, revert = update_to_standard_coords(ds)
    # THEN
    assert "lat" in res.coords
    assert "time" in res.coords
    assert "lon" in res.coords
    assert res.rename(revert).coords.keys() == ds.coords.keys()


class Test_ReadDataset:
    OUTPUT_NC_FILE = "tmp.nc"
    OUTPUT_NC_FILE_2 = "tmp-2.nc"
    OUTPUT_ZARR_STORE = "tmp.zarr"
    OUTPUT_UNKNOWN_FORMAT = "tmp.cacahuete"
    pr_da = None
    tas_da = None

    @pytest.fixture(autouse=True)
    def cleanup(self):
        # -- setup
        self.pr_da = xr.DataArray(
            data=np.full(10, 42).reshape((10, 1, 1)),
            coords=dict(
                latitude=[42],
                longitude=[42],
                t=pd.date_range("2042-01-01", periods=10, freq="D"),
            ),
            dims=["t", "latitude", "longitude"],
            name="pr",
            attrs={"units": "kg m-2 d-1"},
        )
        self.tas_da = xr.DataArray(
            data=np.full(10, 42).reshape((10, 1, 1)),
            coords=dict(
                latitude=[42],
                longitude=[42],
                t=pd.date_range("2042-01-01", periods=10, freq="D"),
            ),
            dims=["t", "latitude", "longitude"],
            name="tas",
            attrs={"units": "degC"},
        )
        yield
        # -- teardown
        shutil.rmtree(self.OUTPUT_ZARR_STORE, ignore_errors=True)
        for f in [
            self.OUTPUT_NC_FILE,
            self.OUTPUT_NC_FILE_2,
            self.OUTPUT_UNKNOWN_FORMAT,
        ]:
            try:
                os.remove(f)
            except FileNotFoundError:
                pass

    def test_read_dataset_xr_DataArray__simple(self):
        # WHEN
        res = read_dataset(self.pr_da)
        # THEN
        assert "pr" in res.data_vars

    def test_read_dataset_xr_DataArray__error_1_var_when_2_needed(self):
        # THEN
        with pytest.raises(InvalidIcclimArgumentError):
            # WHEN
            read_dataset(self.pr_da, EcadIndex.WW)

    def test_read_dataset_xr_DataArray__rename_var(self):
        # WHEN
        ds_res = read_dataset(self.pr_da, EcadIndex.TX90P)
        # THEN
        xr.testing.assert_equal(ds_res.tasmax, self.pr_da)

    def test_read_dataset_xr_da_user_index_success(self):
        # WHEN
        ds_res = read_dataset(self.pr_da, None)
        # THEN
        xr.testing.assert_equal(ds_res.pr, self.pr_da)

    def test_read_dataset_xr_ds__simple(self):
        # GIVEN
        ds = xr.Dataset({"pouet": self.pr_da})
        # WHEN
        ds_res = read_dataset(ds)
        # THEN
        xr.testing.assert_equal(ds_res.pouet, ds.pouet)

    def test_read_dataset_netcdf_success(self):
        # GIVEN
        ds = xr.Dataset({"pouet": self.pr_da})
        ds.to_netcdf(self.OUTPUT_NC_FILE)
        # WHEN
        ds_res = read_dataset(self.OUTPUT_NC_FILE)
        # THEN
        xr.testing.assert_equal(ds_res.pouet, ds.pouet)

    def test_read_dataset_multi_netcdf_success(self):
        # GIVEN
        ds = xr.Dataset({"pouet": self.pr_da})
        ds.to_netcdf(self.OUTPUT_NC_FILE)
        ds.rename({"pouet": "patapouet"}).to_netcdf(self.OUTPUT_NC_FILE_2)
        # WHEN
        ds_res = read_dataset([self.OUTPUT_NC_FILE, self.OUTPUT_NC_FILE_2])
        # THEN
        xr.testing.assert_equal(ds_res.pouet, ds.pouet)
        xr.testing.assert_equal(ds_res.patapouet, ds.pouet)

    def test_read_dataset_zarr_store_success(self):
        # GIVEN
        ds = xr.Dataset({"pouet": self.pr_da})
        ds.to_zarr(self.OUTPUT_ZARR_STORE)
        # WHEN
        ds_res = read_dataset(self.OUTPUT_ZARR_STORE)
        # THEN
        xr.testing.assert_equal(ds_res.pouet, ds.pouet)

    def test_read_dataset_not_implemented_error(self):
        # THEN
        with pytest.raises(NotImplementedError):
            # WHEN
            read_dataset(42)  # noqa

    def test_read_dataset(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        ds.to_netcdf(self.OUTPUT_NC_FILE)
        # WHEN
        res_ds = read_dataset(
            in_data={"ninja": self.OUTPUT_NC_FILE, "precipitoto": self.pr_da}
        )
        # THEN
        # asserts variable names are the ones in the actual DataArray/Datasets
        assert "ninja" not in res_ds.data_vars
        assert "precipitoto" in res_ds.data_vars
        assert "tas" in res_ds.data_vars
        assert "pr" not in res_ds.data_vars

    def test_read_dataset__with_percentiles(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        ds.to_netcdf(self.OUTPUT_NC_FILE)
        per = self.tas_da
        per.coords["percentiles"] = 42
        per = per.rename("tontontonthetatilotetatoux").expand_dims("percentiles")
        per = PercentileDataArray.from_da(
            per, climatology_bounds=["1994-12-02", "1999-01-01"]
        )
        # WHEN
        res_ds = read_dataset(
            in_data={
                "tatas": {
                    "study": ds,
                    "thresholds": per,
                    "climatology_bounds": ("1994-12-02", "1999-01-01"),
                    "per_var_name": "tontontonthetatilotetatoux",
                }
            }
        )
        # THEN
        assert "tas" in res_ds.data_vars
        # A bit weird that
        assert "tatas_thresholds" in res_ds.data_vars

    def test_read_dataset__error_no_percentiles_dimension(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        ds.to_netcdf(self.OUTPUT_NC_FILE)
        # WHEN
        tas: InFileDictionary = {
            "study": ds,
            "thresholds": self.tas_da,
        }
        # THEN
        with pytest.raises(InvalidIcclimArgumentError):
            # WHEN
            read_dataset(in_data={"tatas": tas})

    def test_guess_variables__error_no_index(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # THEN
        with pytest.raises(InvalidIcclimArgumentError):
            # WHEN
            guess_var_names(ds)

    def test_guess_variables__error_too_many_args(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # THEN
        with pytest.raises(InvalidIcclimArgumentError):
            # WHEN
            guess_var_names(ds, in_data={}, var_names=["coin-coin"])

    def test_guess_variables__error_wrong_name_for_index(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # THEN
        with pytest.raises(InvalidIcclimArgumentError):
            # WHEN
            guess_var_names(ds, index=EcadIndex.DTR.climate_index)

    def test_guess_variables__simple(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # WHEN
        res = guess_var_names(ds, index=EcadIndex.TG.climate_index)
        # THEN
        assert res == ["tas"]

    @patch("icclim.pre_processing.input_parsing.InFileType")
    def test_guess_variables__from_dict(self, in_file_mock: MagicMock):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # WHEN
        res = guess_var_names(ds, in_data={"pouet": in_file_mock})
        # THEN
        assert res == ["pouet"]

    def test_guess_variables__from_string(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # WHEN
        res = guess_var_names(ds, var_names="cocoLasticot")
        # THEN
        assert res == ["cocoLasticot"]

    def test_guess_variables__from_list(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # WHEN
        res = guess_var_names(ds, var_names=["pinçon"])
        # THEN
        assert res == ["pinçon"]

    def test_guess_variables__from_alias(self):
        # GIVEN
        ds = xr.Dataset({"tasmaxAdjust": self.tas_da})
        # WHEN
        res = guess_var_names(ds, index=EcadIndex.SU.climate_index)
        # THEN
        assert res == ["tasmaxAdjust"]
