import numpy as np
import pandas as pd
import xarray as xr
import pytest
import icclim

class TestSpatiallyVaryingSeasons:
    def test_tg_spatially_varying(self):
        time = pd.date_range("2000-01-01", periods=366, freq="D")
        # Create a 2x1 grid
        # Pixel 1: values are 10 everywhere
        # Pixel 2: values are 20 everywhere
        data = np.zeros((366, 1, 2))
        data[:, 0, 0] = 10
        data[:, 0, 1] = 20
        
        tas = xr.DataArray(
            data,
            coords={"time": time, "lat": [45], "lon": [5, 10]},
            dims=["time", "lat", "lon"],
            attrs={"units": "degC"},
        )
        
        # Pixel 1: season is doy 1 to 50 (50 days)
        # Pixel 2: season is doy 100 to 150 (51 days)
        start = xr.DataArray(
            [[1, 100]], dims=["lat", "lon"], coords={"lat": [45], "lon": [5, 10]}
        )
        end = xr.DataArray(
            [[50, 150]], dims=["lat", "lon"], coords={"lat": [45], "lon": [5, 10]}
        )
        
        result = icclim.index(
            in_files={"tas": tas},
            index_name="TG",
            slice_mode=(start, end),
        )
        
        # TG is the mean
        # Pixel 1 should have 10
        # Pixel 2 should have 20
        assert result.TG.isel(time=0, lat=0, lon=0) == 10
        assert result.TG.isel(time=0, lat=0, lon=1) == 20

    def test_su_spatially_varying(self):
        time = pd.date_range("2000-01-01", periods=366, freq="D")
        data = np.zeros((366, 1, 2))
        # Pixel 1: 30°C on doy 1 to 10 (10 days), 0 elsewhere
        data[0:10, 0, 0] = 30
        # Pixel 2: 30°C on doy 100 to 120 (21 days), 0 elsewhere
        data[99:120, 0, 1] = 30
        
        tasmax = xr.DataArray(
            data,
            coords={"time": time, "lat": [45], "lon": [5, 10]},
            dims=["time", "lat", "lon"],
            attrs={"units": "degC"},
        )
        
        # Seasonal bounds that cover the hot periods
        start = xr.DataArray(
            [[1, 100]], dims=["lat", "lon"], coords={"lat": [45], "lon": [5, 10]}
        )
        end = xr.DataArray(
            [[20, 150]], dims=["lat", "lon"], coords={"lat": [45], "lon": [5, 10]}
        )
        
        result = icclim.index(
            in_files={"tasmax": tasmax},
            index_name="SU",
            slice_mode=(start, end),
        )
        
        # Pixel 1: 10 days >= 25
        # SU should have 10
        # Pixel 2 should have 21
        if "lat" in result.SU.dims:
            assert result.SU.isel(time=0, lat=0, lon=0) == 10
            assert result.SU.isel(time=0, lat=0, lon=1) == 21
        else:
            assert result.SU.isel(time=0, lon=0) == 10
            assert result.SU.isel(time=0, lon=1) == 21

    def test_wrapping_season_spatially_varying(self):
        # Using a dummy calendar or enough years to test wrapping.
        # Simplest: check if it works on a single year with a wrapping mask.
        time = pd.date_range("2000-01-01", periods=366, freq="D")
        data = np.zeros((366, 1, 1))
        # 10°C on doy 360 to 366 (7 days) and doy 1 to 5 (5 days)
        # Total 12 days in the season doy 360 to doy 5
        data[359:366, 0, 0] = 10
        data[0:5, 0, 0] = 10
        
        tas = xr.DataArray(
            data,
            coords={"time": time, "lat": [45], "lon": [5]},
            dims=["time", "lat", "lon"],
            attrs={"units": "degC"},
        )
        
        # Wrapping season: 360 to 5
        start = xr.DataArray([[360]], dims=["lat", "lon"], coords={"lat": [45], "lon": [5]})
        end = xr.DataArray([[5]], dims=["lat", "lon"], coords={"lat": [45], "lon": [5]})
        
        result = icclim.index(
            in_files={"tas": tas},
            index_name="TG",
            slice_mode=(start, end),
        )
        
        # Mean should be 10 (ignoring 0s outside the season)
        assert result.TG.isel(time=0, lat=0, lon=0) == 10
