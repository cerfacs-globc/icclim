"""Logging utilities for icclim."""

from __future__ import annotations

import dataclasses
import logging
import time

from icclim._core.model.registry import Registry

_logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Verbosity:
    """Represent a verbosity level for icclim logging."""

    verbosity_level: str
    log_level: str


class VerbosityRegistry(Registry[Verbosity]):
    """Registry of available verbosity levels."""

    _item_class = Verbosity
    LOW = Verbosity("LOW", "INFO")
    HIGH = Verbosity("HIGH", "INFO")
    SILENT = Verbosity("SILENT", "ERROR")

    @staticmethod
    def get_item_aliases(item: Verbosity) -> list[str]:
        """Return the aliases for the given verbosity level."""
        return [item.verbosity_level.upper()]


class IcclimLogger:
    """
    Singleton to display and control logs in icclim library.
    """

    __instance = None
    verbosity: Verbosity = VerbosityRegistry.LOW

    @staticmethod
    def get_instance(verbosity: Verbosity = VerbosityRegistry.LOW) -> IcclimLogger:
        """Return the singleton instance of IcclimLogger."""
        if IcclimLogger.__instance is None:
            return IcclimLogger(verbosity)
        return IcclimLogger.__instance

    def __init__(self, verbosity: Verbosity) -> None:
        """Initialize the IcclimLogger singleton."""
        if IcclimLogger.__instance is not None:
            msg = "This class is a singleton! Use IcclimLogger.get_instance()."
            raise RuntimeError(msg)
        IcclimLogger.__instance = self
        self.verbosity = verbosity
        logging.basicConfig(level=verbosity.log_level, format="%(asctime)s %(message)s")

    def set_verbosity(self, verbosity: str | Verbosity) -> None:
        """Set the verbosity level of icclim logging."""
        if isinstance(verbosity, str):
            verbosity = VerbosityRegistry.lookup(verbosity)
        self.verbosity = verbosity
        logging.root.setLevel(verbosity.log_level)

    def start_message(self) -> None:
        """Log the start message for icclim computation."""
        from icclim import __version__ as icclim_version  # noqa: PLC0415

        time_now = time.asctime(time.gmtime())
        if self.verbosity == VerbosityRegistry.SILENT:
            return
        if self.verbosity == VerbosityRegistry.LOW:
            _logger.info("--- icclim %s", icclim_version)
            _logger.info("--- BEGIN EXECUTION")
            return
        _logger.info(
            "   ********************************************************************************************"
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info("   *          icclim                %s   *", icclim_version)
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   *          %s                                                    *",
            time_now,
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   *          BEGIN EXECUTION                                                                 *"
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   ********************************************************************************************"
        )

    def ending_message(self, time_cpu: float) -> None:
        """Log the ending message for icclim computation."""
        from icclim import __version__ as icclim_version  # noqa: PLC0415

        time_now = time.asctime(time.gmtime())
        if self.verbosity == VerbosityRegistry.SILENT:
            return
        if self.verbosity == VerbosityRegistry.LOW:
            _logger.info("--- icclim %s", icclim_version)
            _logger.info("--- CPU SECS = %-10.3f", time_cpu)
            _logger.info("--- END EXECUTION")
            return
        _logger.info(
            "   ********************************************************************************************"
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info("   *          icclim                %s   *", icclim_version)
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   *          %s                                                    *",
            time_now,
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   *          END EXECUTION                                                                   *"
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   *          CP SECS = %s                                                            *",
            time_cpu,
        )
        _logger.info(
            "   *                                                                                          *"
        )
        _logger.info(
            "   ********************************************************************************************"
        )

    def info(self, *args: object) -> None:
        """Log an info message."""
        _logger.info(args)

    def deprecation_warning(self, old: str, new: str | None = None) -> None:
        """Emit a deprecation warning."""
        if new:
            _logger.warning(
                "DEPRECATION_WARNING: `%s` is deprecated. Use `%s` instead.",
                old,
                new,
            )
        else:
            _logger.warning(
                "DEPRECATION_WARNING: `%s` is deprecated and will be removed. Its value is ignored.",
                old,
            )

    def callback(self, percent: float) -> None:
        """Log the current processing percentage."""
        _logger.info("Processing: %s%%", percent)
