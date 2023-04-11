from __future__ import annotations

import abc
from abc import ABC
from datetime import timedelta
from functools import partial, reduce
from typing import Any, Callable
from warnings import warn

import jinja2
import numpy
import numpy as np
import xarray as xr
from jinja2 import Environment
from pint import DefinitionSyntaxError, Quantity, UndefinedUnitError
from xarray import DataArray
from xarray.core.resample import DataArrayResample
from xarray.core.rolling import DataArrayRolling
from xclim.core.calendar import select_time
from xclim.core.cfchecks import cfcheck_from_name
from xclim.core.datachecks import check_freq
from xclim.core.missing import MissingBase
from xclim.core.options import MISSING_METHODS, MISSING_OPTIONS, OPTIONS
from xclim.core.units import convert_units_to, rate2amount, str2pint, to_agg_units
from xclim.core.units import units as xc_units
from xclim.core.units import units2pint
from xclim.indices import run_length

from icclim.generic_indices.generic_templates import INDICATORS_TEMPLATES_EN
from icclim.generic_indices.threshold import PercentileThreshold, Threshold
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import CfCalendarRegistry
from icclim.models.climate_variable import ClimateVariable
from icclim.models.constants import (
    GROUP_BY_METHOD,
    GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD,
    PART_OF_A_WHOLE_UNIT,
    REFERENCE_PERIOD_ID,
    RESAMPLE_METHOD,
    UNITS_KEY,
)
from icclim.models.frequency import RUN_INDEXER, Frequency, FrequencyRegistry
from icclim.models.index_config import IndexConfig
from icclim.models.logical_link import LogicalLink
from icclim.models.operator import OperatorRegistry
from icclim.models.registry import Registry

jinja_env = Environment()


class MissingMethodLike(metaclass=abc.ABCMeta):
    """workaround xclim missing type"""

    # todo: PR that to xclim

    def execute(self, *args, **kwargs) -> MissingBase:
        ...

    def validate(self, *args, **kwargs) -> bool:
        ...


