from __future__ import annotations

import abc
from datetime import timedelta
from functools import partial, reduce
from typing import Any, Callable
from warnings import warn

import numpy
import numpy as np
import xarray as xr
from jinja2 import Environment
from xarray import DataArray
from xarray.core.resample import DataArrayResample
from xarray.core.rolling import DataArrayRolling
from xclim.core import datachecks
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import resample_doy, select_time
from xclim.core.cfchecks import cfcheck_from_name
from xclim.core.options import MISSING_METHODS, MISSING_OPTIONS, OPTIONS
from xclim.core.units import convert_units_to, rate2amount, to_agg_units
from xclim.core.utils import PercentileDataArray
from xclim.indices import run_length

from icclim.generic_indices.generic_templates import INDICATORS_TEMPLATES_EN
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import CfCalendarRegistry
from icclim.models.climate_variable import ClimateVariable
from icclim.models.constants import PART_OF_A_WHOLE_UNIT, UNITS_ATTRIBUTE_KEY
from icclim.models.frequency import Frequency, FrequencyRegistry
from icclim.models.index_config import IndexConfig
from icclim.models.logical_link import LogicalLink
from icclim.models.operator import Operator
from icclim.models.registry import Registry
from icclim.models.threshold import Threshold

jinja_env = Environment()


class Indicator(metaclass=abc.ABCMeta):
    identifier: str
    standard_name: str
    long_name: str
    cell_methods: str

    templated_properties = [
        "identifier",
        "standard_name",
        "long_name",
        "cell_methods",
    ]

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> DataArray:
        ...

    @abc.abstractmethod
    def preprocess(self, *args, **kwargs) -> list[DataArray]:
        ...

    @abc.abstractmethod
    def postprocess(self, *args, **kwargs) -> DataArray:
        ...


class ResamplingIndicator(Indicator):
    missing: str
    missing_options: dict | None

    def __init__(self, missing="from_context", missing_options=None):
        self.missing_options = missing_options
        self.missing = missing
        if self.missing == "from_context" and self.missing_options is not None:
            raise ValueError(
                "Cannot set `missing_options` with `missing` method being from context."
            )
        missing_method = MISSING_METHODS[self.missing]
        self._missing = missing_method.execute
        if self.missing_options:
            missing_method.validate(**self.missing_options)
        super().__init__()

    def datachecks(self, climate_vars: list[ClimateVariable], src_freq: str):
        if src_freq is None:
            return
        for climate_var in climate_vars:
            da = climate_var.studied_data
            if "time" in da.coords and da.time.ndim == 1 and len(da.time) > 3:
                # todo useless ? (checks are done in CLimateVariable building)
                datachecks.check_freq(da, src_freq, strict=True)

    def cfcheck(self, climate_vars: list[ClimateVariable]):
        """Compare metadata attributes to CF-Convention standards.

        Default cfchecks use the specifications in `xclim.core.utils.VARIABLES`,
        assuming the indicator's inputs are using the CMIP6/xclim variable names
        correctly.
        Variables absent from these default specs are silently ignored.

        When subclassing this method, use functions decorated using
        `xclim.core.options.cfcheck`.
        """
        for da in climate_vars:
            try:
                cfcheck_from_name(str(da.name), da)
            except KeyError:
                # Silently ignore unknown variables.
                pass

    def preprocess(
        self,
        climate_vars: list[ClimateVariable],
        jinja_scope: dict[str, Any],
        output_frequency: Frequency,
        src_freq: Frequency,
        indicator: GenericIndicator,
        output_unit: str | None,
        coef: float | None,
    ) -> list[ClimateVariable]:
        self.datachecks(climate_vars, src_freq.pandas_freq)
        self.cfcheck(climate_vars)
        self.format(jinja_scope=jinja_scope)
        if output_frequency.indexer and indicator.select_time_before_computation:
            for climate_var in climate_vars:
                climate_var.studied_data = select_time(
                    climate_var.studied_data, **output_frequency.indexer
                )
        return climate_vars

    def postprocess(
        self,
        result: DataArray,
        das: list[DataArray],
        output_freq: str,
        src_freq: str,
        indexer: dict,
        out_unit: str | None,
    ):
        if out_unit is not None:
            result = convert_units_to(result, out_unit)
        if self.missing != "skip" and indexer is not None:
            result = self._handle_missing_values(
                resample_freq=output_freq,
                src_freq=src_freq,
                indexer=indexer,
                in_data=das,
                out_data=result,
            )
        for prop in self.templated_properties:
            result.attrs[prop] = getattr(self, prop)
        result.attrs["history"] = ""
        return result

    def format(self, jinja_scope: dict):
        for property in self.templated_properties:
            template = jinja_env.from_string(
                getattr(self, property),
                globals=jinja_scope,
            )
            setattr(self, property, template.render())

    def _handle_missing_values(
        self,
        in_data: list[DataArray],
        resample_freq: str,
        src_freq: str,
        indexer: dict | None,
        out_data: DataArray,
    ) -> DataArray:
        options = self.missing_options or OPTIONS[MISSING_OPTIONS].get(self.missing, {})
        # We flag periods according to the missing method. skip variables without a time
        # coordinate.
        miss = (
            MISSING_METHODS[self.missing].execute(
                da, resample_freq, src_freq, options, indexer
            )
            for da in in_data
            if "time" in da.coords
        )
        # Reduce by or and broadcast to ensure the same length in time
        # When indexing is used and there are no valid points in the last period,
        # mask will not include it
        mask = reduce(np.logical_or, miss)
        if isinstance(mask, DataArray) and mask.time.size < out_data.time.size:
            mask = mask.reindex(time=out_data.time, fill_value=True)
        return out_data.where(~mask)


