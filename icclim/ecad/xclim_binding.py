from collections.abc import Sequence

import xarray
import xclim
from icclim_exceptions import InvalidIcclimArgumentError

from icclim.generic_indices.generic_indicators import _get_couple_of_var, get_single_var
from icclim.generic_indices.standard_variable import StandardVariableRegistry
from icclim.models.climate_variable import ClimateVariable
from icclim.models.index_config import IndexConfig


class XCLIM_BINDING:
    class growing_season_length:
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

    @staticmethod
    def standardized_precipitation_index_3(config: IndexConfig) -> xarray.DataArray:
        study, ref = _get_couple_of_var(config.climate_variables, "SPI")
        return xclim.atmos.standardized_precipitation_index(
            pr=study, pr_cal=ref, freq="MS", window=3, dist="gamma", method="APP"
        )

    @staticmethod
    def standardized_precipitation_index_6(config: IndexConfig) -> xarray.DataArray:
        study, ref = _get_couple_of_var(config.climate_variables, "SPI")
        return xclim.atmos.standardized_precipitation_index(
            pr=study, pr_cal=ref, freq="MS", window=6, dist="gamma", method="APP"
        )

    @staticmethod
    def potential_evapotranspiration(config: IndexConfig) -> xarray.DataArray:
        return xclim.atmos.potential_evapotranspiration(
            tasmin=get_specific_var(config.climate_variables, "tasmin"),
            tasmax=get_specific_var(config.climate_variables, "tasmax"),
            hurs=get_specific_var(config.climate_variables, "hurs"),
            rsds=get_specific_var(config.climate_variables, "rsds"),
            rsus=get_specific_var(config.climate_variables, "rsus"),
            rlds=get_specific_var(config.climate_variables, "rlds"),
            rlus=get_specific_var(config.climate_variables, "rlus"),
            sfcwind=get_specific_var(config.climate_variables, "sfcwind"),
            method="FAO_PM98",
        )


def get_specific_var(
    climate_variables: Sequence[ClimateVariable], var_alias: str
) -> ClimateVariable:
    standardized_var = StandardVariableRegistry.lookup(var_alias)
    for climate_var in climate_variables:
        if climate_var.standard_var == standardized_var:
            return climate_var
    climate_variables_display = list(
        map(lambda x: x.standard_var.short_name, climate_variables)
    )
    raise InvalidIcclimArgumentError(
        f"Could not find {var_alias} or equivalent "
        f"in the available climate variables:"
        f" {climate_variables_display}."
    )
