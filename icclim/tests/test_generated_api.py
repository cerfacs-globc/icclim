from unittest.mock import MagicMock, patch

import icclim  # noqa (used in eval)
from icclim.icclim_logger import Verbosity
from icclim.models.constants import (
    MODIFIABLE_QUANTILE_WINDOW,
    MODIFIABLE_THRESHOLD,
    MODIFIABLE_UNIT,
    QUANTILE_BASED,
)
from icclim.models.ecad_indices import EcadIndex
from icclim.models.frequency import Frequency
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation

DEFAULT_ARGS = dict(
    in_files="pouet.nc",
    var_name=None,
    slice_mode=Frequency.YEAR,
    time_range=None,
    out_file=None,
    ignore_Feb29th=False,
    netcdf_version=NetcdfVersion.NETCDF4,
    logs_verbosity=Verbosity.LOW,
)


def build_expected_args(index):
    expected_call_args = {"index_name": index.name}
    expected_call_args.update(DEFAULT_ARGS)
    if MODIFIABLE_THRESHOLD in index.qualifiers:
        expected_call_args.update({"threshold": None})
    if QUANTILE_BASED in index.qualifiers:
        expected_call_args.update(
            {
                "base_period_time_range": None,
                "only_leap_years": False,
                "interpolation": QuantileInterpolation.MEDIAN_UNBIASED,
                "save_percentile": False,
            }
        )
    if MODIFIABLE_QUANTILE_WINDOW in index.qualifiers:
        expected_call_args.update({"window_width": 5})
    if MODIFIABLE_UNIT in index.qualifiers:
        expected_call_args.update({"out_unit": None})

    return expected_call_args


@patch("icclim.index")
def test_generated_api(generic_index_fun_mock: MagicMock):
    for i in EcadIndex:
        print(i)
        # GIVEN
        api_index_fun = eval(f"icclim.{i.name.lower()}")
        # WHEN
        api_index_fun(**DEFAULT_ARGS)
        # THEN
        expected_call_args = build_expected_args(i)
        generic_index_fun_mock.assert_called_with(**expected_call_args)
