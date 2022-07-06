from __future__ import annotations

import abc
from enum import Enum
from functools import reduce

import numpy
import numpy as np
from generic_indices.cf_var_metadata import CfVarMetadata
from icclim_exceptions import InvalidIcclimArgumentError
from jinja2 import Environment
from models.logical_operation import Operator
from xarray import DataArray
from xclim.core import datachecks
from xclim.core.calendar import select_time
from xclim.core.cfchecks import cfcheck_from_name
from xclim.core.options import MISSING_METHODS, MISSING_OPTIONS, OPTIONS
from xclim.core.units import convert_units_to, to_agg_units

from icclim.models.climate_index import ClimateIndex
from icclim.models.climate_variable import ClimateVariable
from icclim.models.frequency import Frequency
from icclim.models.index_config import IndexConfig
from icclim.models.user_index_config import LogicalOperation

# jinja_env = Environment(autoescape=True)
# todo could be a security issue to have autoescape=False (default)
#      but otherwise > and < are replaced by &gt and &lt
jinja_env = Environment()


class Indicator:
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
    ]  # todo make it a decorator ?

    def compute(self, *args, **kwargs):
        raise NotImplementedError("")

    def __call__(self, *args, **kwargs):
        # TODO make it abstract as well ?
        #      it would give more flexibility on how and when preprocess
        #      and postprocess are called
        #      It may also fix the issue of useless `**kwargs` parameter.
        self.preprocess(*args, **kwargs)
        result = self.compute(*args, **kwargs)
        return self.postprocess(result, *args, **kwargs)

    @abc.abstractmethod
    def preprocess(self, *args, **kwargs) -> None:
        raise NotImplementedError("")

    @abc.abstractmethod
    def postprocess(self, *args, **kwargs) -> DataArray:
        raise NotImplementedError("")


class ResamplingIndicator(Indicator):
    missing: str = "from_context"
    missing_options = None

    def __init__(self, **kwds):
        if self.missing == "from_context" and self.missing_options is not None:
            raise ValueError(
                "Cannot set `missing_options` with `missing` method being from context."
            )
        if self.missing_options:
            MISSING_METHODS[self.missing].validate(**self.missing_options)
        super().__init__()

    def datachecks(self, das: list[DataArray]):
        if self.src_freq is None:
            return
        for da in das:
            if "time" in da.coords and da.time.ndim == 1 and len(da.time) > 3:
                datachecks.check_freq(da, self.src_freq.pandas_freq, strict=True)

    def cfcheck(self, das: list[DataArray]):
        """Compare metadata attributes to CF-Convention standards.

        Default cfchecks use the specifications in `xclim.core.utils.VARIABLES`,
        assuming the indicator's inputs are using the CMIP6/xclim variable names
        correctly.
        Variables absent from these default specs are silently ignored.

        When subclassing this method, use functions decorated using
        `xclim.core.options.cfcheck`.
        """
        for da in das:
            try:
                cfcheck_from_name(str(da.name), da)
            except KeyError:
                # Silently ignore unknown variables.
                pass

    def preprocess(
        self,
        /,
        das: list[DataArray],
        jinja_scope: dict,
        freq: str = "YS",
        indexer: dict = None,
        *args,
        **kwargs,
    ):
        self.datachecks(das)
        self.cfcheck(das)
        self.format(
            jinja_scope=jinja_scope,
            **kwargs,
        )
        if indexer:
            das = [select_time(da, **indexer) for da in das]
            kwargs.update({"das": das})

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
                getattr(self, property), globals=jinja_scope
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


