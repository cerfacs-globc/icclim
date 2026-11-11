# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""
Main entry point of icclim.

This module expose icclim principal function, notably `index` which is use by the
generated API.
A convenience function `indices` is also exposed to compute multiple indices at once.
"""

from __future__ import annotations

import datetime as dt
import json
import operator
import os
import sys
import time
from collections.abc import Callable, Sequence
from functools import reduce
from typing import TYPE_CHECKING, Any, Literal, Union
from warnings import catch_warnings, simplefilter, warn

import numpy as np
import xarray as xr

from icclim import provenance
from icclim._core.climate_variable import (
    ClimateVariable,
    build_climate_vars,
)
from icclim._core.constants import (
    ICCLIM_REFERENCE,
    RESAMPLE_METHOD,
    UNITS_KEY,
)
from icclim._core.generic.indicator import GenericIndicator
from icclim._core.input_parsing import build_input_dict
from icclim._core.model.index_config import (
    CompletenessLike,
    IndexConfig,
    resolve_completeness_policy,
)
from icclim._core.model.index_group import IndexGroup, IndexGroupRegistry
from icclim._core.model.logical_link import LogicalLinkRegistry
from icclim._core.model.netcdf_version import NetcdfVersion, NetcdfVersionRegistry
from icclim._core.model.quantile_interpolation import (
    QuantileInterpolation,
    QuantileInterpolationRegistry,
)
from icclim._core.model.standard_index import StandardIndex
from icclim._core.model.threshold import Threshold
from icclim._core.utils import read_date
from icclim.dcsc.registry import DcscIndexRegistry
from icclim.ecad.binding import (
    StandardizedPrecipitationIndex3,
    StandardizedPrecipitationIndex6,
)
from icclim.ecad.registry import EcadIndexRegistry
from icclim.exception import InvalidIcclimArgumentError
from icclim.frequency import Frequency, FrequencyRegistry
from icclim.generic.registry import GenericIndicatorRegistry
from icclim.logger import IcclimLogger, Verbosity, VerbosityRegistry
from icclim.threshold.factory import build_threshold

if TYPE_CHECKING:
    from xarray.core.dataarray import DataArray
    from xarray.core.dataset import Dataset

    from icclim._core.legacy.user_index.model import UserIndexDict
    from icclim._core.model.icclim_types import (
        FrequencyLike,
        InFileLike,
        SamplingMethodLike,
    )
    from icclim._core.model.in_file_dictionary import InFileDictionary
    from icclim._core.model.indicator import Indicator
    from icclim._core.model.logical_link import LogicalLink

SliceMode = Union[str, Sequence[str], "Frequency", "FrequencyLike"]

log: IcclimLogger = IcclimLogger.get_instance(VerbosityRegistry.LOW)

HISTORY_CF_KEY = "history"
SOURCE_CF_KEY = "source"
NUMBER_OF_NOTNULL_VAR = "number_of_notnull"
OUTPUT_COMPRESSION_LEVEL_ENV = "ICCLIM_OUTPUT_COMPRESSION_LEVEL"
OUTPUT_CHUNKS_ENV = "ICCLIM_OUTPUT_CHUNKS"
MAX_OUTPUT_COMPRESSION_LEVEL = 9


class NormalizedIndexRequest:
    """Small container for deprecated-parameter normalization results."""

    def __init__(
        self,
        index_name: str | GenericIndicator | StandardIndex | None,
        legacy_user_index: UserIndexDict | None,
        save_thresholds: bool,
        doy_window_width: int,
    ) -> None:
        self.index_name = index_name
        self.legacy_user_index = legacy_user_index
        self.save_thresholds = save_thresholds
        self.doy_window_width = doy_window_width


class ParsedIndicatorConfig:
    """Small container for standard or generic indicator selection results."""

    def __init__(
        self,
        *,
        standard_index: StandardIndex | None,
        indicator: Indicator,
        threshold: str | Threshold | Sequence[str | Threshold] | None,
        rename: str | None,
        output_unit: str | None,
        reference: str,
        indicator_name: str,
    ) -> None:
        self.standard_index = standard_index
        self.indicator = indicator
        self.threshold = threshold
        self.rename = rename
        self.output_unit = output_unit
        self.reference = reference
        self.indicator_name = indicator_name


class ParsedLegacyUserIndexConfig:
    """Small container for the deprecated user-index bridge."""

    def __init__(
        self,
        *,
        indicator: Indicator,
        parsed_threshold: Threshold | Sequence[Threshold] | None,
        logical_link: LogicalLink,
        coef: float | None,
        date_event: bool,
        rename: str,
        output_unit: str | None,
        rolling_window_width: int | None,
        reference_period: tuple[str, str] | None,
    ) -> None:
        self.indicator = indicator
        self.parsed_threshold = parsed_threshold
        self.logical_link = logical_link
        self.coef = coef
        self.date_event = date_event
        self.rename = rename
        self.output_unit = output_unit
        self.rolling_window_width = rolling_window_width
        self.reference_period = reference_period


def indices(
    index_group: Sequence[str] | str | IndexGroup | StandardIndex,
    *,
    ignore_error: bool = False,
    **kwargs,
) -> Dataset:
    """
    Compute multiple indices at the same time.

    The input dataset(s) must include all the necessary variables.
    It can only be used with keyword arguments (kwargs).

    Parameters
    ----------
    index_group : "all" | str | IndexGroup | list[str]
        Either the name of an IndexGroup or an instance of IndexGroup or a list
        of index short names or the name(s) of standard variable(s) (such as 'tasmax').
        The value "all" can also be used to compute every indices.
        Note that the input given by ``in_files`` must include all the necessary
        variables to compute the indices of this group.
    ignore_error: bool
        When True, ignore indices that fails to compute. This is option is particularly
        useful when used with `index_group='all'` to compute everything that can be
        computed given the input.
    kwargs : Dict
        ``icclim.index`` keyword arguments.

    Returns
    -------
    xr.Dataset
        A Dataset with one data variable per index.

    Notes
    -----
    If ``output_file`` is part of kwargs, the result is written in a single netCDF
    file, which will contain all the index results of this group.
    """
    with catch_warnings(record=True) as captured_warnings:
        simplefilter("always")
        indices = _get_ecad_indices_of_group(index_group)
        out_file = kwargs.get("out_file")
        index_kwargs = _build_indices_call_kwargs(kwargs)
        acc = []
        for standard_index in indices:
            log.info("Computing index %s", standard_index.short_name)
            try:
                res = index(
                    **_with_requested_index_name(
                        index_kwargs, standard_index.short_name
                    )
                )
                res = _rename_coords(res, standard_index.short_name)
                res = _drop_group_auxiliary_vars(res)
                acc.append(res)
            except Exception:
                if ignore_error:
                    warn(
                        f"Could not compute {standard_index.short_name}.", stacklevel=2
                    )
                else:
                    raise
        ds: Dataset = xr.merge(acc, compat="no_conflicts", join="outer")
        if out_file is not None:
            bundle = provenance.build_output_provenance(
                config=None,
                result_ds=ds,
                out_file=out_file,
                entrypoint="icclim.indices",
                user_parameters={
                    "index_group": index_group,
                    "ignore_error": ignore_error,
                    "kwargs": _build_provenance_user_parameters(kwargs),
                },
                resolved_overrides={
                    "requested_indices": [
                        standard_index.short_name for standard_index in indices
                    ],
                },
                captured_warnings=captured_warnings,
            )
            provenance.add_provenance_attrs(ds, bundle)
            _write_output_file(
                result_ds=ds,
                input_time_encoding=ds.time.encoding,
                netcdf_version=index_kwargs.get(
                    "netcdf_version", NetcdfVersionRegistry.NETCDF4
                ),
                file_path=out_file,
            )
            bundle = provenance.finalize_written_output_provenance(out_file, bundle)
            provenance.write_provenance_json(out_file, bundle)
        return ds


def _build_indices_call_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    index_kwargs = dict(kwargs)
    index_kwargs.pop("out_file", None)
    return index_kwargs


def _with_requested_index_name(
    kwargs: dict[str, Any],
    index_name: str,
) -> dict[str, Any]:
    return {**kwargs, "index_name": index_name}


def _get_ecad_indices_of_group(
    query: Sequence[str] | str | IndexGroup | StandardIndex,
) -> list[StandardIndex]:
    if _is_wildcard_index_group_query(query):
        return EcadIndexRegistry.values()
    query_list = query if isinstance(query, (list, tuple)) else [query]

    indices = _find_named_standard_indices(query_list)
    if indices:
        return indices

    indices = _find_indices_matching_source_variables(query_list)
    if indices:
        return indices

    indices = _find_indices_from_named_groups(query_list)
    if indices:
        return indices

    msg = f"The index group {query} was not recognized."
    raise InvalidIcclimArgumentError(msg)


def _is_wildcard_index_group_query(
    query: Sequence[str] | str | IndexGroup | StandardIndex,
) -> bool:
    return query == IndexGroupRegistry.WILD_CARD_GROUP or (
        isinstance(query, str)
        and query.lower() == IndexGroupRegistry.WILD_CARD_GROUP.name
    )


def _find_named_standard_indices(query: Sequence[Any]) -> list[StandardIndex] | None:
    indices = [EcadIndexRegistry.lookup_no_error(i) for i in query]
    res = [i for i in indices if i is not None]
    if len(res) == len(query):
        return res
    return None


def _find_indices_matching_source_variables(
    query: Sequence[Any],
) -> list[StandardIndex] | None:
    indices = [
        ecad_index
        for ecad_index in EcadIndexRegistry.values()
        if _matches_requested_source_variables(ecad_index, query)
    ]
    if len(indices) >= len(query):
        return indices
    return None


def _matches_requested_source_variables(
    ecad_index: StandardIndex,
    requested_variables: Sequence[Any],
) -> bool:
    if ecad_index.input_variables is None:
        return False
    for input_variable in ecad_index.input_variables:
        matching_aliases = (
            requested_variable in input_variable.aliases
            for requested_variable in requested_variables
        )
        if not any(matching_aliases):
            return False
    return True


def _find_indices_from_named_groups(query: Sequence[Any]) -> list[StandardIndex] | None:
    groups = [IndexGroupRegistry.lookup_no_error(i) for i in query]
    res = [i for i in groups if i is not None]
    if res:
        indices = [x.get_indices() for x in res]
        return reduce(operator.add, indices, [])  # flatten list[list]
    return None


def indice(*args, **kwargs) -> Dataset:
    """
    Proxy for `icclim.index` function.

    Deprecated: to be deleted in a future release.
    """
    log.deprecation_warning(old="icclim.indice", new="icclim.index")
    return index(*args, **kwargs)


def index(
    in_files: InFileLike,
    index_name: str | GenericIndicator | StandardIndex | None = None,
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[dt.datetime | str] | None = None,
    out_file: str | None = None,
    threshold: str | Threshold | Sequence[str | Threshold] | None = None,
    callback: Callable[[int], None] = log.callback,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None = None,
    bootstrap: bool | None = None,
    doy_window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    user_index: UserIndexDict | None = None,
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
    min_spell_length: int | None = 6,
    rolling_window_width: int | None = 5,
    sampling_method: SamplingMethodLike = RESAMPLE_METHOD,
    run_index: str | None = None,
    allow_partial_seasons: bool | Literal["start", "end"] | None = None,
    completeness: CompletenessLike = None,
    allow_missing_periods: bool | None = None,
    allow_partial_final_period: bool = False,
    *,
    split_runs_at_period_boundary: bool = False,
    # deprecated params are kwargs only
    window_width: int | None = None,
    save_percentile: bool | None = None,
    indice_name: str | None = None,
    user_indice: UserIndexDict | None = None,
    transfer_limit_Mbytes: float | None = None,
) -> Dataset:
    """
    Compute climate index.

    This is the main entry point for icclim.

    .. warning::
       The ``user_index`` parameter is deprecated, treated as a legacy
       compatibility bridge, and will lose support in a future version.
       New custom indices should use the generic index API instead.

    Parameters
    ----------
    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    index_name: str | StandardIndex
        Climate index name.
        For ECA&D index, case insensitive name used to lookup the index.
        For the deprecated ``user_index`` bridge, it's the name of the output variable.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the
        climate index wanted.
        Mandatory for the deprecated ``user_index`` bridge.
    slice_mode: FrequencyLike | Frequency
        Type of temporal aggregation:
        The possible values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas
        frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Spatially varying seasons can be defined by providing a tuple of
        two ``xarray.DataArray`` objects (start day-of-year and end day-of-year):
        ``(start_da, end_da)``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime.datetime ] | list[str]  | tuple[str, str] | None
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
    threshold: float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    transfer_limit_Mbytes: float
        Deprecated, does not have any effect.
    callback: Callable[[int], None]
        ``optional`` Progress bar printing. If ``None``, progress bar will not be
        printed.
    callback_percentage_start_value: int
        ``optional`` Initial value of percentage of the progress bar (default: 0).
    callback_percentage_total: int
        ``optional`` Total percentage value (default: 100).
    base_period_time_range: list[datetime.datetime ] | list[str] | tuple[str, str] | None
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
        (that is, an anomaly) if a single variable is given in input.
    bootstrap: bool | None
        ``optional`` Override bootstrap behavior for day-of-year percentile thresholds.
        Use ``None`` (default) to rely on icclim's overlap-based bootstrap logic,
        ``False`` to disable bootstrap, or ``True`` to force it when supported by the
        threshold type. For dask-backed percentile count indices, icclim automatically
        uses bounded spatial tiles so users do not have to find a working dask chunking
        strategy by trial and error. The safe path derives its spatial tile size from
        ``ICCLIM_BOOTSTRAP_SAFE_TILE_MEMORY`` (default: ``2GB``), unless
        ``ICCLIM_BOOTSTRAP_SAFE_TILE_CELLS`` is set as an expert override.
        Set ``ICCLIM_BOOTSTRAP_MODE=default`` only for diagnostics to keep the reference bootstrap
        dask graph path. ``bootstrap=False`` should only be used as an explicit user
        shortcut for fast exploratory assessments, because disabling bootstrap removes
        the overlap correction and can bias percentile-based results.
    doy_window_width: int
        ``optional`` Window width used to aggregate day-of-year values when computing
        day of year percentiles (doy_per)
        Default: 5 (5 days).
    min_spell_length: int
        ``optional`` Minimum spell duration to be taken into account when computing
        the sum_of_spell_lengths.
    rolling_window_width: int
        ``optional`` Window width of the rolling window for indicators such as
        `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`
    run_index: str | None
        ``optional`` The index used to attribute a run that crosses an output-period
        boundary. Since icclim 7.4.0, omitting this argument selects ``"last"`` for
        ``CDD``, ``CWD``, ``CFD``, ``CSU``, ``PXCDD``, ``PXCWD`` and
        ``max_consecutive_occurrence``: the whole run is counted in the period where
        it ends. Pass ``run_index="first"`` for the pre-7.4.0 behavior, or pass
        ``split_runs_at_period_boundary=True`` to cut runs at every boundary.
        The default attribution of ``WSDI`` and ``CSDI`` is unchanged. ECA&D ATBD v11, pp. 20--21 specifies
        end-period attribution for CDD and CWD; the same convention is applied to
        CFD, CSU, PXCDD, PXCWD and the generic function for consistency.
    split_runs_at_period_boundary: bool
        ``optional`` Only used by the indices based on ``max_consecutive_occurrence``
        (``CDD``, ``CWD``, ``CFD``, ``CSU``) and on ``sum_of_spell_lengths``
        (``WSDI``, ``CSDI``), ignored otherwise.
        When ``False`` (default), a run of consecutive days that crosses the end of
        an output period is counted whole in a single period: the one where the run
        starts with ``run_index="first"``, or the one where it ends with
        ``run_index="last"`` (the default since 7.4.0). The following (or preceding) period then gets no
        credit for the days of that run, so its value can be 0.
        When ``True``, runs are cut at the boundary of every output period and each
        period gets the longest run found inside it. ``run_index`` then has no
        effect on the values.
        For ``WSDI`` and ``CSDI`` the runs are cut first and only the pieces of at
        least 6 days are summed (the pieces, not the whole spell, must reach 6 days).
        Default is ``False``.
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non-percentile-based indices.
    out_unit: str | None
        ``optional`` Output unit for certain indices: "days" or "%"
        (default: "days").
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    user_index: UserIndexDict
        ``optional`` Legacy dictionary-based custom-index configuration.
        **Deprecated** and kept only for backward compatibility.
        New code should use the generic index API instead.
        See :ref:`custom_indices_recipes` only to migrate old code.
        Ignored for ECA&D indices.
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting
        netcdf file (default: False).
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    sampling_method: str
        Choose whether the output sampling configured in `slice_mode` is a
        `groupby` operation or a `resample` operation (as per xarray definitions).
        Possible values:
        ``{"groupby", "resample", "groupby_ref_and_resample_study"}``
        (default: "resample")
        `groupby_ref_and_resample_study` may only be used when computing the
        `difference_of_means` (a.k.a the anomaly).
    indice_name: str | None
        DEPRECATED, use index_name instead.
    user_indice: dict | None
        DEPRECATED, use user_index instead.
    window_width: int
        DEPRECATED, use doy_window_width, min_spell_length or rolling_window_width
        instead.
    save_percentile: bool
        DEPRECATED, use save_thresholds instead.
    allow_partial_seasons : bool | "start" | "end"
        Flag indicating whether to allow partial seasons to be included in the
        index calculation.
        - True: Unmasks both the first and last periods.
        - False: Masks any incomplete periods (standard behavior).
        - "start": Unmasks only the first period.
        - "end": Unmasks only the last period.
        Default is False.
    completeness : {"ecad", "wmo", "strict", "none"} | float | None
        Completeness rule used to decide whether an output period has enough
        source observations to be calculated. ``None`` selects the ECA&D ATBD
        profile automatically: at least 350 daily values for a year, 175 for a
        half-year, 85 for a three-month season, and 25 for a month. ``strict``
        requires every expected value. ``wmo`` applies the aggregation-specific
        WMO-No. 1203 rules: the 11-day/5-consecutive-day monthly rule for means
        and counts, complete data for sums, and no completeness mask for simple
        extrema. Unclassified operations, unsupported period types, non-daily
        WMO inputs, and spatially varying seasons safely fall back to strict.
        ``none`` always computes from available values, and a fraction in
        ``(0, 1]`` sets a configurable minimum valid fraction. Do not combine
        this parameter with the legacy ``allow_missing_periods`` parameter.
    allow_missing_periods : bool | None
        Compatibility parameter for 7.2 workflows. An explicit False selects
        strict completeness, while True computes from available source values.
        None delegates to ``completeness`` and therefore uses ECA&D by default.
        When neither parameter is explicit, icclim warns if an irregular source
        time coordinate is detected or an already-eager mask shows an incomplete
        period. Lazy inputs are not evaluated solely to emit a warning.
    allow_partial_final_period : bool
        When True, incomplete historical output periods are still masked, but
        the final output period is allowed to be computed from available source
        timesteps. This is useful for an ongoing month or year at the end of a
        time series. Ignored when ``allow_missing_periods=True``.

    Examples
    --------
    Compute Summer Days (SU) from an in-memory xarray DataArray:

    >>> import numpy as np, pandas as pd, xarray as xr, icclim
    >>> time = pd.date_range("2000-01-01", periods=366, freq="D")
    >>> tasmax = xr.DataArray(
    ...     np.full(366, 303.15),
    ...     coords={"time": time},
    ...     dims=["time"],
    ...     attrs={"units": "K"},
    ... )
    >>> result = icclim.index(in_files=tasmax, index_name="SU", var_name="tasmax")
    >>> int(result["SU"].isel(time=0).values)
    366

    Compute a generic index with spatially varying seasons:

    >>> import numpy as np, pandas as pd, xarray as xr, icclim
    >>> time = pd.date_range("2000-01-01", periods=366, freq="D")
    >>> tas = xr.DataArray(
    ...     np.full((366, 1, 2), 300.0),
    ...     coords={"time": time, "lat": [45], "lon": [5, 10]},
    ...     dims=["time", "lat", "lon"],
    ...     attrs={"units": "K"},
    ... )
    >>> # Pixel 1: season is JJA (doy 153 to 244 in leap year)
    >>> # Pixel 2: season is SON (doy 245 to 335 in leap year)
    >>> start = xr.DataArray(
    ...     [[153, 245]], dims=["lat", "lon"], coords={"lat": [45], "lon": [5, 10]}
    ... )
    >>> end = xr.DataArray(
    ...     [[244, 335]], dims=["lat", "lon"], coords={"lat": [45], "lon": [5, 10]}
    ... )
    >>> result = icclim.index(
    ...     in_files=tas,
    ...     index_name="TG",
    ...     slice_mode=(start, end),
    ... )
    >>> # TG is the mean temperature over the season.
    >>> # Since all values are 300K (26.85°C), the result should be ~26.85
    >>> round(float(result["TG"].isel(time=0, lat=0, lon=0).values), 2)
    26.85

    Compute an index with an incomplete season at the end (Hellmann style):

    >>> import numpy as np, pandas as pd, xarray as xr, icclim
    >>> time = pd.date_range("2020-01-01", "2021-12-31", freq="D")
    >>> tas = xr.DataArray(
    ...     np.full(len(time), 30.0),
    ...     coords={"time": time},
    ...     dims=["time"],
    ...     attrs={"units": "degC"},
    ... )
    >>> slice_mode = ("season", ("1 november", "31 march"))
    >>> result = icclim.index(
    ...     in_files=tas,
    ...     index_name="SU",
    ...     slice_mode=slice_mode,
    ...     allow_partial_seasons=True,
    ... )
    >>> # The last season (2021-11-01 to 2022-03-31) is partial (61 days in 2021)
    >>> int(result["SU"].values[-1])
    61
    """
    with catch_warnings(record=True) as captured_warnings:
        simplefilter("always")
        _setup(callback, callback_percentage_start_value, logs_verbosity)
        normalized_request = _normalize_index_request(
            index_name=index_name,
            user_index=user_index,
            save_thresholds=save_thresholds,
            doy_window_width=doy_window_width,
            indice_name=indice_name,
            transfer_limit_mbytes=transfer_limit_Mbytes,
            user_indice=user_indice,
            save_percentile=save_percentile,
            window_width=window_width,
        )
        config = _build_config_from_request(
            in_files=in_files,
            var_name=var_name,
            slice_mode=slice_mode,
            time_range=time_range,
            threshold=threshold,
            callback=callback,
            base_period_time_range=base_period_time_range,
            bootstrap=bootstrap,
            only_leap_years=only_leap_years,
            ignore_feb29th=ignore_Feb29th,
            interpolation=interpolation,
            out_unit=out_unit,
            netcdf_version=netcdf_version,
            date_event=date_event,
            min_spell_length=min_spell_length,
            rolling_window_width=rolling_window_width,
            sampling_method=sampling_method,
            run_index=run_index or "first",
            split_runs_at_period_boundary=split_runs_at_period_boundary,
            allow_partial_seasons=allow_partial_seasons or False,
            completeness=completeness,
            allow_missing_periods=allow_missing_periods,
            allow_partial_final_period=allow_partial_final_period,
            warn_on_missing_periods=(
                allow_missing_periods is None and allow_partial_seasons is None
            ),
            normalized_request=normalized_request,
        )
        run_index = _resolve_run_index(config, run_index)
        provenance_user_parameters = _build_index_provenance_user_parameters(
            index_name=index_name,
            var_name=var_name,
            slice_mode=slice_mode,
            time_range=time_range,
            out_file=out_file,
            threshold=threshold,
            base_period_time_range=base_period_time_range,
            bootstrap=bootstrap,
            doy_window_width=doy_window_width,
            only_leap_years=only_leap_years,
            ignore_feb29th=ignore_Feb29th,
            interpolation=interpolation,
            out_unit=out_unit,
            netcdf_version=netcdf_version,
            user_index=user_index,
            save_thresholds=save_thresholds,
            date_event=date_event,
            min_spell_length=min_spell_length,
            rolling_window_width=rolling_window_width,
            sampling_method=sampling_method,
            run_index=run_index,
            split_runs_at_period_boundary=split_runs_at_period_boundary,
            allow_partial_seasons=allow_partial_seasons,
            completeness=completeness,
            allow_missing_periods=allow_missing_periods,
            allow_partial_final_period=allow_partial_final_period,
            normalized_request=normalized_request,
        )
        result_ds = _run_index_workflow(
            config,
            out_file,
            callback_percentage_total,
            callback,
            provenance_user_parameters=provenance_user_parameters,
            captured_warnings=captured_warnings,
        )
        log.ending_message(time.process_time())
    _reemit_actionable_warnings(captured_warnings)
    return result_ds


# Names of the indices whose run_index default notice was already printed in this
# process (the notice is printed once per index).
_RUN_INDEX_NOTICE_SHOWN: set[str] = set()


def _reset_run_index_notices() -> None:
    """Forget which indices already printed the run_index notice (for tests)."""
    _RUN_INDEX_NOTICE_SHOWN.clear()


def _resolve_run_index(config: IndexConfig, requested: str | None) -> str:
    """Resolve the longest-run default and emit its unfilterable notice once."""
    if requested is not None:
        return requested
    if config.indicator.name != GenericIndicatorRegistry.MaxConsecutiveOccurrence.name:
        config.run_index = "first"
        return "first"

    config.run_index = "last"
    index_name = config.indicator_name
    if index_name not in _RUN_INDEX_NOTICE_SHOWN:
        _RUN_INDEX_NOTICE_SHOWN.add(index_name)
        sys.stdout.write(
            f"Since icclim 7.4.0, {index_name} defaults to "
            'run_index="last", so a run crossing a period boundary is counted where '
            'it ends. Use run_index="first" for the pre-7.4.0 result, or '
            "split_runs_at_period_boundary=True to cut the run at each boundary.\n"
        )
    return "last"


def _reemit_actionable_warnings(captured_warnings: list[Any]) -> None:
    emitted: set[tuple[type[Warning], str]] = set()
    for item in captured_warnings:
        message = str(item.message)
        warning_key = (item.category, message)
        if warning_key not in emitted and (
            "source time series is incomplete" in message
            or "completeness policy will mask" in message
            or "will not attach that standard-variable metadata" in message
        ):
            warn(item.message, item.category, stacklevel=3)
            emitted.add(warning_key)


def _run_index_workflow(
    config: IndexConfig,
    out_file: str | None,
    callback_percentage_total: int,
    callback: Callable[[int], None],
    provenance_user_parameters: dict[str, Any] | None = None,
    captured_warnings: list[Any] | None = None,
) -> Dataset:
    """Compute, optionally write, and finalize one climate-index request."""
    result_ds = _compute_climate_index(
        climate_index=config.indicator,
        config=config,
        initial_history=config.climate_variables[0].global_metadata["history"],
        initial_source=config.climate_variables[0].global_metadata["source"],
        rename=config.rename,
        reference=config.reference,
    )
    if out_file is not None:
        bundle = provenance.build_output_provenance(
            config=config,
            result_ds=result_ds,
            out_file=out_file,
            entrypoint="icclim.index",
            user_parameters=provenance_user_parameters,
            captured_warnings=captured_warnings,
        )
        provenance.add_provenance_attrs(result_ds, bundle)
        _write_output_file(
            result_ds,
            config.climate_variables[0].global_metadata["time_encoding"],
            config.netcdf_version,
            out_file,
        )
        bundle = provenance.finalize_written_output_provenance(out_file, bundle)
        provenance.write_provenance_json(out_file, bundle)
    callback(callback_percentage_total)
    return result_ds


def _build_provenance_user_parameters(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {
        key: _serialize_provenance_value(value)
        for key, value in kwargs.items()
        if key not in {"callback"}
    }


def _build_index_provenance_user_parameters(
    *,
    index_name: str | GenericIndicator | StandardIndex | None,
    var_name: str | Sequence[str] | None,
    slice_mode: FrequencyLike | Frequency,
    time_range: Sequence[dt.datetime | str] | None,
    out_file: str | None,
    threshold: str | Threshold | Sequence[str | Threshold] | None,
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    bootstrap: bool | None,
    doy_window_width: int,
    only_leap_years: bool,
    ignore_feb29th: bool,
    interpolation: str | QuantileInterpolation,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    user_index: UserIndexDict | None,
    save_thresholds: bool,
    date_event: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    sampling_method: SamplingMethodLike,
    run_index: str | None,
    split_runs_at_period_boundary: bool,
    allow_partial_seasons: bool | Literal["start", "end"],
    completeness: CompletenessLike,
    allow_missing_periods: bool | None,
    allow_partial_final_period: bool,
    normalized_request: NormalizedIndexRequest,
) -> dict[str, Any]:
    return {
        "index_name": _serialize_provenance_value(index_name),
        "normalized_index_name": _serialize_provenance_value(
            normalized_request.index_name
        ),
        "legacy_user_index_used": normalized_request.legacy_user_index is not None,
        "var_name": _serialize_provenance_value(var_name),
        "slice_mode": _serialize_provenance_value(slice_mode),
        "time_range": _serialize_provenance_value(time_range),
        "out_file": out_file,
        "threshold": _serialize_provenance_value(threshold),
        "base_period_time_range": _serialize_provenance_value(base_period_time_range),
        "bootstrap": bootstrap,
        "doy_window_width": doy_window_width,
        "only_leap_years": only_leap_years,
        "ignore_feb29th": ignore_feb29th,
        "interpolation": _serialize_provenance_value(interpolation),
        "out_unit": out_unit,
        "netcdf_version": _serialize_provenance_value(netcdf_version),
        "user_index": _serialize_provenance_value(user_index),
        "save_thresholds": save_thresholds,
        "date_event": date_event,
        "min_spell_length": min_spell_length,
        "rolling_window_width": rolling_window_width,
        "sampling_method": _serialize_provenance_value(sampling_method),
        "run_index": run_index,
        "split_runs_at_period_boundary": split_runs_at_period_boundary,
        "allow_partial_seasons": allow_partial_seasons,
        "completeness": completeness,
        "allow_missing_periods": allow_missing_periods,
        "allow_partial_final_period": allow_partial_final_period,
    }


def _serialize_provenance_value(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_serialize_provenance_value(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _serialize_provenance_value(item) for key, item in value.items()
        }
    if hasattr(value, "name"):
        return value.name
    return str(value)


def _build_config_from_request(
    *,
    in_files: InFileLike,
    var_name: str | Sequence[str] | None,
    slice_mode: FrequencyLike | Frequency,
    time_range: Sequence[dt.datetime | str] | None,
    threshold: str | Threshold | Sequence[str | Threshold] | None,
    callback: Callable[[int], None],
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    bootstrap: bool | None,
    only_leap_years: bool,
    ignore_feb29th: bool,
    interpolation: str | QuantileInterpolation,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    date_event: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    sampling_method: SamplingMethodLike,
    run_index: str | None,
    split_runs_at_period_boundary: bool,
    allow_partial_seasons: bool | Literal["start", "end"],
    completeness: CompletenessLike,
    allow_missing_periods: bool | None,
    allow_partial_final_period: bool,
    warn_on_missing_periods: bool,
    normalized_request: NormalizedIndexRequest,
) -> IndexConfig:
    """Build an IndexConfig from a normalized user request."""
    return _build_config(
        in_files=in_files,
        index_name=normalized_request.index_name,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        threshold=threshold,
        callback=callback,
        base_period_time_range=base_period_time_range,
        bootstrap=bootstrap,
        doy_window_width=normalized_request.doy_window_width,
        only_leap_years=only_leap_years,
        ignore_feb29th=ignore_feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        legacy_user_index=normalized_request.legacy_user_index,
        save_thresholds=normalized_request.save_thresholds,
        date_event=date_event,
        min_spell_length=min_spell_length,
        rolling_window_width=rolling_window_width,
        sampling_method=sampling_method,
        run_index=run_index,
        split_runs_at_period_boundary=split_runs_at_period_boundary,
        allow_partial_seasons=allow_partial_seasons,
        completeness=completeness,
        allow_missing_periods=allow_missing_periods,
        allow_partial_final_period=allow_partial_final_period,
        warn_on_missing_periods=warn_on_missing_periods,
    )


def _build_config(
    in_files: InFileLike,
    index_name: str | GenericIndicator | StandardIndex | None,
    var_name: str | Sequence[str] | None,
    slice_mode: FrequencyLike | Frequency,
    time_range: Sequence[dt.datetime | str] | None,
    threshold: str | Threshold | Sequence[str | Threshold] | None,
    callback: Callable[[int], None],
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    bootstrap: bool | None,
    doy_window_width: int,
    only_leap_years: bool,
    ignore_feb29th: bool,
    interpolation: str | QuantileInterpolation,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    legacy_user_index: UserIndexDict | None,
    save_thresholds: bool,
    date_event: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    sampling_method: SamplingMethodLike,
    run_index: str | None,
    split_runs_at_period_boundary: bool,
    allow_partial_seasons: bool | Literal["start", "end"],
    completeness: CompletenessLike,
    allow_missing_periods: bool | None,
    allow_partial_final_period: bool,
    warn_on_missing_periods: bool,
) -> IndexConfig:
    if _uses_legacy_user_index_recipe(legacy_user_index, index_name):
        return _build_legacy_user_index_config(
            legacy_user_index,
            in_files=in_files,
            index_name=index_name,
            var_name=var_name,
            slice_mode=slice_mode,
            time_range=time_range,
            callback=callback,
            base_period_time_range=base_period_time_range,
            bootstrap=bootstrap,
            doy_window_width=doy_window_width,
            only_leap_years=only_leap_years,
            ignore_feb29th=ignore_feb29th,
            interpolation=interpolation,
            out_unit=out_unit,
            netcdf_version=netcdf_version,
            save_thresholds=save_thresholds,
            min_spell_length=min_spell_length,
            rolling_window_width=rolling_window_width,
            sampling_method=sampling_method,
            run_index=run_index,
            split_runs_at_period_boundary=split_runs_at_period_boundary,
            allow_partial_seasons=allow_partial_seasons,
            completeness=completeness,
            allow_missing_periods=allow_missing_periods,
            allow_partial_final_period=allow_partial_final_period,
            warn_on_missing_periods=warn_on_missing_periods,
        )
    if index_name is not None:
        return _build_standard_index_config(
            in_files=in_files,
            index_name=index_name,
            var_name=var_name,
            slice_mode=slice_mode,
            time_range=time_range,
            threshold=threshold,
            callback=callback,
            base_period_time_range=base_period_time_range,
            bootstrap=bootstrap,
            doy_window_width=doy_window_width,
            only_leap_years=only_leap_years,
            ignore_feb29th=ignore_feb29th,
            interpolation=interpolation,
            out_unit=out_unit,
            netcdf_version=netcdf_version,
            save_thresholds=save_thresholds,
            date_event=date_event,
            min_spell_length=min_spell_length,
            rolling_window_width=rolling_window_width,
            sampling_method=sampling_method,
            run_index=run_index,
            split_runs_at_period_boundary=split_runs_at_period_boundary,
            allow_partial_seasons=allow_partial_seasons,
            completeness=completeness,
            allow_missing_periods=allow_missing_periods,
            allow_partial_final_period=allow_partial_final_period,
            warn_on_missing_periods=warn_on_missing_periods,
        )
    msg = "You must fill either index_name or user_index to compute a climate index."
    raise InvalidIcclimArgumentError(msg)


def _uses_legacy_user_index_recipe(
    user_index: UserIndexDict | None,
    index_name: str | GenericIndicator | StandardIndex | None,
) -> bool:
    return user_index is not None and (
        index_name is None or isinstance(index_name, str)
    )


def _get_reference_period(
    base_period_time_range: Sequence[dt.datetime | str] | None,
) -> tuple | None:
    if base_period_time_range is not None:
        return tuple(
            (read_date(t).strftime("%m-%d-%Y") for t in base_period_time_range),
        )
    return None


def _parse_threshold(
    threshold: str | Threshold | Sequence[str | Threshold] | None,
    doy_window_width: int,
    reference_period: Sequence[dt.datetime | str] | None,
    only_leap_years: bool,
    interpolation: QuantileInterpolation,
) -> Threshold | Sequence[Threshold] | None:
    if isinstance(threshold, Threshold):
        return threshold
    if isinstance(threshold, (str, dict)):
        return _build_request_threshold(
            threshold,
            doy_window_width=doy_window_width,
            reference_period=reference_period,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
        )
    if isinstance(threshold, Sequence):
        return [
            _build_request_threshold(
                t,
                doy_window_width=doy_window_width,
                reference_period=reference_period,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
            )
            for t in threshold
        ]
    return None


def _build_legacy_user_index_config(
    user_index: UserIndexDict,
    in_files: InFileLike,
    index_name: str | None,
    var_name: str | Sequence[str] | None,
    slice_mode: FrequencyLike | Frequency,
    time_range: Sequence[dt.datetime | str] | None,
    callback: Callable[[int], None],
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    bootstrap: bool | None,
    doy_window_width: int,
    only_leap_years: bool,
    ignore_feb29th: bool,
    interpolation: str | QuantileInterpolation,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    save_thresholds: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    sampling_method: SamplingMethodLike,
    run_index: str | None,
    split_runs_at_period_boundary: bool,
    allow_partial_seasons: bool | Literal["start", "end"],
    completeness: CompletenessLike,
    allow_missing_periods: bool | None,
    allow_partial_final_period: bool,
    warn_on_missing_periods: bool,
) -> IndexConfig:
    interpolation = QuantileInterpolationRegistry.lookup(interpolation)
    sampling_frequency = FrequencyRegistry.lookup(slice_mode)  # type: ignore[arg-type]
    legacy_user_index_config = _parse_legacy_user_index_config(
        user_index=user_index,
        index_name=index_name,
        out_unit=out_unit,
        rolling_window_width=rolling_window_width,
        base_period_time_range=base_period_time_range,
        doy_window_width=doy_window_width,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )
    climate_variables, is_compared_to_ref = _build_index_climate_variables(
        in_files=in_files,
        var_names=var_name,
        threshold=legacy_user_index_config.parsed_threshold,
        standard_index=None,
        ignore_feb29th=ignore_feb29th,
        time_range=time_range,
        reference_period=legacy_user_index_config.reference_period,
        bootstrap=bootstrap,
    )
    return _assemble_index_config(
        climate_variables=climate_variables,
        frequency=sampling_frequency,
        save_thresholds=save_thresholds,
        min_spell_length=min_spell_length,
        rolling_window_width=legacy_user_index_config.rolling_window_width,
        out_unit=legacy_user_index_config.output_unit,
        netcdf_version=netcdf_version,
        interpolation=interpolation,
        callback=callback,
        is_compared_to_reference=is_compared_to_ref,
        reference_period=legacy_user_index_config.reference_period,
        indicator_name=legacy_user_index_config.indicator.name,
        logical_link=legacy_user_index_config.logical_link,
        coef=legacy_user_index_config.coef,
        date_event=legacy_user_index_config.date_event,
        sampling_method=sampling_method,
        rename=legacy_user_index_config.rename,
        indicator=legacy_user_index_config.indicator,
        reference=ICCLIM_REFERENCE,
        run_index=run_index,
        split_runs_at_period_boundary=split_runs_at_period_boundary,
        allow_partial_seasons=allow_partial_seasons,
        completeness=completeness,
        allow_missing_periods=allow_missing_periods,
        allow_partial_final_period=allow_partial_final_period,
        warn_on_missing_periods=warn_on_missing_periods,
    )


def _build_standard_index_config(
    in_files: InFileLike,
    index_name: str | GenericIndicator | StandardIndex,
    var_name: str | Sequence[str] | None,
    slice_mode: FrequencyLike | Frequency,
    time_range: Sequence[dt.datetime | str] | None,
    threshold: str | Threshold | Sequence[str | Threshold] | None,
    callback: Callable[[int], None],
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    bootstrap: bool | None,
    doy_window_width: int,
    only_leap_years: bool,
    ignore_feb29th: bool,
    interpolation: str | QuantileInterpolation,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    save_thresholds: bool,
    date_event: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    sampling_method: SamplingMethodLike,
    run_index: str | None,
    split_runs_at_period_boundary: bool,
    allow_partial_seasons: bool | Literal["start", "end"],
    completeness: CompletenessLike,
    allow_missing_periods: bool | None,
    allow_partial_final_period: bool,
    warn_on_missing_periods: bool,
) -> IndexConfig:
    interpolation = QuantileInterpolationRegistry.lookup(interpolation)
    # logical link here link two climate_variable computations as with user_index.
    # It isalways AND for standard indices.
    logical_link = LogicalLinkRegistry.LOGICAL_AND
    sampling_frequency = FrequencyRegistry.lookup(slice_mode)  # type: ignore[arg-type]
    coef = None
    indicator_config = _parse_indicator_config(index_name, out_unit, threshold)
    standard_index = indicator_config.standard_index
    indicator = indicator_config.indicator
    threshold = indicator_config.threshold
    rename = indicator_config.rename
    output_unit = indicator_config.output_unit
    reference = indicator_config.reference
    indicator_name = indicator_config.indicator_name
    reference_period = _get_reference_period(base_period_time_range)
    parsed_threshold = _parse_threshold(
        indicator_config.threshold,
        doy_window_width=doy_window_width,
        reference_period=reference_period,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )
    climate_variables, is_compared_to_ref = _build_index_climate_variables(
        in_files=in_files,
        var_names=var_name,
        threshold=parsed_threshold,
        standard_index=standard_index,
        ignore_feb29th=ignore_feb29th,
        time_range=time_range,
        reference_period=reference_period,
        bootstrap=bootstrap,
    )
    return _assemble_index_config(
        climate_variables=climate_variables,
        frequency=sampling_frequency,
        save_thresholds=save_thresholds,
        min_spell_length=min_spell_length,
        rolling_window_width=rolling_window_width,
        out_unit=output_unit,
        netcdf_version=netcdf_version,
        interpolation=interpolation,
        callback=callback,
        is_compared_to_reference=is_compared_to_ref,
        reference_period=reference_period,
        indicator_name=indicator_name,
        logical_link=logical_link,
        coef=coef,
        date_event=date_event,
        sampling_method=sampling_method,
        rename=rename,
        indicator=indicator,
        reference=reference,
        run_index=run_index,
        split_runs_at_period_boundary=split_runs_at_period_boundary,
        allow_partial_seasons=allow_partial_seasons,
        completeness=completeness,
        allow_missing_periods=allow_missing_periods,
        allow_partial_final_period=allow_partial_final_period,
        warn_on_missing_periods=warn_on_missing_periods,
    )


def _parse_legacy_user_index_config(
    *,
    user_index: UserIndexDict,
    index_name: str | None,
    out_unit: str | None,
    rolling_window_width: int | None,
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    doy_window_width: int,
    only_leap_years: bool,
    interpolation: QuantileInterpolation,
) -> ParsedLegacyUserIndexConfig:
    from icclim._core.legacy.user_index import parse  # noqa: PLC0415

    return ParsedLegacyUserIndexConfig(
        indicator=parse.read_indicator(user_index),
        parsed_threshold=parse.read_thresholds(
            user_index,
            doy_window_width=doy_window_width,
            reference_period=base_period_time_range,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
        ),
        logical_link=parse.read_logical_link(user_index),
        coef=parse.read_coef(user_index),
        date_event=parse.read_date_event(user_index),
        rename=index_name or user_index.get("index_name", None) or "user_index",
        output_unit=out_unit,
        rolling_window_width=user_index.get("window_width", rolling_window_width),
        reference_period=_get_reference_period(
            user_index.get("ref_time_range", base_period_time_range)
        ),
    )


def _build_index_climate_variables(
    *,
    in_files: InFileLike,
    var_names: str | Sequence[str] | None,
    threshold: Threshold | Sequence[Threshold] | None,
    standard_index: StandardIndex | None,
    ignore_feb29th: bool,
    time_range: Sequence[dt.datetime | str] | None,
    reference_period: Sequence[str] | None,
    bootstrap: bool | None,
) -> tuple[list[ClimateVariable], bool]:
    climate_vars_dict = build_input_dict(
        in_files=in_files,
        var_names=var_names,
        threshold=threshold,
        standard_index=standard_index,
    )
    is_compared_to_reference = _must_add_reference_var(
        climate_vars_dict,
        reference_period,
    )
    climate_variables = build_climate_vars(
        climate_vars_dict=climate_vars_dict,
        ignore_feb29th=ignore_feb29th,
        time_range=time_range,
        base_period=reference_period,
        standard_index=standard_index,
        is_compared_to_reference=is_compared_to_reference,
        bootstrap=bootstrap,
    )
    return climate_variables, is_compared_to_reference


def _assemble_index_config(
    *,
    climate_variables: list[ClimateVariable],
    frequency: Frequency,
    save_thresholds: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    interpolation: QuantileInterpolation,
    callback: Callable[[int], None],
    is_compared_to_reference: bool,
    reference_period: tuple[str, str] | None,
    indicator_name: str,
    logical_link: LogicalLink,
    coef: float | None,
    date_event: bool,
    sampling_method: SamplingMethodLike,
    rename: str | None,
    indicator: Indicator,
    reference: str,
    run_index: str | None,
    split_runs_at_period_boundary: bool,
    allow_partial_seasons: bool | Literal["start", "end"],
    completeness: CompletenessLike,
    allow_missing_periods: bool | None,
    allow_partial_final_period: bool,
    warn_on_missing_periods: bool,
) -> IndexConfig:
    return IndexConfig(
        save_thresholds=save_thresholds,
        frequency=frequency,
        climate_variables=climate_variables,
        min_spell_length=min_spell_length,
        rolling_window_width=rolling_window_width,
        out_unit=out_unit,
        netcdf_version=NetcdfVersionRegistry.lookup(netcdf_version),
        interpolation=interpolation,
        callback=callback,
        is_compared_to_reference=is_compared_to_reference,
        reference_period=reference_period,
        indicator_name=indicator_name,
        logical_link=logical_link,
        coef=coef,
        date_event=date_event,
        sampling_method=sampling_method,
        rename=rename,
        indicator=indicator,
        reference=reference,
        run_index=run_index,
        split_runs_at_period_boundary=split_runs_at_period_boundary,
        allow_partial_seasons=allow_partial_seasons,
        completeness_policy=resolve_completeness_policy(
            completeness=completeness,
            allow_missing_periods=allow_missing_periods,
            frequency=frequency,
            source_frequency=climate_variables[0].source_frequency,
            missing_method=getattr(indicator, "missing", "any"),
            missing_options=getattr(indicator, "missing_options", None),
            wmo_aggregation=getattr(indicator, "wmo_aggregation", "other"),
        ),
        allow_partial_final_period=allow_partial_final_period,
        warn_on_missing_periods=warn_on_missing_periods,
    )


def _parse_index_kind(
    index_name: StandardIndex | GenericIndicator | str,
) -> StandardIndex | GenericIndicator:
    if isinstance(index_name, str):
        res: StandardIndex | GenericIndicator | None
        res = EcadIndexRegistry.lookup_no_error(index_name)
        if res is None:
            res = DcscIndexRegistry.lookup_no_error(index_name)
        if res is None:
            res = GenericIndicatorRegistry.lookup(index_name)
        return res
    return index_name


def _write_output_file(
    result_ds: xr.Dataset,
    input_time_encoding: dict | None,
    netcdf_version: NetcdfVersion,
    file_path: str,
) -> None:
    """Write `result_ds` to a netCDF file on `out_file` path."""
    encoding = _build_output_encoding(
        result_ds,
        input_time_encoding,
        netcdf_version,
    )
    result_ds.to_netcdf(
        file_path,
        format=netcdf_version.name,
        encoding=encoding,
    )


def _build_output_encoding(
    result_ds: xr.Dataset,
    input_time_encoding: dict | None,
    netcdf_version: NetcdfVersion,
) -> dict[str, dict[str, Any]]:
    """Build default time encoding plus explicitly requested storage options."""
    if input_time_encoding:
        time_encoding = {
            "calendar": input_time_encoding.get("calendar"),
            UNITS_KEY: input_time_encoding.get(UNITS_KEY),
            # Force float64 to avoid serialization warning
            "dtype": np.float64,
        }
    else:
        time_encoding = {
            UNITS_KEY: "days since 1850-1-1",
            "dtype": np.float64,  # force float
        }
    encoding: dict[str, dict[str, Any]] = {"time": time_encoding}
    compression_level = _read_output_compression_level()
    requested_chunks = _read_output_chunks()
    if compression_level is not None and netcdf_version.name.startswith("NETCDF3"):
        msg = (
            f"{OUTPUT_COMPRESSION_LEVEL_ENV} requires a NETCDF4 output format, "
            f"not {netcdf_version.name}."
        )
        raise InvalidIcclimArgumentError(msg)
    if requested_chunks is not None and netcdf_version.name.startswith("NETCDF3"):
        msg = (
            f"{OUTPUT_CHUNKS_ENV} requires a NETCDF4 output format, "
            f"not {netcdf_version.name}."
        )
        raise InvalidIcclimArgumentError(msg)
    if compression_level is None and requested_chunks is None:
        return encoding
    for name, data_var in result_ds.data_vars.items():
        variable_encoding: dict[str, Any] = {}
        if compression_level is not None:
            variable_encoding.update(zlib=True, complevel=compression_level)
        if requested_chunks is not None and data_var.dims:
            variable_encoding["chunksizes"] = tuple(
                min(
                    data_var.sizes[dim],
                    requested_chunks.get(
                        dim,
                        _first_chunk_size(data_var, dim),
                    ),
                )
                for dim in data_var.dims
            )
        if variable_encoding:
            encoding[str(name)] = variable_encoding
    return encoding


def _first_chunk_size(data_var: xr.DataArray, dim: str) -> int:
    if data_var.chunksizes:
        return int(data_var.chunksizes[dim][0])
    return int(data_var.sizes[dim])


def _read_output_compression_level() -> int | None:
    raw_level = os.environ.get(OUTPUT_COMPRESSION_LEVEL_ENV)
    if raw_level is None:
        return None
    try:
        level = int(raw_level)
    except ValueError as error:
        msg = f"{OUTPUT_COMPRESSION_LEVEL_ENV} must be an integer from 1 to 9."
        raise InvalidIcclimArgumentError(msg) from error
    if not 1 <= level <= MAX_OUTPUT_COMPRESSION_LEVEL:
        msg = f"{OUTPUT_COMPRESSION_LEVEL_ENV} must be an integer from 1 to 9."
        raise InvalidIcclimArgumentError(msg)
    return level


def _read_output_chunks() -> dict[str, int] | None:
    raw_chunks = os.environ.get(OUTPUT_CHUNKS_ENV)
    if raw_chunks is None:
        return None
    try:
        chunks = json.loads(raw_chunks)
    except json.JSONDecodeError as error:
        msg = f"{OUTPUT_CHUNKS_ENV} must be a JSON object of dimension sizes."
        raise InvalidIcclimArgumentError(msg) from error
    if (
        not isinstance(chunks, dict)
        or not chunks
        or any(
            not isinstance(dim, str)
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size <= 0
            for dim, size in chunks.items()
        )
    ):
        msg = f"{OUTPUT_CHUNKS_ENV} must be a JSON object of positive integer sizes."
        raise InvalidIcclimArgumentError(msg)
    return chunks


def _normalize_index_request(
    index_name: str | GenericIndicator | StandardIndex | None,
    user_index: UserIndexDict | None,
    save_thresholds: bool,
    doy_window_width: int | None,
    indice_name: str | None,
    transfer_limit_mbytes: float | None,
    user_indice: UserIndexDict | None,
    save_percentile: bool | None,
    window_width: int | None,
) -> NormalizedIndexRequest:
    if indice_name is not None:
        log.deprecation_warning(old="indice_name", new="index_name")
        index_name = indice_name
    if user_indice is not None:
        log.deprecation_warning(old="user_indice", new="user_index")
        user_index = user_indice
    if transfer_limit_mbytes is not None:
        log.deprecation_warning(old="transfer_limit_Mbytes")
    if save_percentile is not None:
        log.deprecation_warning(old="save_percentile", new="save_thresholds")
        save_thresholds = save_percentile
    if window_width is not None:
        log.deprecation_warning(old="window_width", new="doy_window_width")
        doy_window_width = window_width
    return NormalizedIndexRequest(
        index_name=index_name,
        legacy_user_index=user_index,
        save_thresholds=save_thresholds,
        doy_window_width=doy_window_width,
    )


def _setup(
    callback: Callable[[int], None],
    callback_start_value: int,
    logs_verbosity: Verbosity | str,
) -> None:
    import xclim  # noqa: PLC0415

    # make xclim input daily check a warning instead of an error
    # TODO @bzah: it might be safer to feed a context manager which will setup
    #             and teardown these confs
    # https://github.com/cerfacs-globc/icclim/issues/289
    xclim.set_options(data_validation="warn")
    # keep attributes through xarray operations
    xr.set_options(keep_attrs=True)
    log.set_verbosity(logs_verbosity)
    log.start_message()
    callback(callback_start_value)


def _get_unit(output_unit: str | None, da: DataArray) -> str | None:
    da_unit = da.attrs.get(UNITS_KEY, None)
    if da_unit is None:
        if output_unit is None:
            warn(
                "No unit computed or provided for the index was found."
                " Use out_unit parameter to add one.",
                stacklevel=2,
            )
            return ""
        return output_unit
    return da_unit


def _compute_climate_index(
    climate_index: Indicator,
    config: IndexConfig,
    initial_history: str | None,
    initial_source: str | None,
    reference: str,
    rename: str | None = None,
) -> Dataset:
    result_da = climate_index(config)
    result_da = _rename_result_dataarray(result_da, climate_index, rename)
    result_da.attrs[UNITS_KEY] = _get_unit(config.out_unit, result_da)
    result_ds = _build_result_dataset(result_da, config.frequency, climate_index)
    if config.save_thresholds:
        result_ds = _merge_exported_thresholds(result_ds, config.climate_variables)
    history = _build_history(result_da, config, initial_history, climate_index)
    return _add_result_metadata(
        result_ds,
        climate_index,
        history,
        initial_source,
        reference,
    )


def _rename_result_dataarray(
    result_da: DataArray,
    climate_index: Indicator,
    rename: str | None,
) -> DataArray:
    if rename:
        return result_da.rename(rename)
    return result_da.rename(climate_index.name)


def _build_result_dataset(
    result_da: DataArray,
    frequency: Frequency,
    climate_index: Indicator,
) -> Dataset:
    if not _must_post_process_time_axis(result_da, frequency, climate_index):
        return result_da.to_dataset()
    processed_da, time_bounds = frequency.post_processing(result_da)
    result_ds = processed_da.to_dataset()
    if time_bounds is not None:
        result_ds.coords["time_bounds"] = time_bounds
        result_ds.time.attrs["bounds"] = "time_bounds"
    return result_ds


def _must_post_process_time_axis(
    result_da: DataArray,
    frequency: Frequency,
    climate_index: Indicator,
) -> bool:
    return (
        frequency.post_processing is not None
        and "time" in result_da.dims
        and not isinstance(
            climate_index,
            (
                StandardizedPrecipitationIndex6,
                StandardizedPrecipitationIndex3,
            ),
        )
    )


def _merge_exported_thresholds(
    result_ds: Dataset,
    climate_variables: list[ClimateVariable],
) -> Dataset:
    return xr.merge(
        [result_ds, _format_thresholds_for_export(climate_variables)],
    )


def _add_result_metadata(
    result_ds: Dataset,
    computed_index: Indicator,
    history: str,
    initial_source: str | None,
    reference: str,
) -> Dataset:
    result_ds.attrs.update(
        {
            "title": computed_index.standard_name,
            "references": reference,
            "institution": "Climate impact portal (https://climate4impact.eu)",
            "history": history,
            "source": initial_source if initial_source is not None else "",
            "Conventions": "CF-1.6",
        },
    )
    try:
        result_ds.lat.encoding["_FillValue"] = None
        result_ds.lon.encoding["_FillValue"] = None
    except AttributeError:
        try:
            result_ds.latitude.encoding["_FillValue"] = None
            result_ds.longitude.encoding["_FillValue"] = None
        except AttributeError:
            pass
    return result_ds


def _build_history(
    result_da: DataArray,
    config: IndexConfig,
    initial_history: str | None,
    computed_index: Indicator,
) -> str:
    from icclim import __version__ as icclim_version  # noqa: PLC0415

    if initial_history is None:
        # get xclim history
        initial_history = result_da.attrs[HISTORY_CF_KEY]
    else:
        # append xclim history
        initial_history = f"{initial_history}\n{result_da.attrs[HISTORY_CF_KEY]}"
    del result_da.attrs[HISTORY_CF_KEY]
    current_time = dt.datetime.now(tz=dt.UTC).strftime(
        "%Y-%m-%d %H:%M:%S",
    )
    return (
        f"{initial_history}\n"
        f" [{current_time}]"
        f" Calculation of {computed_index.name}"
        f" index ({config.frequency.adjective})"
        f" - icclim version: {icclim_version}"
    )


def _build_request_threshold(
    threshold: str | dict | Threshold,
    doy_window_width: int,
    reference_period: Sequence[dt.datetime | str] | None,
    only_leap_years: bool,
    interpolation: QuantileInterpolation,
) -> Threshold:
    if isinstance(threshold, Threshold):
        from copy import deepcopy  # noqa: PLC0415

        from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
            PercentileThreshold,
        )

        threshold = deepcopy(threshold)
        if isinstance(threshold, PercentileThreshold):
            threshold.doy_window_width = doy_window_width
            threshold.reference_period = reference_period
            threshold.only_leap_years = only_leap_years
            threshold.interpolation = interpolation
        return threshold
    if isinstance(threshold, dict):
        kwargs = {
            "doy_window_width": doy_window_width,
            "reference_period": reference_period,
            "only_leap_years": only_leap_years,
            "interpolation": interpolation,
            **threshold,
        }
        return build_threshold(**kwargs)
    return build_threshold(
        threshold,
        doy_window_width=doy_window_width,
        reference_period=reference_period,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )


def _format_thresholds_for_export(climate_vars: list[ClimateVariable]) -> Dataset:
    return xr.merge(
        [v for v in (_format_threshold(v) for v in climate_vars) if v is not None],
    )


def _format_threshold(cf_var: ClimateVariable) -> DataArray | None:
    if cf_var.threshold is not None:
        ensure_ready = getattr(cf_var.threshold, "ensure_ready", None)
        if ensure_ready is not None:
            ensure_ready(cf_var.studied_data)
        val = cf_var.threshold.value
        if isinstance(val, xr.DataArray):
            return val.rename(cf_var.name + "_thresholds").reindex()  # type: ignore[return-value]
        if isinstance(val, xr.Dataset):
            return val.rename(
                dict.fromkeys(val.data_vars, cf_var.name + "_thresholds")
            ).reindex()  # type: ignore[arg-type]
    return None


def _must_add_reference_var(
    climate_vars_dict: dict[str, InFileDictionary],
    reference_period: Sequence[str] | None,
) -> bool:
    """
    Check if the reference variable must be added to the input variables.

    Return True whenever the input has no threshold and only one studied variable but
    there is a reference period.
    Example case: the anomaly of tx(1960-2100) by tx(1960-1990).
    """
    t = next(iter(climate_vars_dict.values())).get("thresholds", None)
    return t is None and len(climate_vars_dict) == 1 and reference_period is not None


def _rename_coords(ds: Dataset, short_name: str) -> Dataset:
    if "percentiles" in ds.coords:
        ds = ds.rename({"percentiles": short_name + "_percentiles"})
    if "thresholds" in ds.coords:
        ds = ds.rename({"thresholds": short_name + "_thresholds"})
    return ds


def _drop_group_auxiliary_vars(ds: Dataset) -> Dataset:
    return ds.drop_vars(NUMBER_OF_NOTNULL_VAR, errors="ignore")


def _parse_indicator_config(
    index_name: str | GenericIndicator | StandardIndex,
    out_unit: str | None,
    threshold: str | Threshold | Sequence[str | Threshold] | None,
) -> ParsedIndicatorConfig:
    index = _parse_index_kind(index_name)
    if isinstance(index, StandardIndex):
        standard_index = index.clone()
        indicator = standard_index.indicator.clone()
        return ParsedIndicatorConfig(
            standard_index=standard_index,
            indicator=indicator,
            threshold=(
                threshold if threshold is not None else standard_index.threshold
            ),
            rename=standard_index.short_name,
            output_unit=out_unit or standard_index.output_unit,
            reference=standard_index.reference,
            indicator_name=standard_index.short_name,
        )
    if isinstance(index, GenericIndicator):
        indicator = index.clone()
        return ParsedIndicatorConfig(
            standard_index=None,
            indicator=indicator,
            threshold=threshold,
            rename=None,
            output_unit=out_unit,
            reference=ICCLIM_REFERENCE,
            indicator_name=indicator.name,
        )
    err = f"Unknown index_name : `{index_name}`"
    raise InvalidIcclimArgumentError(err)
