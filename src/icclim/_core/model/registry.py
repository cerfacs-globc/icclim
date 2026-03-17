"""Contain the Registry class, a fancy enum replacement."""

from __future__ import annotations

from abc import ABC
from copy import deepcopy
from typing import Any, Generic, TypeVar, cast

from icclim.exception import InvalidIcclimArgumentError

T = TypeVar("T")


class Registry(ABC, Generic[T]):
    """
    Registry classes acts as fancy enums.

    It allows to easily store and find constants of similar type.
    Registries are namespaces, so there is no need to instantiate it or any of
    its subclasses, every item is a class attribute.

    Notes
    -----
    Registries are not meant to store large collections, they are just fancy lookup
    tables for items with aliases and no case sensitivity.
    """

    _item_class: type  # runtime type for the generic `T`

    @classmethod
    def lookup(cls: type[Registry], query: T | str) -> T:
        """
        Look up an item in the registry.

        Parameters
        ----------
        query : T or str
            The item to look up. It can be either an instance of the item class or a
            string.

        Returns
        -------
        T
            The found item.

        Raises
        ------
        InvalidIcclimArgumentError
            If the item is not found in the registry.

        Notes
        -----
        This method performs a case-insensitive lookup.
        It first checks if the query is an instance of the item class, and if so,
        returns a deep copy of the query.
        """
        if isinstance(query, cls._item_class):
            return cast("T", deepcopy(query))
        if isinstance(query, str):
            q = query.upper()
            for key, item in cls.catalog().items():
                if q == key.upper() or q in cls.get_item_aliases(item):
                    return cast("T", deepcopy(item))
        msg = (
            f"Unknown {cls._item_class.__qualname__}: '{query}'. "
            f"Use one of {cls.every_aliases()}."
        )
        raise InvalidIcclimArgumentError(msg)

    @classmethod
    def lookup_no_error(cls: type[Registry], query: T | str) -> T | None:
        """
        Also look up an item in the registry, but return None if not found.

        Parameters
        ----------
        query : T or str
            The item to look up. It can be either an instance of the item class or a
            string.

        Returns
        -------
        T or None
            The found item, or None if not found.

        """
        try:
            return cls.lookup(query)
        except InvalidIcclimArgumentError:
            return None

    @classmethod
    def every_aliases(cls: type[Registry]) -> list[list[str]]:
        """
        Return a list of all aliases for items in the registry.

        Returns
        -------
        list[T]
            A list of all aliases for items in the registry.

        """
        return list(map(cls.get_item_aliases, list(cls.catalog().values())))

    @staticmethod
    def get_item_aliases(item: Any) -> list[str]:  # noqa: ANN401
        """
        Get the aliases for the given item.

        Parameters
        ----------
        item : Any
            The item to get aliases for.

        Returns
        -------
        list[str]
            A list of aliases for the item.

        Notes
        -----
        Should be overridden in subclasses.
        """
        return [item.name.upper()]

    @classmethod
    def catalog(cls: type[Registry]) -> dict[str, T]:
        """
        Return a dictionary of all items in the registry.

        Returns
        -------
        dict[str, T]
            A dictionary containing all items in the registry, where the keys are the
            item names and the values are the item instances.

        """
        return {
            k: cast("T", v)
            for k, v in cls.__dict__.items()
            if isinstance(v, cls._item_class)
        }

    @classmethod
    def values(cls: type[Registry]) -> list[T]:
        """
        Return a list of all items in the registry.

        Returns
        -------
        list[T]
            A list containing all items in the registry.

        """
        return [
            cast("T", v) for v in cls.__dict__.values() if isinstance(v, cls._item_class)
        ]