class Indicator(ABC):
    name: str
    standard_name: str
    long_name: str
    cell_methods: str

    templated_properties = [
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


class ResamplingIndicator(Indicator, ABC):
    """Abstract class for indicators."""

    missing: str
    missing_options: dict | None

    def __init__(self, missing="from_context", missing_options=None):
        self.missing_options = missing_options
        self.missing = missing
        if self.missing == "from_context" and self.missing_options is not None:
            raise ValueError(
                "Cannot set `missing_options` with `missing` method being from context."
            )
        missing_method: MissingMethodLike = MISSING_METHODS[self.missing]  # noqa typing
        self._missing = missing_method.execute
        if self.missing_options:
            missing_method.validate(**self.missing_options)
        super().__init__()

    def preprocess(
        self,
        climate_vars: list[ClimateVariable],
        jinja_scope: dict[str, Any],
        src_freq: Frequency,
    ) -> list[ClimateVariable]:
        _check_data(climate_vars, src_freq.pandas_freq)
        _check_cf(climate_vars)
        self.format(jinja_scope=jinja_scope)
        return climate_vars

    def postprocess(
        self,
        result: DataArray,
        climate_vars: list[ClimateVariable],
        output_freq: str,
        src_freq: str,
        indexer: dict,
        out_unit: str | None,
    ):
        if out_unit is not None:
            result = convert_units_to(result, out_unit, context="hydro")
        if self.missing != "skip" and indexer is not None:
            # reference variable is a subset of the studied variable,
            # so no need to check it.
            das = filter(lambda cv: not cv.is_reference, climate_vars)
            das = map(lambda cv: cv.studied_data, das)
            das = list(das)
            if "time" in result.dims:
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
        for templated_property in self.templated_properties:
            template = jinja_env.from_string(
                getattr(self, templated_property),
                globals=jinja_scope,
            )
            setattr(self, templated_property, template.render())

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
        missing_method: MissingMethodLike = MISSING_METHODS[self.missing]  # noqa typing
        miss = (
            missing_method.execute(da, resample_freq, src_freq, options, indexer)
            for da in in_data
            if "time" in da.coords
        )
        # Reduce by or and broadcast to ensure the same length in time
        # When indexing is used and there are no valid points in the last period,
        # mask will not include it
        mask = reduce(np.logical_or, miss)  # noqa typing
        if isinstance(mask, DataArray) and mask.time.size < out_data.time.size:
            mask = mask.reindex(time=out_data.time, fill_value=True)
        return out_data.where(~mask)


class GenericIndicator(ResamplingIndicator):
    def __init__(
        self,
        name: str,
        process: Callable[..., DataArray],
        definition: str,
        check_vars: (
            Callable[[list[ClimateVariable], GenericIndicator], None] | None
        ) = None,
        sampling_methods: list[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        local = INDICATORS_TEMPLATES_EN
        self.name = name
        self.process = process
        self.standard_name = local[name]["standard_name"]
        self.cell_methods = local[name]["cell_methods"]
        self.long_name = local[name]["long_name"]
        self.check_vars = check_vars
        self.definition = definition
        self.sampling_methods = (
            sampling_methods if sampling_methods is not None else [RESAMPLE_METHOD]
        )

    def preprocess(  # noqa signature != from super
        self,
        climate_vars: list[ClimateVariable],
        jinja_scope: dict[str, Any],
        output_frequency: Frequency,
        src_freq: Frequency,
        output_unit: str | None,
        coef: float | None,
        sampling_method: str,
    ) -> list[ClimateVariable]:
        if not _same_freq_for_all(climate_vars):
            raise InvalidIcclimArgumentError(
                "All variables must have the same time frequency (for example daily) to"
                " be compared with each others, but this was not the case."
            )
        if self.check_vars is not None:
            self.check_vars(climate_vars, self)
        if sampling_method not in self.sampling_methods:
            raise InvalidIcclimArgumentError(
                f"{self.name} can only be computed with the following"
                f" sampling_method(s): {self.sampling_methods}"
            )
        if output_unit is not None:
            if _is_amount_unit(output_unit):
                climate_vars = _convert_rates_to_amounts(
                    climate_vars=climate_vars, output_unit=output_unit
                )
            elif _is_a_diff_indicator(self) and output_unit != "%":
                # [gh:255] Indicators computing the difference between two
                # variables must first convert the units of input variables
                # to the expected output unit in order to avoid converting
                # the output which would be a relative "temperature".
                # In other words: a 15 Kelvin difference *is* equivalent
                # to a 15 degC and *is not* to a -258.15 degC.
                for climate_var in climate_vars:
                    climate_var.studied_data = convert_units_to(
                        climate_var.studied_data, target=output_unit
                    )
            else:
                pass  # nothing to do
        if coef is not None:
            for climate_var in climate_vars:
                climate_var.studied_data = coef * climate_var.studied_data
        if output_frequency.indexer:
            for climate_var in climate_vars:
                climate_var.studied_data = select_time(
                    climate_var.studied_data, **output_frequency.indexer, drop=True
                )
        return super().preprocess(
            climate_vars=climate_vars,
            jinja_scope=jinja_scope,
            src_freq=src_freq,
        )

    def __call__(self, config: IndexConfig) -> DataArray:
        src_freq = config.climate_variables[0].source_frequency
        base_jinja_scope = {
            "np": numpy,
            "enumerate": enumerate,
            "len": len,
            "output_freq": config.frequency,
            "source_freq": src_freq,
        }
        climate_vars_meta = _get_climate_vars_metadata(
            config.climate_variables, src_freq, base_jinja_scope, jinja_env
        )
        jinja_scope: dict[str, Any] = {
            "min_spell_length": config.min_spell_length,
            "rolling_window_width": config.rolling_window_width,
            "climate_vars": climate_vars_meta,
            "is_compared_to_reference": config.is_compared_to_reference,
            "reference_period": config.reference_period,
        }
        jinja_scope.update(base_jinja_scope)
        climate_vars = self.preprocess(
            climate_vars=config.climate_variables,
            jinja_scope=jinja_scope,
            output_frequency=config.frequency,
            src_freq=src_freq,
            output_unit=config.out_unit,
            coef=config.coef,
            sampling_method=config.sampling_method,
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
            sampling_method=config.sampling_method,
        )
        return self.postprocess(
            result,
            climate_vars=climate_vars,
            output_freq=config.frequency.pandas_freq,
            src_freq=src_freq.pandas_freq,
            indexer=config.frequency.indexer,
            out_unit=config.out_unit,
        )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, GenericIndicator)
            and self.long_name == other.long_name
            and self.standard_name == other.standard_name
            and self.process == other.process
        )


def count_occurrences(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    date_event: bool,
    to_percent: bool,
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
        result.attrs[UNITS_KEY] = "%"
        return result
    else:
        return to_agg_units(result, climate_vars[0].studied_data, "count")


def max_consecutive_occurrence(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    date_event: bool,
    source_freq_delta: timedelta,
    **kwargs,  # noqa
) -> DataArray:
    merged_exceedances = _compute_exceedances(
        climate_vars, resample_freq.pandas_freq, logical_link
    )
    rle = run_length.rle(merged_exceedances, dim="time", index="first")
    resampled = rle.resample(time=resample_freq.pandas_freq)
    if date_event:
        result = _consecutive_occurrences_with_dates(resampled, source_freq_delta)
    else:
        result = resampled.max(dim="time")
    return to_agg_units(result, climate_vars[0].studied_data, "count")


def sum_of_spell_lengths(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    min_spell_length: int,
    **kwargs,  # noqa
) -> DataArray:
    merged_exceedances = _compute_exceedances(
        climate_vars, resample_freq.pandas_freq, logical_link
    )
    rle = run_length.rle(merged_exceedances, dim="time", index="first")
    cropped_rle = rle.where(rle >= min_spell_length, other=0)
    result = cropped_rle.resample(time=resample_freq.pandas_freq).max(dim="time")
    return to_agg_units(result, climate_vars[0].studied_data, "count")


def excess(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa
) -> DataArray:
    study, threshold = get_single_var(climate_vars)
    if threshold.operator is not OperatorRegistry.REACH:
        raise InvalidIcclimArgumentError("")
    excesses = threshold.compute(study, override_op=lambda da, th: da - th)
    res = (
        (excesses).clip(min=0).resample(time=resample_freq.pandas_freq).sum(dim="time")
    )
    return to_agg_units(res, study, "delta_prod")


def deficit(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa
) -> DataArray:
    study, threshold = get_single_var(climate_vars)
    deficit = threshold.compute(study, override_op=lambda da, th: th - da)
    res = deficit.clip(min=0).resample(time=resample_freq.pandas_freq).sum(dim="time")
    return to_agg_units(res, study, "delta_prod")


def fraction_of_total(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    to_percent: bool,
    **kwargs,  # noqa
) -> DataArray:
    study, threshold = get_single_var(climate_vars)
    if threshold.threshold_min_value is not None:
        total = (
            study.where(threshold.operator(study, threshold.threshold_min_value.m))
            .resample(time=resample_freq.pandas_freq)
            .sum(dim="time")
        )
    else:
        total = study.resample(time=resample_freq.pandas_freq).sum(dim="time")
    exceedance = _compute_exceedance(
        study=study,
        threshold=threshold,
        freq=resample_freq.pandas_freq,
        bootstrap=_must_run_bootstrap(study, threshold),
    ).squeeze()
    over = (
        study.where(exceedance, 0)
        .resample(time=resample_freq.pandas_freq)
        .sum(dim="time")
    )
    res = over / total
    if to_percent:
        res = res * 100
        res.attrs[UNITS_KEY] = "%"
    else:
        res.attrs[UNITS_KEY] = PART_OF_A_WHOLE_UNIT
    return res


def maximum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    date_event: bool,
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
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.sum,
        date_event=False,
        must_convert_rate=True,
    )


def standard_deviation(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
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
    **kwargs,  # noqa
):
    study, ref = get_couple_of_var(climate_vars, "mean_of_difference")
    mean_of_diff = (study - ref).resample(time=resample_freq.pandas_freq).mean()
    mean_of_diff.attrs["units"] = study.attrs["units"]
    return mean_of_diff


def difference_of_extremes(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa
):
    study, ref = get_couple_of_var(climate_vars, "difference_of_extremes")
    max_study = study.resample(time=resample_freq.pandas_freq).max()
    min_ref = ref.resample(time=resample_freq.pandas_freq).min()
    diff_of_extremes = max_study - min_ref
    diff_of_extremes.attrs["units"] = study.attrs["units"]
    return diff_of_extremes


def mean_of_absolute_one_time_step_difference(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa
) -> DataArray:
    """
    Generification of ECAD's vDTR index.

    Parameters
    ----------
    climate_vars : List[ClimateVariable]
    The two climate variables necessary to compute the indicator.
    resample_freq :  Frequency
    Expected frequency of the output.
    kwargs : dict
    Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
    mean_of_absolute_one_time_step_difference as a xarray.DataArray
    """
    study, ref = get_couple_of_var(
        climate_vars, "mean_of_absolute_one_time_step_difference"
    )
    one_time_step_diff = (study - ref).diff(dim="time")
    res = abs(one_time_step_diff).resample(time=resample_freq.pandas_freq).mean()
    res.attrs["units"] = study.attrs["units"]
    return res


def difference_of_means(
    climate_vars: list[ClimateVariable],
    to_percent: bool,
    resample_freq: Frequency,
    sampling_method: str,
    is_compared_to_reference: bool,
    **kwargs,  # noqa
):
    if is_compared_to_reference and sampling_method == RESAMPLE_METHOD:
        raise InvalidIcclimArgumentError(
            "It does not make sense to resample the reference variable if it is"
            " already a subsample of the studied variable. Try setting"
            f" `sampling_method='{GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD}'`"
            f" instead."
        )
    study, ref = get_couple_of_var(climate_vars, "difference_of_means")
    if sampling_method == GROUP_BY_METHOD:
        if resample_freq.group_by_key == RUN_INDEXER:
            mean_study = study.mean(dim="time")
            mean_ref = ref.mean(dim="time")
        else:
            mean_study = study.groupby(resample_freq.group_by_key).mean()
            mean_ref = ref.groupby(resample_freq.group_by_key).mean()
    elif sampling_method == RESAMPLE_METHOD:
        mean_study = study.resample(time=resample_freq.pandas_freq).mean()
        mean_ref = ref.resample(time=resample_freq.pandas_freq).mean()
    elif sampling_method == GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD:
        if (
            resample_freq.group_by_key == RUN_INDEXER
            or resample_freq == FrequencyRegistry.YEAR
        ):
            mean_study = study.resample(time=resample_freq.pandas_freq).mean()
            # data is already filtered with only the indexed values.
            # Thus there is only one "group".
            mean_ref = ref.mean(dim="time")
        else:
            return _diff_of_means_of_resampled_x_by_groupedby_y(
                resample_freq, to_percent, study, ref
            )
    else:
        raise NotImplementedError(f"Unknown sampling_method: '{sampling_method}'.")
    diff_of_means = mean_study - mean_ref
    if to_percent:
        diff_of_means = diff_of_means / mean_ref * 100
        diff_of_means.attrs["units"] = "%"
    else:
        diff_of_means.attrs["units"] = study.attrs["units"]
    return diff_of_means


def _diff_of_means_of_resampled_x_by_groupedby_y(
    resample_freq: Frequency, to_percent: bool, study: DataArray, ref: DataArray
) -> DataArray:
    mean_ref = ref.groupby(resample_freq.group_by_key).mean()
    acc = []
    if resample_freq == FrequencyRegistry.MONTH:
        key = "month"
        dt_selector = lambda x: x.time.dt.month  # noqa lamdab assigned
    elif resample_freq == FrequencyRegistry.DAY:
        key = "dayofyear"
        dt_selector = lambda x: x.time.dt.dayofyear  # noqa lamdab assigned
    else:
        raise NotImplementedError(
            f"Can't use {GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD}"
            f" with the frequency {resample_freq.long_name}."
        )
    for label, sample in study.resample(time=resample_freq.pandas_freq):
        sample_mean = sample.mean(dim="time")
        ref_group_mean = mean_ref.sel({key: dt_selector(sample).values[0]})
        sample_diff_of_means = sample_mean - ref_group_mean
        if to_percent:
            sample_diff_of_means = sample_diff_of_means / ref_group_mean * 100
        del sample_diff_of_means[key]
        sample_diff_of_means = sample_diff_of_means.expand_dims(time=[label])
        acc.append(sample_diff_of_means)
    diff_of_means = xr.concat(acc, dim="time")
    if to_percent:
        diff_of_means.attrs["units"] = "%"
    else:
        diff_of_means.attrs["units"] = study.attrs["units"]
    return diff_of_means


def _check_single_var(climate_vars: list[ClimateVariable], indicator: GenericIndicator):
    if len(climate_vars) > 1:
        raise InvalidIcclimArgumentError(
            f"{indicator.name} can only be computed on a single variable."
        )


def _check_couple_of_vars(
    climate_vars: list[ClimateVariable], indicator: GenericIndicator
):
    if len(climate_vars) != 2:
        raise InvalidIcclimArgumentError(
            f"{indicator.name} can only be computed on two variables sharing the same"
            f" unit (e.g. 2 temperatures). You can either provide a secondary variable"
            f" with `in_files` or `var_name`, or you can let icclim compute this"
            f" second variable as a subset of the first one using"
            f" `base_period_time_range`."
        )


class GenericIndicatorRegistry(Registry[GenericIndicator]):
    def __init__(self):
        super().__init__()

    _item_class = GenericIndicator

    CountOccurrences = GenericIndicator(
        "count_occurrences",
        count_occurrences,
        definition="Count occurrences where threshold(s) are met"
        " (e.g. SU, Tx90p, RR1).",
    )
    MaxConsecutiveOccurrence = GenericIndicator(
        "max_consecutive_occurrence",
        max_consecutive_occurrence,
        definition="Count the maximum number of consecutive occurrences when"
        " threshold(s) are met (e.g. CDD, CSU, CWD).",
    )
    SumOfSpellLengths = GenericIndicator(
        "sum_of_spell_lengths",
        sum_of_spell_lengths,
        definition="Sum the lengths of each consecutive occurrence spell when"
        " threshold(s) are met. The minimum spell length is controlled by"
        " `min_spell_length` (e.g. WSDI, CSDI).",
    )
    Excess = GenericIndicator(
        "excess",
        excess,
        check_vars=_check_single_var,
        definition="Compute the excess over the given threshold. The excess is"
        " `sum(x[x>t] - t)` where x is the studied variable and t the threshold"
        " (e.g. GD4).",
    )
    Deficit = GenericIndicator(
        "deficit",
        deficit,
        check_vars=_check_single_var,
        definition="Compute the deficit below the given threshold. The deficit is"
        " `sum(t - x[x<t])` where x is the studied variable and t the threshold"
        " (e.g. HD17).",
    )
    FractionOfTotal = GenericIndicator(
        "fraction_of_total",
        fraction_of_total,
        check_vars=_check_single_var,
        definition="Compute the fraction of values meeting threshold(s) over the sum of"
        " every values (e.g. R75pTOT, R95pTOT).",
    )
    Maximum = GenericIndicator(
        "maximum",
        maximum,
        definition="Maximum of values that met threshold(s), if threshold(s) are given"
        " (e.g. Txx, Tnx).",
    )
    Minimum = GenericIndicator(
        "minimum",
        minimum,
        definition="Minimum of values that met threshold(s), if threshold(s) are given"
        " (e.g. Txn, Tnn).",
    )
    Average = GenericIndicator(
        "average",
        average,
        definition="Average of values that met threshold(s), if threshold(s) are given"
        " (e.g. Tx, Tn)",
    )
    Sum = GenericIndicator(
        "sum",
        sum,
        definition="Sum of values that met threshold(s), if threshold(s) are given"
        " (e.g. PRCPTOT, RR).",
    )
    StandardDeviation = GenericIndicator(
        "standard_deviation",
        standard_deviation,
        definition="Standard deviation of values that met threshold(s),"
        " if threshold(s) are given.",
    )
    MaxOfRollingSum = GenericIndicator(
        "max_of_rolling_sum",
        max_of_rolling_sum,
        check_vars=_check_single_var,
        definition="Maximum of rolling sum over time dimension"
        " (e.g. RX5DAY: maximum 5 days window of precipitation accumulation).",
    )
    MinOfRollingSum = GenericIndicator(
        "min_of_rolling_sum",
        min_of_rolling_sum,
        check_vars=_check_single_var,
        definition="Minimum of rolling sum over time dimension.",
    )
    MaxOfRollingAverage = GenericIndicator(
        "max_of_rolling_average",
        max_of_rolling_average,
        check_vars=_check_single_var,
        definition="Maximum of rolling average over time dimension.",
    )
    MinOfRollingAverage = GenericIndicator(
        "min_of_rolling_average",
        min_of_rolling_average,
        check_vars=_check_single_var,
        definition="Minimum of rolling average over time dimension.",
    )
    MeanOfDifference = GenericIndicator(
        "mean_of_difference",
        mean_of_difference,
        check_vars=_check_couple_of_vars,
        definition="Average of the difference between two variables"
        ", or one variable and it's reference period values"
        " (e.g. DTR: `mean(tasmax - tasmin)`).",
    )
    DifferenceOfExtremes = GenericIndicator(
        "difference_of_extremes",
        difference_of_extremes,
        check_vars=_check_couple_of_vars,
        definition="Difference of extremes between two variables"
        ", or one variable and it's reference period values."
        " The extremes are always `maximum` for the first variable and"
        " `minimum` for the second variable"
        " (e.g. ETR: `max(tasmax) - min(tasmin)`).",
    )
    MeanOfAbsoluteOneTimeStepDifference = GenericIndicator(
        "mean_of_absolute_one_time_step_difference",
        mean_of_absolute_one_time_step_difference,
        check_vars=_check_couple_of_vars,
        definition="Average of the absolute one time step by one time step difference"
        " between two variables,"
        " or one variable and it's reference period values"
        " (e.g. vDTR:"
        " `mean((tasmax[i] - tasmin[i]) - (tasmax[i-1] - tasmin[i-1])` ;"
        " where i is the day of measure).",
    )
    DifferenceOfMeans = GenericIndicator(
        "difference_of_means",
        difference_of_means,
        check_vars=_check_couple_of_vars,
        sampling_methods=[
            RESAMPLE_METHOD,
            GROUP_BY_METHOD,
            GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD,
        ],
        definition="Difference of the average between two variables"
        ", or one variable and it's reference period values"
        " (e.g. anomaly: `mean(tasmax) - mean(tasmax_ref]))`.",
    )


def _compute_exceedance(
    study: DataArray,
    threshold: Threshold,
    freq: str,  # noqa used by @percentile_bootstrap (don't rename, it breaks bootstrap)
    bootstrap: bool,  # noqa used by @percentile_bootstrap
) -> DataArray:
    exceedances = threshold.compute(study, freq=freq, bootstrap=bootstrap)
    if bootstrap:
        exceedances.attrs[REFERENCE_PERIOD_ID] = threshold.value.attrs[
            "climatology_bounds"
        ]
    return exceedances


def get_couple_of_var(
    climate_vars: list[ClimateVariable], indicator: str
) -> tuple[DataArray, DataArray]:
    if len(climate_vars) != 2:
        raise InvalidIcclimArgumentError(
            f"{indicator} needs two variables **or** one variable and a "
            f"`base_period_time_range` period to extract a reference variable."
        )
    if climate_vars[0].threshold or climate_vars[1].threshold:
        raise InvalidIcclimArgumentError(
            f"{indicator} cannot be computed with thresholds."
        )
    study = climate_vars[0].studied_data
    ref = climate_vars[1].studied_data
    study = convert_units_to(study, ref, context="hydro")
    return study, ref


def _run_rolling_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    rolling_op: Callable[[DataArrayRolling], DataArray],  # sum | mean
    resampled_op: Callable[[DataArray], DataArray],  # max | min
    date_event: bool,
    source_freq_delta: timedelta,
) -> DataArray:
    study, threshold = get_single_var(climate_vars)
    if threshold:
        exceedance = _compute_exceedance(
            study=study,
            freq=resample_freq.pandas_freq,
            threshold=threshold,
            bootstrap=_must_run_bootstrap(study, threshold),
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
    must_convert_rate: bool = False,
):
    study, threshold = get_single_var(climate_vars)
    if threshold is not None:
        exceedance = _compute_exceedance(
            study=study,
            freq=resample_freq.pandas_freq,
            threshold=threshold,
            bootstrap=_must_run_bootstrap(study, threshold),
        ).squeeze()
        filtered_study = study.where(exceedance)
    else:
        filtered_study = study
    if must_convert_rate:
        if _is_rate(filtered_study):
            filtered_study = rate2amount(filtered_study)
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
            study=climate_var.studied_data,
            threshold=climate_var.threshold,
            freq=resample_freq,
            bootstrap=_must_run_bootstrap(
                climate_var.studied_data, climate_var.threshold
            ),
        ).squeeze()
        for climate_var in climate_vars
    ]
    return logical_link(exceedances)


