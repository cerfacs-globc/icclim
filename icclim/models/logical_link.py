from __future__ import annotations

import dataclasses

from icclim.models.registry import Registry


@dataclasses.dataclass
class LogicalLink:
    name: str


class LogicalLinkRegistry(Registry):
    _item_class = LogicalLink

    LOGICAL_OR = LogicalLink("or")
    # todo: "OR" should be equivalent to Threshold with a min_value e.g:
    #       Threshold(">= 30 doy_per", min_value="10 degC"). Maybe we should add a
    #       max_value though, so that we can do: `<= 30 doy_per OR <= 20 degC`
    LOGICAL_AND = LogicalLink("and")
