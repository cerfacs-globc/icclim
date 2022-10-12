"""
This module has been auto-generated.
To modify these, edit the extractor tool in `tools/extract-icclim-funs.py`.
This module exposes each climate index as individual functions for convenience.
"""
# flake8: noqa E501
from __future__ import annotations

import datetime
from typing import Sequence

from xarray.core.dataset import Dataset

import icclim
from icclim.icclim_logger import Verbosity
from icclim.icclim_types import InFileLike, SamplingMethodLike
from icclim.models.frequency import Frequency, FrequencyLike
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.threshold import build_threshold
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
    "rr",
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
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TG: Mean of daily mean temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def tn(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TN: Mean of daily minimum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def tx(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TX: Mean of daily maximum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def dtr(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    DTR: Mean Diurnal Temperature Range

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def etr(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    ETR: Intra-period extreme temperature range

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def vdtr(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    vDTR: Mean day-to-day variation in Diurnal Temperature Range

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def su(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    SU: Number of Summer Days (Tmax > 25C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 25 degree_Celsius",
        ),
        out_unit="day",
    )


def tr(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TR: Number of Tropical Nights (Tmin > 20C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 20 degree_Celsius",
        ),
        out_unit="day",
    )


def wsdi(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    WSDI: Warm-spell duration index (days)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 90 doy_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
        ),
        out_unit="day",
    )


def tg90p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TG90p: Days when Tmean > 90th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 90 doy_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
        ),
        out_unit="day",
    )


def tn90p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TN90p: Days when Tmin > 90th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 90 doy_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
        ),
        out_unit="day",
    )


def tx90p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TX90p: Days when Tmax > 90th daily percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 90 doy_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
        ),
        out_unit="day",
    )


def txx(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TXx: Maximum daily maximum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def tnx(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TNx: Maximum daily minimum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def csu(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    CSU: Maximum number of consecutive summer days (Tmax >25 C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 25 degree_Celsius",
        ),
        out_unit="day",
    )


def gd4(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    GD4: Growing degree days (sum of Tmean > 4 C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="4 degree_Celsius",
        ),
        out_unit="degree_Celsius day",
    )


def fd(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    FD: Number of Frost Days (Tmin < 0C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="< 0 degree_Celsius",
        ),
        out_unit="day",
    )


def cfd(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    CFD: Maximum number of consecutive frost days (Tmin < 0 C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="< 0 degree_Celsius",
        ),
        out_unit="day",
    )


def hd17(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    HD17: Heating degree days (sum of Tmean < 17 C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="17 degree_Celsius",
        ),
        out_unit="degree_Celsius day",
    )


def id(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    ID: Number of sharp Ice Days (Tmax < 0C)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="< 0 degree_Celsius",
        ),
        out_unit="day",
    )


def tg10p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TG10p: Days when Tmean < 10th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="< 10 doy_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
        ),
        out_unit="day",
    )


def tn10p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TN10p: Days when Tmin < 10th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="< 10 doy_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
        ),
        out_unit="day",
    )


def tx10p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TX10p: Days when Tmax < 10th percentile

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="< 10 doy_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
        ),
        out_unit="day",
    )


def txn(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TXn: Minimum daily maximum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def tnn(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    TNn: Minimum daily minimum temperature

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="degree_Celsius",
    )


def csdi(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    CSDI: Cold-spell duration index (days)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="< 10 doy_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
        ),
        out_unit="day",
    )


def cdd(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    CDD: Maximum consecutive dry days (Precip < 1mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query="< 1 mm/day",
        ),
        out_unit="day",
    )


def prcptot(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    PRCPTOT: Total precipitation during Wet Days

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 1 mm/day",
        ),
        out_unit="mm",
    )


def rr1(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    RR1: Number of Wet Days (precip >= 1 mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 1 mm/day",
        ),
        out_unit="day",
    )


def sdii(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    SDII: Average precipitation during Wet Days (SDII)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 1 mm/day",
        ),
        out_unit="mm/day",
    )


def cwd(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    CWD: Maximum consecutive wet days (Precip >= 1mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 1 mm/day",
        ),
        out_unit="day",
    )


