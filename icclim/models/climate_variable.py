from __future__ import annotations

from dataclasses import dataclass

from xarray import DataArray

from generic_indices.cf_var_metadata import CfVarMetadata
from icclim.models.frequency import Frequency
from models.threshold import Threshold


@dataclass()
class ClimateVariable:
    """Internal icclim structure.

    Parameters
    ----------
    name: str
        Name of the variable.
    study_da: DataArray
        The variable studied.
    reference_da: DataArray
        The variable studied limited to the in base period.
    """

    name: str
    cf_meta: CfVarMetadata
    study_da: DataArray
    threshold: Threshold | None = None
    # todo add operand (or add it in Threshold)

    def to_dict(self, src_freq: Frequency):
        return {"threshold": self.threshold.to_dict(src_freq)} | self.cf_meta.to_dict()
