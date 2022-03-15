import os
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim.models.ecad_indices import EcadIndex


def test_indices():
    res = icclim.list_indices()
    assert len(res) == len(EcadIndex)


@patch("icclim.main.index")
@patch("icclim.icclim_logger.IcclimLogger")
def test_deprecated_indice(log_mock: MagicMock, index_mock: MagicMock):
    icclim.main.log = log_mock
    icclim.indice()
    log_mock.deprecation_warning.assert_called_once_with(
        old="icclim.indice", new="icclim.index"
    )
    index_mock.assert_called_once()


@pytest.mark.slow
class Test_Integration:
    """
    Simple integration test.
    We are not testing here the actual indices results, they are already tested in
    `test_ecad_indices.py` as well as in xclim directly.
    The goal it to make sure every the whole app can run smoothly

    These tests have side effect:
    - writing and removing of "out.nc" file

    """

    VALUE_COUNT = 365 * 2
    OUTPUT_FILE = "out.nc"
    data = xr.DataArray(
        data=(np.full(VALUE_COUNT, 20).reshape((VALUE_COUNT, 1, 1))),
        dims=["time", "lat", "lon"],
        coords=dict(
            lat=[42],
            lon=[42],
            time=pd.date_range("2042-01-01", periods=VALUE_COUNT, freq="D"),
        ),
        attrs={"units": "degC"},
    )

    @pytest.fixture(autouse=True)
    def cleanup(self):
        # setup
        # ...
        yield
        # teardown
        try:
            os.remove(self.OUTPUT_FILE)
        except FileNotFoundError:
            pass

    def test_index_SU(self):
        res = icclim.index(
            indice_name="SU", in_files=self.data, out_file=self.OUTPUT_FILE
        )
        np.testing.assert_array_equal(0, res.SU)
