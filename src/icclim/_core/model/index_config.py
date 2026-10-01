"""
Contain the IndexConfig class.

It holds the compiled configuration for the computation of climate indices.
"""

from __future__ import annotations

import dataclasses
import json
from numbers import Real
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

    from icclim._core.climate_variable import ClimateVariable
    from icclim._core.model.indicator import Indicator
    from icclim._core.model.logical_link import LogicalLink
    from icclim._core.model.netcdf_version import NetcdfVersion
    from icclim._core.model.quantile_interpolation import QuantileInterpolation
    from icclim.frequency import Frequency


@dataclasses.dataclass(frozen=True)
class CompletenessPolicy:
    """Resolved missing-data policy used by the indicator execution path."""

    name: str
    method: str | None
    options: dict[str, Any] = dataclasses.field(default_factory=dict)
    reference: str | None = None
    version: str | None = None
    period: str | None = None
    minimum_valid_fraction: float | None = None

    @property
    def is_applied(self) -> bool:
        """Whether a missing-data mask must be applied."""
        return self.method is not None

    def metadata(self) -> dict[str, str]:
        """Return stable, NetCDF-serializable provenance attributes."""
        metadata = {
            "completeness_policy": self.name,
            "completeness_method": (
                f"xclim:{self.method}" if self.method is not None else "not_applied"
            ),
            "completeness_options": json.dumps(
                self.options,
                sort_keys=True,
                default=str,
            ),
        }
        if self.reference is not None:
            metadata["completeness_reference"] = self.reference
        if self.version is not None:
            metadata["completeness_policy_version"] = self.version
        if self.period is not None:
            metadata["completeness_period"] = self.period
        if self.minimum_valid_fraction is not None:
            metadata["completeness_minimum_valid_fraction"] = str(
                self.minimum_valid_fraction
            )
        return metadata


CompletenessLike = Literal["ecad", "strict", "none"] | float | None
"""Public completeness configuration accepted by :func:`icclim.index`."""


_ECAD_MINIMUM_VALID_DAYS = {
    "year": 350,
    "half_year": 175,
    "season": 85,
    "month": 25,
}
_ECAD_PERIOD_DAY_RANGES = {
    "month": (27, 31),
    "season": (85, 93),
    "half_year": (175, 184),
    "year": (350, 366),
}
_ECAD_REFERENCE = (
    "ECA&D Algorithm Theoretical Basis Document, version 11, section 5.1; "
    "https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf#page=21"
)


def resolve_legacy_completeness_policy(
    *,
    allow_missing_periods: bool,
    missing_method: str,
    missing_options: dict[str, Any] | None,
) -> CompletenessPolicy:
    """Resolve the 7.2 public boolean to the internal policy representation."""
    if allow_missing_periods or missing_method == "skip":
        return CompletenessPolicy(name="none", method=None)
    return CompletenessPolicy(
        name="strict" if missing_method == "any" else missing_method,
        method=missing_method,
        options=dict(missing_options or {}),
    )


def resolve_completeness_policy(
    *,
    completeness: CompletenessLike,
    allow_missing_periods: bool | None,
    frequency: Frequency,
    source_frequency: Frequency | str | None,
    missing_method: str,
    missing_options: dict[str, Any] | None,
) -> CompletenessPolicy:
    """Resolve public completeness settings to one execution policy.

    ``None`` selects the ECA&D profile. The legacy boolean remains authoritative
    when it is explicitly supplied, so existing callers can retain 7.2 behavior.
    """
    if allow_missing_periods is not None:
        if completeness is not None:
            msg = (
                "completeness and allow_missing_periods cannot be set together; "
                "use completeness='none' instead of allow_missing_periods=True."
            )
            raise ValueError(msg)
        return resolve_legacy_completeness_policy(
            allow_missing_periods=allow_missing_periods,
            missing_method=missing_method,
            missing_options=missing_options,
        )

    completeness = "ecad" if completeness is None else completeness
    if isinstance(completeness, Real) and not isinstance(completeness, bool):
        return _resolve_fraction_policy(float(completeness), frequency)
    if not isinstance(completeness, str):
        msg = "completeness must be 'ecad', 'strict', 'none', or a fraction in (0, 1]."
        raise TypeError(msg)

    return _resolve_named_policy(
        completeness.casefold(),
        frequency=frequency,
        source_frequency=source_frequency,
        missing_method=missing_method,
    )


