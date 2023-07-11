import xarray as xr

import icclim


def test_spi6():
    dataset = xr.open_dataset("./icclim/pr.nc")
    dataset = icclim.index(
        index_name="spi6",
        in_files=dataset,
        var_name="pr",
        base_period_time_range=["2015-01-01", "2015-06-01"],
    ).load()
    assert "time_bounds" not in dataset.coords
