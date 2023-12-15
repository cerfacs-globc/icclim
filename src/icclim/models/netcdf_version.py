from __future__ import annotations

import dataclasses
from typing import Literal

from icclim.models.registry import Registry


@dataclasses.dataclass
class NetcdfVersion:
    name: Literal["NETCDF4", "NETCDF4_CLASSIC", "NETCDF3_64BIT", "NETCDF3_CLASSIC"]


class NetcdfVersionRegistry(Registry[NetcdfVersion]):
    _item_class = NetcdfVersion

    NETCDF4 = NetcdfVersion("NETCDF4")
    NETCDF4_CLASSIC = NetcdfVersion("NETCDF4_CLASSIC")
    NETCDF3_CLASSIC = NetcdfVersion("NETCDF3_CLASSIC")
    NETCDF3_64BIT = NetcdfVersion("NETCDF3_64BIT")
