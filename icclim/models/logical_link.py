from __future__ import annotations

import dataclasses

from icclim.models.registry import Registry


@dataclasses.dataclass
class LogicalLink:
    name: str


class LogicalLinkRegistry(Registry):
    _item_class = LogicalLink

    LOGICAL_OR = LogicalLink("or")
    LOGICAL_AND = LogicalLink("and")
