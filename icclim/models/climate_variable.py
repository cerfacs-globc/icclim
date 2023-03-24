from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import jinja2
import xarray
from xarray.core.dataarray import DataArray

from icclim.generic_indices.standard_variable import StandardVariable
from icclim.generic_indices.threshold import (
    PercentileThreshold,
    Threshold,
    build_threshold,
)
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_types import InFileBaseType, InFileLike
from icclim.models.constants import REFERENCE_PERIOD_INDEX, UNITS_KEY
from icclim.models.frequency import Frequency, FrequencyRegistry
from icclim.models.global_metadata import GlobalMetadata
from icclim.models.standard_index import StandardIndex
from icclim.pre_processing.in_file_dictionary import InFileDictionary
from icclim.pre_processing.input_parsing import (
    DEFAULT_INPUT_FREQUENCY,
    build_reference_da,
    build_studied_data,
    guess_input_type,
    guess_var_names,
    read_dataset,
)


@dataclass
class ClimateVariable:
    """Internal icclim structure.
    It groups together the input variable (studied_data),
    its associated metadata (standard_var) and, if any,
    the threshold it must be compared to.

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
    """

    name: str
    standard_var: StandardVariable | None
    studied_data: DataArray
    global_metadata: GlobalMetadata
    source_frequency: Frequency
    threshold: Threshold | None = None
    is_reference: bool = False

    def build_indicator_metadata(
        self,
        src_freq: Frequency,
        must_run_bootstrap: bool,
        jinja_scope: dict[str, Any],
        jinja_env: jinja2.Environment,
    ) -> dict[str, str | dict]:
        metadata: dict[str, str | dict] = {"threshold": {}}
        if self.standard_var is None:
            metadata.update(
                dict(
                    standard_name="unknown_variable",
                    long_name="unknown variable",
                    short_name="input",
                )
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
                    )
                }
            )
        return metadata


def build_climate_vars(
    climate_vars_dict: dict[str, InFileDictionary],
    ignore_Feb29th: bool,
    time_range: Sequence[str],
    base_period: Sequence[str] | None,
    standard_index: StandardIndex | None,
    is_compared_to_reference: bool,
) -> list[ClimateVariable]:
    if standard_index is not None and len(standard_index.input_variables) > len(
        climate_vars_dict
    ):
        raise InvalidIcclimArgumentError(
            f"Index {standard_index.short_name} needs"
            f" {len(standard_index.input_variables)} variables."
            f" Please provide them with an xarray.Dataset, netCDF file(s) or a"
            f" zarr store."
        )
    acc = []
    for i, raw_climate_var in enumerate(climate_vars_dict.items()):
        if standard_index is not None:
            standard_var = standard_index.input_variables[i]
        else:
            standard_var = None
        acc.append(
            _build_climate_var(
                raw_climate_var[0],
                raw_climate_var[1],
                ignore_Feb29th,
                time_range,
                standard_var=standard_var,
            )
        )
    if _standard_index_needs_ref(
        standard_index, is_compared_to_reference
    ) or _generic_index_needs_ref(standard_index, is_compared_to_reference):
        standard_var = (
            standard_index.input_variables[0] if standard_index is not None else None
        )
        added_var = _build_reference_variable(
            base_period,
            climate_vars_dict,
            standard_var=standard_var,
        )
        acc.append(added_var)
    return acc


def _standard_index_needs_ref(standard_index, is_compared_to_reference):
    return (
        standard_index
        and standard_index.qualifiers
        and REFERENCE_PERIOD_INDEX in standard_index.qualifiers
        and is_compared_to_reference
    )


def _generic_index_needs_ref(standard_index, is_compared_to_reference):
    return standard_index is None and is_compared_to_reference


def _build_reference_variable(
    reference_period: Sequence[str] | None,
    in_files,
    standard_var: StandardVariable,
) -> ClimateVariable:
    """This function add a secondary variable for indices such as anomaly that needs
    exactly two variables but where the second variable could just be a subset of the
    first one.
    """
    if reference_period is None:
        raise InvalidIcclimArgumentError(
            "Can't build a reference variable without a `base_period_time_range`"
        )
    var_name = list(in_files.keys())[0]
    if isinstance(in_files, dict):
        study_ds = read_dataset(
            list(in_files.values())[0]["study"],
            standard_var=standard_var,
            var_name=var_name,
        )
    else:
        study_ds = read_dataset(
            list(in_files.values())[0], standard_var=standard_var, var_name=var_name
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
        global_metadata={
            "history": study_ds.attrs.get("history", None),
            "source": study_ds.attrs.get("source", None),
            "time_encoding": study_ds.time.encoding,
        },
        source_frequency=FrequencyRegistry.lookup(
            xarray.infer_freq(studied_data.time) or DEFAULT_INPUT_FREQUENCY
        ),
        is_reference=True,
    )


