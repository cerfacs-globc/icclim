from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence
from warnings import warn

from xarray.core.dataarray import DataArray
from xclim.core.calendar import resample_doy

from icclim.generic_indices.cf_var_metadata import CfVarMetadata
from icclim.icclim_types import InFileBaseType, InFileType
from icclim.models.climate_index import ClimateIndex
from icclim.models.consolidated_metadata import GlobalMetadata
from icclim.models.constants import UNITS_ATTRIBUTE_KEY
from icclim.models.frequency import Frequency
from icclim.models.threshold import Threshold
from icclim.pre_processing.in_file_dictionary import InFileDictionary
from icclim.pre_processing.input_parsing import (
    build_study_da,
    guess_input_type,
    guess_var_names,
    read_dataset,
)


@dataclass
class ClimateVariable:
    """Internal icclim structure. It groups together the input variable (study_da),
    its associated metadata (cf_meta) and the threshold it must be compared to.

    Parameters
    ----------
    name: str
        Name of the variable.
    study_da: DataArray
        The variable studied.
    cf_meta: CfVarMetadata
        metadata
    threshold: Threshold | None
        thresholds for this variable
    """

    name: str
    cf_meta: CfVarMetadata
    study_da: DataArray
    global_metadata: GlobalMetadata  # todo to be replaced by provenance processing
    threshold: Threshold | None = None

    def build_indicator_metadata(self, src_freq: Frequency) -> dict[str, str]:
        return {
            "threshold": self.threshold.get_metadata(src_freq),
        } | self.cf_meta.get_metadata()


def read_climate_vars(
    ignore_Feb29th: bool,
    in_files: InFileType,
    index: ClimateIndex,
    sampling_frequency: Frequency,
    threshold: Threshold,
    time_range: Sequence[str],
    var_names: str | Sequence[str] | None,
) -> list[ClimateVariable]:
    iter_in_files = _to_dictionary(in_files, var_names, index, threshold).items()
    return [
        _build_climate_var(
            k,
            v,
            ignore_Feb29th,
            index,
            sampling_frequency,
            threshold,
            time_range,
        )
        for k, v in iter_in_files
    ]


def _to_dictionary(
    in_files: InFileType,
    var_names: Sequence[str],
    index: ClimateIndex,
    threshold: Threshold,
) -> dict[str, InFileDictionary]:
    if isinstance(in_files, dict):
        if var_names is not None:
            warn("`var_name` is ignored, `in_files` keys are used instead.")
        return in_files
    if not isinstance(in_files, dict):
        input_dataset = read_dataset(in_files, index, var_names)
        var_names = guess_var_names(input_dataset, index, var_names)
        return {
            var_name: {"study": input_dataset[var_name], "thresholds": threshold}
            for var_name in var_names
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
        cf_meta = guess_input_type(study_ds[climate_var_name])
        # todo: deprecate climate_var_data.get("per_var_name", None)
        #       for threshold_var_name
        if climate_var_data.get("thresholds", None) is not None:
            climate_var_thresh = climate_var_data.get("thresholds", None)
        else:
            climate_var_thresh = threshold
    else:
        climate_var_data: InFileBaseType
        study_ds = read_dataset(climate_var_data, index, climate_var_name)
        cf_meta = guess_input_type(study_ds[climate_var_name])
        climate_var_thresh = threshold
    study_da = build_study_da(
        study_ds[climate_var_name],
        time_range,
        ignore_Feb29th,
        sampling_frequency,
        cf_meta.units,
    )
    if climate_var_thresh is not None:
        if isinstance(climate_var_thresh, str):
            climate_var_thresh: Threshold = Threshold(climate_var_thresh)
        if isinstance(climate_var_thresh.value, Callable):
            climate_var_thresh.value = climate_var_thresh.value(
                sampling_frequency=sampling_frequency, study_da=study_da
            )
        climate_var_thresh.unit = study_da.attrs[UNITS_ATTRIBUTE_KEY]
        if climate_var_thresh.is_doy_per_threshold:
            climate_var_thresh.value = resample_doy(climate_var_thresh.value, study_da)
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
