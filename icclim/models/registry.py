from __future__ import annotations

from abc import ABC
from copy import deepcopy
from typing import Generic, TypeVar

from icclim.icclim_exceptions import InvalidIcclimArgumentError

T = TypeVar("T")


class Registry(Generic[T], ABC):
    """This class is a fancy enum to easily store and find constant items of
    similar type.
    It acts as a namespace so there is no need to instantiate it or any of
    its subclasses.

    Notes
    -----
    Registries are not meant to store large collections, they are just fancy lookup
    tables for items with aliases and no case sensitivity.
    """

    _item_class: type  # runtime type for the generic `T`

    @classmethod
    def lookup(cls, query: T | str, no_error: bool = False) -> T:
        if isinstance(query, cls._item_class):
            return query
        if isinstance(query, str):
            q = query.upper()
            for key, item in cls.catalog().items():
                if q == key.upper() or q in cls.get_item_aliases(item):
                    return deepcopy(item)
        if no_error:
            return None
        raise InvalidIcclimArgumentError(
            f"Unknown {cls._item_class.__qualname__}: '{query}'. "
            f"Use one of {cls.every_aliases()}."
        )

    @classmethod
    def every_aliases(cls) -> list[T]:
        return list(map(cls.get_item_aliases, list(cls.catalog().values())))

    @staticmethod
    def get_item_aliases(item: T) -> list[str]:
        """Should be overridden."""
        return [item.name.upper()]

    @classmethod
    def catalog(cls) -> dict[str, T]:
        return {k: v for k, v in cls.__dict__.items() if isinstance(v, cls._item_class)}

    @classmethod
    def values(cls) -> list[T]:
        return [v for k, v in cls.__dict__.items() if isinstance(v, cls._item_class)]
