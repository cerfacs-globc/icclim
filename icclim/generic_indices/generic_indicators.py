from __future__ import annotations

import abc
from functools import reduce
from typing import Any, Callable

import numpy
import numpy as np
import xarray as xr
from jinja2 import Environment
from xarray import DataArray
from xarray.core.rolling import DataArrayRolling
from xclim.core import datachecks
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import resample_doy, select_time
from xclim.core.cfchecks import cfcheck_from_name
from xclim.core.options import MISSING_METHODS, MISSING_OPTIONS, OPTIONS
from xclim.core.units import convert_units_to, to_agg_units
from xclim.core.utils import PercentileDataArray
from xclim.indices import run_length

from icclim.generic_indices.generic_templates import INDICATORS_TEMPLATES_EN
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.climate_variable import ClimateVariable
from icclim.models.constants import UNITS_ATTRIBUTE_KEY
from icclim.models.frequency import Frequency
from icclim.models.index_config import IndexConfig
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
        if self.missing_options:
            MISSING_METHODS[self.missing].validate(**self.missing_options)
        super().__init__()

    def datachecks(self, climate_vars: list[ClimateVariable], src_freq: str):
        if src_freq is None:
            return
        for climate_var in climate_vars:
            da = climate_var.study_da
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
    ) -> list[ClimateVariable]:
        self.datachecks(climate_vars, src_freq.pandas_freq)
        self.cfcheck(climate_vars)
        self.format(jinja_scope=jinja_scope)
        if output_frequency.indexer:
            for climate_var in climate_vars:
                climate_var.study_da = select_time(
                    climate_var.study_da, **output_frequency.indexer
                )
        return climate_vars

    def postprocess(
        self,
        result: DataArray,
        das: list[DataArray],
        output_freq: str,
        src_freq: str,
        indexer: dict = None,
    ):
        if self.missing == "skip":
            return self._handle_missing_values(
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
        self, in_data, resample_freq: str, src_freq: str, indexer: dict | None, out_data
    ):
        options = self.missing_options or OPTIONS[MISSING_OPTIONS].template(
            self.missing, {}
        )
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
        if isinstance(mask, DataArray) and mask.time.size < out_data[0].time.size:
            mask = mask.reindex(time=out_data[0].time, fill_value=True)
        return [out.where(~mask) for out in out_data]


class GenericIndicator(ResamplingIndicator):
    name: str

    def __init__(self, name: str, process: Callable[..., DataArray], **kwargs):
        super().__init__(**kwargs)
        local = INDICATORS_TEMPLATES_EN
        self.name = name
        self.process = process
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
    ) -> list[ClimateVariable]:
        if not _same_freq_for_all(climate_vars):
            raise InvalidIcclimArgumentError(
                "All variables must have the same time frequency (for example daily) to"
                " be compared with each others, but this was not the case."
            )
        return super().preprocess(
            climate_vars=climate_vars,
            jinja_scope=jinja_scope,
            output_frequency=output_frequency,
            src_freq=src_freq,
        )

    def __call__(self, config: IndexConfig) -> DataArray:
        # icclim  wrapper
        src_freq = config.climate_variables[0].cf_meta.frequency
        jinja_scope = {
            "output_freq": config.frequency,
            "source_freq": src_freq,
            "min_spell_length": config.window,
            "rolling_window_width": config.window,
            "np": numpy,
            "enumerate": enumerate,
            "len": len,
            "climate_vars": _get_inputs_metadata(config.climate_variables, src_freq),
            "is_single_var": config.is_single_var,
            "reference_period": config.reference_period,
        }
        climate_vars = self.preprocess(
            climate_vars=config.climate_variables,
            jinja_scope=jinja_scope,
            output_frequency=config.frequency,
            src_freq=src_freq,
        )
        result = self.process(
            climate_vars=climate_vars,
            resample_freq=config.frequency.pandas_freq,
            min_spell_length=config.window,
            rolling_window_width=config.window,
            group_by_freq=config.frequency.group_by_key,
            is_single_var=config.is_single_var,
        )
        return self.postprocess(
            result,
            das=list(map(lambda cv: cv.study_da, climate_vars)),
            output_freq=config.frequency.pandas_freq,
            src_freq=src_freq.pandas_freq,
        )


def count_occurrences(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_exceedances_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=lambda mask: mask.sum(dim="time"),
    )


def max_consecutive_occurrence(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_exceedances_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=lambda mask: mask.map(run_length.longest_run, dim="time"),
    )


def sum_of_spell_lengths(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    min_spell_length: int = 6,
) -> DataArray:
    return _run_exceedances_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=lambda mask: mask.map(
            run_length.windowed_run_count, window=min_spell_length, dim="time"
        ),
    )