class CountEventComparedToThreshold(ResamplingIndicator):
    # TODO: Add aliases to recognize common indices (heatwave, SU, tropical_night, etc).
    #       or just define catalogs (ecad, xclim, ettcdi) ?
    identifier = (
        "{{src_freq_units}}_when"
        "{% for i, input in enumerate(inputs) %}"
        "_{{input.short_name}}"
        "_{{operator.standard_name}}"
        "_than_{{input.threshold.standard_name}}"
        "{% if i != len(inputs) - 1 %}"
        "_and"  # todo make it configurable logical operator ? and | or | xor ?
        "{% endif%}"
        "{% endfor %}"
    )
    #       for example heat_wave when it's tmax > 20 and tmin > 15 (or whatever)
    units = "{{src_freq_units}}"
    standard_name = (
        "number_of_{{src_freq_units}}_when"
        "{% for i, input in enumerate(inputs) %}"
        "_{{input.standard_name}}"
        "_{{operator.standard_name}}"
        "_{{input.threshold.standard_name}}"
        "{% if i != len(inputs) - 1 %}"
        "_and"  # todo make it configurable logical operator ? and | or | xor ?
        "{% endif%}"
        "{% endfor %}"
    )
    long_name = (
        "Number of {{src_freq_units}} when"
        "{% for i, input in enumerate(inputs) %}"
        " {{input.short_name}}"
        " {{operator.operand}}"
        " {{input.threshold.value}}"
        "{% if i != len(inputs) - 1 %}"
        " and"  # todo make it configurable logical operator ? and | or | xor ?
        "{% endif%}"
        "{% endfor %}"
        "."
    )
    description = (
        "Number of {{src_freq_units}} when"
        " {{output_freq}}"
        "{% for i, input in enumerate(inputs) %}"
        " {{input.long_name}} is"
        " {{operator.long_name}} than"
        " {{input.threshold.value}}"
        "{% if i != len(inputs) - 1 %}"
        " and"  # todo make it configurable logical operator ? and | or | xor ?
        "{% endif%}"
        "{% endfor %}"
        "."
    )
    cell_methods = "time: sum over {{src_freq_units}}"

    operator: LogicalOperation

    def __init__(self, short_name: str, operator: LogicalOperation, **kwds):
        super().__init__(**kwds)
        self.short_name = short_name
        self.compute = self._compare_climate_vars_to_thresholds
        self.operator = operator
        # self.input_variables = None  # generic, no input expected
        # self.qualifiers = [MODIFIABLE_THRESHOLD]
        # self.group = IndexGroup.GENERIC
        # self.output_var_name = None

    def preprocess(self, /, config: IndexConfig, *args, **kwargs):
        # todo:
        #       probably unsafe to do `config.cf_variables[0]`
        #       in case config.cf_variables[1] has a != frequency
        self.src_freq = config.cf_variables[0].cf_meta.frequency
        inputs = list(
            map(
                lambda cf_var: {"threshold": cf_var.threshold.to_dict()}
                | cf_var.cf_meta.to_dict(),
                config.cf_variables,
            )
        )
        jinja_scope = {
            "inputs": inputs,
            "operator": self.operator,
            "output_freq": config.frequency.description,
            "np": numpy,
            "enumerate": enumerate,
            "len": len,
            "src_freq_units": self.src_freq.units,
        }
        super().preprocess(jinja_scope=jinja_scope, *args, **kwargs)

    def __call__(self, /, config: IndexConfig, *args, **kwargs) -> DataArray:
        # icclim  wrapper
        das = list(map(lambda i: i.study_da, config.cf_variables))
        thresholds = list(map(lambda i: i.threshold.value, config.cf_variables))
        result = super().__call__(
            config=config,
            das=das,
            freq=config.frequency.pandas_freq,
            indexer=config.frequency.indexer,
            operator=self.operator,
            thresholds=thresholds,
        )
        return result

    def _compare_climate_vars_to_thresholds(
        self,
        /,
        das: list[DataArray],
        operator: Operator,
        thresholds: DataArray,
        freq: str = "YS",
        **kwargs,  # noqa ignore extra kwargs used by preprocess or postprocess
    ) -> DataArray:
        intermediary = [
            self._compare_climate_var_to_thresh(da, operator, thresholds[i], freq)
            for i, da in enumerate(das)
        ]
        return reduce(np.logical_and, intermediary)  # noqa

    def _compare_climate_var_to_thresh(
        self,
        data: DataArray,
        operator: Operator,
        thresholds: DataArray,
        freq: str = "YS",
    ) -> DataArray:
        # xclim index function
        # signature is not exact as parameters can be injected
        thresholds = convert_units_to(thresholds, data)
        res = operator(data, thresholds).resample(time=freq).sum(dim="time")
        return to_agg_units(res, data, "count")