class GenericIndicator(ResamplingIndicator):
    name: str

    def __init__(
        self,
        name: str,
        process: Callable[..., DataArray],
        select_time_before_computation=True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        local = INDICATORS_TEMPLATES_EN
        self.name = name
        self.process = process
        self.select_time_before_computation = select_time_before_computation
        self.identifier = local[name]["identifier"]
        self.standard_name = local[name]["standard_name"]
        self.cell_methods = local[name]["cell_methods"]
        self.long_name = local[name]["long_name"]

    def preprocess(
        self,
        climate_vars: list[ClimateVariable],
        jinja_scope: dict[str, Any],
        output_frequency: Frequency,
        src_freq: Frequency,
        indicator: GenericIndicator,
        output_unit: str | None,
        coef: float | None,
    ) -> list[ClimateVariable]:
        if not _same_freq_for_all(climate_vars):
            raise InvalidIcclimArgumentError(
                "All variables must have the same time frequency (for example daily) to"
                " be compared with each others, but this was not the case."
            )
        if output_unit is not None and _is_amount_unit(output_unit):
            for climate_var in climate_vars:
                current_unit = climate_var.studied_data.attrs.get(
                    UNITS_ATTRIBUTE_KEY, None
                )
                if current_unit is not None and not _is_amount_unit(current_unit):
                    climate_var.studied_data = rate2amount(
                        climate_var.studied_data, out_units=output_unit
                    )
        if coef is not None:
            for climate_var in climate_vars:
                climate_var.studied_data = coef * climate_var.studied_data
        return super().preprocess(
            climate_vars=climate_vars,
            jinja_scope=jinja_scope,
            output_frequency=output_frequency,
            src_freq=src_freq,
            indicator=indicator,
            output_unit=output_unit,
            coef=coef,
        )

    def __call__(self, config: IndexConfig) -> DataArray:
        # icclim  wrapper
        src_freq = config.climate_variables[0].source_frequency
        jinja_scope = {
            "output_freq": config.frequency,
            "source_freq": src_freq,
            "min_spell_length": config.min_spell_length,
            "rolling_window_width": config.rolling_window_width,
            "np": numpy,
            "enumerate": enumerate,
            "len": len,
            "climate_vars": _get_inputs_metadata(
                config.climate_variables, src_freq, config.indicator_name
            ),
            "is_compared_to_reference": config.is_compared_to_reference,
            "reference_period": config.reference_period,
        }
        climate_vars = self.preprocess(
            climate_vars=config.climate_variables,
            jinja_scope=jinja_scope,
            output_frequency=config.frequency,
            src_freq=src_freq,
            indicator=self,
            output_unit=config.out_unit,
            coef=config.coef,
        )
        result = self.process(
            climate_vars=climate_vars,
            resample_freq=config.frequency,
            min_spell_length=config.min_spell_length,
            rolling_window_width=config.rolling_window_width,
            group_by_freq=config.frequency.group_by_key,
            is_compared_to_reference=config.is_compared_to_reference,
            logical_link=config.logical_link,
            date_event=config.date_event,
            source_freq_delta=src_freq.delta,
            to_percent=config.out_unit == "%",
        )
        return self.postprocess(
            result,
            das=list(map(lambda cv: cv.studied_data, climate_vars)),
            output_freq=config.frequency.pandas_freq,
            src_freq=src_freq.pandas_freq,
            indexer=config.frequency.indexer,
            out_unit=config.out_unit,
        )


def count_occurrences(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    date_event: bool,
    to_percent: bool,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    if date_event:
        reducer_op = _count_occurrences_with_date
    else:
        reducer_op = partial(DataArray.sum, dim="time")
    merged_exceedances = _compute_exceedances(
        climate_vars, resample_freq.pandas_freq, logical_link
    )
    result = reducer_op(merged_exceedances.resample(time=resample_freq.pandas_freq))
    if to_percent:
        result = _to_percent(result, resample_freq)
        result.attrs[UNITS_ATTRIBUTE_KEY] = "%"
        return result
    else:
        return to_agg_units(result, climate_vars[0].studied_data, "count")


def max_consecutive_occurrence(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    date_event: bool,
    source_freq_delta: timedelta,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    merged_exceedances = _compute_exceedances(
        climate_vars, resample_freq.pandas_freq, logical_link
    )
    # todo wait for xclim#1134 to benefit from the run_length algo update
    rle = run_length.rle(merged_exceedances, dim="time", index="first")
    if resample_freq.indexer:
        rle = select_time(rle, **resample_freq.indexer)
    resampled = rle.resample(time=resample_freq.pandas_freq)
    if date_event:
        max_consecutive_occurrence = _consecutive_occurrences_with_dates(
            resampled, source_freq_delta
        )
    else:
        max_consecutive_occurrence = resampled.max(dim="time")
    return to_agg_units(
        max_consecutive_occurrence, climate_vars[0].studied_data, "count"
    )


def sum_of_spell_lengths(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    min_spell_length: int,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    merged_exceedances = _compute_exceedances(
        climate_vars, resample_freq.pandas_freq, logical_link
    )
    # todo wait for xclim#1134 to benefit from the run_length algo update
    rle = run_length.rle(merged_exceedances, dim="time", index="first")
    cropped_rle = rle.where(rle >= min_spell_length, other=0)
    if resample_freq.indexer:
        cropped_rle = select_time(cropped_rle, **resample_freq.indexer)
    sum_of_spell_lengths = cropped_rle.resample(time=resample_freq.pandas_freq).max(
        dim="time"
    )
    return to_agg_units(sum_of_spell_lengths, climate_vars[0].studied_data, "count")


def excess(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    op, study, threshold = _check_single_var(climate_vars)
    if threshold.is_doy_per_threshold:
        thresh = resample_doy(threshold.value, study)
    else:
        thresh = threshold.value
    res = (
        (study - thresh)
        .clip(min=0)
        .resample(time=resample_freq.pandas_freq)
        .sum(dim="time")
    )
    return to_agg_units(res, study, "delta_prod")


def deficit(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    op, study, threshold = _check_single_var(climate_vars)
    if threshold.is_doy_per_threshold:
        thresh = resample_doy(threshold.value, study)
    else:
        thresh = threshold.value
    res = (
        (thresh - study)
        .clip(min=0)
        .resample(time=resample_freq.pandas_freq)
        .sum(dim="time")
    )
    return to_agg_units(res, study, "delta_prod")


def fraction_of_total(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    op, study, threshold = _check_single_var(climate_vars)
    if threshold.threshold_min_value:
        total = (
            study.where(op(study, threshold.threshold_min_value.value))
            .resample(time=resample_freq.pandas_freq)
            .sum(dim="time")
        )
    else:
        total = study.resample(time=resample_freq.pandas_freq).sum(dim="time")
    exceedance = _compute_exceedance(
        operator=op,
        study=study,
        threshold=threshold.value,
        freq=resample_freq.pandas_freq,
        bootstrap=_must_run_bootstrap(study, threshold),
        is_doy_per=threshold.is_doy_per_threshold,
    ).squeeze()
    over = (
        study.where(exceedance).resample(time=resample_freq.pandas_freq).sum(dim="time")
    )
    res = over / total
    res.attrs[UNITS_ATTRIBUTE_KEY] = PART_OF_A_WHOLE_UNIT
    return res


def maximum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    date_event: bool,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.max,
        date_event=date_event,
    )


def minimum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    date_event: bool,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.min,
        date_event=date_event,
    )


def average(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.mean,
        date_event=False,
    )


def sum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.sum,
        date_event=False,
    )


def std(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(
        climate_vars, resample_freq, DataArrayResample.std, date_event=False
    )


def max_of_rolling_sum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    date_event: bool,
    source_freq_delta: timedelta,
    *args,  # noqa
    **kwargs,  # noqa
):
    return _run_rolling_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        rolling_window_width=rolling_window_width,
        rolling_op=DataArrayRolling.sum,
        resampled_op=DataArrayResample.max,
        date_event=date_event,
        source_freq_delta=source_freq_delta,
    )


def min_of_rolling_sum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    date_event: bool,
    source_freq_delta: timedelta,
    *args,  # noqa
    **kwargs,  # noqa
):
    return _run_rolling_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        rolling_window_width=rolling_window_width,
        rolling_op=DataArrayRolling.sum,
        resampled_op=DataArrayResample.min,
        date_event=date_event,
        source_freq_delta=source_freq_delta,
    )


def min_of_rolling_average(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    date_event: bool,
    source_freq_delta: timedelta,
    *args,  # noqa
    **kwargs,  # noqa
):
    return _run_rolling_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        rolling_window_width=rolling_window_width,
        rolling_op=DataArrayRolling.mean,
        resampled_op=DataArrayResample.min,
        date_event=date_event,
        source_freq_delta=source_freq_delta,
    )