def rr(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    RR: Precipitation sum (mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
    Notes
    -----
    This function has been auto-generated.

    """
    return icclim.index(
        index_name="RR",
        in_files=in_files,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        out_file=out_file,
        ignore_Feb29th=ignore_Feb29th,
        netcdf_version=netcdf_version,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        out_unit="mm",
    )


def r10mm(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    R10mm: Number of heavy precipitation days (Precip >=10mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 10 mm/day",
        ),
        out_unit="day",
    )


def r20mm(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    R20mm: Number of very heavy precipitation days (Precip >= 20mm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 20 mm/day",
        ),
        out_unit="day",
    )


def rx1day(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    RX1day: maximum 1-day total precipitation

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="mm/day",
    )


def rx5day(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    RX5day: maximum 5-day total precipitation

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="mm",
    )


def r75p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    R75p: Days with RR > 75th percentile of daily amounts (moderate wet days) (d)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 75 period_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
            threshold_min_value="1.0 millimeter / day",
        ),
        out_unit="day",
    )


def r75ptot(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    R75pTOT: Precipitation fraction due to moderate wet days (> 75th percentile)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 75 period_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
            threshold_min_value="1.0 millimeter / day",
        ),
        out_unit="%",
    )


def r95p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    R95p: Days with RR > 95th percentile of daily amounts (very wet days) (days)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 95 period_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
            threshold_min_value="1.0 millimeter / day",
        ),
        out_unit="day",
    )


def r95ptot(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    R95pTOT: Precipitation fraction due to very wet days (> 95th percentile)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 95 period_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
            threshold_min_value="1.0 millimeter / day",
        ),
        out_unit="%",
    )


def r99p(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    R99p: Days with RR > 99th percentile of daily amounts (extremely wet days)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 99 period_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
            threshold_min_value="1.0 millimeter / day",
        ),
        out_unit="day",
    )


def r99ptot(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    R99pTOT: Precipitation fraction due to extremely wet days (> 99th percentile)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=build_threshold(
            query="> 99 period_per",
            doy_window_width=5,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
            reference_period=base_period_time_range,
            threshold_min_value="1.0 millimeter / day",
        ),
        out_unit="%",
    )


def sd(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    SD: Mean of daily snow depth

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        out_unit="cm",
    )


def sd1(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    SD1: Snow days (SD >= 1 cm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 1 cm",
        ),
        out_unit="day",
    )


def sd5cm(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    SD5cm: Number of days with snow depth >= 5 cm

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 5 cm",
        ),
        out_unit="day",
    )


def sd50cm(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    ignore_Feb29th: bool = False,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    SD50cm: Number of days with snow depth >= 50 cm

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        date_event=date_event,
        threshold=build_threshold(
            query=">= 50 cm",
        ),
        out_unit="day",
    )


def cd(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    CD: Days with TG < 25th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum (cold/dry days)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=[
            build_threshold(
                query="< 25 doy_per",
                doy_window_width=5,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                reference_period=base_period_time_range,
            ),
            build_threshold(
                query="< 25 period_per",
                doy_window_width=5,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                reference_period=base_period_time_range,
                threshold_min_value="1.0 millimeter / day",
            ),
        ],
        out_unit="day",
    )


def cw(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    CW: Days with TG < 25th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum (cold/wet days)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=[
            build_threshold(
                query="< 25 doy_per",
                doy_window_width=5,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                reference_period=base_period_time_range,
            ),
            build_threshold(
                query="> 75 period_per",
                doy_window_width=5,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                reference_period=base_period_time_range,
                threshold_min_value="1.0 millimeter / day",
            ),
        ],
        out_unit="day",
    )


def wd(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    WD: Days with TG > 75th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum (warm/dry days)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=[
            build_threshold(
                query="> 75 doy_per",
                doy_window_width=5,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                reference_period=base_period_time_range,
            ),
            build_threshold(
                query="< 25 period_per",
                doy_window_width=5,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                reference_period=base_period_time_range,
                threshold_min_value="1.0 millimeter / day",
            ),
        ],
        out_unit="day",
    )


def ww(
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
) -> Dataset:
    """
    WW: Days with TG > 75th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum (warm/wet days)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
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
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        threshold=[
            build_threshold(
                query="> 75 doy_per",
                doy_window_width=5,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                reference_period=base_period_time_range,
            ),
            build_threshold(
                query="> 75 period_per",
                doy_window_width=5,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
                reference_period=base_period_time_range,
                threshold_min_value="1.0 millimeter / day",
            ),
        ],
        out_unit="day",
    )


def custom_index(
    user_index: UserIndexDict,
    in_files: InFileLike,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    doy_window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
    min_spell_length: int | None = 6,
    rolling_window_width: int | None = 5,
    sampling_method: SamplingMethodLike = "resample",
) -> Dataset:
    """
    This function can be used to create indices using simple operators.
    Use the `user_index` parameter to describe how the index should be computed.
    You can find some examples in our documentation at :ref:`custom_indices`.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    doy_window_width: int
        ``optional`` Window width used to aggreagte day of year values when computing
        day of year percentiles (doy_per)
        Default: 5 (5 days).
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit: str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
    min_spell_length: int
        ``optional`` Minimum spell duration to be taken into account when computing the
        sum_of_spell_lengths.
    rolling_window_width: int
        ``optional`` Window width of the rolling window for indicators such as
        `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`  # noqa
    sampling_method: str
        Choose whether the output sampling configured in `slice_mode` is a
        `groupby` operation or a `resample` operation (as per xarray definition).
        Possible values: ``{"groupby", "resample", "groupby_ref_and_resample_study"}``
        (default: "resample")
        `groupby_ref_and_resample_study` may only be used when computing the
        `difference_of_means` (a.k.a the anomaly).
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
        doy_window_width=doy_window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        save_thresholds=save_thresholds,
        logs_verbosity=logs_verbosity,
        date_event=date_event,
        min_spell_length=min_spell_length,
        rolling_window_width=rolling_window_width,
        sampling_method=sampling_method,
    )
