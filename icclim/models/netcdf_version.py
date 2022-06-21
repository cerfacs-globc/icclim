from __future__ import annotations

from enum import Enum

from icclim.icclim_exceptions import InvalidIcclimArgumentError


class NetcdfVersion(Enum):
    NETCDF4 = "NETCDF4"
    NETCDF4_CLASSIC = "NETCDF4_CLASSIC"
    NETCDF3_CLASSIC = "NETCDF3_CLASSIC"
    NETCDF3_64BIT = "NETCDF3_64BIT"

    @staticmethod
    def lookup(query: str | NetcdfVersion):
        if isinstance(query, NetcdfVersion):
            return query
        for version in NetcdfVersion:
            if version.name.upper() == query.upper():
                return version
        raise InvalidIcclimArgumentError(f"Unknown netcdf version {query}")
