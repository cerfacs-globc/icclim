import numpy as np
import pandas as pd
import xarray as xr

from icclim import create_optimized_zarr_store


def test_create_optimized_zarr_store_success():
    ds = xr.Dataset(
        {
            "tas": xr.DataArray(
                data=np.full(10, 42).reshape((10, 1, 1)),
                coords=dict(
                    lat=[42],
                    lon=[42],
                    time=pd.date_range("2042-01-01", periods=10, freq="D"),
                ),
                dims=["time", "lat", "lon"],
                name="pr",
                attrs={"units": "kg m-2 d-1"},
            )
        }
    ).chunk({"time": 2})
    with create_optimized_zarr_store(
        in_files=ds,
        var_names="tas",
        target_zarr_store_name="yolo.zarr",
        dim="time",
    ) as result:
        assert len(result.chunks["time"]) == 1
        np.testing.assert_array_equal(result.tas.values, ds.tas.values)
        np.testing.assert_array_equal(result.data_vars.keys(), ds.data_vars.keys())
