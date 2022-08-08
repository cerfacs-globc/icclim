from __future__ import annotations

from functools import reduce
from typing import Callable, TypedDict

import numpy as np
from xarray import DataArray
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.units import to_agg_units
from xclim.indices import run_length

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.climate_variable import ClimateVariable
from icclim.models.constants import UNITS_ATTRIBUTE_KEY
from icclim.models.frequency import Frequency
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
        climate_vars: list[ClimateVariable],
        freq: str,
        bootstrap: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        exceedances = [
            climate_var.threshold(climate_var.study_da).squeeze()
            for climate_var in climate_vars
        ]
        merged_exceedance = (
            reduce(np.logical_and, exceedances)  # noqa (np/xarray compatibility)
            .resample(time=freq)
            .sum(dim="time")
        )
        # we assume all climate vars have the same time dimension here
        return to_agg_units(merged_exceedance, climate_vars[0].study_da, "count")

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
        climate_vars: list[ClimateVariable],
        freq: str,
        bootstrap: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        exceedances = [
            climate_var.threshold(climate_var.study_da) for climate_var in climate_vars
        ]
        merged_exceedance = (
            reduce(np.logical_and, exceedances)  # noqa (np/xarray compatibility)
            .resample(time=freq)
            .map(run_length.longest_run, dim="time")
        )
        # we assume all climate vars have the same time dimension here
        return to_agg_units(merged_exceedance, climate_vars[0].study_da, "count")

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
        climate_vars: list[ClimateVariable],
        freq: str,
        bootstrap: bool,
        min_spell_length: int = 6,
        *args,
        **kwargs,
    ) -> DataArray:
        exceedances = [
            climate_var.threshold(climate_var.study_da) for climate_var in climate_vars
        ]
        merged_exceedance = (
            reduce(np.logical_and, exceedances)  # noqa (np/xarray compatibility)
            .resample(time=freq)
            .map(run_length.windowed_run_count, window=min_spell_length, dim="time")
        )
        return to_agg_units(merged_exceedance, climate_vars[0].study_da, "count")

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
        climate_vars: list[ClimateVariable],
        freq: str,
        bootstrap: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        if len(climate_vars) != 1:
            raise InvalidIcclimArgumentError(
                "Excess can only be computed on a single variable."
            )
        study = climate_vars[0].study_da
        thresholds = climate_vars[0].threshold.value
        res = (study - thresholds).clip(min=0).resample(time=freq).sum(dim="time")
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
        climate_vars: list[ClimateVariable],
        freq: str,
        bootstrap: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        if len(climate_vars) != 1:
            raise InvalidIcclimArgumentError(
                "Deficit can only be computed on a single variable."
            )
        study = climate_vars[0].study_da
        thresholds = climate_vars[0].threshold.value
        res = (thresholds - study).clip(min=0).resample(time=freq).sum(dim="time")
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
        climate_vars: list[ClimateVariable],
        freq: str,
        bootstrap: bool,
        *args,
        **kwargs,
    ) -> DataArray:
        if len(climate_vars) != 1:
            raise InvalidIcclimArgumentError(
                "FractionOfTotal can only be computed on a single variable."
            )
        study = climate_vars[0].study_da
        threshold = climate_vars[0].threshold
        op = threshold.operator
        if threshold.threshold_min_value:
            total = (
                study.where(op(study, threshold.threshold_min_value))
                .resample(time=freq)
                .sum(dim="time")
            )
        else:
            total = study.resample(time=freq).sum(dim="time")
        over = (
            study.where(op(study, threshold.value)).resample(time=freq).sum(dim="time")
        )
        res = over / total
        res.attrs[UNITS_ATTRIBUTE_KEY] = ""  # unit less
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
