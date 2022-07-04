from __future__ import annotations

from dataclasses import dataclass

from generic_indices.cf_var_metadata import CfVarMetadata
from models.threshold import Threshold
from xarray import DataArray


@dataclass()
class ClimateVariable:
    """CfVariable groups together two xarray DataArray for the same variable.
    One represent the whole studied period. The other is only the in-base period used by
    percentile based indices to compute percentiles.
    This is an internal icclim structure.

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
