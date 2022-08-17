from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from xarray.core.dataarray import DataArray

from icclim.generic_indices.cf_var_metadata import CfVarMetadata
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_types import InFileBaseType, InFileType
from icclim.models.climate_index import ClimateIndex
from icclim.models.consolidated_metadata import GlobalMetadata
from icclim.models.constants import UNITS_ATTRIBUTE_KEY
from icclim.models.frequency import Frequency
from icclim.models.threshold import Threshold
from icclim.pre_processing.in_file_dictionary import InFileDictionary
from icclim.pre_processing.input_parsing import (
    build_reference_da,
    build_study_da,
    guess_input_type,
    guess_var_names,
    read_dataset,
)


@dataclass
class ClimateVariable:
    """Internal icclim structure. It groups together the input variable (study_da),
    its associated metadata (cf_meta) and the threshold it must be compared to.

    Attributes
    ----------
    name: str
        Name of the variable.
    cf_meta: CfVarMetadata
        CF metadata bounded to the standard variable used for this ClimateVariable.
    study_da: DataArray
        The variable studied.
    threshold: Threshold | None
        thresholds for this variable
    """

    name: str
    cf_meta: CfVarMetadata | None
    study_da: DataArray
    global_metadata: GlobalMetadata  # todo to be replaced by provenance processing
    threshold: Threshold | None = None

    def build_indicator_metadata(
        self, src_freq: Frequency, must_run_bootstrap: bool
    ) -> dict[str, str] | None:
        if self.cf_meta is None:
            return None
        if self.threshold:
            return {
                "threshold": self.threshold.get_metadata(src_freq, must_run_bootstrap),
            } | self.cf_meta.get_metadata()
        else:
            return self.cf_meta.get_metadata()


def build_climate_vars(
    climate_vars_dict: dict[str, InFileDictionary],
    ignore_Feb29th: bool,
    index: ClimateIndex,
    sampling_frequency: Frequency,
    threshold: Threshold | None,
    time_range: Sequence[str],
    base_period: Sequence[str] | None,
) -> list[ClimateVariable]:
    if must_add_reference_var(threshold, climate_vars_dict, base_period):
        added_var = build_reference_var_dict(
            base_period, climate_vars_dict, index, sampling_frequency
        )
        climate_vars_dict.update(added_var)
    return [
        _build_climate_var(
            k, v, ignore_Feb29th, index, sampling_frequency, threshold, time_range
        )
        for k, v in climate_vars_dict.items()
    ]


def build_reference_var_dict(
    base_period, in_files, index, sampling_frequency
) -> dict[str, InFileDictionary]:
    """This function add a secondary variable for indices such as anomaly that needs
    exactly two variables but where the second variable could just be a subset of the
    first one.
    """
    var_name = list(in_files.keys())[0]
    if isinstance(in_files, dict):
        study_ds = read_dataset(list(in_files.values())[0]["study"], index, var_name)
    else:
        study_ds = read_dataset(list(in_files.values())[0], index, var_name)
    v = build_reference_da(
        study_ds[var_name],
        base_period,
        only_leap_years=False,
        sampling_frequency=sampling_frequency,
        percentile_min_value=None,
    )
    return {var_name + "_reference": {"study": v}}


def must_add_reference_var(
    threshold,
    climate_vars_dict,
    base_period: Sequence[str] | None,
) -> bool:
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
    index: ClimateIndex,
    threshold: Threshold | Sequence[Threshold],
) -> dict[str, InFileDictionary]:
    if isinstance(in_files, dict):
        if var_names is not None:
            raise InvalidIcclimArgumentError(
                "`var_name` must be None when `in_files`"
                " is a dictionary."
                " The dictionary keys are used in place of"
                " `var_name`."
            )
        return in_files
    if not isinstance(in_files, dict):
        input_dataset = read_dataset(in_files, index, var_names)
        var_names = guess_var_names(input_dataset, index, var_names)
        if threshold:
            if not isinstance(threshold, Sequence):
                threshold = [threshold]
            if len(threshold) != len(var_names):
                raise InvalidIcclimArgumentError(
                    "There must be as many thresholds as there"
                    " are variables."
                    f" There was {len(threshold)} thresholds"
                    f" and {len(var_names)} variables."
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
    index: ClimateIndex,
    sampling_frequency: Frequency,
    threshold: Threshold | None,
    time_range: Sequence[str],
):
    if isinstance(climate_var_data, dict):
        study_ds = read_dataset(climate_var_data["study"], index, climate_var_name)
        # todo: deprecate climate_var_data.get("per_var_name", None)
        #       for threshold_var_name
        if climate_var_data.get("thresholds", None) is not None:
            climate_var_thresh = climate_var_data.get("thresholds", None)
        else:
            climate_var_thresh = threshold
    else:
        climate_var_data: InFileBaseType
        study_ds = read_dataset(climate_var_data, index, climate_var_name)
        climate_var_thresh = threshold
    cf_meta = guess_input_type(study_ds[climate_var_name])
    study_da = build_study_da(
        study_ds[climate_var_name],
        time_range,
        ignore_Feb29th,
        sampling_frequency,
        cf_meta,
    )
    if climate_var_thresh is not None:
        if isinstance(climate_var_thresh, str):
            climate_var_thresh: Threshold = Threshold(climate_var_thresh)
        if isinstance(climate_var_thresh.value, Callable):
            climate_var_thresh.value = climate_var_thresh.value(
                sampling_frequency=sampling_frequency, study_da=study_da
            )
        climate_var_thresh.unit = study_da.attrs[UNITS_ATTRIBUTE_KEY]
        climate_var_thresh.value = climate_var_thresh.value.chunk("auto")
    return ClimateVariable(
        name=climate_var_name,
        cf_meta=cf_meta,
        study_da=study_da,
        threshold=climate_var_thresh,
        global_metadata={
            "history": study_ds.attrs.get("history", None),
            "source": study_ds.attrs.get("source", None),
            "time_encoding": study_ds.time.encoding,
        },
    )
