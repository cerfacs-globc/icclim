# from __future__ import annotations
#
# import xclim.core.indicator
# from xclim.core.indicator import Indicator
#
# from icclim.ecad.ecad_functions import (
#     _compute_percentile_doy,
#     _compute_precip_percentile_over_period,
# )
# from icclim.icclim_exceptions import InvalidIcclimArgumentError
# from icclim.models.climate_index import StandardIndex
# from icclim.models.constants import PR, SFC_WIND, TAS, TAS_MAX, TAS_MIN
# from icclim.models.index_config import IndexConfig
# from icclim.models.registry import Registry
#
#
# class XclimIndexRegistry(Registry):
#     # TODO: NOT TESTED ! Finish this or delete it.
#     _item_class = StandardIndex
#     # Don't fill this enum, its values are built dynamically with
#     # ::build_xclim_indices
#
#     @staticmethod
#     def lookup(query: str, no_error=False) -> StandardIndex:
#         for e in XclimIndexRegistry.values():
#             if e.short_name.upper() == query.upper():
#                 return e
#         raise InvalidIcclimArgumentError(f"Unknown Xclim index {query}.")
#
#     @staticmethod
#     def list() -> list[str]:
#         return [
#             f"{i.group.built_value} | {i.short_name} | {i.definition}"
#             for i in XclimIndexRegistry.values()
#         ]
#
#     @classmethod
#     def build_xclim_indices(cls):
#         xclim_indicators = {}
#         xclim_indicators.update(xclim.seaIce.__dict__)
#         xclim_indicators.update(xclim.land.__dict__)
#         # xclim_indicators.update(xclim.ocean.__dict__)
#         xclim_indicators.update(xclim.atmos.__dict__)
#         xclim_indicators = list(map(lambda x: x, xclim_indicators.values()))
#         xclim_indicators = list(
#             filter(lambda x: isinstance(x, Indicator), xclim_indicators)
#         )
#         indices = {i.identifier: _build_climate_index(i) for i in xclim_indicators}
#         cls.__dict__.update(indices)
#
#
# def _build_climate_index(indicator: Indicator) -> StandardIndex:
#     def compute_fun_translated(config: IndexConfig):
#         kw = config.xclim_kwargs  # todo add xclim_kwargs to icclim::index
#         for param_name, param_value in indicator.parameters.items():
#             if "pr" == param_name:
#                 kw.update({"pr": config.pr.studied_data})
#             elif "tas" == param_name:
#                 kw.update({"tas": config.tas.studied_data})
#             elif "tasmax" == param_name:
#                 kw.update({"tasmax": config.tasmax.studied_data})
#             elif "tasmin" == param_name:
#                 kw.update({"tasmin": config.tasmin.studied_data})
#             elif "pr_per" == param_name:
#                 pr_per = _compute_precip_percentile_over_period(
#                     config.pr, config.interpolation, config.scalar_thresholds
#                 )
#                 kw.update({"pr_per": pr_per})
#             elif "tas_per" == param_name:
#                 tas_per, bootstrap = _compute_percentile_doy(
#                     config.tas,
#                     config.scalar_thresholds,
#                     config.window,
#                     config.interpolation,
#                     config.callback,
#                 )
#                 kw.update({"tas_per": tas_per})
#                 kw.update({"bootstrap": bootstrap})
#             elif "tasmax_per" == param_name:
#                 tasmax_per, bootstrap = _compute_percentile_doy(
#                     config.tasmax,
#                     config.scalar_thresholds,
#                     config.window,
#                     config.interpolation,
#                     config.callback,
#                 )
#                 kw.update({"tasmax_per": tasmax_per})
#                 kw.update({"bootstrap": bootstrap})
#             elif "tasmin_per" == param_name:
#                 tasmin_per, bootstrap = _compute_percentile_doy(
#                     config.tasmin,
#                     config.scalar_thresholds,
#                     config.window,
#                     config.interpolation,
#                     config.callback,
#                 )
#                 kw.update({"tasmin_per": tasmin_per})
#                 kw.update({"bootstrap": bootstrap})
#             elif "sfcWind" == param_name:
#                 kw.update({"sfcWind": config.sfcWind})
#             # else: do nothing
#             # TODO: add other variables
#             #       (uas, vas, sfcWind, tdps, huss, ps, delta_tas, pr_baseline...)
#             kw.update(**config.frequency.build_frequency_kwargs())
#         return indicator.compute(**kw)
#
#     return StandardIndex(
#         short_name=indicator.identifier,
#         compute=compute_fun_translated,
#         group=indicator.realm,
#         input_variables=_get_input_variables(indicator),
#         qualifiers=None,  # unused as we wont generate API from these indices
#         source=f"xclim {indicator.realm}",
#         definition=indicator.description,
#         output_var_name=indicator.identifier,
#     )
#
#
# def _get_input_variables(indicator: Indicator):
#     acc = []
#     for param_name in indicator.parameters.items():
#         if param_name in PR:
#             acc.append(PR)
#         elif param_name in TAS:
#             acc.append(TAS)
#         elif param_name in TAS_MAX:
#             acc.append(TAS_MAX)
#         elif param_name in TAS_MIN:
#             acc.append(TAS_MIN)
#         elif param_name in SFC_WIND:
#             acc.append(SFC_WIND)
#     # TODO: add other variables
#     #      (uas, vas, sfcWind, tdps, huss, ps, delta_tas, pr_baseline...)
#     return acc
