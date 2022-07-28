from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from models.registry import Registry
from xclim.core.calendar import select_time

from icclim.models.climate_variable import ClimateVariable
from icclim.models.frequency import Frequency
from icclim.models.logical_link import LOGICAL_LINK_REGISTRY, LogicalLink
from icclim.models.operator import OPERATOR_REGISTRY, Operator
from icclim.utils import get_date_to_iso_format


@dataclass
class ExtremeMode:
    name: str


MIN = ExtremeMode("min")
MAX = ExtremeMode("max")
EXTREME_MODE_REGISTRY = Registry[ExtremeMode]([MIN, MAX], lambda e: e.name.upper())


@dataclass
class NbEventConfig:
    logical_operation: list[Operator]
    thresholds: list[float | str]
    link_logical_operations: LogicalLink | None = None
    data_arrays: list[ClimateVariable] | None = None


@dataclass
class UserIndexConfig:
    index_name: str
    calc_operation: str
    cf_vars: list[ClimateVariable]
    freq: Frequency
    date_event: bool
    is_percent: bool
    logical_operation: Operator | None = None
    thresh: float | int | str | list[float | int | str] | None = None
    link_logical_operations: LogicalLink | None = None
    extreme_mode: ExtremeMode | None = None
    window_width: int | None = None
    coef: float | None = None
    var_type: str | None = None
    nb_event_config: NbEventConfig | None = None
    save_percentile: bool = False

    def __init__(
        self,
        index_name: str,
        # Any should be CalcOperation but it causes circular import
        calc_operation: str | Any,
        freq: Frequency,
        cf_vars: list[ClimateVariable],
        logical_operation: str = None,
        thresh=None,
        link_logical_operations: str = None,
        extreme_mode: str = None,
        window_width=None,
        coef=None,
        date_event=None,
        var_type=None,
        is_percent=False,
        save_percentile=False,
        ref_time_range: list[str] = None,
    ) -> None:
        self.index_name = index_name
        self.calc_operation = calc_operation
        self.freq = freq
        if logical_operation is not None:
            self.logical_operation = OPERATOR_REGISTRY.lookup(logical_operation)
        self.thresh = thresh
        if extreme_mode is not None:
            self.extreme_mode = EXTREME_MODE_REGISTRY.lookup(extreme_mode)
        self.window_width = window_width
        self.coef = coef
        self.date_event = date_event
        self.var_type = var_type
        self.is_percent = is_percent
        if freq.indexer is not None:
            for cf_var in cf_vars:
                cf_var.study_da = select_time(cf_var.study_da, **freq.indexer)
                cf_var.reference_da = select_time(cf_var.reference_da, **freq.indexer)
        self.cf_vars = cf_vars
        if thresh is not None and logical_operation is not None:
            self.nb_event_config = get_nb_event_conf(
                logical_operation, link_logical_operations, thresh, cf_vars
            )
        self.save_percentile = save_percentile
        if (rtr := ref_time_range) is not None:
            rtr = [get_date_to_iso_format(date) for date in rtr]
            for cf_var in cf_vars:
                cf_var.reference_da = cf_var.study_da.sel(time=slice(rtr[0], rtr[1]))


def get_nb_event_conf(
    logical_operation: Sequence[str] | str,
    link_logical_operations: str | None,
    thresholds: Sequence[str | float] | float | str,
    climate_vars: list[ClimateVariable],
) -> NbEventConfig:
    if not isinstance(thresholds, (tuple, list)):
        threshold_list = [thresholds]
    else:
        threshold_list = thresholds
    if isinstance(logical_operation, (tuple, list)):
        logical_operations = list(map(OPERATOR_REGISTRY.lookup, logical_operation))
    else:
        logical_operations = [OPERATOR_REGISTRY.lookup(logical_operation)]
    if link_logical_operations is not None:
        link_logical_operation_list = LOGICAL_LINK_REGISTRY.lookup(
            link_logical_operations
        )
    else:
        link_logical_operation_list = None
    return NbEventConfig(
        logical_operation=logical_operations,
        link_logical_operations=link_logical_operation_list,
        thresholds=threshold_list,
        data_arrays=climate_vars,
    )
