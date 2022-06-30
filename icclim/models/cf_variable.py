from __future__ import annotations

from dataclasses import dataclass

from generic_indices.generic_indices import CfInputVar
from xarray import DataArray
from xclim.core.utils import PercentileDataArray


@dataclass()
class CfVariable:
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
    cf_meta: CfInputVar
    study_da: DataArray
    reference_da: DataArray | PercentileDataArray | None = None

    # def __hash__(self):
    #     return self.name.__hash__()
