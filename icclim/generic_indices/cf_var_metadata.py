from __future__ import annotations

import dataclasses

from icclim.models.frequency import Frequency
from icclim.models.registry import Registry


@dataclasses.dataclass
class CfVarMetadata:
    # todo add __hash__ ? (and see if dataclass unsafe_hash=True would work)
    #      it would make it possible to do
    #      `dataset[TAS_MAX] = da` (where TAS_MAX is a CfVarMetadata)
    short_name: str
    standard_name: str
    long_name: str
    aliases: list[str]
    default_units: str
    frequency: Frequency = None
    units: str = None  # runtime unit # todo pint.Unit ?
    cell_method: str = None  # todo class to build it ?

    def get_metadata(self):
        return self.__dict__  # todo safe ?


class CfVarMetadataRegistry(Registry):
    _item_class = CfVarMetadata
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
        default_units="cm",
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

    # todo add sunshine, cloudiness

    @staticmethod
    def get_item_aliases(item: CfVarMetadata) -> list[str]:
        aliases = list(map(str.upper, item.aliases))
        aliases.append(item.standard_name.upper())
        aliases.append(item.long_name.upper())
        return aliases