def _resolve_fraction_policy(
    minimum_valid_fraction: float,
    frequency: Frequency,
) -> CompletenessPolicy:
    if not 0 < minimum_valid_fraction <= 1:
        msg = "A numeric completeness value must be greater than 0 and at most 1."
        raise ValueError(msg)
    if minimum_valid_fraction == 1:
        return CompletenessPolicy(name="strict", method="any")
    # xclim's percentage method masks when the missing fraction reaches its
    # tolerance, so move by one float to make the stated valid fraction inclusive.
    tolerance = float(np.nextafter(round(1 - minimum_valid_fraction, 15), 1))
    return CompletenessPolicy(
        name="minimum_valid_fraction",
        method="pct",
        options={"tolerance": tolerance},
        period=_classify_ecad_period(frequency),
        minimum_valid_fraction=minimum_valid_fraction,
    )


def _resolve_named_policy(
    profile: str,
    *,
    frequency: Frequency,
    source_frequency: Frequency | str | None,
    missing_method: str,
) -> CompletenessPolicy:
    if profile == "none":
        return CompletenessPolicy(name="none", method=None)
    if profile == "strict":
        return CompletenessPolicy(name="strict", method="any")
    if profile != "ecad":
        msg = "Unknown completeness profile. Use 'ecad', 'strict', or 'none'."
        raise ValueError(msg)
    if missing_method == "skip":
        return CompletenessPolicy(name="none", method=None)

    period = _classify_ecad_period(frequency)
    minimum_days = _ECAD_MINIMUM_VALID_DAYS.get(period)
    observations_per_day = _observations_per_day(source_frequency)
    if (
        minimum_days is None
        or observations_per_day is None
        or frequency.seasonal_bounds is not None
    ):
        # The ATBD only specifies daily inputs and four period classes. Preserve
        # strict masking for other frequencies and per-cell season definitions.
        return CompletenessPolicy(
            name="ecad",
            method="any",
            reference=_ECAD_REFERENCE,
            version="11",
            period=period or "strict_fallback",
        )
    return CompletenessPolicy(
        name="ecad",
        method="at_least_n",
        options={"n": minimum_days * observations_per_day},
        reference=_ECAD_REFERENCE,
        version="11",
        period=period,
    )


def _observations_per_day(source_frequency: Frequency | str | None) -> int | None:
    """Return a regular daily/sub-daily sampling multiplier when available."""
    if source_frequency is None:
        return None
    delta = getattr(source_frequency, "delta", None)
    if delta is None:
        return (
            1
            if isinstance(source_frequency, str) and source_frequency.upper() == "D"
            else None
        )
    unit, _ = np.datetime_data(delta.dtype)
    if unit not in {"D", "h", "m", "s", "ms", "us", "ns"}:
        return None
    ratio = float(np.timedelta64(1, "D") / delta)
    rounded_ratio = round(ratio)
    if ratio < 1 or not np.isclose(ratio, rounded_ratio):
        return None
    return rounded_ratio


def _classify_ecad_period(frequency: Frequency) -> str | None:
    """Map an output frequency to one of the period classes defined by ECA&D."""
    unit, _ = np.datetime_data(frequency.delta.dtype)
    amount = int(frequency.delta / np.timedelta64(1, unit))
    period = "year" if unit == "Y" and amount == 1 else None
    if unit == "M":
        period = {1: "month", 3: "season", 6: "half_year", 12: "year"}.get(amount)
    elif unit in {"D", "h", "m", "s", "ms", "us", "ns"}:
        days = float(frequency.delta / np.timedelta64(1, "D"))
        period = next(
            (
                name
                for name, (minimum, maximum) in _ECAD_PERIOD_DAY_RANGES.items()
                if minimum <= days <= maximum
            ),
            None,
        )
    return period


