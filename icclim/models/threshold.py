from __future__ import annotations

from xarray import DataArray
from xclim.core.utils import PercentileDataArray


class Threshold:
    value: DataArray

    @property
    def units(self) -> str:
        return self.value.attrs["units"]

    def __init__(self, value: DataArray | float | list[float], units: str):
        if isinstance(value, DataArray):
            self.value = value
            self.value.attrs["units"] = units  # todo ok to override units ?
        else:
            self.value = DataArray(
                data=value, coords={"threshold": value}, attrs={"units": units}
            )

    def to_dict(self):
        if self.value.size == 1:
            return {
                "standard_name": f"{self.value.values[()]}{self.units}",
                "value": f"{self.value.values[()]}{self.units}",
            }
        elif isinstance(self.value, DataArray):
            if self.value.size < 10:
                display_value = f"{self.value.values}{self.units}"
            else:
                display_value = f"between {self.value.min()}{self.units}" \
                                f" and {self.value.max()}{self.units}"
            return {"standard_name": "thresholds", "value": display_value}
        elif isinstance(self.value, PercentileDataArray):
            return {
                "per_thresh": self.value.coords["percentiles"].values,
                "per_window": self.value.attrs.get("window", None),
                "per_period": self.value.attrs.get(
                    "climatology_bounds"  # todo rename reference_epoch ?
                ),
            }