def max_of_rolling_average(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    date_event: bool,
    source_freq_delta: timedelta,
    *args,  # noqa
    **kwargs,  # noqa
):
    return _run_rolling_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        rolling_window_width=rolling_window_width,
        rolling_op=DataArrayRolling.mean,
        resampled_op=DataArrayResample.max,
        date_event=date_event,
        source_freq_delta=source_freq_delta,
    )


def mean_of_difference(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
):
    var_0, var_1 = _check_couple_of_var(climate_vars, "mean_of_difference")
    mean_of_diff = (var_0 - var_1).resample(time=resample_freq.pandas_freq).mean()
    mean_of_diff.attrs["units"] = var_0.attrs["units"]
    return mean_of_diff


def difference_of_extremes(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
):
    var_0, var_1 = _check_couple_of_var(climate_vars, "difference_of_extremes")
    max_var_0 = var_0.resample(time=resample_freq.pandas_freq).max()
    min_var_1 = var_1.resample(time=resample_freq.pandas_freq).min()
    diff_of_extremes = max_var_0 - min_var_1
    diff_of_extremes.attrs["units"] = var_0.attrs["units"]
    return diff_of_extremes


def mean_of_absolute_one_time_step_difference(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    *args,  # noqa
    **kwargs,  # noqa
):
    var_0, var_1 = _check_couple_of_var(
        climate_vars, "mean_of_absolute_one_time_step_difference"
    )
    one_time_step_diff = (var_0 - var_1).diff(dim="time")
    res = abs(one_time_step_diff).resample(time=resample_freq.pandas_freq).mean()
    res.attrs["units"] = var_0.attrs["units"]
    return res


