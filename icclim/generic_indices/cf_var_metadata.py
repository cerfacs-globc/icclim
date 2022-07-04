import dataclasses

from icclim.models.frequency import Frequency


@dataclasses.dataclass
class CfVarMetadata:
    # todo add __hash__ ? (and see if dataclass unsafe_hash=True would work)
    #      it would make it possible to do dataset[CfInputVar()] = da
    short_name: str
    standard_name: str
    long_name: str
    aliases: list[str]
    default_units: str
    frequency: Frequency = None  # todo Frequency ?
    units: str = None  # todo pint.Unit ?
    cell_method: str = None  # todo class to build it ?

    # todo add cell-method

    def to_dict(self):
        return self.__dict__  # todo safe ?
