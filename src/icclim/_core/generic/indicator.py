"""Contain the GenericIndicator class."""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from copy import deepcopy
from functools import reduce
from typing import TYPE_CHECKING, Any

import numpy as np
import xarray as xr
from jinja2 import Environment
from xarray import DataArray
from xclim.core.calendar import select_time
from xclim.core.cfchecks import cfcheck_from_name
from xclim.core.missing import MISSING_METHODS
from xclim.core.units import convert_units_to, rate2amount
from xclim.core.units import units as ureg

try:
    from pint import (
        DefinitionSyntaxError,
        DimensionalityError,
        OffsetUnitCalculusError,
        UndefinedUnitError,
    )
except ImportError:
    pass


from icclim._core.climate_variable import must_run_bootstrap
from icclim._core.constants import (
    RESAMPLE_METHOD,
)
from icclim._core.generic.functions import check_freq
from icclim._core.generic.generic_templates import INDICATORS_TEMPLATES_EN
from icclim._core.model.indicator import Indicator
from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    import jinja2

    from icclim._core.climate_variable import ClimateVariable
    from icclim._core.model.index_config import IndexConfig
    from icclim.frequency import Frequency


# Hydro context for precipitation-like variables
context_hydro = ureg.Context("hydro")
context_hydro.add_transformation(
    "[mass] / [length] ** 2",
    "[length]",
    lambda ureg, x: x * ureg("1 mm") / ureg("1 kg / m^2"),
)
context_hydro.add_transformation(
    "[length]",
    "[mass] / [length] ** 2",
    lambda ureg, x: x * ureg("1 kg / m^2") / ureg("1 mm"),
)
context_hydro.add_transformation(
    "[mass] / [length] ** 2 / [time]",
    "[length] / [time]",
    lambda ureg, x: x * ureg("1 mm / s") / ureg("1 kg / m^2 / s"),
)
context_hydro.add_transformation(
    "[length] / [time]",
    "[mass] / [length] ** 2 / [time]",
    lambda ureg, x: x * ureg("1 kg / m^2 / s") / ureg("1 mm / s"),
)


jinja_env = Environment(autoescape=True)


