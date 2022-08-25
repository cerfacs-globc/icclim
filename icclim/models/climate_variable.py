from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import xarray
from xarray.core.dataarray import DataArray

from icclim.generic_indices.cf_var_metadata import StandardVariable
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_types import InFileBaseType, InFileType
from icclim.models.climate_index import StandardIndex
from icclim.models.consolidated_metadata import GlobalMetadata
from icclim.models.constants import UNITS_ATTRIBUTE_KEY
from icclim.models.frequency import Frequency, FrequencyRegistry
from icclim.models.threshold import Threshold
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
    """Internal icclim structure. It groups together the input variable (studied_data),
    its associated metadata (standard_var) and the threshold it must be compared to.

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

    def build_indicator_metadata(
        self, src_freq: Frequency, must_run_bootstrap: bool, indicator_name: str
    ) -> dict[str, str] | None:
        metadata = {"threshold": {}}
        if self.standard_var is not None:
            metadata.update(self.standard_var.get_metadata())
        if self.threshold is not None:
            metadata.update(
                {
                    "threshold": self.threshold.get_metadata(
                        src_freq, must_run_bootstrap, indicator_name
                    )
                }
            )
        return metadata


def build_climate_vars(
    climate_vars_dict: dict[str, InFileDictionary],
    ignore_Feb29th: bool,
    threshold: Threshold | None,
    time_range: Sequence[str],
    base_period: Sequence[str] | None,
    standard_index: StandardIndex | None,
    indicator_name: str,
) -> list[ClimateVariable]:
    if must_add_reference_var(threshold, climate_vars_dict, base_period):
        added_var = build_reference_var_dict(
            base_period,
            climate_vars_dict,
            standard_index=standard_index,
        )
        climate_vars_dict.update(added_var)
    return [
        _build_climate_var(
            k,
            v,
            ignore_Feb29th,
            threshold,
            time_range,
            standard_index=standard_index,
            indicator_name=indicator_name,
        )
        for k, v in climate_vars_dict.items()
    ]


def build_reference_var_dict(
    reference_period: Sequence[str] | None,
    in_files,
    standard_index: StandardIndex,
) -> dict[str, InFileDictionary]:
    """This function add a secondary variable for indices such as anomaly that needs
    exactly two variables but where the second variable could just be a subset of the
    first one.
    """
    if reference_period is None:
        raise InvalidIcclimArgumentError(
            "Can't build a reference variable without a base_period_time_range"
        )
    var_name = list(in_files.keys())[0]
    if isinstance(in_files, dict):
        study_ds = read_dataset(
            list(in_files.values())[0]["study"],
            standard_index=standard_index,
            var_name=var_name,
        )
    else:
        study_ds = read_dataset(
            list(in_files.values())[0], standard_index=standard_index, var_name=var_name
        )
    v = build_reference_da(
        study_ds[var_name],
        reference_period,
        only_leap_years=False,
        percentile_min_value=None,
    )
    return {var_name + "_reference": {"study": v}}


def must_add_reference_var(
    threshold: Threshold | None,
    climate_vars_dict: dict[str, InFileDictionary],
    base_period: Sequence[str] | None,
) -> bool:
    """True if the a secondary variable must be added based on base_period.
    Example case: the anomaly of tx(60-2100) by tx(60-90).
    """
    if isinstance(climate_vars_dict, dict):
        t = list(climate_vars_dict.values())[0].get("threshold", None)
        return t is None and len(climate_vars_dict) == 1 and base_period is not None
    else:
        return (
            threshold is None
            and len(climate_vars_dict) == 1
            and base_period is not None
        )


def to_dictionary(
    in_files: InFileType,
    var_names: Sequence[str],
    threshold: Threshold | Sequence[Threshold] | None,
    standard_index: StandardIndex,
) -> dict[str, InFileDictionary]:
    if isinstance(in_files, dict):
        if var_names is None:
            return in_files
        else:
            raise InvalidIcclimArgumentError(
                "`var_name` must be None when `in_files` is a dictionary."
                " The dictionary keys are used in place of `var_name`."
            )
    else:
        input_dataset = read_dataset(in_files, standard_index, var_names)
        var_names = guess_var_names(
            input_dataset, standard_index=standard_index, var_names=var_names
        )
        if threshold:
            if not isinstance(threshold, Sequence):
                threshold = [threshold]
            if len(threshold) != len(var_names):
                raise InvalidIcclimArgumentError(
                    "There must be as many thresholds as there are variables. There was"
                    f" {len(threshold)} thresholds and {len(var_names)} variables."
                )
            return {
                var_name: {"study": input_dataset[var_name], "thresholds": threshold[i]}
                for i, var_name in enumerate(var_names)
            }
        else:
            return {
                var_name: {"study": input_dataset[var_name]} for var_name in var_names
            }


def _build_climate_var(
    climate_var_name: str,
    climate_var_data: InFileDictionary | InFileBaseType,
    ignore_Feb29th: bool,
    threshold: Threshold | None,
    time_range: Sequence[str],
    standard_index: StandardIndex | None,
    indicator_name: str,
) -> ClimateVariable:
    if isinstance(climate_var_data, dict):
        study_ds = read_dataset(
            climate_var_data["study"], standard_index, climate_var_name
        )
        # todo: deprecate climate_var_data.get("per_var_name", None)
        #       for threshold_var_name
        if climate_var_data.get("thresholds", None) is not None:
            climate_var_thresh = climate_var_data.get("thresholds", None)
        else:
            climate_var_thresh = threshold
    else:
        climate_var_data: InFileBaseType
        study_ds = read_dataset(climate_var_data, standard_index, climate_var_name)
        climate_var_thresh = threshold
    if standard_index is not None and len(standard_index.input_variables) == 1:
        standard_var = standard_index.input_variables[0]
    else:
        standard_var = guess_input_type(study_ds[climate_var_name])
    studied_data = build_studied_data(
        study_ds[climate_var_name],
        time_range,
        ignore_Feb29th,
        standard_var,
    )
    if climate_var_thresh is not None:
        climate_var_thresh = _build_threshold(
            indicator_name, climate_var_thresh, studied_data
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
    indicator_name: str,
    climate_var_thresh: str | Threshold,
    studied_data: DataArray,
) -> Threshold:
    if isinstance(climate_var_thresh, str):
        climate_var_thresh: Threshold = Threshold(climate_var_thresh)
    if isinstance(climate_var_thresh.value, Callable):
        climate_var_thresh.value = climate_var_thresh.value(
            studied_data=studied_data,
            indicator_name=indicator_name,
        )
    climate_var_thresh.unit = studied_data.attrs[UNITS_ATTRIBUTE_KEY]
    climate_var_thresh.value = climate_var_thresh.value.chunk("auto")
    return climate_var_thresh
