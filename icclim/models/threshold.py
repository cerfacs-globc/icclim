from __future__ import annotations

from xarray import DataArray
from xclim.core.utils import PercentileDataArray


class Threshold:
    value: DataArray

    def __init__(self, value: DataArray | float | list[float], units: str):
        if isinstance(value, DataArray):
            self.value = value
            self.value.attrs["units"] = units  # todo ok to override ?
        else:
            self.value = DataArray(
                data=value, coords={"threshold": value}, attrs={"units": units}
            )

    def to_dict(self):
        res = {}
        if self.value.size == 1:
            res.update(
                {
                    "standard_name": "threshold",
                    "value": self.value,
                }
            )
        elif isinstance(self.value, DataArray):
            if self.value.size < 10:
                display_value = self.value.values
            else:
                display_value = f"between {self.value.min()} and {self.value.max()}"
            res.update({"standard_name": "thresholds", "value": display_value})
        elif isinstance(self.value, PercentileDataArray):
            return res.update(
                {
                    "per_thresh": self.value.coords["percentiles"].values,
                    "per_window": self.value.attrs.get("window", None),
                    "per_period": self.value.attrs.get(
                        "climatology_bounds"
                    ),  # todo rename reference_epoch ?
                }
            )
        return res