def read_in_files(
    in_files: InFileLike,
    var_names: Sequence[str] | None,
    threshold: Threshold | Sequence[Threshold] | None,
    standard_index: StandardIndex | None,
) -> dict[str, InFileDictionary]:
    if isinstance(in_files, dict):
        if var_names is not None:
            raise InvalidIcclimArgumentError(
                "`var_name` must be None when `in_files` is a dictionary."
                " The dictionary keys are used in place of `var_name`."
            )
        if isinstance(list(in_files.values())[0], dict):
            # case of in_files={tasmax: {"study": "tasmax.nc"}}
            return in_files
        else:
            # case of in_files={tasmax: "tasmax.nc"}
            return _build_in_file_dict(
                in_files=list(in_files.values()),
                standard_index=standard_index,
                threshold=threshold,
                var_names=list(in_files.keys()),
            )
    else:
        # case of in_files="tasmax.nc" and var_names="tasmax"
        return _build_in_file_dict(in_files, var_names, threshold, standard_index)


def _build_in_file_dict(
    in_files: InFileBaseType,
    var_names: Sequence[str],
    threshold: Threshold | Sequence[Threshold] | None,
    standard_index: StandardIndex | None,
):
    standard_var = (
        standard_index.input_variables[0] if standard_index is not None else None
    )
    input_dataset = read_dataset(
        in_files=in_files, standard_var=standard_var, var_name=var_names
    )
    var_names = guess_var_names(
        ds=input_dataset, standard_index=standard_index, var_names=var_names
    )
    if threshold is not None:
        if len(var_names) == 1:
            return {
                var_names[0]: {
                    "study": input_dataset[var_names[0]],
                    "thresholds": threshold,
                }
            }
        if not isinstance(threshold, Sequence):
            threshold = [threshold]
        if len(threshold) != len(var_names):
            # Allow 1 var with multiple thresholds or 1 threshold per var
            # but no other case
            raise InvalidIcclimArgumentError(
                "There must be as many thresholds as there are variables. There was"
                f" {len(threshold)} thresholds and {len(var_names)} variables."
            )
        return {
            var_name: {"study": input_dataset[var_name], "thresholds": threshold[i]}
            for i, var_name in enumerate(var_names)
        }
    else:
        return {var_name: {"study": input_dataset[var_name]} for var_name in var_names}


def _build_climate_var(
    climate_var_name: str,
    climate_var_data: InFileDictionary | InFileBaseType,
    ignore_Feb29th: bool,
    time_range: Sequence[str],
    standard_var: StandardVariable | None,
) -> ClimateVariable:
    if isinstance(climate_var_data, dict):
        study_ds = read_dataset(
            climate_var_data["study"], standard_var, climate_var_name
        )
        # todo: deprecate climate_var_data.get("per_var_name", None)
        #       for threshold_var_name
        climate_var_thresh = climate_var_data.get("thresholds", None)
    else:
        climate_var_data: InFileBaseType
        study_ds = read_dataset(climate_var_data, standard_var, climate_var_name)
        climate_var_thresh = None
    if standard_var is None:
        standard_var = guess_input_type(study_ds[climate_var_name])
    studied_data = build_studied_data(
        study_ds[climate_var_name],
        time_range,
        ignore_Feb29th,
        standard_var,
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
        global_metadata={
            "history": study_ds.attrs.get("history", None),
            "source": study_ds.attrs.get("source", None),
            "time_encoding": study_ds.time.encoding,
        },
        source_frequency=FrequencyRegistry.lookup(
            xarray.infer_freq(studied_data.time) or DEFAULT_INPUT_FREQUENCY
        ),
    )


def _build_threshold(
    climate_var_thresh: str | Threshold,
    original_data: DataArray,
    conversion_unit: str,
) -> Threshold:
    if isinstance(climate_var_thresh, str):
        climate_var_thresh: Threshold = build_threshold(climate_var_thresh)
    if (
        isinstance(climate_var_thresh, PercentileThreshold)
        and not climate_var_thresh.is_ready
    ):
        climate_var_thresh.prepare(original_data)
    climate_var_thresh.unit = conversion_unit
    return climate_var_thresh
