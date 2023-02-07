from __future__ import annotations

import os
import shutil

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import UNITS_KEY
from icclim.pre_processing.input_parsing import (
    PercentileDataArray,
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
                attrs={UNITS_KEY: "kg m-2 d-1"},
            )
        }
    )
    # WHEN
    res = update_to_standard_coords(ds)
    # THEN
    assert "time" in res.coords


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
                time=pd.date_range("2042-01-01", periods=10, freq="D"),
            ),
            dims=["time", "latitude", "longitude"],
            name="pr",
            attrs={UNITS_KEY: "kg m-2 d-1"},
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
            attrs={UNITS_KEY: "degC"},
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
        res_ds = read_dataset(self.OUTPUT_NC_FILE)
        # THEN
        # asserts variable names are the ones in the actual DataArray/Datasets
        assert "tas" in res_ds.data_vars

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
        ds["tontontonthetatilotetatoux"] = per
        # WHEN
        res_ds = read_dataset(ds)
        # THEN
        assert "tas" in res_ds.data_vars
        assert "tontontonthetatilotetatoux" in res_ds.data_vars

    def test_guess_variables__cant_guess_var_name(self):
        # GIVEN
        ds = xr.Dataset({"canard": self.tas_da, "bergeronnette": self.tas_da})
        # THEN
        with pytest.raises(InvalidIcclimArgumentError):
            # WHEN
            guess_var_names(ds, standard_index=EcadIndexRegistry.SU, var_names=None)

    def test_guess_variables__simple(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # WHEN
        res = guess_var_names(ds, standard_index=EcadIndexRegistry.TG, var_names=None)
        # THEN
        assert res == ["tas"]

    def test_guess_variables__from_string(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # WHEN
        res = guess_var_names(ds, standard_index=None, var_names="cocoLasticot")
        # THEN
        assert res == ["cocoLasticot"]

    def test_guess_variables__from_list(self):
        # GIVEN
        ds = xr.Dataset({"tas": self.tas_da})
        # WHEN
        res = guess_var_names(ds, standard_index=None, var_names=["pinçon"])
        # THEN
        assert res == ["pinçon"]

    def test_guess_variables__from_alias(self):
        # GIVEN
        ds = xr.Dataset({"tasmaxAdjust": self.tas_da, "turlututut": self.tas_da})
        # WHEN
        res = guess_var_names(ds, standard_index=EcadIndexRegistry.SU, var_names=None)
        # THEN
        assert res == ["tasmaxAdjust"]
