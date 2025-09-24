"""Proxy icclim indicators that redirect to xclim indicators."""

from __future__ import annotations

from typing import TYPE_CHECKING

import xclim
from pandas import to_datetime

from icclim._core.generic.functions import get_single_var
from icclim._core.generic.indicator import Indicator
from icclim.exception import InvalidIcclimArgumentError
from icclim.frequency import FrequencyRegistry

if TYPE_CHECKING:
    import xarray

    from icclim._core.model.index_config import IndexConfig


class GrowingSeasonLength(Indicator):
    """
    Proxy for xclim.growing_season_length.

    icclim indicator that redirect to xclim `growing_season_length` indicator.
    """

    name = "growing_season_length"
    standard_name = xclim.atmos.growing_season_length.standard_name
    long_name = "ECAD Growing Season Length (Tmean > 5 degree_Celsius)"
    cell_methods = ""

    def __call__(self, config: IndexConfig) -> xarray.DataArray:
        """Compute the growing season length."""
        study, _ = get_single_var(config.climate_variables)
        return xclim.atmos.growing_season_length(
            tas=study,
            thresh="5 degree_Celsius",
            window=6,
            mid_date="07-01",
            freq=config.frequency.pandas_freq,
        )

    def preprocess(self, *args, **kwargs) -> list[xarray.DataArray]:
        """Not implemented as xclim indicator already handle pre/post processing."""
        raise NotImplementedError

    def postprocess(self, *args, **kwargs) -> xarray.DataArray:
        """Not implemented as xclim indicator already handle pre/post processing."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Check if the other object is a GrowingSeasonLength instance."""
        return isinstance(other, GrowingSeasonLength)


class StandardizedPrecipitationIndex3(Indicator):
    """
    Proxy for xclim.atmos.standardized_precipitation_index.

    icclim indicator that redirect to xclim `standardized_precipitation_index`
    indicator, with 3 MS frequency preconfigured.
    """

    name = "standardized_precipitation_index_3"
    standard_name = xclim.atmos.standardized_precipitation_index.standard_name
    long_name = "3-Month Standardized Precipitation Index (SPI3)"
    cell_methods = ""

    def __call__(self, config: IndexConfig) -> xarray.DataArray:
        """Compute the 3-Month Standardized Precipitation Index."""
        if config.frequency is not FrequencyRegistry.YEAR:  # year is default freq
            msg = "`slice_mode` cannot be configured when computing SPI3"
            raise InvalidIcclimArgumentError(msg)
        study, _ = get_single_var(config.climate_variables)
        # Parse with correct format
        study_cv = config.climate_variables[0]  # the ClimateVariable
        if study_cv.reference_period is None:
            raise ValueError("reference_period is missing for SPI index")
        start, end = to_datetime(study_cv.reference_period, format="%m-%d-%Y")
        # Convert back to YYYY-MM-DD
        cal_start, cal_end = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        return xclim.atmos.standardized_precipitation_index(
            pr=study,
            freq="MS",
            window=3,
            cal_start=cal_start,
            cal_end=cal_end,
            dist="gamma",
            method="APP",
            fitkwargs={"floc": 0},
        )

    def preprocess(self, *args, **kwargs) -> list[xarray.DataArray]:
        """Not implemented as xclim indicator already handle pre/post processing."""
        raise NotImplementedError

    def postprocess(self, *args, **kwargs) -> xarray.DataArray:
        """Not implemented as xclim indicator already handle pre/post processing."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Check if the other object is a StandardizedPrecipitationIndex3 instance."""
        return isinstance(other, StandardizedPrecipitationIndex3)


class StandardizedPrecipitationIndex6(Indicator):
    """
    Proxy for xclim.atmos.standardized_precipitation_index.

    icclim indicator that redirect to xclim `standardized_precipitation_index`
    indicator, with 6 MS configured.
    """

    name = "standardized_precipitation_index_6"
    standard_name = xclim.atmos.standardized_precipitation_index.standard_name
    long_name = "6-Month Standardized Precipitation Index (SPI6)"
    cell_methods = ""

    def __call__(self, config: IndexConfig) -> xarray.DataArray:
        """Compute the 6-Month Standardized Precipitation Index."""
        if config.frequency is not FrequencyRegistry.YEAR:  # year is default freq
            msg = "`slice_mode` cannot be configured when computing SPI6"
            raise InvalidIcclimArgumentError(msg)
        study, _ = get_single_var(config.climate_variables)
        # Parse with correct format
        study_cv = config.climate_variables[0]  # the ClimateVariable
        if study_cv.reference_period is None:
            raise ValueError("reference_period is missing for SPI index")
        start, end = to_datetime(study_cv.reference_period, format="%m-%d-%Y")
        # Convert back to YYYY-MM-DD
        cal_start, cal_end = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        return xclim.atmos.standardized_precipitation_index(
            pr=study,
            freq="MS",
            window=6,
            cal_start=cal_start,
            cal_end=cal_end,
            dist="gamma",
            method="APP",
            fitkwargs={"floc": 0},
        )

    def preprocess(self, *args, **kwargs) -> list[xarray.DataArray]:
        """Not implemented as xclim indicator already handle pre/post processing."""
        raise NotImplementedError

    def postprocess(self, *args, **kwargs) -> xarray.DataArray:
        """Not implemented as xclim indicator already handle pre/post processing."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Check if the other object is a StandardizedPrecipitationIndex6 instance."""
        return isinstance(other, StandardizedPrecipitationIndex6)
