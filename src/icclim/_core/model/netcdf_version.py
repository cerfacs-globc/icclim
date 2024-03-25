"""Module containing the NetCDF version model and its registry."""

from __future__ import annotations

import dataclasses
from typing import Literal

from icclim._core.model.registry import Registry


@dataclasses.dataclass
class NetcdfVersion:
    """
    Class representing a NetCDF version.

    Attributes
    ----------
    name : {'NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_64BIT', 'NETCDF3_CLASSIC'}
        The name of the NetCDF version.
    """

    name: Literal["NETCDF4", "NETCDF4_CLASSIC", "NETCDF3_64BIT", "NETCDF3_CLASSIC"]


class NetcdfVersionRegistry(Registry[NetcdfVersion]):
    """Registry of NetCDF versions."""

    _item_class = NetcdfVersion

    NETCDF4 = NetcdfVersion("NETCDF4")
    NETCDF4_CLASSIC = NetcdfVersion("NETCDF4_CLASSIC")
    NETCDF3_CLASSIC = NetcdfVersion("NETCDF3_CLASSIC")
    NETCDF3_64BIT = NetcdfVersion("NETCDF3_64BIT")
