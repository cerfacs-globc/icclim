from __future__ import annotations

import xarray
import xclim

from icclim.generic_indices.generic_indicators import (
    Indicator,
    get_couple_of_var,
    get_single_var,
)
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import FrequencyRegistry
from icclim.models.index_config import IndexConfig


class XCLIM_BINDING:
    class GrowingSeasonLength(Indicator):
        """
        Fake icclim indicator that redirect to xclim `growing_season_length` indicator.
        """

        name = "growing_season_length"
        standard_name = xclim.atmos.growing_season_length.standard_name
        long_name = "ECAD Growing Season Length (Tmean > 5 degree_Celsius)"
        cell_methods = ""

        def __call__(self, config: IndexConfig) -> xarray.DataArray:
            study, threshold = get_single_var(config.climate_variables)
            return xclim.atmos.growing_season_length(
                tas=study,
                thresh="5 degree_Celsius",
                window=6,
                mid_date="07-01",
                freq=config.frequency.pandas_freq,
            )

        def preprocess(self, *args, **kwargs) -> list[xarray.DataArray]:
            """Not implemented as xclim indicator already handle pre/post processing"""
            raise NotImplementedError()

        def postprocess(self, *args, **kwargs) -> xarray.DataArray:
            """Not implemented as xclim indicator already handle pre/post processing"""
            raise NotImplementedError()

    class StandardizedPrecipitationIndex3(Indicator):
        """
        Fake icclim indicator that redirect to xclim `standardized_precipitation_index`
        indicator, with 3 MS configured.
        """

        name = "standardized_precipitation_index_3"
        standard_name = xclim.atmos.standardized_precipitation_index.standard_name
        long_name = "3-Month Standardized Precipitation Index (SPI3)"
        cell_methods = ""

        def __call__(self, config: IndexConfig) -> xarray.DataArray:
            if config.frequency is not FrequencyRegistry.YEAR:  # year is default freq
                raise InvalidIcclimArgumentError(
                    "`slice_mode` cannot be configured when computing SPI3"
                )
            study, ref = get_couple_of_var(config.climate_variables, "SPI")
            return xclim.atmos.standardized_precipitation_index(
                pr=study, pr_cal=ref, freq="MS", window=3, dist="gamma", method="APP"
            )

        def preprocess(self, *args, **kwargs) -> list[xarray.DataArray]:
            """Not implemented as xclim indicator already handle pre/post processing"""
            raise NotImplementedError()

        def postprocess(self, *args, **kwargs) -> xarray.DataArray:
            """Not implemented as xclim indicator already handle pre/post processing"""
            raise NotImplementedError()

    class StandardizedPrecipitationIndex6(Indicator):
        """
        Fake icclim indicator that redirect to xclim `standardized_precipitation_index`
        indicator, with 6 MS configured.
        """

        name = "standardized_precipitation_index_6"
        standard_name = xclim.atmos.standardized_precipitation_index.standard_name
        long_name = "6-Month Standardized Precipitation Index (SPI6)"
        cell_methods = ""

        def __call__(self, config: IndexConfig) -> xarray.DataArray:
            if config.frequency is not FrequencyRegistry.YEAR:  # year is default freq
                raise InvalidIcclimArgumentError(
                    "`slice_mode` cannot be configured when computing SPI6"
                )
            study, ref = get_couple_of_var(config.climate_variables, "SPI")
            return xclim.atmos.standardized_precipitation_index(
                pr=study, pr_cal=ref, freq="MS", window=6, dist="gamma", method="APP"
            )

        def preprocess(self, *args, **kwargs) -> list[xarray.DataArray]:
            """Not implemented as xclim indicator already handle pre/post processing"""
            raise NotImplementedError()

        def postprocess(self, *args, **kwargs) -> xarray.DataArray:
            """Not implemented as xclim indicator already handle pre/post processing"""
            raise NotImplementedError()
