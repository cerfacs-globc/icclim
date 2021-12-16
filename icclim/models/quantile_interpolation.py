from enum import Enum


class QuantileInterpolation(Enum):
    LINEAR = ("linear", 1, 1)
    MEDIAN_UNBIASED = ("hyndman_fan", 1.0 / 3, 1.0 / 3)

    def __init__(self, alias, alpha, beta):
        self.alias = alias
        self.alpha = alpha
        self.beta = beta

    @staticmethod
    def lookup(s: str):
        for interpolation in QuantileInterpolation:
            if interpolation.value.upper() == s.upper():
                return interpolation
        valid_values = list(map(lambda x: x.value, QuantileInterpolation))
        raise NotImplementedError(
            f"Interpolation must be one of the following: {valid_values}"
        )
