from __future__ import annotations

from dataclasses import dataclass

from generic_indices.cf_var_metadata import CfVarMetadata
from models.threshold import Threshold
from xarray import DataArray


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

    def to_dict(self):
        return {"threshold": self.threshold.to_dict()} | self.cf_meta.to_dict()
