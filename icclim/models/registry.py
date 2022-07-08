from typing import Any, Callable, Generic, Sequence, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self, data: Sequence[T]):
        self.data = data

    def lookup(self, query: Any) -> T:
        ...
