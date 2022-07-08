from __future__ import annotations

from datetime import datetime
from functools import reduce
from typing import Sequence

import numpy as np
import xarray as xr
from xarray import DataArray
from xclim.core.calendar import percentile_doy, build_climatology_bounds
from xclim.core.units import str2pint
from xclim.core.utils import PercentileDataArray, calc_perc

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import Frequency
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim_types import ThresholdType
from pre_processing.input_parsing import (
    check_time_range_pre_validity,
    check_time_range_post_validity,
)
from utils import get_date_to_iso_format


class Threshold:
    value: DataArray | PercentileDataArray
    additional_metadata: str = ""

    @property
    def units(self) -> str:
        return self.value.attrs["units"]

    def __init__(
            self,
            threshold: ThresholdType,
            study_da: DataArray,
            sampling_frequency: Frequency,
            units: str | None,
            window: int | None,
            only_leap_years: bool | None,
            interpolation: QuantileInterpolation | None,
            base_period_time_range: Sequence[datetime | str] | None,
    ):
        def __build_from_scalar(threshold: ThresholdType) -> DataArray:
            return _build_from_scalar(
                threshold=threshold,
                study_da=study_da,
                sampling_frequency=sampling_frequency,
                units=units,
                window=window,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                base_period_time_range=base_period_time_range,
            )
        #  TODO add _read_threshold features here
        if PercentileDataArray.is_compatible(threshold):
            self.value = PercentileDataArray.from_da(threshold)
            self.value.attrs["units"] = units
        elif isinstance(threshold, DataArray):
            self.value = threshold
            self.value.attrs["units"] = units
        elif isinstance(threshold, (list, tuple)):
            if all(map(lambda x: isinstance(x, (int, float)), threshold)):
                self.value = DataArray(
                    data=threshold,
                    coords={"threshold": threshold},
                    attrs={"units": units},
                )
            elif all(map(lambda x: _pintable(x), threshold)):
                thresholds = list(
                    map(lambda x: str2pint(x).to(units).magnitude, threshold)
                )
                self.value = DataArray(
                    data=thresholds,
                    coords={"threshold": thresholds},
                    attrs={"units": units},
                )
            #     TODO [optimization] add elif to compute multiple percentiles at once !
            else:
                # mixed type (e.g. R75p:= pr>1mm AND pr>"75th period_per")
                # TODO do `np.minimum` if operand is <= (so we need the operator on Threshold)
                operator = np.maximum
                scalars = [__build_from_scalar(t) for t in threshold]
                self.value = reduce(operator, scalars)  # noqa
                self.additional_metadata += f"thresholds were computed on {operator}({threshold}), "
        elif np.isscalar(threshold):
            self.value = __build_from_scalar(threshold=threshold, )
        else:
            raise NotImplementedError(
                "Unknown type for thresholds."
                " It must be either a DataArray, a number or a"
                " list of numbers."
            )

    def to_dict(self, src_freq: Frequency) -> dict[str, str]:
        # TODO: localize/translate these
        if self.value.size == 1:
            res = {
                "standard_name": f"than_{self.value.values[()]}{self.units}",
                "value":         f"{self.value.values[()]}{self.units}",
            }
        elif isinstance(self.value, PercentileDataArray):
            percentiles = self.value.coords["percentiles"].values
            if np.isscalar(percentiles[()]):
                display_pers = f"{percentiles[()]}th percentile"
                standard_name = f"than_{percentiles[()]}th_percentile"
            else:
                display_pers = list(map(lambda x: f"{x}th", percentiles))
                standard_name = f"than_percentiles"
            window = self.value.attrs.get("window", None)
            # TODO: distinguish between doy and period percentiles
            #       ( lazy way: if window!=None then it's doy)
            bds = self.value.attrs.get("climatology_bounds")
            self.additional_metadata += (f"percentiles were computed over {bds}"
                                         f" on a {window} {src_freq.units} window ")
            res = {
                "standard_name": standard_name,
                "value":         f"{display_pers} "
            }
        elif isinstance(self.value, DataArray):
            if self.value.size < 10:
                display_value = f"{self.value.values}{self.units}"
            else:
                display_value = (
                    f"between {self.value.min().values[()]}{self.units}"
                    f" and {self.value.max().values[()]}{self.units}"
                )
            res = {"standard_name": "than_thresholds", "value": display_value}
        else:
            raise NotImplementedError(f"Threshold::value must be a DataArray."
                                      f" It was a {type(self.value)}.")
        return res | {"additional_metadata": self.additional_metadata}


