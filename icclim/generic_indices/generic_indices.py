from __future__ import annotations

import abc
from functools import reduce
from typing import Callable

import numpy
import numpy as np
from jinja2 import Environment
from xarray import DataArray
from xclim.core import datachecks
from xclim.core.calendar import select_time
from xclim.core.cfchecks import cfcheck_from_name
from xclim.core.options import MISSING_METHODS, MISSING_OPTIONS, OPTIONS

from icclim.generic_indices.generic_index_functions import (
    CountOccurrencesReducer,
    Deficit,
    Excess,
    MaxConsecutiveOccurrence,
    Reducer,
    SumOfSpellLengths,
    _can_run_bootstrap,
)
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.climate_variable import ClimateVariable
from icclim.models.frequency import Frequency
from icclim.models.index_config import IndexConfig

jinja_env = Environment()
# jinja_env = Environment(autoescape=True)
# todo could be a security issue to have autoescape=False (default)
#      but otherwise > and < are replaced by &gt and &lt


class Indicator(Callable):
    identifier: str
    units: str
    standard_name: str
    long_name: str
    description: str
    cell_methods: str
    src_freq: Frequency
    short_name: str

    templated_properties = [
        "identifier",
        "units",
        "standard_name",
        "long_name",
        "description",
        "cell_methods",
        "short_name",
    ]  # todo make it a decorator ?

    @abc.abstractmethod  # todo  is abc.abstractmethod really needed ?
    def __call__(self, *args, **kwargs):
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
                # todo useless ?
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
        /,
        climate_vars: list[ClimateVariable],
        jinja_scope: dict,
        freq: str,
        indexer: dict,
        *args,
        **kwargs,
    ) -> list[ClimateVariable]:
        self.datachecks(climate_vars, freq)
        self.cfcheck(climate_vars)
        self.format(
            jinja_scope=jinja_scope,
            **kwargs,
        )
        if indexer:
            for climate_var in climate_vars:
                climate_var.study_da = select_time(climate_var.study_da, **indexer)
        return climate_vars

    def postprocess(
        self,
        result: DataArray,
        /,
        das: list[DataArray],
        freq: str,
        indexer: dict = None,
        *args,
        **kwargs,
    ):
        if self.missing == "skip":
            return self._handle_missing_values(
                freq=freq, indexer=indexer, in_data=das, out_data=result
            )
        for prop in self.templated_properties:
            result.attrs[prop] = getattr(self, prop)
        result.attrs["history"] = ""
        return result

    def format(self, /, jinja_scope, **kwargs):  # noqa ignore extra kwargs
        for property in self.templated_properties:
            template = jinja_env.from_string(
                getattr(self, property),  # todo instead get the localized version
                globals=jinja_scope,
            )
            setattr(self, property, template.render())

    def _handle_missing_values(
        self, in_data, freq: str, indexer: dict | None, out_data
    ):
        options = self.missing_options or OPTIONS[MISSING_OPTIONS].get(self.missing, {})
        # We flag periods according to the missing method. skip variables without a time
        # coordinate.
        miss = (
            MISSING_METHODS[self.missing].execute(
                da, freq, self.src_freq.pandas_freq, options, indexer
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
    # TODO: Add aliases to recognize common indices (heatwave, SU, tropical_night, etc).
    #       Or simply define catalogs (ecad, xclim, ettcdi)
    #       that use these generic indices ?
    identifier = (
        "{{reducer.standard_name}}"
        "{% for i, input in enumerate(inputs) %}"
        "_{{input.short_name}}"
        "{% if i != len(inputs) - 1 %}"
        "_and"
        "{% endif%}"
        "{% endfor %}"
        "_{{src_freq.units}}"
    )
    # todo: units should probably depend on the reducer (e.g. DTR)
    units = "{{src_freq.units}}"
    # todo: add canonical_form instead making a mess with `standard_name`
    standard_name = (
        "{{reducer.standard_name}}"
        "_{{src_freq.units}}_when"
        "{% for i, input in enumerate(inputs) %}"
        "_{{input.standard_name}}"
        "_{{input.threshold.standard_name}}"
        "{% if i != len(inputs) - 1 %}"
        "_and"
        "{% endif%}"
        "{% endfor %}"
    )
    long_name = (
        "{{reducer.long_name}}"
        " {{src_freq.units}} when"
        "{% for i, input in enumerate(inputs) %}"
        " {{input.short_name}} is"
        " {{input.threshold.long_name}}"
        "{% if i != len(inputs) - 1 %}"
        " and"
        "{% endif%}"
        "{% endfor %}"
        ".{{reducer.additional_metadata}}"
    )
    description = (
        "{{reducer.long_name}}"
        " {{src_freq.units}} of"
        " {{output_freq}} when"
        "{% for i, input in enumerate(inputs) %}"
        " {{input.long_name}} is"
        " {{input.threshold.long_name}}"
        "{% if input.threshold.additional_metadata %}"
        " {{input.threshold.additional_metadata}}"
        "{% endif%}"
        "{% if i != len(inputs) - 1 %}"
        " and"
        "{% endif%}"
        "{% endfor %}"
        ".{{reducer.additional_metadata}}"
    )
    cell_methods = "{{reducer.cell_methods}} {{src_freq.units}}"

    reducer: Reducer

    def __init__(self, reducer: str, min_spell_length: int = 6, **kwds):
        super().__init__(**kwds)
        self.input_variables = None
        self.short_name = self.identifier  # todo no need to duplicate properties
        if reducer == CountOccurrencesReducer.KEY:
            self.reducer = CountOccurrencesReducer()
        elif reducer == MaxConsecutiveOccurrence.KEY:
            self.reducer = MaxConsecutiveOccurrence()
        elif reducer == SumOfSpellLengths.KEY:
            self.reducer = SumOfSpellLengths(min_spell_length)
        elif reducer == Excess.KEY:
            self.reducer = Excess()
        elif reducer == Deficit.KEY:
            self.reducer = Deficit()
        else:
            raise InvalidIcclimArgumentError(f"Unknown reducer: {reducer}.")

    def preprocess(
        self,
        /,
        climate_vars: list[ClimateVariable],
        frequency: Frequency,
        indexer: dict,
        *args,
        **kwargs,
    ) -> list[ClimateVariable]:
        inputs = list(
            map(
                lambda cf_var: cf_var.build_indicator_metadata(self.src_freq),
                climate_vars,
            )
        )
        jinja_scope = {
            # todo [xclim backport] localize these
            "reducer": self.reducer.get_metadata(self.src_freq),
            "inputs": inputs,
            "output_freq": frequency.description,
            "np": numpy,
            "enumerate": enumerate,
            "len": len,
            "src_freq": self.src_freq,
        }
        return super().preprocess(
            climate_vars=climate_vars,
            jinja_scope=jinja_scope,
            freq=frequency.pandas_freq,
            indexer=frequency.indexer,
            *args,
            **kwargs,
        )

    def __call__(self, /, config: IndexConfig, *args, **kwargs) -> DataArray:
        # icclim  wrapper
        # todo:
        #       probably unsafe to rely `config.cf_variables[0]`
        #       in case config.cf_variables[1] (or others) have a != frequency
        self.src_freq = config.climate_variables[0].cf_meta.frequency
        climate_vars = self.preprocess(
            frequency=config.frequency,
            indexer=config.frequency.indexer,
            climate_vars=config.climate_variables,
            *args,
            **kwargs,
        )
        result = self._compare_climate_vars_to_thresholds(
            climate_vars=climate_vars, freq=config.frequency
        )
        return self.postprocess(
            result,
            das=list(map(lambda cv: cv.study_da, climate_vars)),
            freq=config.frequency.pandas_freq,
        )

    def _compare_climate_vars_to_thresholds(
        self, /, climate_vars: list[ClimateVariable], freq: Frequency
    ) -> DataArray:
        intermediary = [
            self.reducer(
                climate_var.study_da,
                climate_var.threshold.value,
                freq.pandas_freq,
                bootstrap=_can_run_bootstrap(
                    climate_var.study_da, climate_var.threshold
                ),
                operator=climate_var.threshold.operator,
                is_doy_per=climate_var.threshold.is_doy_per_threshold,
            )
            for climate_var in climate_vars
        ]
        return reduce(np.logical_and, intermediary)  # noqa
