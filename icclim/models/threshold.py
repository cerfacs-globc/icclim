from __future__ import annotations

from datetime import datetime

from icclim.models.frequency import Frequency

from icclim.models.quantile_interpolation import QuantileInterpolation
from xclim.core.calendar import percentile_doy

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from xarray import DataArray, Dataset
from xclim.core.utils import PercentileDataArray
import xarray as xr

from pre_processing.input_parsing import (
    check_time_range_pre_validity,
    check_time_range_post_validity,
)
from utils import get_date_to_iso_format


class Threshold:
    value: DataArray | PercentileDataArray

    @property
    def units(self) -> str:
        return self.value.attrs["units"]

    def __init__(
        self,
        threshold: DataArray | float | list[float],
        study_da: DataArray,
        units: str,
        sampling_frequency: Frequency,
        window: int = None,
        only_leap_years: bool = None,
        interpolation: QuantileInterpolation = None,
        base_period_time_range: list[datetime] | list[str] | tuple[str, str] = None,
    ):
        if isinstance(threshold, DataArray):
            if base_period_time_range is not None:
                raise InvalidIcclimArgumentError(
                    "Cannot determine the data to use for percentiles when"
                    " `base_period_time_range` is filled and `value` is a DataArray."
                    " Please fill only one of the two."
                )
            if PercentileDataArray.is_compatible(threshold):
                self.value = PercentileDataArray.from_da(threshold)
            else:
                self.value = threshold
            self.value.attrs["units"] = units  # todo ok to override units ?
        elif isinstance(threshold, (float, int, list)):
            if base_period_time_range is not None:
                reference = _build_reference_da(
                    study_da,
                    base_period_time_range,
                    only_leap_years,
                    sampling_frequency,
                )
                self.value = percentile_doy(
                    arr = reference,
                    window=window,
                    per=threshold,
                    alpha=interpolation.alpha,
                    beta=interpolation.beta,
                ).compute() # "optimization" (diminish dask scheduler workload)
            else:
                self.value = DataArray(
                    data=threshold,
                    coords={"threshold": threshold},
                    attrs={"units": units},
                )
        else:
            raise NotImplementedError(
                "Unknown type for thresholds."
                " It must be either a DataArray, a number or a"
                " list of numbers."
            )

    def to_dict(self):
        if self.value.size == 1:
            return {
                "standard_name": f"{self.value.values[()]}{self.units}",
                "value": f"{self.value.values[()]}{self.units}",
            }
        elif isinstance(self.value, DataArray):
            if self.value.size < 10:
                display_value = f"{self.value.values}{self.units}"
            else:
                display_value = (
                    f"between {self.value.min()}{self.units}"
                    f" and {self.value.max()}{self.units}"
                )
            return {"standard_name": "thresholds", "value": display_value}
        elif isinstance(self.value, PercentileDataArray):
            return {
                "per_thresh": self.value.coords["percentiles"].values,
                "per_window": self.value.attrs.get("window", None),
                "per_period": self.value.attrs.get(
                    "climatology_bounds"  # todo rename reference_epoch ?
                ),
            }


def _build_reference_da(
    original_da: DataArray,
    base_time_range: list[str],
    only_leap_years: bool,
    sampling_frequency: Frequency,
) -> DataArray:
    check_time_range_pre_validity("base_period_time_range", base_time_range)
    base_time_range = [get_date_to_iso_format(x) for x in base_time_range]
    da = original_da.sel(time=slice(base_time_range[0], base_time_range[1]))
    if sampling_frequency.time_clipping is not None:
        da = sampling_frequency.time_clipping(da)
    check_time_range_post_validity(
        da, original_da, "base_period_time_range", base_time_range
    )
    if only_leap_years:
        da = _reduce_only_leap_years(original_da)
    return da


def _reduce_only_leap_years(da: DataArray) -> DataArray:
    reduced_list = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if not reduced_list:
        raise InvalidIcclimArgumentError(
            "No leap year in current dataset. Do not use `only_leap_years` parameter."
        )
    return xr.concat(reduced_list, "time")


def _has_thresholds_variable(ds: Dataset, name: str) -> bool:
    # fixme: Not the best to use a string (the name) to identify percentiles data
    # TODO +1 IT'S A FUCKING BAD IDEA
    #      We should definitly build ClimateVariable with a Threshold early
    return f"{name}_thresholds" in ds.data_vars