def difference_of_means(
    climate_vars: list[ClimateVariable],
    is_compared_to_reference: bool,
    to_percent: bool,
    group_by_freq: str | None = None,
    resample_freq: Frequency | None = None,
    *args,  # noqa
    **kwargs,  # noqa
):
    var_0, var_1 = _check_couple_of_var(climate_vars, "difference_of_means")
    if is_compared_to_reference:
        mean_var_0 = var_0.groupby(group_by_freq).mean()
        mean_var_1 = var_1.groupby(group_by_freq).mean()
    else:
        mean_var_0 = var_0.resample(time=resample_freq.pandas_freq).mean()
        mean_var_1 = var_1.resample(time=resample_freq.pandas_freq).mean()
    diff_of_means = mean_var_0 - mean_var_1
    if to_percent:
        diff_of_means = diff_of_means / mean_var_1 * 100
        diff_of_means.attrs["units"] = "%"
    else:
        diff_of_means.attrs["units"] = var_0.attrs["units"]
    return diff_of_means


class GenericIndicatorRegistry(Registry):
    _item_class = GenericIndicator

    CountOccurrences = GenericIndicator("count_occurrences", count_occurrences)
    MaxConsecutiveOccurrence = GenericIndicator(
        "max_consecutive_occurrence",
        max_consecutive_occurrence,
        select_time_before_computation=False,
    )
    SumOfSpellLengths = GenericIndicator(
        "sum_of_spell_lengths",
        sum_of_spell_lengths,
        select_time_before_computation=False,
    )
    Excess = GenericIndicator("excess", excess)
    Deficit = GenericIndicator("deficit", deficit)
    FractionOfTotal = GenericIndicator("fraction_of_total", fraction_of_total)
    Maximum = GenericIndicator("maximum", maximum)
    Minimum = GenericIndicator("minimum", minimum)
    Average = GenericIndicator("average", average)
    Sum = GenericIndicator("sum", sum)
    StandardDeviation = GenericIndicator("std", std)
    MaxOfRollingSum = GenericIndicator("max_of_rolling_sum", max_of_rolling_sum)
    MinOfRollingSum = GenericIndicator("min_of_rolling_sum", min_of_rolling_sum)
    MaxOfRollingAverage = GenericIndicator(
        "max_of_rolling_average", max_of_rolling_average
    )
    MinOfRollingAverage = GenericIndicator(
        "min_of_rolling_average", min_of_rolling_average
    )
    MeanOfDifference = GenericIndicator("mean_of_difference", mean_of_difference)
    DifferenceOfExtremes = GenericIndicator(
        "difference_of_extremes", difference_of_extremes
    )
    MeanOfAbsoluteOneTimeStepDifference = GenericIndicator(
        "mean_of_absolute_one_time_step_difference",
        mean_of_absolute_one_time_step_difference,
    )
    DifferenceOfMeans = GenericIndicator(
        "difference_of_means",
        difference_of_means,
    )
    # TODO: implement or remove comments below
    # DoyPercentile = GenericIndicator(
    #     "doy_percentile",
    #     doy_percentile,
    # )
    # PeriodPercentile = GenericIndicator(
    #     "period_percentile",
    #     period_percentile,
    # )
    # MoyPercentile = GenericIndicator(
    #     "moy_percentile",
    #     moy_percentile,
    # )