# class CountEventComparedDoyPercentile(ClimateIndex):
#
#     def __init__(self, operator: LogicalOperation):
#         super().__init__()
#         self.xclim_indicator = JinjaTemplatedIndicator(
#             identifier="{{input.short_name}}_{{input.frequency}}_{{operator.standard_name}}_day_of_year_percentile",
#             units="{{input.frequency}}",
#             standard_name="{{input.frequency}}_when_{{input.standard_name}}_{{operator.standard_name}}_day_of_year_percentile",
#             long_name="Number of {{input.frequency}} when {{input.short_name}} {{operator.operand}} {{per_thresh}}th percentile(s)",
#             description="{{freq}} number of {{input.frequency}} when {{input.long_name}} "
#                         "{{operator.long_name}} the {{per_thresh}}th percentile(s)"
#                         "{% if scalar_thresh is not None %}"
#                         " and above {{scalar_thresh}}"
#                         "{% endif %}"
#                         ". A {{per_window}} {{input.frequency}} centred window "
#                         "{{per_period}} period, is used to compute the {{per_thresh}}}th "
#                         "percentile(s).",
#             cell_methods="time: sum over days",
#             compute=self.days_above_doy_percentiles_fun,
#         )
#         self.compute = lambda c: self._wrapped_compare_climate_var_to_threshold(
#             config=c, operator=operator
#         )
#         self.input_variables = None  # generic, no input expected
#         self.qualifiers = [MODIFIABLE_THRESHOLD]
#         self.group = IndexGroup.GENERIC
#         self.output_var_name = None
#
#     def _wrapped_compare_climate_var_to_threshold(
#             self, config: IndexConfig, operator: LogicalOperation
#     ) -> DataArray:
#         # icclim  wrapper
#         input = config.cf_variables[0]  # todo make sur len == 1 ?
#         jinja_scope = {
#             "input":     input.cf_meta.to_dict(),
#             "threshold": config.thresholds.to_dict(),
#             "operator":  operator,
#             "freq":      config.frequency.description,
#             "np":        numpy,
#         }
#         result = self.xclim_indicator(
#             input=input.study_da,
#             threshold=input.threshold,
#             operator=operator,
#             **config.frequency.build_frequency_kwargs(),
#             jinja_scope=jinja_scope
#             # todo not sure it will work, it is supposed to act as injected parameters
#         )
#         self.definition = result.attrs["description"]
#         self.short_name = result.attrs["identifier"]
#         return result
#
#     @percentile_bootstrap
#     def days_above_doy_percentiles_fun(
#             input: DataArray,
#             per: PercentileDataArray,
#             scalar_thresh: str | None = None,
#             freq: str = "YS",
#             bootstrap=False,  # noqa (used by @percentile_bootstrap)
#     ):
#         thresholds = convert_units_to(per, input)
#         if scalar_thresh:
#             scalar_thresh = convert_units_to(scalar_thresh, input)
#             thresholds = np.maximum(thresholds, scalar_thresh)
#         thresh_time_series = resample_doy(thresholds, input)
#         out = threshold_count(input, ">", thresh_time_series, freq)
#         return to_agg_units(out, input, "count")


class IndexCatalog:
    _catalog: dict[str, ClimateIndex]

    def __init__(self, catalog=None, **kwargs):
        if catalog:
            self._catalog = catalog
        else:
            self._catalog = kwargs

    def lookup(self, query: str) -> ClimateIndex | None:
        for k, v in self._catalog.items():
            if query == k or query == v.short_name:
                return v
        return None


GenericIndexCatalog = IndexCatalog(
    greater=CountEventComparedToThreshold(
        short_name="greater", operator=LogicalOperation.GREATER
    ),
    greater_or_equal=CountEventComparedToThreshold(
        short_name="greater_or_equal", operator=LogicalOperation.GREATER_OR_EQUAL
    ),
    lower=CountEventComparedToThreshold(
        short_name="lower", operator=LogicalOperation.LOWER
    ),
    lower_or_equal=CountEventComparedToThreshold(
        short_name="lower_or_equal", operator=LogicalOperation.LOWER_OR_EQUAL
    ),
    equal=CountEventComparedToThreshold(
        short_name="equal", operator=LogicalOperation.EQUAL
    ),
)


