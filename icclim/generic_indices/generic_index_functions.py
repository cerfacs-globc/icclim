from __future__ import annotations

from typing import Any, Callable, Sequence, TypedDict

import numpy as np
import xarray as xr
from xarray import DataArray
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import build_climatology_bounds, percentile_doy, resample_doy
from xclim.core.units import convert_units_to, to_agg_units
from xclim.core.utils import PercentileDataArray, calc_perc
from xclim.indices import run_length

from icclim.models.frequency import Frequency
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.registry import Registry


class ReducerMetadataDict(TypedDict):
    standard_name: str
    long_name: str
    cell_methods: str
    additional_metadata: str


class Reducer(Callable):
    KEY: str

    def __call__(self, *args, **kwargs):
        ...

    def get_metadata(self, src_freq: Frequency) -> ReducerMetadataDict:
        ...


class CountOccurrences(Reducer):
    name = "count_occurrences"

    @percentile_bootstrap
    def __call__(
        self,
        study: DataArray,
        thresholds: DataArray | PercentileDataArray,
        freq: str,
        bootstrap: bool,  # noqa
        operator: Callable,
        is_doy_per: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        converted_thresholds = convert_units_to(thresholds, study)
        if is_doy_per:
            converted_thresholds = resample_doy(converted_thresholds, study)
        res = operator(study, converted_thresholds).resample(time=freq).sum(dim="time")
        return to_agg_units(res, study, "count")

    def get_metadata(self, src_freq: Frequency) -> ReducerMetadataDict:
        return {
            "standard_name": "number_of",
            "long_name": "Number of",
            "cell_methods": "time: sum over",
            "additional_metadata": "",
        }


class MaxConsecutiveOccurrence(Reducer):
    name = "max_consecutive_occurrence"

    @percentile_bootstrap
    def __call__(
        self,
        study: DataArray,
        thresholds: DataArray | PercentileDataArray,
        freq: str,
        bootstrap: bool,  # noqa
        operator: Callable,
        is_doy_per: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        converted_thresholds = convert_units_to(
            thresholds, study
        )  # todo could be done before
        if is_doy_per:  # todo could be done before
            converted_thresholds = resample_doy(converted_thresholds, study)
        res = (
            operator(study, converted_thresholds)
            .resample(time=freq)
            .map(run_length.longest_run, dim="time")
        )
        return to_agg_units(res, study, "count")

    def get_metadata(self, src_freq: Frequency) -> ReducerMetadataDict:
        return {
            "standard_name": "spell_length_of",
            "long_name": "Maximum number of consecutive",
            "cell_methods": "time: maximum over",
            "additional_metadata": "",
        }


class SumOfSpellLengths(Reducer):
    name = "sum_of_spell_lengths"

    @percentile_bootstrap
    def __call__(
        self,
        study: DataArray,
        thresholds: DataArray | PercentileDataArray,
        freq: str,
        bootstrap: bool,  # noqa
        operator: Callable,
        is_doy_per: bool,
        min_spell_length: int = 6,
        *args,
        **kwargs,
    ) -> DataArray:
        converted_thresholds = convert_units_to(
            thresholds, study
        )  # todo could be done before
        if is_doy_per:  # todo could be done before
            converted_thresholds = resample_doy(converted_thresholds, study)
        res = (
            operator(study, converted_thresholds)
            .resample(time=freq)
            .map(run_length.windowed_run_count, window=min_spell_length, dim="time")
        )
        return to_agg_units(res, study, "count")

    def get_metadata(self, src_freq: Frequency) -> ReducerMetadataDict:
        return {
            "standard_name": "sum_of_spell_lengths_of",
            "long_name": "Sum of spell lengths of",
            "cell_methods": "time: sum over",
            "additional_metadata": f" Spells are at least {self.min_spell_length}."
            f" {src_freq.units} long",
        }


class Excess(Reducer):
    name = "excess"

    @percentile_bootstrap
    def __call__(
        self,
        study: DataArray,
        thresholds: DataArray | PercentileDataArray,
        freq: str,
        bootstrap: bool,
        operator: Callable,
        is_doy_per: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        converted_thresholds = convert_units_to(
            thresholds, study
        )  # todo could be done before
        if is_doy_per:  # todo could be done before
            converted_thresholds = resample_doy(converted_thresholds, study)
        res = (
            (study - converted_thresholds)
            .clip(min=0)
            .resample(time=freq)
            .sum(dim="time")
        )
        return to_agg_units(res, study, "delta_prod")

    def get_metadata(self, src_freq: Frequency) -> ReducerMetadataDict:
        return {
            "standard_name": "excess_of_integral_of",
            "long_name": "Excess of integral of",
            "cell_methods": "time: sum over",
            "additional_metadata": "",
        }


class Deficit(Reducer):
    name = "deficit"

    @percentile_bootstrap
    def __call__(
        self,
        study: DataArray,
        thresholds: DataArray | PercentileDataArray,
        freq: str,
        bootstrap: bool,
        operator: Callable,
        is_doy_per: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        converted_thresholds = convert_units_to(
            thresholds, study
        )  # todo could be done before
        if is_doy_per:  # todo could be done before
            converted_thresholds = resample_doy(converted_thresholds, study)
        res = (
            (converted_thresholds - study)
            .clip(min=0)
            .resample(time=freq)
            .sum(dim="time")
        )
        return to_agg_units(res, study, "delta_prod")

    def get_metadata(self, src_freq: Frequency) -> ReducerMetadataDict:
        return {
            "standard_name": "deficit_of_integral_of",
            "long_name": "Deficit of integral of",
            "cell_methods": "time: sum over",
            "additional_metadata": "",
        }


class FractionOfTotal(Reducer):
    name = "fraction_of_total"

    @percentile_bootstrap
    def __call__(
        self,
        study: DataArray,
        thresholds: DataArray | PercentileDataArray,
        freq: str,
        bootstrap: bool,
        operator: Callable,
        is_doy_per: bool,
        threshold_min_value: float | str | None,
        *args,
        **kwargs,
    ) -> DataArray:
        converted_thresholds = convert_units_to(thresholds, study)
        if is_doy_per:
            converted_thresholds = resample_doy(converted_thresholds, study)
        if threshold_min_value:
            threshold_min_value = convert_units_to(threshold_min_value, study)
            total = (
                study.where(operator(study, threshold_min_value))
                .resample(time=freq)
                .sum(dim="time")
            )
        else:
            total = study.resample(time=freq).sum(dim="time")
        over = (
            study.where(operator(study, converted_thresholds))
            .resample(time=freq)
            .sum(dim="time")
        )
        res = over / total
        res.attrs["units"] = ""  # unit less
        return res

    def get_metadata(self, src_freq: Frequency) -> ReducerMetadataDict:
        return {
            "standard_name": "fraction_of_total_of",
            "long_name": "Fraction of total of",
            "cell_methods": "time: fraction",  # todo fraction is NOT in CF !
            "additional_metadata": "",
        }


class ReducerRegistry(Registry):
    _item_class = Reducer

    CountOccurrences = CountOccurrences()
    MaxConsecutiveOccurrence = MaxConsecutiveOccurrence()
    SumOfSpellLengths = SumOfSpellLengths()
    Excess = Excess()
    Deficit = Deficit()
    FractionOfTotal = FractionOfTotal()


def _can_run_bootstrap(da: DataArray, threshold: Any) -> bool:
    """Avoid bootstrapping if there is one single year overlapping
    or no year overlapping or all year overlapping.
    """
    # TODO: When true add bootstrap to metadata with add_bootstrap_meta
    # TODO: Don't run bootstrap when not on extreme percentile
    #       (below 20? 10? or above 80? 90?)
    if not threshold.is_doy_per_threshold:
        return False
    reference = threshold.value
    study_years = np.unique(da.indexes.get("time").year)
    overlapping_years = np.unique(
        da.sel(time=_get_ref_period_slice(reference)).indexes.get("time").year
    )
    return 1 < len(overlapping_years) < len(study_years)


def _get_ref_period_slice(da: DataArray) -> slice:
    if (bds := da.attrs.get("climatology_bounds", None)) is not None:
        return slice(*bds)
    time_length = len(da.time)
    return slice(*da.time[0 :: time_length - 1].dt.strftime("%Y-%m-%d").values)


def build_period_per(
    per_val: float,
    base_period_time_range: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    sampling_frequency: Frequency,
    study_da: DataArray,
    percentile_min_value: float | None,
) -> PercentileDataArray:
    # todo [refacto] move back to threshold ?
    from icclim.pre_processing.input_parsing import build_reference_da

    reference = build_reference_da(
        study_da,
        base_period_time_range,
        only_leap_years,
        sampling_frequency,
        percentile_min_value=percentile_min_value,
    )
    computed_per = xr.apply_ufunc(
        calc_perc,
        reference,
        input_core_dims=[["time"]],
        output_core_dims=[["percentiles"]],
        keep_attrs=True,
        kwargs=dict(
            percentiles=[per_val],
            alpha=interpolation.alpha,
            beta=interpolation.beta,
            copy=True,
        ),
        dask="parallelized",
        output_dtypes=[reference.dtype],
        dask_gufunc_kwargs=dict(output_sizes={"percentiles": 1}, allow_rechunk=True),
    )
    computed_per = computed_per.assign_coords(
        percentiles=xr.DataArray([per_val], dims=("percentiles",))
    )
    res = PercentileDataArray.from_da(
        source=computed_per,
        climatology_bounds=build_climatology_bounds(reference),
    )
    return res


def build_doy_per(
    per_val: float,
    base_period_time_range: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    window: int,
    sampling_frequency: Frequency,
    study_da: DataArray,
    percentile_min_value: float | None,
) -> PercentileDataArray:
    # todo [refacto] move back to threshold ?
    from icclim.pre_processing.input_parsing import build_reference_da

    reference = build_reference_da(
        study_da,
        base_period_time_range,
        only_leap_years,
        sampling_frequency,
        percentile_min_value,
    )
    res = percentile_doy(
        arr=reference,
        window=window,
        per=per_val,
        alpha=interpolation.alpha,
        beta=interpolation.beta,
    ).compute()  # "optimization" (diminish dask scheduler workload)
    return res
