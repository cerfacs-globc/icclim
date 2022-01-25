from enum import Enum
from typing import Any

from icclim_exceptions import InvalidIcclimArgumentError


class IcclimDaskConfiguration(Enum):
    MOUNTAIN = (100, True, 0, 8, 1)
    HILL = (50, True, 0, 8, 1)
    TALUS = (50, True, 0, 8, 1)

    def __init__(
        self,
        chunk_size,
        start_local_cluster,
        mem_limit,
        nb_threads,
        nb_process,
    ):
        self.chunk_size = chunk_size
        self.start_local_cluster = start_local_cluster
        self.nb_threads = nb_threads
        self.nb_process = nb_process

    @staticmethod
    def lookup(query: str) -> Any:
        for e in IcclimDaskConfiguration:
            if e.index_name.upper() == query.upper():
                return e
        raise InvalidIcclimArgumentError(
            f"Unknown configuration {query}."
            f"Use one of {[f for f in IcclimDaskConfiguration]}"
        )
