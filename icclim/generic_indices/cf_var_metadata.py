from __future__ import annotations

import dataclasses
from typing import Hashable, TypedDict

from icclim.models.registry import Registry


class IndicatorMetadata(TypedDict):
    identifier: str
    standard_name: str
    long_name: str
    cell_methods: str


@dataclasses.dataclass
class StandardVariable(Hashable):
    short_name: str
    standard_name: str
    long_name: str
    aliases: list[str]
    default_units: str
    # todo: rework units, each constant instance should not have runtime values
    units: str = None  # runtime unit
    # todo add a run_time name ?
    #      So that we could have in the same Dataset tas and tasAdjust for example.
    #      In that case, below declaration should probably be classes instead of
    #      instances (to instantiate two TAS in the example)

    def __hash__(self) -> int:
        return hash(self.short_name + self.standard_name)

    def get_metadata(self):
        return dict(
            standard_name=self.standard_name,
            long_name=self.long_name,
            units=self.units,
            short_name=self.short_name,
        )


class StandardVariableRegistry(Registry):
    _item_class = StandardVariable
    PR = StandardVariable(
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
    TAS = StandardVariable(
        short_name="tg",
        standard_name="average_air_temperature",
        long_name="average air temperature",
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
    TAS_MIN = StandardVariable(
        short_name="tn",
        standard_name="minimum_air_temperature",
        long_name="minimum air temperature",
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
    TAS_MAX = StandardVariable(
        short_name="tx",
        standard_name="maximum_air_temperature",
        long_name="maximum air temperature",
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
    HURS = StandardVariable(
        short_name="hurs",
        standard_name="relative_humidity",
        long_name="relative humidity",
        aliases=["hurs", "hursAdjust", "rh", "RH"],
        default_units="",  # todo
    )
    PSL = StandardVariable(
        short_name="psl",
        standard_name="air_pressure_at_sea_level ",
        long_name="air pressure",
        aliases=["psl", "mslp", "slp", "pp", "MSLP", "SLP", "PP"],
        default_units="",  # todo
    )
    SND = StandardVariable(
        short_name="snd",
        standard_name="surface_snow_thickness",
        long_name="snow thickness",
        aliases=["snd", "sd", "SD"],
        default_units="cm",
    )
    SUND = StandardVariable(
        short_name="sund",
        standard_name="duration_of_sunshine",
        long_name="duration of sunshine",
        aliases=["sund", "ss", "SS"],
        default_units="",  # todo
    )
    WSGS_MAX = StandardVariable(
        short_name="wsgs_max",
        standard_name="wind_speed_of_gust",
        long_name="wind speed of gust",
        aliases=["wsgsmax", "fx", "FX"],
        default_units="",  # todo
    )
    SFC_WIND = StandardVariable(
        short_name="sfcWind",
        standard_name="wind_speed",
        long_name="wind speed",
        aliases=["sfcWind", "sfcwind", "fg", "FG"],
        default_units="",  # todo
    )
    SNW = StandardVariable(
        short_name="snw",
        standard_name="surface_snow_amount",
        long_name="surface snow amount",
        aliases=["snw", "swe", "SW"],
        default_units="",  # todo
    )
    # todo add sunshine, cloudiness

    @staticmethod
    def get_item_aliases(item: StandardVariable) -> list[str]:
        aliases = list(map(str.upper, item.aliases))
        aliases.append(item.standard_name.upper())
        aliases.append(item.long_name.upper())
        return aliases
