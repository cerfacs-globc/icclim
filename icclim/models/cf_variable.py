from dataclasses import dataclass

from xarray import DataArray


@dataclass()
class CfVariable:
    """CfVariable groups together two xarray DataArray for the same variable.
    One represent the whole studied period. The other is only the in base period used by
    percentile based indices to compute percentiles.

    # todo: maybe we should supercharge xr.Dataset

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
    study_da: DataArray
    reference_da: DataArray = None
    # percentiles: PercentileDataArray = None
