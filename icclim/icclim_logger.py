import logging
import os
import time
from enum import Enum
from typing import Union

import pkg_resources

from icclim.icclim_exceptions import InvalidIcclimArgumentError


class Verbosity(Enum):
    LOW = ("LOW", "INFO")
    HIGH = ("HIGH", "INFO")
    SILENT = ("SILENT", "ERROR")

    def __init__(self, icc_verbosity: str, log_level: str):
        self.icc_verbosity = icc_verbosity
        self.log_level = log_level

    @staticmethod
    def lookup(query: str):
        for v in Verbosity:
            if query.upper() == v.name:
                return v
        raise InvalidIcclimArgumentError(
            f"Unrecognized log verbosity {query}. "
            f"Use one of {[v.name for v in Verbosity]}"
        )


class IcclimLogger:
    __instance = None
    verbosity = Verbosity.LOW

    @staticmethod
    def get_instance(verbosity: Verbosity):
        if IcclimLogger.__instance is None:
            IcclimLogger(verbosity)
        return IcclimLogger.__instance

    def __init__(self, verbosity: Verbosity):
        if IcclimLogger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            IcclimLogger.__instance = self
            self.verbosity = verbosity
            os.environ["TZ"] = "GMT"
            time.tzset()
            self.timezone = time.tzname[0]
            self.icclim_version = pkg_resources.get_distribution("icclim").version
            logging.basicConfig(
                level=verbosity.log_level, format="%(asctime)s %(message)s"
            )

    def set_verbosity(self, verbosity: Union[str, Verbosity]):
        if isinstance(verbosity, str):
            verbosity = Verbosity.lookup(verbosity)
        self.verbosity = verbosity
        logging.root.setLevel(verbosity.log_level)

    def start_message(self):
        # flake8: noqa
        time_now = time.asctime(time.gmtime()) + " " + self.timezone
        if self.verbosity == Verbosity.SILENT:
            return
        if self.verbosity == Verbosity.LOW:
            logging.info(f"--- Icclim {self.icclim_version}")
            logging.info("--- BEGIN EXECUTION")
            return
        logging.info(
            "   ********************************************************************************************"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(f"   *          Icclim                {self.icclim_version}   *")
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            f"   *          {time_now}                                                    *"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            "   *          BEGIN EXECUTION                                                                 *"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            "   ********************************************************************************************"
        )

    def ending_message(self, time_cpu):
        # flake8: noqa
        time_now = time.asctime(time.gmtime()) + " " + self.timezone
        if self.verbosity == Verbosity.SILENT:
            return
        if self.verbosity == Verbosity.LOW:
            logging.info(f"--- Icclim {self.icclim_version}")
            logging.info("--- CPU SECS = %-10.3f", time_cpu)
            logging.info("--- END EXECUTION")
            return
        logging.info(
            "   ********************************************************************************************"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(f"   *          Icclim                {self.icclim_version}   *")
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            f"   *          {time_now}                                                    *"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            "   *          END EXECUTION                                                                   *"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            f"   *          CP SECS = {time_cpu}                                                            *"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(
            "   ********************************************************************************************"
        )

    def deprecation_warning(self, old: str, new: str):
        logging.warning(
            f"DEPRECATION_WARNING: `{old}` is deprecated. Use `{new}` instead."
        )
