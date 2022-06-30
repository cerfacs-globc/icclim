from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Callable, Iterable

import numpy as np
import pint
from jinja2 import Environment
from xarray import DataArray
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import resample_doy
from xclim.core.formatting import AttrFormatter, default_formatter
from xclim.core.indicator import ResamplingIndicatorWithIndexing
from xclim.core.units import convert_units_to, declare_units, to_agg_units
from xclim.core.utils import PercentileDataArray
from xclim.indices import tn_days_above
from xclim.indices.generic import threshold_count

from icclim.models.cf_variable import CfVariable
from icclim.models.climate_index import ClimateIndex, ClimateIndexEnum
from icclim.models.constants import MODIFIABLE_THRESHOLD
from icclim.models.index_config import IndexConfig
from icclim.models.index_group import IndexGroup


@dataclasses.dataclass
class Operator:
    # TODO merge with LogicalOperation
    short_name: str
    long_name: str
    standard_name: str
    operand: str
    compute: Callable[[DataArray, DataArray], DataArray]

    def __call__(self, *args, **kwargs):
        return self.compute(*args, **kwargs)


stricly_above = Operator(
    short_name="gt",
    operand=">",
    standard_name="greater",
    long_name="greater",
    compute=lambda x, y: x > y,  # noqa
)
greater_or_equal = Operator(
    short_name="get",
    operand=">=",
    standard_name="greater_or_equal",
    long_name="greater or equal",
    compute=lambda x, y: x > y,  # noqa
)


class CompareToScalar(ClimateIndex):
    xclim_indicator: JinjaTemplatedIndicator

    def __init__(self, operator: Operator):
        super().__init__()
        self.xclim_indicator = JinjaTemplatedIndicator(
            identifier="{{input.short_name}}_{{input.frequency}}_{{operator.standard_name}}_scalar_threshold",
            units="{{input.frequency}}",
            standard_name="number_of_{{input.frequency}}_with_{{input.standard_name}}_{{operator.standard_name}}_threshold",
            long_name="Number of {{input.frequency}} with {{input.short_name} {{operator.operand}} {thresh}}",
            description="{{freq} number of {{input.frequency}} where {{input.long_name}} is {{operator.long_name}} than {thresh}}.",
            cell_methods="time: sum over {{input.frequency}}",
            compute=self._compare_climate_var_to_scalar,
        )
        self.short_name = "compare_climate_var_to_scalar"  # todo: useless ? we could use xclim_indicator.identifier
        self.compute = lambda c: self._wrapped_compare_climate_var_to_scalar(
            config=c, operator=operator
        )
        self.input_variables = None  # generic, no input expected
        self.qualifiers = [MODIFIABLE_THRESHOLD]
        self.group = IndexGroup.GENERIC
        self.output_var_name = None

    def _wrapped_compare_climate_var_to_scalar(
        self, config: IndexConfig, operator: Operator
    ) -> DataArray:
        # icclim  wrapper
        input = config.cf_variables[0]  # todo make sur len == 1 ?
        self.xclim_indicator.jinja_scope.update(input.cf_meta.to_dict())
        self.xclim_indicator.jinja_scope.update({"operator": operator})
        result = self.xclim_indicator(
            input=input.study_da,
            thresh=config.scalar_thresholds,
            operator=operator,
            **config.frequency.build_frequency_kwargs(),
        )
        self.definition = result.attrs["description"]
        return result

    def _compare_climate_var_to_scalar(
        self, input: DataArray, operator: Callable, thresh: str, freq: str = "YS"
    ) -> DataArray:
        # xclim index function
        # signature is not exact as parameters can be injected
        thresh = convert_units_to(thresh, input)
        res = operator(input, thresh).resample(time=freq).sum(dim="time")
        return to_agg_units(res, input, "count")


class GenericIndex(ClimateIndexEnum):
    """
    Generic indices.
        short_name: str
            The index name used in the output.
        compute: Callable
            The function to compute the index. It wraps Xclim functions.
        group: IndexGroup
            The index group category.
        variables: List[List[str]]
            The Cf variables needed to compute the index.
            The variable are individually described by a list of aliases.
        qualifiers: List[str]
            ``optional`` List of configuration to compute the index.
            Used internally to generate modules for C3S.
    """

    def __init__(self, climate_index: ClimateIndex):
        super().__init__(climate_index)
        self.climate_index.source = "icclim"

    VAR_STRICTLY_GREATER_SCALAR = CompareToScalar(operator=stricly_above)
    VAR_GREATER_OR_EQUAL_SCALAR = CompareToScalar(operator=greater_or_equal)
    days_above_doy_percentiles = CompareToScalar()


