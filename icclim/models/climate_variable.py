from __future__ import annotations

from dataclasses import dataclass

from generic_indices.cf_var_metadata import CfVarMetadata
from models.threshold import BoundedThresholds, Threshold
from xarray import DataArray

from icclim.models.frequency import Frequency


@dataclass()
class ClimateVariable:
    """Internal icclim structure.

    Parameters
    ----------
    name: str
        Name of the variable.
    study_da: DataArray
        The variable studied.
    cf_meta: CfVarMetadata
        metadata
    threshold: Threshold

    """

    name: str
    cf_meta: CfVarMetadata
    study_da: DataArray
    threshold: Threshold | None | BoundedThresholds = None

    def get_metadata(self, src_freq: Frequency) -> dict[str, str]:
        return {
            "threshold": self.threshold.get_metadata(src_freq)
        } | self.cf_meta.to_dict()