class CfInputEnum(Enum):
    # todo
    #      - Turn it into a module (a list + singletons)
    #      - Use xclim variable.yml to complete it
    #      - Upstream it to cf-xarray
    def __init__(self, cf_input: CfVarMetadata):
        self._cf_input = cf_input

    PR = CfVarMetadata(
        short_name="pr",
        standard_name="precipitation_flux",
        long_name="precipitation",
        aliases=[
            "pr",
            "prAdjust",
            "prec",
            "rr",
            "precip",
            "PREC",
            "Prec",
            "RR",
            "PRECIP",
            "Precip",
        ],
        default_units="mm",
    )
    TAS = CfVarMetadata(
        short_name="tg",
        standard_name="air_temperature",
        long_name="average temperature",
        aliases=[
            "tas",
            "tavg",
            "ta",
            "tasAdjust",
            "tmean",
            "tm",
            "tg",
            "meant",
            "TMEAN",
            "Tmean",
            "TM",
            "TG",
            "MEANT",
            "meanT",
            "tasmidpoint",
        ],
        default_units="degC",
    )
    TAS_MIN = CfVarMetadata(
        short_name="tn",
        standard_name="air_temperature",
        long_name="minimum temperature",
        aliases=[
            "tasmin",
            "tasminAdjust",
            "tmin",
            "tn",
            "mint",
            "TMIN",
            "Tmin",
            "TN",
            "MINT",
            "minT",
        ],
        default_units="degC",
    )
    TAS_MAX = CfVarMetadata(
        short_name="tx",
        standard_name="air_temperature",
        long_name="maximum temperature",
        aliases=[
            "tasmax",
            "tasmaxAdjust",
            "tmax",
            "tx",
            "maxt",
            "TMAX",
            "Tmax",
            "TX",
            "MAXT",
            "maxT",
        ],
        default_units="degC",
    )
    HURS = CfVarMetadata(
        short_name="hurs",
        standard_name="relative_humidity",
        long_name="relative humidity",
        aliases=["hurs", "hursAdjust", "rh", "RH"],
        default_units="",  # todo
    )
    PSL = CfVarMetadata(
        short_name="psl",
        standard_name="air_pressure_at_sea_level ",
        long_name="air pressure",
        aliases=["psl", "mslp", "slp", "pp", "MSLP", "SLP", "PP"],
        default_units="",  # todo
    )
    SND = CfVarMetadata(
        short_name="snd",
        standard_name="surface_snow_thickness",
        long_name="snow thickness",
        aliases=["snd", "sd", "SD"],
        default_units="",  # todo
    )
    SUND = CfVarMetadata(
        short_name="sund",
        standard_name="duration_of_sunshine",
        long_name="duration of sunshine",
        aliases=["sund", "ss", "SS"],
        default_units="",  # todo
    )
    WSGS_MAX = CfVarMetadata(
        short_name="wsgs_max",
        standard_name="wind_speed_of_gust",
        long_name="wind speed of gust",
        aliases=["wsgsmax", "fx", "FX"],
        default_units="",  # todo
    )
    SFC_WIND = CfVarMetadata(
        short_name="sfcWind",
        standard_name="wind_speed",
        long_name="wind speed",
        aliases=["sfcWind", "sfcwind", "fg", "FG"],
        default_units="",  # todo
    )
    SNW = CfVarMetadata(
        short_name="snw",
        standard_name="surface_snow_amount",
        long_name="surface snow amount",
        aliases=["snw", "swe", "SW"],
        default_units="",  # todo
    )

    @property
    def short_name(self):
        return self._cf_input.short_name

    @property
    def standard_name(self):
        return self._cf_input.standard_name

    @property
    def long_name(self):
        return self._cf_input.long_name

    @property
    def aliases(self):
        return self._cf_input.aliases

    @staticmethod
    def lookup(query: DataArray) -> CfInputEnum:
        query_up = str(query.name).upper()
        # Todo: we could also look for attrs["units"], attrs[""] and cell-method.
        for cf_input in CfInputEnum:
            if (
                query_up in map(str.upper, cf_input.aliases)
                or query_up == cf_input.standard_name.upper()
                or query_up == cf_input.long_name.upper()
            ):
                return cf_input
        raise InvalidIcclimArgumentError(
            f"Unknown logical operator {query}."
            f"Use one of {[op.aliases for op in CfInputEnum]}."
        )


def days_above_thresholds(
    input: DataArray,
    gridcell_thresholds: DataArray,
    scalar_thresh: str | None = None,
    freq: str = "YS",
):
    gridcell_thresholds = convert_units_to(gridcell_thresholds, input)
    scalar_thresh = convert_units_to(scalar_thresh, input)
    thresholds = np.maximum(gridcell_thresholds, scalar_thresh)
    out = input > thresholds
    out = out.resample(time=freq).sum(dim="time")
    return to_agg_units(out, input, "count")


def days_where_study_is_above_reference(
    input: ClimateVariable,
    freq: str = "YS",
):
    out = input.study_da > input.reference_da
    out = out.resample(time=freq).sum(dim="time")
    return to_agg_units(out, input.study_da, "count")