def excess(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    op, study, threshold = _check_single_var(climate_vars)
    if threshold.is_doy_per_threshold:
        thresh = resample_doy(threshold.value, study)
    else:
        thresh = threshold.value
    res = (study - thresh).clip(min=0).resample(time=resample_freq).sum(dim="time")
    return to_agg_units(res, study, "delta_prod")


def deficit(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    op, study, threshold = _check_single_var(climate_vars)
    if threshold.is_doy_per_threshold:
        thresh = resample_doy(threshold.value, study)
    else:
        thresh = threshold.value
    res = (thresh - study).clip(min=0).resample(time=resample_freq).sum(dim="time")
    return to_agg_units(res, study, "delta_prod")


def fraction_of_total(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    op, study, threshold = _check_single_var(climate_vars)
    if threshold.threshold_min_value:
        total = (
            study.where(op(study, threshold.threshold_min_value.value))
            .resample(time=resample_freq)
            .sum(dim="time")
        )
    else:
        total = study.resample(time=resample_freq).sum(dim="time")
    exceedance = _compute_exceedance(
        operator=op,
        study=study,
        threshold=threshold.value,
        resample_freq=resample_freq,
        bootstrap=_must_run_bootstrap(study, threshold),
        is_doy_per=threshold.is_doy_per_threshold,
    ).squeeze()
    over = study.where(exceedance).resample(time=resample_freq).sum(dim="time")
    res = over / total
    res.attrs[UNITS_ATTRIBUTE_KEY] = ""  # unit less
    return res


def maximum(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(climate_vars, resample_freq, DataArray.max)


def minimum(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(climate_vars, resample_freq, DataArray.min)


def average(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(climate_vars, resample_freq, DataArray.mean)


def sum(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(climate_vars, resample_freq, DataArray.sum)


def std(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
) -> DataArray:
    return _run_simple_reducer(climate_vars, resample_freq, DataArray.std)


def max_of_rolling_sum(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    rolling_window_width: int,
    *args,  # noqa
    **kwargs,  # noqa
):
    return _run_rolling_reducer(
        climate_vars,
        resample_freq,
        rolling_window_width,
        DataArrayRolling.sum,
        DataArray.max,
    )


def min_of_rolling_sum(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    rolling_window_width: int,
    *args,  # noqa
    **kwargs,  # noqa
):
    return _run_rolling_reducer(
        climate_vars,
        resample_freq,
        rolling_window_width,
        DataArrayRolling.sum,
        DataArray.min,
    )


def min_of_rolling_average(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    rolling_window_width: int,
    *args,  # noqa
    **kwargs,  # noqa
):
    return _run_rolling_reducer(
        climate_vars,
        resample_freq,
        rolling_window_width,
        DataArrayRolling.mean,
        DataArray.min,
    )


def mean_of_difference(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
):
    var_0, var_1 = _check_couple_of_var(climate_vars, "mean_of_difference")
    mean_of_diff = (var_0 - var_1).resample(time=resample_freq).mean()
    mean_of_diff.attrs["units"] = var_0.attrs["units"]
    return mean_of_diff


def difference_of_extremes(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
):
    var_0, var_1 = _check_couple_of_var(climate_vars, "difference_of_extremes")
    max_var_0 = var_0.resample(time=resample_freq).max()
    min_var_1 = var_1.resample(time=resample_freq).min()
    diff_of_extremes = max_var_0 - min_var_1
    diff_of_extremes.attrs["units"] = var_0.attrs["units"]
    return diff_of_extremes


def mean_of_absolute_one_time_step_difference(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    *args,  # noqa
    **kwargs,  # noqa
):
    var_0, var_1 = _check_couple_of_var(
        climate_vars, "mean_of_absolute_one_time_step_difference"
    )
    one_time_step_diff = (var_0 - var_1).diff(dim="time")
    res = abs(one_time_step_diff).resample(time=resample_freq).mean()
    res.attrs["units"] = var_0.attrs["units"]
    return res


def difference_of_means(
    climate_vars: list[ClimateVariable],
    is_single_var: bool,
    group_by_freq: str | None = None,
    resample_freq: str | None = None,
    *args,  # noqa
    **kwargs,  # noqa
):
    var_0, var_1 = _check_couple_of_var(climate_vars, "difference_of_means")
    if is_single_var:
        mean_0 = var_0.groupby(group_by_freq).mean()
        mean_1 = var_1.groupby(group_by_freq).mean()
    else:
        mean_0 = var_0.resample(time=resample_freq).mean()
        mean_1 = var_1.resample(time=resample_freq).mean()
    diff_of_means = mean_0 - mean_1
    diff_of_means.attrs["units"] = var_0.attrs["units"]
    return diff_of_means


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
    var_0 = climate_vars[0].study_da
    var_1 = climate_vars[1].study_da
    var_0 = convert_units_to(var_0, var_1)
    return var_0, var_1


def max_of_rolling_average(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    rolling_window_width: int,
    *args,  # noqa
    **kwargs,  # noqa
):
    return _run_rolling_reducer(
        climate_vars,
        resample_freq,
        rolling_window_width,
        DataArrayRolling.mean,
        DataArray.min,
    )


def _run_rolling_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    rolling_window_width: int,
    accumulator_op: Callable[[DataArrayRolling], DataArray],
    reducer_op: Callable[..., DataArray],
    dim="time",
):
    thresh_operator, study, threshold = _check_single_var(climate_vars)
    if threshold:
        exceedance = _compute_exceedance(
            operator=thresh_operator,
            study=study,
            resample_freq=resample_freq,
            threshold=threshold.value,
            bootstrap=_must_run_bootstrap(study, threshold),
            is_doy_per=threshold.is_doy_per_threshold,
        ).squeeze()
        data = study.where(exceedance)
    else:
        data = study
    data = accumulator_op(data.rolling(time=rolling_window_width)).resample(
        time=resample_freq
    )
    return reducer_op(data, dim=dim)


def _run_simple_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    reducer_op: Callable[..., DataArray],
    dim="time",
):
    thresh_op, study, threshold = _check_single_var(climate_vars)
    if threshold:
        exceedance = _compute_exceedance(
            operator=thresh_op,
            study=study,
            resample_freq=resample_freq,
            threshold=threshold.value,
            bootstrap=_must_run_bootstrap(study, threshold),
            is_doy_per=threshold.is_doy_per_threshold,
        ).squeeze()
        study = study.where(exceedance)
    else:
        study = study
    return reducer_op(study.resample(time=resample_freq), dim=dim)


def _run_exceedances_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    reducer_op: Callable[[DataArray], DataArray],
):
    exceedances = [
        _compute_exceedance(
            operator=climate_var.threshold.operator,
            study=climate_var.study_da,
            threshold=climate_var.threshold.value,
            resample_freq=resample_freq,
            bootstrap=_must_run_bootstrap(climate_var.study_da, climate_var.threshold),
            is_doy_per=climate_var.threshold.is_doy_per_threshold,
        ).squeeze()
        for climate_var in climate_vars
    ]
    # we assume all climate vars have compatible dimensions
    merged_exceedance: DataArray = reduce(np.logical_and, exceedances)  # noqa np->xr
    result = reducer_op(merged_exceedance.resample(time=resample_freq))
    return to_agg_units(result, climate_vars[0].study_da, "count")


@percentile_bootstrap
def _compute_exceedance(
    study: DataArray,
    threshold: DataArray | PercentileDataArray,
    operator: Operator,
    resample_freq: str,  # noqa @percentile_bootstrap
    bootstrap: bool,  # noqa @percentile_bootstrap
    is_doy_per: bool,
) -> DataArray:
    # squeeze the threshold dim if it exists and has length of 1
    if is_doy_per:
        threshold = resample_doy(threshold, study)
    return operator(study, threshold)


class GenericIndicatorRegistry(Registry):
    _item_class = GenericIndicator

    # todo: replace strings by a ref to the LOCAL dictionary keys
    CountOccurrences = GenericIndicator("count_occurrences", count_occurrences)
    MaxConsecutiveOccurrence = GenericIndicator(
        "max_consecutive_occurrence", max_consecutive_occurrence
    )
    SumOfSpellLengths = GenericIndicator("sum_of_spell_lengths", sum_of_spell_lengths)
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
    # DoyPercentile = GenericIndicator(
    #     "doy_percentile",
    #     doy_percentile,
    # )
    # PeriodPercentile = GenericIndicator(
    #     "period_percentile",
    #     period_percentile,
    # )


def _check_single_var(
    climate_vars: list[ClimateVariable],
) -> tuple[Operator, DataArray, Threshold]:
    if len(climate_vars) != 1:
        raise InvalidIcclimArgumentError("Too many variables.")
    return (
        climate_vars[0].threshold.operator,
        climate_vars[0].study_da,
        climate_vars[0].threshold,
    )


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
    freqs = list(map(lambda a: xr.infer_freq(a.study_da.time), climate_vars))
    return all(map(lambda x: x == freqs[0], freqs[1:]))


def _get_inputs_metadata(
    climate_vars: list[ClimateVariable], resample_freq: Frequency
) -> list[dict[str, str]]:
    return list(
        map(
            lambda cf_var: cf_var.build_indicator_metadata(
                resample_freq, _must_run_bootstrap(cf_var.study_da, cf_var.threshold)
            ),
            climate_vars,
        )
    )