class GenericIndicator(Indicator):
    """
    GenericIndicator are climate indicators wich are not specific to a particular domain.

    They can be computed from any climate variable and are combined with `Threshold` objects
    to create personalized indicators.

    Parameters
    ----------
    name: str
        The name of the indicator.
    process: Callable[..., DataArray]
        The function that processes the indicator.
    definition: str
        The definition of the indicator.
    check_vars: Callable[[list[ClimateVariable], GenericIndicator], None], optional
        A function that checks if the variables meet the indicator requirements.
        Defaults to None.
    sampling_methods: list[str], optional
        A list of sampling methods that can be used with the indicator.
        Defaults to None.
    missing: str, optional
        The method for handling missing values. Defaults to "any".
    missing_options: dict, optional
        Additional options for handling missing values. Defaults to None.
    qualifiers: tuple, optional
        Additional qualifiers for the indicator. Defaults to ().


    Attributes
    ----------
    missing: str
        The method for handling missing values.
    missing_options: dict | None
        Additional options for handling missing values.
    """  # noqa: E501

    missing: str
    missing_options: dict | None

    def __init__(
        self,
        name: str,
        process: Callable[..., DataArray],
        definition: str,
        check_vars: (
            Callable[[list[ClimateVariable], GenericIndicator], None] | None
        ) = None,
        sampling_methods: list[str] | None = None,
        missing: str = "any",
        missing_options: dict | None = None,
        qualifiers: tuple = (),
    ) -> None:
        """
        Initialize a GenericIndicator object.

        Parameters
        ----------
        name : str
            The name of the indicator.
        process : Callable[..., DataArray]
            The processing function of the indicator.
        definition : str
            A definition for the indicator.
        check_vars : Callable[[list[ClimateVariable], GenericIndicator], None] | None, optional
            A function that checks the variables used by the indicator, by default None.
        sampling_methods : list[str] | None, optional
            The sampling methods used by the indicator, by default None.
        missing : str, optional
            The method for handling missing values, by default "any".
        missing_options : Any, optional
            The options for handling missing values, by default None.
        qualifiers : tuple, optional
            The qualifiers for the indicator, by default ().

        Raises
        ------
        ValueError
            If `missing_options` is set with `missing` method being from context.

        Notes
        -----
        See the `GenericIndicatorRegistry` class for a list of available indicators.

        Examples
        --------
        >>> from icclim.generic_indices import GenericIndicator
        >>> def process(climate_vars, resample_freq):
        ...     out = climate_vars[0].studied_data + climate_vars[1].studied_data
        ...     out.resample(time=resample_freq).mean()
        ...     return out
        >>> def check_vars(climate_vars, indicator):
        ...     if len(climate_vars) != 2:
        ...         raise ValueError(
        ...             "This indicator requires exactly 2 climate variables."
        ...         )
        >>> indicator = GenericIndicator(
        ...     name="test",
        ...     process=process,
        ...     definition="This is a test indicator",
        ...     check_vars=check_vars,
        ...     sampling_methods=["daily"],
        ...     missing="skip",
        ...     missing_options=None,
        ...     qualifiers=(),
        ... )

        """  # noqa: E501
        super().__init__()
        self.missing_options = missing_options

        # assign missing method name; default is "any"
        self.missing = missing  # <-- make sure to assign this first

        # Assign the missing method (callable) directly
        self._missing = MISSING_METHODS[self.missing]
        if self.missing_options:
            missing_method.validate(**self.missing_options)
        en_indicator_templates = deepcopy(INDICATORS_TEMPLATES_EN[name])
        self.name = name
        self.process = process
        self.standard_name = en_indicator_templates["standard_name"]
        self.cell_methods = en_indicator_templates["cell_methods"]
        self.long_name = en_indicator_templates["long_name"]
        self.check_vars = check_vars
        self.definition = definition
        self.qualifiers = qualifiers
        self.sampling_methods = (
            sampling_methods if sampling_methods is not None else [RESAMPLE_METHOD]
        )

    def preprocess(
        self,
        climate_vars: list[ClimateVariable],
        jinja_scope: dict[str, Any],
        output_frequency: Frequency,
        src_freq: Frequency,
        output_unit: str | None,
        coef: float | None,
        sampling_method: str,
    ) -> list[ClimateVariable]:
        """
        Preprocesses the climate variables before computing the indicator.

        Parameters
        ----------
        climate_vars : list[ClimateVariable]
            The list of climate variables to be preprocessed.
        jinja_scope : dict[str, Any]
            The Jinja scope used for formatting the template.
        output_frequency : Frequency
            The desired frequency of the output.
        src_freq : Frequency
            The source frequency of the climate variables.
        output_unit : str | None
            The desired output unit of the indicator. If None, no unit conversion is
            performed.
        coef : float | None
            The coefficient to multiply the climate variable data with. If None,
            no multiplication is performed.
        sampling_method : str
            The sampling method used for some specific indicators.
            See `difference_of_means` for example.

        Returns
        -------
        list[ClimateVariable]
            The preprocessed climate variables.

        """
        self._check_for_invalid_setup(climate_vars, sampling_method)

        # >>> PATCHED: Convert thresholds to Kelvin if in Celsius
        for cv in climate_vars:
            if hasattr(cv, "threshold") and cv.threshold is not None:
                if cv.threshold.unit in ["C", "degC", "degree_Celsius"]:
                    # Make a copy, update internal fields
                    new_threshold = deepcopy(cv.threshold)
                    new_threshold._value = new_threshold.value + 273.15
                    new_threshold._unit = "K"
                    cv.threshold = new_threshold

        if output_unit is not None:
            if _is_amount_unit(output_unit):
                climate_vars = _convert_rates_to_amounts(
                    climate_vars=climate_vars,
                    output_unit=output_unit,
                )
            elif _is_a_diff_indicator(self) and output_unit != "%":
                # [gh:255] Indicators computing the difference between two
                # variables must first convert the units of input variables
                # to the expected output unit in order to avoid converting
                # the output of the difference.
                # This is because a difference of relative units is not equivalent
                # to a difference of absolute on scale units.
                # In other words: a 15 Kelvin difference *is* equivalent
                # to a 15 degC difference, but if we would convert the unit after
                # computing the difference, we could get -258.15 degC from the
                # 15 Kelvin.
                for climate_var in climate_vars:
                    climate_var.studied_data = convert_units_to(
                        climate_var.studied_data,
                        target=output_unit,
                    )
        if coef is not None:
            for climate_var in climate_vars:
                climate_var.studied_data = coef * climate_var.studied_data
        if output_frequency.indexer:
            for climate_var in climate_vars:
                climate_var.studied_data = select_time(
                    climate_var.studied_data,
                    **output_frequency.indexer,
                    drop=True,
                )
        _check_data(climate_vars, src_freq.pandas_freq)
        _check_cf(climate_vars)
        self._format_template(jinja_scope=jinja_scope)
        return climate_vars

    def postprocess(
        self,
        result: DataArray,
        climate_vars: list[ClimateVariable],
        output_freq: str,
        src_freq: str,
        indexer: dict,
        out_unit: str | None,
    ) -> DataArray:
        """
        Postprocesses the result of the indicator computation.

        Parameters
        ----------
        result : DataArray
            The result of the indicator computation.
        climate_vars : list[ClimateVariable]
            The list of climate variables used for the computation.
        output_freq : str
            The desired output frequency of the postprocessed result.
        src_freq : str
            The source frequency of the input data.
        indexer : dict
            The indexer used to subset the input data.
        out_unit : str | None
            The desired output unit of the postprocessed result.
            If None, no unit conversion is performed.

        Returns
        -------
        DataArray
            The postprocessed result.
        """
        """
        >>> PATCHED: Difference-aware postprocess
        Convert absolute temperatures to degC at the very end.
        Temperature differences (deltaT) remain in K (numerically identical to degC differences).
        Precipitation / amounts handled normally using hydro context.
        """

        if out_unit in ["C", "degC", "degree_Celsius"]:
            # >>> DIFF-AWARE: only convert absolute temps
            if not _is_a_diff_indicator(self):
                result.values = result.values - 273.15
                result.attrs["units"] = "degC"
            else:
                # Differences: keep in K, label as degC
                result.attrs["units"] = "degC"

        elif out_unit is not None and _is_amount_unit(out_unit):
            # Use Pint dimensionality + hydro context for precipitation-like units
            current_unit = result.attrs.get("units", None)
            if current_unit is not None:
                try:
                    q = 1 * ureg(current_unit)
                    if q.check("[mass] / [length] ** 2 / [time]") or q.check(
                        "[mass] / [length] ** 2"
                    ):
                        # Always use hydro context for rates and amounts
                        with context_hydro:
                            result = convert_units_to(result, out_unit, context="hydro")
                    else:
                        result = convert_units_to(result, out_unit)
                except Exception as e:
                    print(
                        f"_convert_rates_to_amounts: exception {e} for unit '{current_unit}', skipping"
                    )
            else:
                result = convert_units_to(result, out_unit)

        if self.missing != "skip" and indexer is not None:
            # reference variable is a subset of the studied variable,
            # so no need to check it.
            das = filter(lambda cv: not cv.is_reference, climate_vars)
            das = (cv.studied_data for cv in das)
            das = list(das)
            if "time" in result.dims:
                # If src_freq cannot be inferred by xclim, fall back to universal check_freq
                if src_freq is None:
                    try:
                        from icclim._core.generic.functions import check_freq

                        src_freq = check_freq(result, dim="time")
                    except Exception:
                        src_freq = "D"  # safe fallback: daily

                result = self._handle_missing_values(
                    in_data=das,
                    out_data=result,
                    resample_freq=output_freq,
                    src_freq=src_freq,
                    indexer=indexer,
                )

        for prop in self.templated_properties:
            result.attrs[prop] = getattr(self, prop)
        result.attrs["history"] = ""
        return result

    # >>> PATCHED helper: difference-aware flag
    def _is_a_diff_indicator(indicator: Indicator) -> bool:
        return "compute_diff" in indicator.qualifiers

    def __call__(self, config: IndexConfig) -> DataArray:
        """
        Compute the indicator based on the given configuration.

        Parameters
        ----------
        config : IndexConfig
            The configuration object containing the settings for computing the
            indicator.

        Returns
        -------
        DataArray
            The computed indicator as a DataArray.
        """
        src_freq = config.climate_variables[0].source_frequency
        base_jinja_scope = {
            "np": np,
            "enumerate": enumerate,
            "len": len,
            "output_freq": config.frequency,
            "source_freq": src_freq,
        }
        climate_vars_meta = _get_climate_vars_metadata(
            config.climate_variables,
            src_freq,
            base_jinja_scope,
            jinja_env,
        )
        jinja_scope: dict[str, Any] = {
            "min_spell_length": config.min_spell_length,
            "rolling_window_width": config.rolling_window_width,
            "climate_vars": climate_vars_meta,
            "is_compared_to_reference": config.is_compared_to_reference,
            "reference_period": config.reference_period,
        }
        jinja_scope.update(base_jinja_scope)
        climate_vars = self.preprocess(
            climate_vars=config.climate_variables,
            jinja_scope=jinja_scope,
            output_frequency=config.frequency,
            src_freq=src_freq,
            output_unit=config.out_unit,
            coef=config.coef,
            sampling_method=config.sampling_method,
        )
        result = self.process(
            climate_vars=climate_vars,
            resample_freq=config.frequency,
            min_spell_length=config.min_spell_length,
            rolling_window_width=config.rolling_window_width,
            group_by_freq=config.frequency.group_by_key,
            is_compared_to_reference=config.is_compared_to_reference,
            logical_link=config.logical_link,
            date_event=config.date_event,
            source_freq_delta=src_freq.delta,
            to_percent=config.out_unit == "%",
            sampling_method=config.sampling_method,
        )
        return self.postprocess(
            result,
            climate_vars=climate_vars,
            output_freq=config.frequency.pandas_freq,
            src_freq=src_freq.pandas_freq,
            indexer=config.frequency.indexer,
            out_unit=config.out_unit,
        )

    def __eq__(self, other: object) -> bool:
        """
        Check if two GenericIndicator objects are equal.

        Parameters
        ----------
        other : Any
            The object to compare with.

        Returns
        -------
        bool
            True if the two objects are equal, False otherwise.
        """
        return (
            isinstance(other, GenericIndicator)
            and self.long_name == other.long_name
            and self.standard_name == other.standard_name
            and self.process == other.process
        )

    def __str__(self) -> str:
        """
        Return the name of the indicator.

        Returns
        -------
        str
            The name of the indicator.
        """
        return self.name

    def _check_for_invalid_setup(
        self,
        climate_vars: list[ClimateVariable],
        sampling_method: str,
    ) -> None:
        if not _same_freq_for_all(climate_vars):
            msg = (
                "All variables must have the same time frequency (for example daily) to"
                " be compared with each others, but this was not the case."
            )
            raise InvalidIcclimArgumentError(msg)
        if sampling_method not in self.sampling_methods:
            msg = (
                f"{self.name} can only be computed with the following"
                f" sampling_method(s): {self.sampling_methods}"
            )
            raise InvalidIcclimArgumentError(msg)
        if self.check_vars is not None:
            # Run indicator specific check method
            self.check_vars(climate_vars, self)

    def _format_template(self, jinja_scope: dict) -> None:
        for templated_property in self.templated_properties:
            template = jinja_env.from_string(
                getattr(self, templated_property),
                globals=jinja_scope,
            )
            setattr(self, templated_property, template.render())

    def _handle_missing_values(
        self, in_data, out_data, resample_freq=None, src_freq=None, indexer=None
    ):
        """
        Handle missing values in climate index computations.

        Parameters
        ----------
        in_data : list[xr.DataArray]
            Input DataArrays with time coordinates.
        out_data : xr.DataArray
            Output DataArray from the index computation.
        resample_freq : str, optional
            Target resampling frequency (e.g. "M", "Y").
        src_freq : str, optional
            Source timestep frequency (e.g. "D").
        indexer : dict, optional
            Extra arguments used by some missing value methods.
        """
        import numpy as np
        from xarray import DataArray
        from xclim.core.missing import MISSING_METHODS

        missing_class = MISSING_METHODS[self.missing]  # Get the class
        missing_obj = missing_class()  # Instantiate with no args

        # We flag periods according to the missing method. Skip variables without a time coordinate.
        miss = (
            missing_obj(
                da, freq=resample_freq, src_timestep=src_freq, **(indexer or {})
            )
            for da in in_data
            if "time" in da.coords
        )

        # Reduce by logical OR across all input masks
        mask = reduce(np.logical_or, miss)

        # Reindex mask to match output if needed
        if isinstance(mask, DataArray) and mask.time.size < out_data.time.size:
            mask = mask.reindex(time=out_data.time, fill_value=True)

        return out_data.where(~mask)