def days_where_studies_are_above_references(
    inputs: [ClimateVariable], freq: str = "YS"
):
    from functools import reduce

    # noqa -> ::map does not infer the proper type
    out: DataArray = map(lambda x: x.study_da > x.reference_da, inputs)  # noqa
    out = reduce(lambda a, b: np.logical_and(a, b), out)
    out = out.resample(time=freq).sum(dim="time")
    return to_agg_units(out, inputs[0].st, "count")


# r99p, r95p, r75p
# days_above_period_percentiles = JinjaTemplatedIndicator(
#     identifier="{{input.short_name}}_days_above_percentile",
#     standard_name="number_of_days_with_{{input.standard_name}}_above_percentile",
#     description="{{freq} number of days when {input.long_name} is above the"
#                 " {pr_per_thresh}}th percentile of {{pr_per_period}} period."
#                 "{% if scalar_thresh is not None %}"
#                 " and above {{scalar_thresh}}."
#                 "{% endif %}"
#                 " Only days with at least {{threshold}} are counted.",
#     units="days",
#     cell_methods="time: sum over days",
#     compute=days_above_thresholds,
# )
#
# days_above_gridcell_thresholds = JinjaTemplatedIndicator(
#     identifier="{{input.short_name}}_days_above_gridcell_thresholds",
#     standard_name="number_of_days_with_{{input.standard_name}}_above_gridcell_thresholds",
#     description="{{freq} number of days with {input.long_name} above gridcell"
#     " thresholds shaped as {{gridcell_thresholds.shape}}"
#     "{% if scalar_thresh is not None %}"
#     " and above scalar {{scalar_thresh}}."
#     "{% endif %}",
#     units="days",
#     cell_methods="time: sum over days",
#     compute=days_above_thresholds,
# )
#
# heat_wave_frequency = JinjaTemplatedIndicator(
#     identifier="days_where_studies_are_above_references",
#     units="days",
#     standard_name="days_where_studies_are_above_references",
#     long_name="Number of event where"
#               "{% for climate_var in inputs %}"
#               " {{input.short_name}} > {{thresh_tasmin}}"
#               "{% endfor %}"
#               "and Tmax > {{thresh_tasmax}} for >= {{window}} days)",
#     description="{{freq}} number of heat wave events over a given period. "
#                 "An event occurs when the minimum and maximum daily "
#                 "temperature both exceeds specific thresholds : "
#                 "{% if np.isscalar(thresh_tasmin) and np.isscalar(thresh_tasmax)%}"
#                 "(Tmin > {{thresh_tasmin}} and Tmax > {{thresh_tasmax}}) "
#                 "{% else %}"
#                 "(Tmin > per_gridcell_tmin_thresholds and Tmax > per_gridcell_tmax_thresholds) "
#                 "{% endif %}"
#                 "over a minimum number of days ({{window}}).",
#     cell_methods="",
#     keywords="health,",
#     compute=days_where_studies_are_above_references,
# )

# # new indices (https://github.com/Ouranosinc/xclim/issues/1093)
# days_above_thresholds (scalar, per-gridcell scalars, percentile_doy, percentile_on_period, )
# # cwd, csu
# max_consecutive_days_above_scalar
# # csdi
# days_where_spell_is_above_day_of_year_percentiles
# # -- COUNT DAYS BELOW
# # fd
# days_below_scalar
# # tx10p
# days_below_day_of_year_percentiles
# # ?
# days_below_period_percentiles
# # new indices
# days_below_tensor
# # cdd, cfd
# max_consecutive_days_below_scalar
# # csdi
# days_where_spell_is_above_day_of_year_percentiles
# # -- SUM
# # hd17
# sum_scalar_exceedance
# # gd4
# sum_scalar_subceedance
# # -- Average
# # tx
# mean
# # sdii
# mean_scalar_exceedance
# # -- MIN
# # txn
# min
# # -- MAX
# # txx, rx1day
# max
# # -- COMPOSITE
# # WW, CW, WD, CD
# logical_and(index1, index2)
# # DTR
# mean_of_difference
# # vDTR
# mean_of_absolute_difference
# # ETR
# max(var1) - min(var2)
# #
#
# # TODO:
# #    - composite indices (DTR, vDTR, WW, CW...)
# #    - rxxpTOT
# #    - prcptot
# #    - handle units