@percentile_bootstrap
def _compute_exceedance(
    study: DataArray,
    threshold: DataArray | PercentileDataArray,
    operator: Operator,
    freq: str,  # noqa @percentile_bootstrap (don't rename it, it breaks bootstrap)
    bootstrap: bool,  # noqa @percentile_bootstrap
    is_doy_per: bool,
) -> DataArray:
    if is_doy_per:
        threshold = resample_doy(threshold, study)
    return operator(study, threshold)


def _check_couple_of_var(climate_vars: list[ClimateVariable], indicator: str):
    if len(climate_vars) != 2:
        raise InvalidIcclimArgumentError(
            f"{indicator} can only be computed on two"
            " variables sharing the same kind of values "
            "(e.g. temperatures)"
        )
    if climate_vars[0].threshold or climate_vars[1].threshold:
        raise InvalidIcclimArgumentError(
            f"{indicator} cannot be computed with thresholds."
        )
    var_0 = climate_vars[0].studied_data
    var_1 = climate_vars[1].studied_data
    var_0 = convert_units_to(var_0, var_1)
    return var_0, var_1


def _run_rolling_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    rolling_op: Callable[[DataArrayRolling], DataArray],  # sum | mean
    resampled_op: Callable[[...], DataArray],  # max | min
    date_event: bool,
    source_freq_delta: timedelta,
) -> DataArray:
    thresh_operator, study, threshold = _check_single_var(climate_vars)
    if threshold:
        exceedance = _compute_exceedance(
            operator=thresh_operator,
            study=study,
            freq=resample_freq.pandas_freq,
            threshold=threshold.value,
            bootstrap=_must_run_bootstrap(study, threshold),
            is_doy_per=threshold.is_doy_per_threshold,
        ).squeeze()
        study = study.where(exceedance)
    study = rolling_op(study.rolling(time=rolling_window_width))
    study = study.resample(time=resample_freq.pandas_freq)
    if date_event:
        return _reduce_with_date_event(
            resampled=study,
            reducer=resampled_op,
            window=rolling_window_width,
            source_delta=source_freq_delta,
        )
    else:
        return resampled_op(study, dim="time")  # type:ignore


