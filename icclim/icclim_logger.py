from __future__ import annotations

import logging
import time
from enum import Enum

from icclim.icclim_exceptions import InvalidIcclimArgumentError


class Verbosity(Enum):
    LOW = ("LOW", "INFO")
    HIGH = ("HIGH", "INFO")
    SILENT = ("SILENT", "ERROR")

    def __init__(self, icc_verbosity: str, log_level: str):
        self.icc_verbosity = icc_verbosity
        self.log_level = log_level

    @staticmethod
    def lookup(query: str) -> Verbosity:
        for v in Verbosity:
            if query.upper() == v.name:
                return v
        raise InvalidIcclimArgumentError(
            f"Unrecognized log verbosity {query}. "
            f"Use one of {[v.name for v in Verbosity]}"
        )


class IcclimLogger:
    """
    Singleton to display and control logs in icclim library.
    """

    __instance = None
    verbosity: Verbosity = Verbosity.LOW

    @staticmethod
    def get_instance(verbosity: Verbosity = Verbosity.LOW):
        if IcclimLogger.__instance is None:
            IcclimLogger(verbosity)
        return IcclimLogger.__instance

    def __init__(self, verbosity: Verbosity):
        if IcclimLogger.__instance is not None:
            raise Exception(
                "This class is a singleton! Use IcclimLogger.get_instance()."
            )
        else:
            IcclimLogger.__instance = self
            self.verbosity = verbosity
            logging.basicConfig(
                level=verbosity.log_level, format="%(asctime)s %(message)s"
            )

    def set_verbosity(self, verbosity: str | Verbosity):
        if isinstance(verbosity, str):
            verbosity = Verbosity.lookup(verbosity)
        self.verbosity = verbosity
        logging.root.setLevel(verbosity.log_level)

    def start_message(self):
        from icclim import __version__ as icclim_version

        # flake8: noqa
        time_now = time.asctime(time.gmtime())
        if self.verbosity == Verbosity.SILENT:
            return
        if self.verbosity == Verbosity.LOW:
            logging.info(f"--- icclim {icclim_version}")
            logging.info("--- BEGIN EXECUTION")
            return
        logging.info(
            "   ********************************************************************************************"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(f"   *          icclim                {icclim_version}   *")
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
        from icclim import __version__ as icclim_version

        # flake8: noqa
        time_now = time.asctime(time.gmtime())
        if self.verbosity == Verbosity.SILENT:
            return
        if self.verbosity == Verbosity.LOW:
            logging.info(f"--- icclim {icclim_version}")
            logging.info("--- CPU SECS = %-10.3f", time_cpu)
            logging.info("--- END EXECUTION")
            return
        logging.info(
            "   ********************************************************************************************"
        )
        logging.info(
            "   *                                                                                          *"
        )
        logging.info(f"   *          icclim                {icclim_version}   *")
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

    def info(*args):
        logging.info(args)

    def deprecation_warning(self, old: str, new: str = None) -> None:
        if new:
            logging.warning(
                f"DEPRECATION_WARNING: `{old}` is deprecated. Use `{new}` instead."
            )
        else:
            logging.warning(
                f"DEPRECATION_WARNING: `{old}` is deprecated and will be removed. Its value is ignored."
            )

    def callback(self, percent) -> None:
        logging.info(f"Processing: {percent}%")
