from __future__ import annotations

from typing import Callable, Generic, Sequence, TypeVar

from icclim.icclim_exceptions import InvalidIcclimArgumentError

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(
        self,
        catalog: Sequence[T],
        lookup_method: Callable[[T], Sequence[str]] = lambda x: [x.name.upper()],
    ):
        self.item_class = catalog[0].__class__
        self.catalog = catalog
        self.lookup_method = lookup_method

    def lookup(self, query: T | str) -> T:
        if isinstance(query, self.item_class):
            return query
        for op in self.catalog:
            if query.upper() in self.lookup_method(op):
                return op
        raise InvalidIcclimArgumentError(
            f"Unknown {self.item_class.__qualname__}: '{query}'. "
            f"Use one of {list(map(self.lookup_method, self.catalog))}."
        )