def _run_simple_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    reducer_op: Callable[..., DataArray],
    date_event: bool,
):
    thresh_op, study, threshold = _check_single_var(climate_vars)
    if threshold is not None:
        exceedance = _compute_exceedance(
            operator=thresh_op,
            study=study,
            freq=resample_freq.pandas_freq,
            threshold=threshold.value,
            bootstrap=_must_run_bootstrap(study, threshold),
            is_doy_per=threshold.is_doy_per_threshold,
        ).squeeze()
        filtered_study = study.where(exceedance)
    else:
        filtered_study = study
    if date_event:
        return _reduce_with_date_event(
            resampled=filtered_study.resample(time=resample_freq.pandas_freq),
            reducer=reducer_op,
        )
    else:
        return reducer_op(
            filtered_study.resample(time=resample_freq.pandas_freq), dim="time"
        )


def _compute_exceedances(
    climate_vars: list[ClimateVariable], resample_freq: str, logical_link: LogicalLink
) -> DataArray:
    exceedances = [
        _compute_exceedance(
            operator=climate_var.threshold.operator,
            study=climate_var.studied_data,
            threshold=climate_var.threshold.value,
            freq=resample_freq,
            bootstrap=_must_run_bootstrap(
                climate_var.studied_data, climate_var.threshold
            ),
            is_doy_per=climate_var.threshold.is_doy_per_threshold,
        ).squeeze()
        for climate_var in climate_vars
    ]
    return logical_link(exceedances)


def _check_single_var(
    climate_vars: list[ClimateVariable],
) -> tuple[Operator | None, DataArray, Threshold | None]:
    if len(climate_vars) > 1:
        raise InvalidIcclimArgumentError("Too many variables.")
    if climate_vars[0].threshold:
        return (
            climate_vars[0].threshold.operator,
            climate_vars[0].studied_data,
            climate_vars[0].threshold,
        )
    else:
        return (None, climate_vars[0].studied_data, None)


def _must_run_bootstrap(da: DataArray, threshold: Threshold | None) -> bool:
    """Avoid bootstrapping if there is one single year overlapping
    or no year overlapping or all year overlapping.
    """
    # TODO: Don't run bootstrap when not on extreme percentile
    #       (below 20? 10? or above 80? 90?)
    if threshold is None or not threshold.is_doy_per_threshold:
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


def _same_freq_for_all(climate_vars: list[ClimateVariable]) -> bool:
    if len(climate_vars) == 1:
        return True
    freqs = list(map(lambda a: xr.infer_freq(a.studied_data.time), climate_vars))
    return all(map(lambda x: x == freqs[0], freqs[1:]))


def _get_inputs_metadata(
    climate_vars: list[ClimateVariable], resample_freq: Frequency, indicator_name
) -> list[dict[str, str]]:
    return list(
        map(
            lambda cf_var: cf_var.build_indicator_metadata(
                resample_freq,
                _must_run_bootstrap(cf_var.studied_data, cf_var.threshold),
                indicator_name,
            ),
            climate_vars,
        )
    )


def _reduce_with_date_event(
    resampled: DataArrayResample,
    reducer: Callable[[DataArrayResample], DataArray],
    source_delta: timedelta | None = None,
    window: int | None = None,
) -> DataArray:
    acc: list[DataArray] = []
    if reducer == DataArrayResample.max:
        group_reducer = DataArray.argmax
    elif reducer == DataArrayResample.min:
        group_reducer = DataArray.argmin
    else:
        raise NotImplementedError(
            f"Can't compute date_event due to unknown reducer:" f" '{reducer}'"
        )
    for label, sample in resampled:
        reduced_result = sample.isel(time=group_reducer(sample, dim="time"))
        if window is not None:
            result = _add_date_coords(
                original_sample=sample,
                result=sample.sum(dim="time"),
                start_time=reduced_result.time,
                end_time=reduced_result.time + window * source_delta,
                label=label,
            )
        else:
            result = _add_date_coords(
                original_sample=sample,
                result=sample.sum(dim="time"),
                event_date=reduced_result.time,
                label=label,
            )
        acc.append(result)
    return xr.concat(acc, "time")


