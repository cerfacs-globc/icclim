from __future__ import annotations

import dataclasses

from icclim.models.registry import Registry


@dataclasses.dataclass
class LogicalLink:
    name: str


LOGICAL_OR = LogicalLink("or")
LOGICAL_AND = LogicalLink("and")
LOGICAL_LINK_REGISTRY = Registry[LogicalLink]([LOGICAL_OR, LOGICAL_AND])
