""" Wrapper for clix-meta yaml file.
    This read the yaml and make its content accessible an instance of ClixMetaIndices.
    It also exposes some type hints of yaml content.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict

import yaml

CLIX_YAML_PATH = (
    Path(os.path.dirname(os.path.abspath(__file__))) / "index_definitions.yml"
)


class EtMetadata(TypedDict):
    short_name: str
    long_name: str
    definition: str
    comment: str


class OutputMetadata(TypedDict):
    var_name: str
    standard_name: str
    long_name: str
    units: str
    cell_methods: Dict


class ClixMetaIndex(TypedDict):
    reference: str
    period: Dict
    output: OutputMetadata
    input: Dict
    index_function: Dict
    ET: EtMetadata


class ClixMetaIndices:
    """
    Singleton to access content of clix-meta yaml file.
    """

    __instance: Any = None
    indices_record: Dict[str, ClixMetaIndex]

    @staticmethod
    def get_instance():
        if ClixMetaIndices.__instance is None:
            ClixMetaIndices.__instance = ClixMetaIndices()
        return ClixMetaIndices.__instance

    def __init__(self):
        if ClixMetaIndices.__instance is not None:
            raise Exception("This class is a singleton! Use Clix::get_instance.")
        else:
            ClixMetaIndices.__instance = self
            with open(CLIX_YAML_PATH, "r") as clix_meta_file:
                self.indices_record = yaml.safe_load(clix_meta_file)["indices"]

    def lookup(self, query: str) -> Optional[ClixMetaIndex]:
        for index in self.indices_record.keys():
            if index.upper() == query.upper():
                return self.indices_record[index]
        return None
