from __future__ import annotations
from xarray import DataArray

from generic_indices.cf_var_metadata import CfVarMetadata
from icclim_exceptions import InvalidIcclimArgumentError
from models.registry import Registry

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
    standard_name="average_air_temperature",
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
    standard_name="minimum_air_temperature",
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
    standard_name="maximum_air_temperature",
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


class CfVarMetadataRegistry(Registry):
    def __init__(self):
        super().__init__([PR, TAS, TAS_MIN, TAS_MAX, HURS, PSL, SND, SUND, WSGS_MAX, SFC_WIND, SNW])

    def lookup(self, query: DataArray) -> CfVarMetadata:
        query_up = str(query.name).upper()
        # Todo: we could also look for attrs["units"], attrs[""] and cell-method.
        for cf_input in self.data:
            if (
                    query_up in map(str.upper, cf_input.aliases)
                    or query_up == cf_input.standard_name.upper()
                    or query_up == cf_input.long_name.upper()
            ):
                return cf_input
        # TODO: do not raise an error to allow computation on ds.pouetpouet
        raise InvalidIcclimArgumentError(
            f"cf variable was not recognized for DataArray: {query.name}."
        )
