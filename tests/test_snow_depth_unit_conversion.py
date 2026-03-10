from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

import icclim


def test_snow_depth_unit_conversion():
    time = pd.date_range("2000-01-01", periods=10)
    da = xr.DataArray(
        np.ones(10), coords=[time], dims=["time"], name="snd", attrs={"units": "mm/s"}
    )

    test_file = Path("test_snow_depth_unit_conversion.nc")
    da.to_netcdf(test_file)

    try:
        res = icclim.index(index_name="SD1", in_files=str(test_file))
        assert res is not None
    finally:
        if test_file.exists():
            test_file.unlink()
