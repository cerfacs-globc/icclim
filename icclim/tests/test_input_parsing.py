import os
import shutil

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.ecad_indices import EcadIndex
from icclim.pre_processing.input_parsing import read_dataset, update_to_standard_coords


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

    @pytest.fixture(autouse=True)
    def cleanup(self):
        # setup
        yield
        # teardown
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

    def test_read_dataset_xr_da_user_index_error(self):
        da = xr.DataArray(
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
        with pytest.raises(InvalidIcclimArgumentError):
            read_dataset(da)

    def test_read_dataset_xr_da_ecad_index_error(self):
        da = xr.DataArray(
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
        with pytest.raises(InvalidIcclimArgumentError):
            read_dataset(da, EcadIndex.WW)

    def test_read_dataset_xr_da_ecad_index_success(self):
        da = xr.DataArray(
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
        ds_res, chunk_it, is_zarr = read_dataset(da, EcadIndex.TX90P)
        xr.testing.assert_equal(ds_res.tasmax, da)
        assert chunk_it is False
        assert is_zarr is False

    def test_read_dataset_xr_da_user_index_success(self):
        da = xr.DataArray(
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
        ds_res, chunk_it, is_zarr = read_dataset(da, None, "doto")
        xr.testing.assert_equal(ds_res.doto, da)
        assert chunk_it is False
        assert is_zarr is False

    def test_read_dataset_xr_ds_success(self):
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
        ds_res, chunk_it, is_zarr = read_dataset(ds)
        xr.testing.assert_equal(ds_res.pouet, ds.pouet)
        assert chunk_it is False
        assert is_zarr is False

    def test_read_dataset_netcdf_success(self):
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
        ds.to_netcdf(self.OUTPUT_NC_FILE)
        ds_res, chunk_it, is_zarr = read_dataset(self.OUTPUT_NC_FILE)
        xr.testing.assert_equal(ds_res.pouet, ds.pouet)
        assert chunk_it is True
        assert is_zarr is False

    def test_read_dataset_multi_netcdf_success(self):
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
        ds.to_netcdf(self.OUTPUT_NC_FILE)
        ds.rename({"pouet": "patapouet"}).to_netcdf(self.OUTPUT_NC_FILE_2)
        # WHEN
        ds_res, chunk_it, is_zarr = read_dataset(
            [self.OUTPUT_NC_FILE, self.OUTPUT_NC_FILE_2]
        )
        # THEN
        xr.testing.assert_equal(ds_res.pouet, ds.pouet)
        xr.testing.assert_equal(ds_res.patapouet, ds.pouet)
        assert chunk_it is True
        assert is_zarr is False

    def test_read_dataset_zarr_store_success(self):
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
        ds.to_zarr(self.OUTPUT_ZARR_STORE)
        # WHEN
        ds_res, chunk_it, is_zarr = read_dataset(self.OUTPUT_ZARR_STORE)
        # THEN
        xr.testing.assert_equal(ds_res.pouet, ds.pouet)
        assert chunk_it is True
        assert is_zarr is True

    def test_read_dataset_not_implemented_error(self):
        # WHEN
        with pytest.raises(NotImplementedError):
            read_dataset(42)  # noqa
