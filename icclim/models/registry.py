from typing import Callable, Sequence, Any, Generic, TypeVar


T = TypeVar("T")
class Registry(Generic[T]):

    def __init__(self, data: Sequence[T]):
        self.data = data

    def lookup(self, query: Any)-> T: ...
