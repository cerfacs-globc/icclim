from __future__ import annotations

import dataclasses

from icclim.models.registry import Registry


@dataclasses.dataclass
class NetcdfVersion:
    name: str


class NetcdfVersionRegistry(Registry):
    _item_class = NetcdfVersion

    NETCDF4 = NetcdfVersion("NETCDF4")
    NETCDF4_CLASSIC = NetcdfVersion("NETCDF4_CLASSIC")
    NETCDF3_CLASSIC = NetcdfVersion("NETCDF3_CLASSIC")
    NETCDF3_64BIT = NetcdfVersion("NETCDF3_64BIT")
