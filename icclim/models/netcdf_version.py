from enum import Enum


class NetcdfVersion(Enum):
    NETCDF4 = "NETCDF4"
    NETCDF4_CLASSIC = "NETCDF4_CLASSIC"
    NETCDF3_CLASSIC = "NETCDF3_CLASSIC"
    NETCDF3_64BIT = "NETCDF3_64BIT"


def get_netcdf_version(s: str):
    for version in NetcdfVersion:
        if version.name.upper() == s.upper():
            return version
    raise Exception(f"Unknown netcdf version {s}")