def get_single_var(
    climate_vars: list[ClimateVariable],
) -> tuple[DataArray, Threshold | None]:
    if climate_vars[0].threshold:
        return (
            climate_vars[0].studied_data,
            climate_vars[0].threshold,
        )
    else:
        return climate_vars[0].studied_data, None


def _must_run_bootstrap(da: DataArray, threshold: Threshold | None) -> bool:
    """Avoid bootstrapping if there is one single year overlapping
    or no year overlapping or all year overlapping.
    """
    # TODO: Don't run bootstrap when not on extreme percentile
    #       (run only below 20? 10? and above 80? 90?)
    if (
        threshold is None
        or not isinstance(threshold, PercentileThreshold)
        or (
            isinstance(threshold, PercentileThreshold)
            and not threshold.is_doy_per_threshold
        )
    ):
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


def _get_climate_vars_metadata(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    jinja_scope: dict[str, Any],
    jinja_env: jinja2.Environment,
) -> list[dict[str, str]]:
    return [
        c_var.build_indicator_metadata(
            resample_freq,
            _must_run_bootstrap(c_var.studied_data, c_var.threshold),
            jinja_scope,
            jinja_env,
        )
        for c_var in climate_vars
    ]


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
            f"Can't compute `date_event` due to unknown reducer:" f" '{reducer}'"
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
        reversed_time = sample.reindex(time=list(reversed(sample.time.values)))
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
    result = xr.concat(acc, "time")
    return result


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
    try:
        u = units2pint(unit)  # turn a cf u
        return xc_units.Quantity(1, u).check("[length]")
    except (UndefinedUnitError, DefinitionSyntaxError):
        return False


