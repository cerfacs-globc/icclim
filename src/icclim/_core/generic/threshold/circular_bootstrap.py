"""Percentile bootstrap of the reference and exact paths, with circular windows.

This is a copy of ``xclim.core.bootstrapping.percentile_bootstrap`` and
``bootstrap_func`` (xclim 0.60 and 1.0, Apache License 2.0). The only difference is the
computation of the percentiles of the altered reference periods (the replicates): xclim
calls ``percentile_doy``, whose centered rolling window is truncated at the ends of the
period, while icclim computes the nominal percentiles, the percentiles of the compiled
bootstrap and those of the eager bootstrap with a window that wraps around the year
boundaries (``_circular_percentile_doy``). With xclim's function the replicates of the
first and of the last days of the year had thresholds that were not those of the
nominal percentile, and the reference and exact paths gave values that differed from
the compiled path.

A copy is used instead of a patch of xclim: xclim does not allow to choose the
percentile function, and replacing ``percentile_doy`` in the module of xclim would
change it for every user of xclim in the process.
"""

from __future__ import annotations

import warnings
from inspect import signature
from typing import TYPE_CHECKING, Any

import numpy as np
import xarray as xr
from boltons.funcutils import wraps
from xclim.core.bootstrapping import (
    BOOTSTRAP_DIM,
    _get_bootstrap_freq,
    _get_year_label,
    build_bootstrap_year_da,
)
from xclim.core.utils import uses_dask

if TYPE_CHECKING:
    from collections.abc import Callable


def percentile_bootstrap(func: Callable) -> Callable:
    """Apply the bootstrap step to a function computing an exceedance over a percentile.

    Same as ``xclim.core.bootstrapping.percentile_bootstrap``, with circular windows
    for the percentiles of the replicates.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> xr.DataArray:  # noqa: ANN401
        ba = signature(func).bind(*args, **kwargs)
        ba.apply_defaults()
        bootstrap = ba.arguments.get("bootstrap", False)
        if bootstrap is False:
            return func(*args, **kwargs)
        return bootstrap_func(func, **ba.arguments)

    return wrapper


def bootstrap_func(  # noqa: C901, PLR0912
    compute_index_func: Callable,
    **kwargs: Any,  # noqa: ANN401
) -> xr.DataArray:
    """Bootstrap the computation of an indicator based on a percentile threshold.

    For each year of the studied period that is in the reference period, the values of
    the year are replaced by those of each other year of the reference period, the
    percentiles are computed on the altered reference period and the index on the
    studied year, and the results are averaged. See
    ``xclim.core.bootstrapping.bootstrap_func``.
    """
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        _circular_percentile_doy,
    )

    # Identify the input and the percentile arrays from the bound arguments
    per_key, da_key = None, None
    for name, val in kwargs.items():
        if isinstance(val, xr.DataArray):
            if "percentile_doy" in val.attrs.get("history", ""):
                per_key = name
            else:
                da_key = name
    if da_key is None or per_key is None:
        msg = "The input data and the percentile xr.DataArray must be provided as named arguments."
        raise KeyError(msg)
    da = kwargs.pop(da_key)
    per_da = kwargs.pop(per_key, None)
    if per_da is None:
        msg = "`bootstrap` can only be used with percentiles computed using `percentile_doy`"
        raise KeyError(msg)
    clim = per_da.attrs["climatology_bounds"]
    if (
        uses_dask(da)
        and da.chunks is not None
        and len(da.chunks[da.get_axis_num("time")]) > 1
    ):
        warnings.warn(
            "The input data is chunked on time dimension and must be fully re-chunked to"
            " run percentile bootstrapping."
            " Beware, this operation can significantly increase the number of tasks dask"
            " has to handle.",
            stacklevel=2,
        )
        chunking: dict[str, Any] = {str(d): "auto" for d in da.dims}
        chunking["time"] = -1
        da = da.chunk(chunking)
    overlap_da = da.sel(time=slice(*clim))
    if len(overlap_da.time) == len(da.time):
        msg = (
            "`bootstrap` is unnecessary when all years are overlapping between reference "
            "(percentiles period) and studied (index period) periods"
        )
        raise KeyError(msg)
    if len(overlap_da) == 0:
        msg = (
            "`bootstrap` is unnecessary when no year overlap between reference "
            "(percentiles period) and studied (index period) periods."
        )
        raise KeyError(msg)
    window = per_da.attrs["window"]
    alpha = per_da.attrs["alpha"]
    beta = per_da.attrs["beta"]
    percentiles = np.atleast_1d(per_da.percentiles.data[()])
    bfreq = _get_bootstrap_freq(kwargs["freq"])
    overlap_years_groups = overlap_da.resample(time=bfreq).groups
    da_years_groups = da.resample(time=bfreq).groups
    acc = []
    for year_key, year_slice in da_years_groups.items():
        kw = {da_key: da.isel(time=year_slice), **kwargs}
        if _get_year_label(year_key) in overlap_da.get_index("time").year:
            bda = build_bootstrap_year_da(overlap_da, overlap_years_groups, year_key)
            # circular windows, like the nominal percentile of icclim
            per = _circular_percentile_doy(
                arr=bda,
                window=window,
                per=percentiles,
                alpha=alpha,
                beta=beta,
            )
            if "percentiles" not in per_da.dims:
                per = per.squeeze("percentiles")
            kw[per_key] = per
            value = compute_index_func(**kw).mean(dim=BOOTSTRAP_DIM, keep_attrs=True)
        else:
            kw[per_key] = per_da
            value = compute_index_func(**kw)
        acc.append(value)
    result = xr.concat(acc, dim="time")
    result.attrs["units"] = value.attrs["units"]
    return result