def _same_freq_for_all(climate_vars: list[ClimateVariable]) -> bool:
    if len(climate_vars) == 1:
        return True
    freqs = [xr.infer_freq(a.studied_data.time) for a in climate_vars]
    return all(x == freqs[0] for x in freqs[1:])


def _get_climate_vars_metadata(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    jinja_scope: dict[str, Any],
    jinja_env: jinja2.Environment,
) -> list[dict[str, str]]:
    return [
        c_var.build_indicator_metadata(
            resample_freq,
            must_run_bootstrap(c_var.studied_data, c_var.threshold),
            jinja_scope,
            jinja_env,
        )
        for c_var in climate_vars
    ]


def _convert_rates_to_amounts(
    climate_vars: list[ClimateVariable], output_unit: str
) -> list[ClimateVariable]:
    """
    Convert rate-like climate variables to amount units using xclim's rate2amount.
    Handles both classic rates (e.g., mm/s) and precipitation (kg m-2 / time)
    using a dedicated Pint context.
    """
    for climate_var in climate_vars:
        # Get the current unit of the variable
        current_unit = climate_var.studied_data.attrs.get("units", None)
        if current_unit is None:
            continue

        # Skip conversion if already an amount
        if _is_amount_unit(current_unit):
            continue

        try:
            # Clean unit string for Pint parsing
            unit_clean = current_unit.replace(" ", "*").replace("-", "**")
            q = 1 * ureg(unit_clean)
            dims = q.dimensionality

            # Determine if this is a precipitation-like unit (mass/area or mass/area/time)
            is_precip = (
                dims == ureg("kg / m^2").dimensionality
                or dims == ureg("kg / m^2 / s").dimensionality
                or "kg/m2" in current_unit.replace(" ", "").lower()
            )

            if is_precip:
                # >>> Hydro context applied here
                print(
                    f"Converting {climate_var.name}: {current_unit} -> {output_unit} with hydro context"
                )
                with context_hydro:
                    da = rate2amount(climate_var.studied_data, out_units=output_unit)
            else:
                # Non-precipitation rates: normal conversion
                da = rate2amount(climate_var.studied_data, out_units=output_unit)

            # Update the variable with converted data
            climate_var.studied_data = da.astype("float64")

        except Exception as e:
            # Skip on error but report it
            print(
                f"_convert_rates_to_amounts: exception {e} for unit '{current_unit}', skipping"
            )
            continue

    return climate_vars