def _is_a_diff_indicator(indicator: Indicator) -> bool:
    return (
        indicator == GenericIndicatorRegistry.DifferenceOfExtremes
        or indicator == GenericIndicatorRegistry.MeanOfDifference
        or indicator == GenericIndicatorRegistry.MeanOfAbsoluteOneTimeStepDifference
        or indicator == GenericIndicatorRegistry.DifferenceOfMeans
    )


def _convert_rates_to_amounts(climate_vars: list[ClimateVariable], output_unit: str):
    for climate_var in climate_vars:
        current_unit = climate_var.studied_data.attrs.get(UNITS_KEY, None)
        if current_unit is not None and not _is_amount_unit(current_unit):
            with xc_units.context("hydro"):
                climate_var.studied_data = rate2amount(
                    climate_var.studied_data, out_units=output_unit
                )
    return climate_vars


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
    da.attrs[UNITS_KEY] = PART_OF_A_WHOLE_UNIT
    return da


def _is_leap_year(da: DataArray) -> np.ndarray:
    time_index = da.indexes.get("time")
    if isinstance(time_index, xr.CFTimeIndex):
        return CfCalendarRegistry.lookup(time_index.calendar).is_leap(da.time.dt.year)
    else:
        return da.time.dt.is_leap_year


def _check_cf(climate_vars: list[ClimateVariable]):
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


def _check_data(climate_vars: list[ClimateVariable], src_freq: str):
    if src_freq is None:
        return
    for climate_var in climate_vars:
        da = climate_var.studied_data
        if "time" in da.coords and da.time.ndim == 1 and len(da.time) > 3:
            check_freq(da, src_freq, strict=True)


def _is_rate(query: Quantity | DataArray) -> bool:
    if isinstance(query, DataArray):
        query = str2pint(query.attrs[UNITS_KEY])
    return query.dimensionality.get("[time]", None) == -1