@dataclasses.dataclass
class IndexConfig:
    """
    Configuration class for defining climate index parameters.

    Parameters
    ----------
    frequency : Frequency
        The time frequency of the output. Built from ``slice_mode``.
    climate_variables : list[ClimateVariable]
        The list of climate variables used in the index calculation.
    min_spell_length : int | None
        The minimum spell length for the index calculation.
        None if the index is not a spell index.
    rolling_window_width : int | None
        The width of the rolling window for the index calculation.
        None if the index is not a rolling index.
    out_unit : str | None
        The output unit for the index calculation.
        Optional, used to override the default unit.
    callback : Callable[[int], None] | None
        The callback function for progress updates during the index calculation.
        Deprecated.
    netcdf_version : NetcdfVersion
        The version of the NetCDF file format to use for saving the index results.
        Default is NetcdfVersion.NETCDF4.
    save_thresholds : bool
        Flag indicating whether to save the threshold values used in the index
        calculation.
    interpolation : QuantileInterpolation
        The interpolation method to use for calculating quantiles/percentiles.
    is_compared_to_reference : bool
        Flag indicating whether the index is compared to a reference period.
    reference_period : tuple[str, str] | None
        The reference period for the index calculation.
    indicator_name : str
        The name of the index.
    logical_link : LogicalLink
        The logical link to use for combining multiple indices.
    coef : float | None
        The coefficient to apply to the index values.
    date_event : bool
        Flag indicating whether the index represents a date or an event.
    sampling_method : str
        The sampling method to use for the index calculation.
        In conjonction with the Frequency, it is used on specific indices such as the
        anomaly (a.k.a diff_of_means) to determine if the reference period and the
        studied period should be grouped by or resampled.
        It can be either 'group_by', 'resample', or
        'group_by_ref_and_resample_study'.
        'group_by' will group the data by the specified frequency, for example every
        data of every January together.
        'resample' will resample the data to the specified frequency, for example every
        days of each month independently together.
        'group_by_ref_and_resample_study' will group the reference data by the specified
        frequency and resample the study data to the same frequency.
        This last method allows for example to compare each January, independently, of
        the study period to every January of the reference period.
        This is typically used to compare the each month of the studied period
        to a normal (the reference) of many aggregated years.
    rename : str | None
        The new name for the output variable.
        Optional, used to override the default index name.
    indicator : Indicator
        The indicator to be computed.
    reference : str
        The reference value for the index calculation.
    run_index : str | None
        The index to use for the run length encoding.
        None if the index is not a spell index.
    allow_partial_seasons : bool | Literal["start", "end"]
        Flag indicating whether to allow partial seasons to be included in the
        index calculation.
        - True: Unmasks both the first and last periods.
        - False: Masks any incomplete periods (standard behavior).
        - "start": Unmasks only the first period.
        - "end": Unmasks only the last period.
        Default is False.
    completeness_policy : CompletenessPolicy
        Resolved missing-data policy. The public ``allow_missing_periods``
        compatibility parameter is translated to this representation before
        indicator execution.
    allow_partial_final_period : bool
        When True, strict missing-period masking is still applied, except for the
        final output period.
    warn_on_missing_periods : bool
        Emit available diagnostics about an irregular time coordinate or an
        already-eager completeness mask. Lazy inputs are not evaluated solely
        to emit a warning.
    """

    frequency: Frequency
    climate_variables: list[ClimateVariable]
    min_spell_length: int | None
    rolling_window_width: int | None
    out_unit: str | None
    callback: Callable[[int], None] | None
    netcdf_version: NetcdfVersion
    save_thresholds: bool
    interpolation: QuantileInterpolation
    is_compared_to_reference: bool
    reference_period: tuple[str, str] | None
    indicator_name: str
    logical_link: LogicalLink
    coef: float | None
    date_event: bool
    sampling_method: str
    rename: str | None
    indicator: Indicator
    reference: str
    run_index: str | None = None
    allow_partial_seasons: bool | Literal["start", "end"] = False
    completeness_policy: CompletenessPolicy = dataclasses.field(
        default_factory=lambda: CompletenessPolicy(name="strict", method="any")
    )
    allow_partial_final_period: bool = False
    warn_on_missing_periods: bool = False
