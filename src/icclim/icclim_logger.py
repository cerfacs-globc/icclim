from __future__ import annotations

import dataclasses
import logging
import time

from icclim.models.registry import Registry


@dataclasses.dataclass
class Verbosity:
    verbosity_level: str
    log_level: str


class VerbosityRegistry(Registry[Verbosity]):
    _item_class = Verbosity
    LOW = Verbosity("LOW", "INFO")
    HIGH = Verbosity("HIGH", "INFO")
    SILENT = Verbosity("SILENT", "ERROR")

    @staticmethod
    def get_item_aliases(item: Verbosity) -> list[str]:
        return [item.verbosity_level.upper()]


class IcclimLogger:
    """
    Singleton to display and control logs in icclim library.
    """

    __instance = None
    verbosity: Verbosity = VerbosityRegistry.LOW

    @staticmethod
    def get_instance(verbosity: Verbosity = VerbosityRegistry.LOW):
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
            verbosity = VerbosityRegistry.lookup(verbosity)
        self.verbosity = verbosity
        logging.root.setLevel(verbosity.log_level)

    def start_message(self):
        from icclim import __version__ as icclim_version

        # flake8: noqa
        time_now = time.asctime(time.gmtime())
        if self.verbosity == VerbosityRegistry.SILENT:
            return
        if self.verbosity == VerbosityRegistry.LOW:
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
        if self.verbosity == VerbosityRegistry.SILENT:
            return
        if self.verbosity == VerbosityRegistry.LOW:
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

    def info(self, *args):
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
