from __future__ import annotations

import dataclasses
from typing import Hashable

from icclim.models.constants import PART_OF_A_WHOLE_UNIT
from icclim.models.registry import Registry


@dataclasses.dataclass
class StandardVariable(Hashable):
    short_name: str
    standard_name: str
    long_name: str
    aliases: list[str]
    default_units: str

    def __hash__(self) -> int:
        return hash(self.short_name + self.standard_name)

    def get_metadata(self):
        return dict(
            standard_name=self.standard_name,
            long_name=self.long_name,
            short_name=self.short_name,
        )


class StandardVariableRegistry(Registry[StandardVariable]):
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
            "RR",
            "PRECIP",
            "Precip",
        ],
        default_units="mm day-1",
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
        default_units="degree_Celsius",
    )
    TAS_MIN = StandardVariable(
        short_name="tn",
        standard_name="minimum_air_temperature",  # not CF nor CMIP (air_temperature)
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
        default_units="degree_Celsius",
    )
    TAS_MAX = StandardVariable(
        short_name="tx",
        standard_name="maximum_air_temperature",  # not CF nor CMIP (air_temperature)
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
        default_units="degree_Celsius",
    )
    HURS = StandardVariable(
        short_name="hurs",
        standard_name="relative_humidity",
        long_name="relative humidity",
        aliases=["hurs", "hursAdjust", "rh", "RH"],
        default_units="1",  # %
    )
    PS = StandardVariable(
        short_name="ps",
        standard_name="surface_air_pressure ",
        long_name="Surface Air Pressure",
        aliases=["ps"],
        default_units="Pa",
    )
    PSL = StandardVariable(
        short_name="psl",
        standard_name="air_pressure_at_sea_level ",
        long_name="Sea Level Pressure",
        aliases=["psl", "mslp", "slp", "pp", "MSLP", "SLP", "PP"],
        default_units="Pa",
    )
    SND = StandardVariable(
        short_name="snd",
        standard_name="surface_snow_thickness",
        long_name="Snow Depth",
        aliases=["snd", "sd", "SD"],
        default_units="m",
    )
    SUND = StandardVariable(
        short_name="sund",
        standard_name="duration_of_sunshine",
        long_name="duration of sunshine",
        aliases=["sund", "ss", "SS"],
        default_units="s",
    )
    WSGS_MAX = StandardVariable(
        short_name="wsgs_max",
        standard_name="wind_speed_of_gust",
        long_name="wind speed of gust",
        aliases=["wsgsmax", "wsgs_max", "fx", "FX"],
        default_units="m s-1",
    )
    SFC_WIND = StandardVariable(
        short_name="sfcWind",
        standard_name="wind_speed",
        long_name="Near-Surface Wind Speed",
        aliases=["sfcWind", "sfcwind", "sfc_wind", "fg", "FG"],
        default_units="m s-1",
    )
    SNW = StandardVariable(
        short_name="snw",
        standard_name="surface_snow_amount",
        long_name="surface snow amount",
        aliases=["snw", "swe", "SW"],
        default_units="kg m-2",
    )
    EVSPSBL = StandardVariable(
        short_name="evspsbl",
        standard_name="water_evapotranspiration_flux",
        long_name="Evaporation Including Sublimation and Transpiration",
        aliases=["evspsbl", "water_evaporation_flux"],
        default_units="kg m-2 s-1",
    )
    HUSS = StandardVariable(
        short_name="huss",
        standard_name="specific_humidity",
        long_name="Near-Surface Specific Humidity",
        aliases=["huss"],
        default_units=PART_OF_A_WHOLE_UNIT,
    )
    UAS = StandardVariable(
        short_name="uas",
        standard_name="eastward_wind",
        long_name="Eastward Near-Surface Wind",
        aliases=["uas"],
        default_units="m s-1",
    )
    VAS = StandardVariable(
        short_name="vas",
        standard_name="northward_wind",
        long_name="Northward Near-Surface Wind",
        aliases=["vas"],
        default_units="m s-1",
    )
    CLT = StandardVariable(
        short_name="clt",
        standard_name="cloud_area_fraction",
        long_name="Total Cloud Cover Percentage",
        aliases=["clt"],
        default_units="m s-1",
    )
    RSDS = StandardVariable(
        short_name="rsds",
        standard_name="surface_downwelling_shortwave_flux_in_air",
        long_name="Surface Downwelling Shortwave Radiation",
        aliases=["rsds", "surface_downwelling_shortwave_flux"],
        default_units="W m-2",
    )
    RLDS = StandardVariable(
        short_name="rlds",
        standard_name="surface_downwelling_longwave_flux_in_air",
        long_name="Surface Downwelling Longwave Radiation",
        aliases=["rlds", "surface_downwelling_longwave_flux"],
        default_units="W m-2",
    )
    RSUS = StandardVariable(
        short_name="rsds",
        standard_name="surface_upwelling_shortwave_flux_in_air",
        long_name="Surface Upwelling Shortwave Radiation",
        aliases=["rsus", "surface_upwelling_shortwave_flux"],
        default_units="W m-2",
    )
    RLUS = StandardVariable(
        short_name="rlds",
        standard_name="surface_upwelling_longwave_flux_in_air",
        long_name="Surface Upwelling Longwave Radiation",
        aliases=["rlus", "surface_upwelling_longwave_flux"],
        default_units="W m-2",
    )
    OROG = StandardVariable(
        short_name="orog",
        standard_name="surface_altitude",
        long_name="Surface Altitude",
        aliases=["orog"],
        default_units="m",
    )
    SFTLF = StandardVariable(
        short_name="sftlf",
        standard_name="land_area_fraction",
        long_name="Percentage of the Grid Cell Occupied by Land",
        aliases=["sftlf"],
        default_units="%",
    )
    WIND_TO_DIRECTION = StandardVariable(
        short_name="DD",
        standard_name="wind_to_direction",
        long_name="Daily mean wind direction",
        aliases=["dd"],
        default_units="degree",
    )
    # X = StandardVariable(
    #     short_name="x",
    #     standard_name="y",
    #     long_name="z",
    #     aliases=["x"],
    #     default_units="w",
    # )
    # todo add tier1 and tier2 aliases from cmip6/cordex https://docs.google.com/spreadsheets/d/1qUauozwXkq7r1g-L4ALMIkCNINIhhCPx/edit?rtpof=true&sd=true#gid=1672965248 # noqa

    @staticmethod
    def get_item_aliases(item: StandardVariable) -> list[str]:
        aliases = list(map(str.upper, item.aliases))
        aliases.append(item.standard_name.upper())
        aliases.append(item.long_name.upper())
        return aliases