def _pintable(thresh: str) -> bool:
    return "per" not in thresh


def _build_from_scalar(
        threshold: ThresholdType,
        study_da: DataArray,
        sampling_frequency: Frequency,
        units: str | None,
        window: int | None,
        only_leap_years: bool | None,
        interpolation: QuantileInterpolation | None,
        base_period_time_range: Sequence[datetime | str] | None,
) -> DataArray:
    if isinstance(threshold, str):
        if "doy_per" in threshold:  # todo add constant for doy_per and period_per
            per_val = float(threshold.rstrip("doy_per"))
            if base_period_time_range is not None:
                reference = _build_reference_da(
                    study_da,
                    base_period_time_range,
                    only_leap_years,
                    sampling_frequency,
                )
            else:
                reference = study_da
            res = percentile_doy(
                arr=reference,
                window=window,
                per=per_val,
                alpha=interpolation.alpha,
                beta=interpolation.beta,
            ).compute()  # "optimization" (diminish dask scheduler workload)
            res["units"] = units
        elif "period_per" in threshold:
            per_val = float(threshold.rstrip("period_per"))
            reference = _build_reference_da(
                study_da, base_period_time_range, only_leap_years, sampling_frequency,
            )
            #  todo overkill to use apply_ufunc here ?
            computed_per = xr.apply_ufunc(
                calc_perc,
                reference,
                input_core_dims=[["time"]],
                output_core_dims=[["percentiles"]],
                keep_attrs=True,
                kwargs=dict(percentiles=[per_val],
                            alpha=interpolation.alpha,
                            beta=interpolation.beta,
                            copy=True),
                dask="parallelized",
                output_dtypes=[reference.dtype],
                dask_gufunc_kwargs=dict(output_sizes={"percentiles": 1},
                                        allow_rechunk=True),
            )
            computed_per= computed_per.assign_coords(percentiles=xr.DataArray([per_val], dims=("percentiles",)))
            res = PercentileDataArray.from_da(
                source=computed_per,
                climatology_bounds=build_climatology_bounds(reference),
            )
            res["units"] = units
        else:
            # todo add this case in xclim ::units2pint
            #     (case of DataArray compose of strings such as ["2K", "30degC"])
            quantity = str2pint(threshold).to(units)
            res = DataArray(
                data=quantity.magnitude,
                coords={"threshold": quantity.magnitude},
                attrs={"units": quantity.units},
            )
    elif isinstance(threshold, (float, int)):
        res = DataArray(
            data=threshold, coords={"threshold": threshold}, attrs={"units": units},
        )
    else:
        raise NotImplementedError(
            "scalar threshold must be a string," " an integer or a float."
        )
    return res


def _build_reference_da(
        original_da: DataArray,
        base_period_time_range: Sequence[datetime | str] | None,
        only_leap_years: bool,
        sampling_frequency: Frequency,
) -> DataArray:
    da = original_da
    if base_period_time_range:
        check_time_range_pre_validity("base_period_time_range", base_period_time_range)
        base_period_time_range = [get_date_to_iso_format(x) for x in
                                  base_period_time_range]
        da = original_da.sel(
            time=slice(base_period_time_range[0], base_period_time_range[1])
        )
        check_time_range_post_validity(
            da, original_da, "base_period_time_range", base_period_time_range
        )
    if sampling_frequency.time_clipping is not None:
        da = sampling_frequency.time_clipping(da)
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