@dataclasses.dataclass
class CfInputVar:
    # todo add __hash__ ? (and see if dataclass unsafe_hash=True would work)
    #      it would make it possible to do dataset[CfInputVar(blabla)] = da
    short_name: str
    standard_name: str
    long_name: str
    aliases: list[str]

    def to_dict(self):
        return self.__dict__  # safe ?


PR_CF_VAR = CfInputVar(
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
)
TAS_CF_VAR = CfInputVar(
    short_name="tas",
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
)
TAS_MIN_CF_VAR = CfInputVar(
    short_name="tasmin",
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
)
TAS_MAX_CF_VAR = CfInputVar(
    short_name="tasmax",
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
)
HURS_CF_VAR = CfInputVar(
    short_name="hurs",
    standard_name="relative_humidity",
    long_name="relative humidity",
    aliases=["hurs", "hursAdjust", "rh", "RH"],
)
PSL_CF_VAR = CfInputVar(
    short_name="psl",
    standard_name="air_pressure_at_sea_level ",
    long_name="air pressure",
    aliases=["psl", "mslp", "slp", "pp", "MSLP", "SLP", "PP"],
)
SND_CF_VAR = CfInputVar(
    short_name="snd",
    standard_name="surface_snow_thickness",
    long_name="snow thickness",
    aliases=["snd", "sd", "SD"],
)
SUND_CF_VAR = CfInputVar(
    short_name="sund",
    standard_name="duration_of_sunshine",
    long_name="duration of sunshine",
    aliases=["sund", "ss", "SS"],
)
WSGS_MAX_CF_VAR = CfInputVar(
    short_name="wsgs_max",
    standard_name="wind_speed_of_gust",
    long_name="wind speed of gust",
    aliases=["wsgsmax", "fx", "FX"],
)
SFC_WIND_CF_VAR = CfInputVar(
    short_name="sfcWind",
    standard_name="wind_speed",
    long_name="wind speed",
    aliases=["sfcWind", "sfcwind", "fg", "FG"],
)
SNW_CF_VAR = CfInputVar(
    short_name="snw",
    standard_name="surface_snow_amount",
    long_name="surface snow amount",
    aliases=["snw", "swe", "SW"],
)

jinja_env = Environment(autoescape=True)


class JinjaTemplatedIndicator(ResamplingIndicatorWithIndexing):
    # todo temporary here, until xclim has jinja enabled
    jinja_scope: dict = {}

    @classmethod
    def _format(
        cls,
        attrs: dict,
        args: dict = None,
        formatter: AttrFormatter = default_formatter,
    ):
        super()._format(attrs, args, formatter)
        jinja_scope = args
        jinja_scope["np"] = np  # noqa
        for key, val in attrs.items():
            if isinstance(val, str):
                attrs[key] = jinja_env.from_string(val, globals=jinja_scope).render()


# -- COUNT DAYS ABOVE
# su


@percentile_bootstrap
def days_above_doy_percentiles_fun(
    input: DataArray,
    per: PercentileDataArray,
    scalar_thresh: str | None = None,
    freq: str = "YS",
    bootstrap=False,  # noqa (used by @percentile_bootstrap)
):
    thresholds = convert_units_to(per, input)
    if scalar_thresh:
        scalar_thresh = convert_units_to(scalar_thresh, input)
        thresholds = np.maximum(thresholds, scalar_thresh)
    thresh_time_series = resample_doy(thresholds, input)
    out = threshold_count(input, ">", thresh_time_series, freq)
    return to_agg_units(out, input, "count")


# ECAD: tx90p, tn90p, tg90p,
# ETCCDI/WMO: r99p, r95p, r75p
days_above_doy_percentiles = JinjaTemplatedIndicator(
    identifier="{{input.short_name}}_days_above_doy_percentile",
    units="days",
    standard_name="days_with_{{input.standard_name}}_above_doy_percentile",
    long_name="Number of days when {{input.short_name} > {per_thresh}}th percentile",
    description=" {{freq} number of days with {input.long_name}} above the"
    " {{per_thresh}}th percentile(s)"
    "{% if scalar_thresh is not None %}"
    " and above {{scalar_thresh}}."
    "{% endif %}"
    " A {{per_window}} day(s) window, centred on each calendar day in the"
    " {{per_period} period, is used to compute the {per_thresh}}th"
    " percentile(s).",
    cell_methods="time: sum over days",
    compute=days_above_doy_percentiles_fun,
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
    input: CfVariable,
    freq: str = "YS",
):
    out = input.study_da > input.reference_da
    out = out.resample(time=freq).sum(dim="time")
    return to_agg_units(out, input.study_da, "count")


