"""
Contain the ClimateVariable class and its related functions.

A climate variable is a structure that contains all the pre-processed input varaible to
compute a climate index.
A climate index may require one or more climate variables to be computed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import xarray

from icclim._core.constants import REFERENCE_PERIOD_INDEX, UNITS_KEY
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.input_parsing import (
    DEFAULT_INPUT_FREQUENCY,
    build_reference_da,
    build_studied_data,
    guess_standard_variable,
    read_dataset,
)
from icclim.exception import InvalidIcclimArgumentError
from icclim.frequency import Frequency, FrequencyRegistry
from icclim.threshold.factory import build_threshold

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    import jinja2
    from xarray.core.dataarray import DataArray

    from icclim._core.model.global_metadata import GlobalMetadata
    from icclim._core.model.icclim_types import InFileBaseType
    from icclim._core.model.in_file_dictionary import InFileDictionary
    from icclim._core.model.standard_index import StandardIndex
    from icclim._core.model.standard_variable import StandardVariable
    from icclim._core.model.threshold import Threshold


@dataclass
class ClimateVariable:
    """
    ClimateVariable is a dataclass that represents a climate variable used to compute a climate index.

    It groups together the input variable (studied_data), its associated metadata
    (standard_var) if any, the threshold it must be compared to.

    Attributes
    ----------
    name: str
        Name of the variable.
    standard_var: StandardVariable
        CF metadata bounded to the standard variable used for this ClimateVariable.
    studied_data: DataArray
        The variable studied.
    threshold: Threshold | None
        thresholds for this variable
    reference_period: Sequence of str | None
        The reference period to consider
    """  # noqa: E501

    name: str
    standard_var: StandardVariable | None
    studied_data: DataArray
    global_metadata: GlobalMetadata
    source_frequency: Frequency
    threshold: Threshold | None = None
    reference_period: Sequence[datetime | str] | None = None
    is_reference: bool = False

    def build_indicator_metadata(
        self,
        src_freq: Frequency,
        must_run_bootstrap: bool,
        jinja_scope: dict[str, Any],
        jinja_env: jinja2.Environment,
    ) -> dict[str, str | dict]:
        """
        Build the metadata for the indicator that will be computed with this variable.

        Parameters
        ----------
        src_freq: Frequency
            The frequency of the source data.
        must_run_bootstrap: bool
            Whether the bootstrap method must be run.
        jinja_scope: dict
            The scope to use for jinja templating.
        jinja_env: jinja2.Environment
            The environment to use for jinja templating.

        Returns
        -------
        dict of str, str | dict
            The metadata for the indicator.
        """
        metadata: dict[str, str | dict] = {"threshold": {}}
        if self.standard_var is None:
            metadata.update(
                {
                    "standard_name": "unknown_variable",
                    "long_name": "unknown variable",
                    "short_name": "input",
                },
            )
        else:
            metadata.update(self.standard_var.get_metadata())
        if self.threshold is not None:
            metadata.update(
                {
                    "threshold": self.threshold.format_metadata(
                        src_freq=src_freq,
                        must_run_bootstrap=must_run_bootstrap,
                        jinja_scope=jinja_scope,
                        jinja_env=jinja_env,
                    ),
                },
            )
        return metadata


def build_climate_vars(
    climate_vars_dict: dict[str, InFileDictionary],
    ignore_Feb29th: bool,  # noqa: N803
    time_range: Sequence[datetime | str] | None,
    base_period: Sequence[str] | None,
    standard_index: StandardIndex | None,
    is_compared_to_reference: bool,
) -> list[ClimateVariable]:
    """
    Build a list of ClimateVariable from a dictionary of input files.

    Parameters
    ----------
    climate_vars_dict: dict of str, InFileDictionary
        The dictionary of input files.
    ignore_Feb29th: bool
        Whether to ignore February 29th.
    time_range: Sequence of datetime | str | None
        The time range to consider.
    base_period: Sequence of str | None
        The base period to consider, used to build a reference variable for indices such
         as anomaly.
    standard_index: StandardIndex | None
        The standard index to compute.

    Returns
    -------
    list of ClimateVariable that will be used to compute the climate index.
    """
    from icclim.ecad.binding import (
        StandardizedPrecipitationIndex3,
        StandardizedPrecipitationIndex6,
    )

    if standard_index is not None and len(standard_index.input_variables) > len(
        climate_vars_dict
    ):
        msg = (
            f"Index {standard_index.short_name} needs"
            f" {len(standard_index.input_variables)} variables."
            f" Please provide them with an xarray.Dataset, netCDF file(s) or a"
            f" zarr store."
        )
        raise InvalidIcclimArgumentError(msg)
    acc = []
    for i, raw_climate_var in enumerate(climate_vars_dict.items()):
        if standard_index is not None:
            standard_var = standard_index.input_variables[i]
        else:
            standard_var = None

        # For SPI, attach reference_period directly to the study variable
        if standard_index is not None and standard_index.short_name.lower() in (
            "spi3",
            "spi6",
        ):
            reference_period = base_period
        else:
            reference_period = None

        cv = build_climate_var(
            raw_climate_var[0],
            raw_climate_var[1],
            ignore_Feb29th,
            time_range,
            standard_var=standard_var,
            reference_period=reference_period,
        )

        acc.append(cv)

    # Only add a reference variable for non-SPI indices
    if not isinstance(
        standard_index,
        (StandardizedPrecipitationIndex3, StandardizedPrecipitationIndex6),
    ):
        if _standard_index_needs_ref(
            standard_index, is_compared_to_reference
        ) or _generic_index_needs_ref(standard_index, is_compared_to_reference):
            standard_var = standard_index.input_variables[0] if standard_index else None
            added_var = _build_reference_variable(
                base_period,
                climate_vars_dict,
                standard_var=standard_var,
            )
            acc.append(added_var)

    return acc


def build_climate_var(
    climate_var_name: str,
    climate_var_data: InFileDictionary | InFileBaseType,
    ignore_Feb29th: bool,  # noqa: N803
    time_range: Sequence[datetime | str] | None,
    standard_var: StandardVariable | None,
    reference_period: Sequence[datetime | str] | None = None,
) -> ClimateVariable:
    """
    Build a ClimateVariable object.

    Parameters
    ----------
    climate_var_name : str
        The name of the climate variable.
    climate_var_data : InFileDictionary | InFileBaseType
        The input data for the climate variable. It can be either a dictionary
        or a file.
    ignore_Feb29th : bool
        Flag indicating whether to ignore February 29th in the time range.
    time_range : Sequence[datetime | str] | None
        The time range to consider for the climate variable. It can be a sequence
        of datetime objects or strings, or None to consider the entire time range.
    standard_var : StandardVariable | None
        The standard variable to use for the climate variable. If None, the input
        data will be used to guess the standard variable.

    Returns
    -------
    ClimateVariable
        The built ClimateVariable object.

    Notes
    -----
    This function builds a ClimateVariable object based on the provided inputs.
    It reads the input data, determines the standard variable, builds the studied
    data, and sets the threshold and global metadata.

    If the input data is a dictionary, it is assumed to have a 'study' key
    containing the study data and an optional 'thresholds' key containing the
    threshold data.

    If the input data is a file, it is assumed to contain the study data.

    The standard variable is used to determine the conversion unit for the
    threshold data.

    The studied data is built based on the study data, time range, ignore_Feb29th
    flag, and standard variable.

    If a threshold is provided in the dictionary, it is added to the ClimateVariable.

    Examples
    --------
    >>> climate_var_name = "tas"
    >>> climate_var_data = {"study": "/path/to/data.nc", "thresholds": ">= 27 degC"}
    >>> ignore_Feb29th = False
    >>> time_range = ["2000-01-01", "2010-12-31"]
    >>> standard_var = StandardVariableRegistry.TAS
    >>> climate_var = build_climate_var(
    ...     climate_var_name, climate_var_data, ignore_Feb29th, time_range, standard_var
    ... )
    """
    if isinstance(climate_var_data, dict):
        study_ds = read_dataset(
            climate_var_data["study"],
            standard_var,
            climate_var_name,
        )
        climate_var_thresh = climate_var_data.get("thresholds", None)
    else:
        study_ds = read_dataset(climate_var_data, standard_var, climate_var_name)
        climate_var_thresh = None
    if standard_var is None:
        standard_var = guess_standard_variable(study_ds[climate_var_name])
    studied_data = build_studied_data(
        study_ds[climate_var_name],
        time_range,
        ignore_Feb29th,
        standard_var.default_units if standard_var else None,
    )
    if climate_var_thresh is not None:
        climate_var_thresh = _build_threshold(
            climate_var_thresh=climate_var_thresh,
            original_data=study_ds[climate_var_name],
            conversion_unit=studied_data.attrs[UNITS_KEY],
        )
    return ClimateVariable(
        name=climate_var_name,
        standard_var=standard_var,
        studied_data=studied_data,
        threshold=climate_var_thresh,
        reference_period=reference_period,
        global_metadata={
            "history": study_ds.attrs.get("history", None),
            "source": study_ds.attrs.get("source", None),
            "time_encoding": study_ds.time.encoding,
        },
        source_frequency=FrequencyRegistry.lookup(
            xarray.infer_freq(studied_data.time) or DEFAULT_INPUT_FREQUENCY,
        ),
    )


def must_run_bootstrap(da: DataArray, threshold: Threshold | None) -> bool:
    """
    Determine whether to run the bootstrap method.

    Parameters
    ----------
    da : DataArray
        The studied data.
    threshold : Threshold | None
        The threshold that contains the reference period.

    Returns
    -------
    bool
        Whether to run the bootstrap method.

    Notes
    -----
    This function is used to avoid bootstrapping if there is one single year
    overlapping or no year overlapping or all year overlapping between the studied
    data `da` and the reference period defined by the threshold.
    """
    # TODO @bzah: Don't run bootstrap when not on extreme percentile
    #       (run only below 20? 10? and above 80? 90?)
    # https://github.com/cerfacs-globc/icclim/issues/289
    if (
        threshold is None
        or not isinstance(threshold, PercentileThreshold)
        or (
            isinstance(threshold, PercentileThreshold)
            and not threshold.is_doy_per_threshold
        )
    ):
        return False
    reference = threshold.value
    study_years = np.unique(da.indexes.get("time").year)
    overlapping_years = np.unique(
        da.sel(time=_get_ref_period_slice(reference)).indexes.get("time").year,
    )
    return 1 < len(overlapping_years) < len(study_years)


def _standard_index_needs_ref(
    standard_index: StandardIndex, is_compared_to_reference: bool
) -> bool:
    return (
        standard_index
        and standard_index.qualifiers
        and REFERENCE_PERIOD_INDEX in standard_index.qualifiers
        and is_compared_to_reference
    )


def _generic_index_needs_ref(
    standard_index: StandardIndex, is_compared_to_reference: bool
) -> bool:
    return standard_index is None and is_compared_to_reference


def _build_reference_variable(
    reference_period: Sequence[str] | None,
    in_files: dict[str, InFileDictionary],
    standard_var: StandardVariable,
) -> ClimateVariable:
    """
    Add a secondary variable for indices such as anomaly.

    This kind of indices require exactly two variables, but the second variable can
    just be a subset of the first one.
    """
    if reference_period is None:
        msg = "Can't build a reference variable without a `base_period_time_range`"
        raise InvalidIcclimArgumentError(msg)
    var_name = next(iter(in_files.keys()))
    if isinstance(in_files, dict):
        study_ds = read_dataset(
            next(iter(in_files.values()))["study"],
            standard_var=standard_var,
            var_name=var_name,
        )
    else:
        study_ds = read_dataset(
            next(iter(in_files.values())),
            standard_var=standard_var,
            var_name=var_name,
        )
    studied_data = build_reference_da(
        study_ds[var_name],
        reference_period,
        only_leap_years=False,
        percentile_min_value=None,
    )
    return ClimateVariable(
        name=var_name + "_reference",
        standard_var=standard_var,
        studied_data=studied_data,
        threshold=None,
        reference_period=reference_period,
        global_metadata={
            "history": study_ds.attrs.get("history", None),
            "source": study_ds.attrs.get("source", None),
            "time_encoding": study_ds.time.encoding,
        },
        source_frequency=FrequencyRegistry.lookup(
            xarray.infer_freq(studied_data.time) or DEFAULT_INPUT_FREQUENCY,
        ),
        is_reference=True,
    )


def _build_threshold(
    climate_var_thresh: str | Threshold,
    original_data: DataArray,
    conversion_unit: str,
) -> Threshold:
    if isinstance(climate_var_thresh, str):
        climate_var_thresh: Threshold = build_threshold(climate_var_thresh)
    if climate_var_thresh.prepare is not None and not climate_var_thresh.is_ready:
        climate_var_thresh.prepare(original_data)
    climate_var_thresh.unit = conversion_unit
    return climate_var_thresh


def _get_ref_period_slice(da: DataArray) -> slice:
    if (bds := da.attrs.get("climatology_bounds", None)) is not None:
        return slice(*bds)
    time_length = len(da.time)
    return slice(*da.time[0 :: time_length - 1].dt.strftime("%Y-%m-%d").to_numpy())