def _is_amount_unit(unit: str) -> bool:
    """
    Return True if `unit` is an amount unit (length-like), False otherwise.
    """
    unit = unit.strip()
    offset_units = ["K", "degC", "degree_Celsius", "C", "?C"]
    if any(u in unit for u in offset_units):
        return False
    try:
        # Fix for Pint parsing: replace spaces with * and '-' with '**'
        unit_clean = unit.replace(" ", "*").replace("-", "**")
        q = 1 * ureg(unit_clean)
        # Compare to the dimensionality of 1 meter
        return q.dimensionality == (1 * ureg("m")).dimensionality
    except Exception as e:
        print(f"_is_amount_unit: exception {e} for unit '{unit}', returning False")
        return False


def _check_cf(climate_vars: list[ClimateVariable]) -> None:
    """Compare metadata attributes to CF-Convention standards.

    Default cfchecks use the specifications in `xclim.core.utils.VARIABLES`,
    assuming the indicator's inputs are using the CMIP6/xclim variable names
    correctly.
    Variables absent from these default specs are silently ignored.

    When subclassing this method, use functions decorated using
    `xclim.core.options.cfcheck`.
    """
    for da in climate_vars:
        with contextlib.suppress(KeyError):
            # Silently ignore unknown variables.
            cfcheck_from_name(str(da.name), da.studied_data)


def _check_data(climate_vars: list, src_freq: str) -> None:
    if src_freq is None:
        return
    for climate_var in climate_vars:
        da = climate_var.studied_data
        if "time" in da.coords and da.time.ndim == 1 and len(da.time) > 3:
            inferred_freq = check_freq(da, dim="time", strict=True)
            if inferred_freq != src_freq:
                raise InvalidIcclimArgumentError(
                    f"[icclim] Frequency mismatch for variable '{climate_var.name}': "
                    f"expected '{src_freq}', inferred '{inferred_freq}'"
                )


def _is_a_diff_indicator(indicator: Indicator) -> bool:
    return "compute_diff" in indicator.qualifiers
