from enum import Enum


class QuantileInterpolation(Enum):
    LINEAR = "linear"
    MEDIAN_UNBIASED = "hyndman_fan"


def get_interpolation(s: str):
    for interpolation in QuantileInterpolation:
        if interpolation.value.upper() == s.upper():
            return interpolation
    valid_values = list(map(lambda x: x.value, QuantileInterpolation))
    raise NotImplementedError(
        f"Interpolation must be one of the following: {valid_values}"
    )
