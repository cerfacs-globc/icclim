"""
This module has been auto-generated.
To modify these, edit the extractor tool in `tools/extract-icclim-funs.py`.
This module exposes each climate index as individual functions for convenience.
"""
from __future__ import annotations

import datetime

from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

import icclim
from icclim.icclim_logger import Verbosity
from icclim.models.frequency import Frequency, SliceMode
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.user_index_dict import UserIndexDict

__all__ = [
    "tg",
    "tn",
    "tx",
    "dtr",
    "etr",
    "vdtr",
    "su",
    "tr",
    "wsdi",
    "tg90p",
    "tn90p",
    "tx90p",
    "txx",
    "tnx",
    "csu",
    "gd4",
    "fd",
    "cfd",
    "hd17",
    "id",
    "tg10p",
    "tn10p",
    "tx10p",
    "txn",
    "tnn",
    "csdi",
    "cdd",
    "prcptot",
    "rr1",
    "sdii",
    "cwd",
    "r10mm",
    "r20mm",
    "rx1day",
    "rx5day",
    "r75p",
    "r75ptot",
    "r95p",
    "r95ptot",
    "r99p",
    "r99ptot",
    "sd",
    "sd1",
    "sd5cm",
    "sd50cm",
    "cd",
    "cw",
    "wd",
    "ww",
    "custom_index",
]


def tg(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TG: Mean of daily mean temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TG",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def tn(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TN: Mean of daily minimum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TN",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def tx(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TX: Mean of daily maximum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TX",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def dtr(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    DTR: Mean Diurnal Temperature Range

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="DTR",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def etr(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    ETR: Intra-period extreme temperature range

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="ETR",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def vdtr(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    vDTR: Mean day-to-day variation in Diurnal Temperature Range

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="VDTR",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def su(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    SU: Number of Summer Days (Tmax > 25C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="SU",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def tr(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TR: Number of Tropical Nights (Tmin > 20C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TR",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def wsdi(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    WSDI:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="WSDI",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def tg90p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TG90p: Percentage of days when Tmean > 90th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TG90P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def tn90p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TN90p: Percentage of days when Tmin > 90th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TN90P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def tx90p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TX90p: Percentage of days when Tmax > 90th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TX90P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def txx(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TXx: Maximum daily maximum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TXX",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def tnx(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TNx: Maximum daily minimum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TNX",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def csu(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    CSU: Maximum number of consecutive summer days (Tmax >25 C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="CSU",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def gd4(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    GD4: Growing degree days (sum of Tmean > 4 C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="GD4",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def fd(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    FD: Number of Frost Days (Tmin < 0C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="FD",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def cfd(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    CFD: Maximum number of consecutive frost days (Tmin < 0 C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="CFD",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def hd17(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    HD17: Heating degree days (sum of Tmean < 17 C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="HD17",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def id(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    ID: Number of sharp Ice Days (Tmax < 0C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="ID",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def tg10p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TG10p: Percentage of days when Tmean < 10th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TG10P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def tn10p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TN10p: Percentage of days when Tmin < 10th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TN10P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def tx10p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TX10p: Percentage of days when Tmax < 10th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TX10P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def txn(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TXn: Minimum daily maximum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TXN",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def tnn(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    TNn: Minimum daily minimum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="TNN",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def csdi(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    CSDI:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="CSDI",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        threshold=threshold,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def cdd(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    CDD: Maximum consecutive dry days (Precip < 1mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="CDD",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def prcptot(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    PRCPTOT: Total precipitation during Wet Days

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="PRCPTOT",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def rr1(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    RR1: Number of Wet Days (precip >= 1 mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="RR1",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def sdii(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    SDII: Average precipitation during Wet Days (SDII)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="SDII",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def cwd(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    CWD: Maximum consecutive wet days (Precip >= 1mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="CWD",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def r10mm(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    R10mm: Number of heavy precipitation days (Precip >=10mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="R10MM",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def r20mm(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    R20mm: Number of very heavy precipitation days (Precip >= 20mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="R20MM",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def rx1day(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    RX1day: Maximum 1-day precipitation

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="RX1DAY",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def rx5day(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    RX5day: Maximum 5-day precipitation

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="RX5DAY",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def r75p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    R75p:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="R75P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def r75ptot(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    R75pTOT:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="R75PTOT",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def r95p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    R95p:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="R95P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def r95ptot(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    R95pTOT:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="R95PTOT",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def r99p(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    R99p:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="R99P",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def r99ptot(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    R99pTOT:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="R99PTOT",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def sd(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    SD: Mean of daily snow depth

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="SD",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def sd1(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    SD1: Snow days (SD >= 1 cm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="SD1",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def sd5cm(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    SD5cm: Number of days with snow depth >= 5 cm

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="SD5CM",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def sd50cm(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    SD50cm: Number of days with snow depth >= 50 cm

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="SD50CM",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
    )


def cd(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    CD:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="CD",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def cw(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    CW:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="CW",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def wd(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    WD:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="WD",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def ww(
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str
    | QuantileInterpolation
    | None = QuantileInterpolation.MEDIAN_UNBIASED,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    WW:

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="WW",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        window_width=window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )


def custom_index(
    user_index: UserIndexDict,
    in_files: str | list[str] | Dataset | DataArray,
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    base_period_time_range: list[datetime] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
) -> Dataset:
    """
    This function can be used to create indices using simple operators.
    Use the `user_index` parameter to describe how the index should be computed.
    You can find some examples in our documentation at :ref:`custom_indices`.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")

    Notes
    -----
    This function has been auto-generated.
    """
    return icclim.index(
        user_index=user_index,
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_percentile=save_percentile,
        logs_verbosity=logs_verbosity,
    )
