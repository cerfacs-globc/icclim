import numpy as np
import pandas as pd
import xarray as xr

import icclim


def test_allow_partial_seasons():
    # Create data from 2020-01-01 to 2021-12-31
    time = pd.date_range("2020-01-01", "2021-12-31", freq="D")
    tas = xr.DataArray(
        np.full(len(time), 30.0),
        coords={"time": time},
        dims=["time"],
        attrs={"units": "degC"},
    )

    # Season from Nov 1st to March 31st
    slice_mode = ("season", ("1 november", "31 march"))

    # Without allow_partial_seasons (default False)
    # The last season (2021-11-01 to 2022-03-31) is incomplete (ends 2021-12-31)
    # It should be NaN
    res_default = icclim.index(
        in_files=tas,
        index_name="SU",  # SU > 25, here all 1.0 so SU should be 0, but masked if partial
        threshold="> 0 degC",  # Let's use TG to see the average or countable values
        slice_mode=slice_mode,
        allow_partial_seasons=False,
    )

    # Seasons:
    # 2019-11-01 to 2020-03-31 -> has data for Jan, Feb, Mar 2020 (91 days)
    # 2020-11-01 to 2021-03-31 -> has full data (151 days)
    # 2021-11-01 to 2022-03-31 -> has data for Nov, Dec 2021 (61 days)

    # Check that the last one is NaN
    assert np.isnan(res_default.SU.values[-1])

    # With allow_partial_seasons=True
    res_partial = icclim.index(
        in_files=tas,
        index_name="SU",
        threshold="> 0 degC",
        slice_mode=slice_mode,
        allow_partial_seasons=True,
    )

    # Check that the last one is NOT NaN and has 61 days (all values are 1.0 > 0)
    assert not np.isnan(res_partial.SU.values[-1])
    assert res_partial.SU.values[-1] == 61


if __name__ == "__main__":
    test_allow_partial_seasons()