def days_where_studies_are_above_references(inputs: [CfVariable], freq: str = "YS"):
    from functools import reduce

    # noqa -> ::map does not infer the proper type
    out: DataArray = map(lambda x: x.study_da > x.reference_da, inputs)  # noqa
    out = reduce(lambda a, b: np.logical_and(a, b), out)
    out = out.resample(time=freq).sum(dim="time")
    return to_agg_units(out, inputs[0].st, "count")


# r99p, r95p, r75p
days_above_period_percentiles = JinjaTemplatedIndicator(
    identifier="{{input.short_name}}_days_above_percentile",
    standard_name="number_of_days_with_{{input.standard_name}}_above_percentile",
    description="{{freq} number of days when {input.long_name} is above the"
    " {pr_per_thresh}}th percentile of {{pr_per_period}} period."
    "{% if scalar_thresh is not None %}"
    " and above {{scalar_thresh}}."
    "{% endif %}"
    " Only days with at least {{thresh}} are counted.",
    units="days",
    cell_methods="time: sum over days",
    compute=days_above_thresholds,
)

days_above_gridcell_thresholds = JinjaTemplatedIndicator(
    identifier="{{input.short_name}}_days_above_gridcell_thresholds",
    standard_name="number_of_days_with_{{input.standard_name}}_above_gridcell_thresholds",
    description="{{freq} number of days with {input.long_name} above gridcell"
    " thresholds shaped as {{gridcell_thresholds.shape}}"
    "{% if scalar_thresh is not None %}"
    " and above scalar {{scalar_thresh}}."
    "{% endif %}",
    units="days",
    cell_methods="time: sum over days",
    compute=days_above_thresholds,
)

heat_wave_frequency = JinjaTemplatedIndicator(
    identifier="days_where_studies_are_above_references",
    units="days",
    standard_name="days_where_studies_are_above_references",
    long_name="Number of event where"
    "{% for climate_var in inputs %}"
    " {{input.short_name}} > {{thresh_tasmin}}"
    "{% endfor %}"
    "and Tmax > {{thresh_tasmax}} for >= {{window}} days)",
    description="{{freq}} number of heat wave events over a given period. "
    "An event occurs when the minimum and maximum daily "
    "temperature both exceeds specific thresholds : "
    "{% if np.isscalar(thresh_tasmin) and np.isscalar(thresh_tasmax)%}"
    "(Tmin > {{thresh_tasmin}} and Tmax > {{thresh_tasmax}}) "
    "{% else %}"
    "(Tmin > per_gridcell_tmin_thresholds and Tmax > per_gridcell_tmax_thresholds) "
    "{% endif %}"
    "over a minimum number of days ({{window}}).",
    cell_methods="",
    keywords="health,",
    compute=days_where_studies_are_above_references,
)

# new indices (https://github.com/Ouranosinc/xclim/issues/1093)
days_above_thresholds
# cwd, csu
max_consecutive_days_above_scalar
# csdi
days_where_spell_is_above_day_of_year_percentiles
# -- COUNT DAYS BELOW
# fd
days_below_scalar
# tx10p
days_below_day_of_year_percentiles
# ?
days_below_period_percentiles
# new indices
days_below_tensor
# cdd, cfd
max_consecutive_days_below_scalar
# csdi
days_where_spell_is_above_day_of_year_percentiles
# -- SUM
# hd17
sum_scalar_exceedance
# gd4
sum_scalar_subceedance
# -- Average
# tx
mean
# sdii
mean_scalar_exceedance
# -- MIN
# txn
min
# -- MAX
# txx, rx1day
max
# -- COMPOSITE
# WW, CW, WD, CD
logical_and(index1, index2)
# DTR
mean_of_difference
# vDTR
mean_of_absolute_difference
# ETR
max(var1) - min(var2)
#

# TODO:
#    - composite indices (DTR, vDTR, WW, CW...)
#    - rxxpTOT
#    - prcptot
#    - handle units