def _count_occurrences_with_date(resampled: DataArrayResample):
    acc: list[DataArray] = []
    for label, sample in resampled:
        # Fixme probably not safe to compute on huge dataset,
        #  it should be fixed with
        #  https://github.com/pydata/xarray/issues/2511
        sample = sample.compute()
        first = sample.isel(time=sample.argmax("time")).time
        reversed_time = sample[::-1, :, :]
        last = reversed_time.isel(time=reversed_time.argmax("time")).time
        dated_occurrences = _add_date_coords(
            original_sample=sample,
            result=sample.sum(dim="time"),
            start_time=first,
            end_time=last,
            label=label,
        )
        acc.append(dated_occurrences)
    return xr.concat(acc, "time")


def _consecutive_occurrences_with_dates(
    resampled: DataArrayResample, source_freq_delta: timedelta
):
    acc = []
    for label, sample in resampled:
        # todo might be unnecessary to replace NaN by 0 with the new rle
        #      (if the new rle does not generate NaN)
        sample = sample.where(~sample.isnull(), 0)
        time_index_of_max_rle = sample.argmax(dim="time")
        # fixme: `.compute` is needed until xarray merges this pr:
        #        https://github.com/pydata/xarray/pull/5873
        time_index_of_max_rle = time_index_of_max_rle.compute()
        dated_longest_run = sample[{"time": time_index_of_max_rle}]
        start_time = sample.isel(
            time=time_index_of_max_rle.where(time_index_of_max_rle > 0, 0)
        ).time
        end_time = start_time + (dated_longest_run * source_freq_delta)
        dated_longest_run = _add_date_coords(
            original_sample=sample,
            result=dated_longest_run,
            start_time=start_time,
            end_time=end_time,
            label=label,
        )
        acc.append(dated_longest_run)
    max_consecutive_occurrence = xr.concat(acc, "time")
    return max_consecutive_occurrence


def _add_date_coords(
    original_sample: DataArray,
    result: DataArray,
    label: str | np.datetime64,
    start_time: DataArray = None,
    end_time: DataArray = None,
    event_date: DataArray = None,
) -> DataArray:
    new_coords = {c: original_sample[c] for c in original_sample.coords if c != "time"}
    if event_date is None:
        new_coords["event_date_start"] = start_time
        new_coords["event_date_end"] = end_time
    else:
        new_coords["event_date"] = event_date
    new_coords["time"] = label
    return DataArray(data=result, coords=new_coords)


def _is_amount_unit(unit: str) -> bool:
    # todo: maybe there is a more generic way to handle that with pint,
    #       we could try to convert to pint and check if it has a "day-1" in it
    #       (or a similar "by-time" unit)
    return unit in ["cm", "mm", "m"]


def _to_percent(da: DataArray, sampling_freq: Frequency) -> DataArray:
    if sampling_freq == FrequencyRegistry.MONTH:
        da = da / da.time.dt.daysinmonth * 100
    elif sampling_freq == FrequencyRegistry.YEAR:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 366
        coef[{"time": ~leap_years}] = 365
        da = da / coef
    elif sampling_freq == FrequencyRegistry.AMJJAS:
        da = da / 183
    elif sampling_freq == FrequencyRegistry.ONDJFM:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 183
        coef[{"time": ~leap_years}] = 182
        da = da / coef
    elif sampling_freq == FrequencyRegistry.DJF:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 91
        coef[{"time": ~leap_years}] = 90
        da = da / coef
    elif sampling_freq in [FrequencyRegistry.MAM, FrequencyRegistry.JJA]:
        da = da / 92
    elif sampling_freq == FrequencyRegistry.SON:
        da = da / 91
    else:
        # TODO improve this for custom resampling
        warn(
            "For now, '%' unit can only be used when `slice_mode` is one of: "
            "{MONTH, YEAR, AMJJAS, ONDJFM, DJF, MAM, JJA, SON}."
        )
        return da
    da.attrs[UNITS_ATTRIBUTE_KEY] = PART_OF_A_WHOLE_UNIT
    return da


def _is_leap_year(da: DataArray) -> np.ndarray:
    time_index = da.indexes.get("time")
    if isinstance(time_index, xr.CFTimeIndex):
        return CfCalendarRegistry.lookup(time_index.calendar).is_leap(da.time.dt.year)
    else:
        return da.time.dt.is_leap_year
