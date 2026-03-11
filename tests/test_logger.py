import logging
from unittest.mock import patch

import pytest

from icclim.logger import IcclimLogger, VerbosityRegistry


class TestIcclimLogger:
    @pytest.fixture(autouse=True)
    def _reset_logger(self):
        # Reset the singleton before and after each test
        IcclimLogger._IcclimLogger__instance = None
        yield
        IcclimLogger._IcclimLogger__instance = None

    def test_singleton_behavior(self):
        # When
        logger1 = IcclimLogger.get_instance(VerbosityRegistry.LOW)
        logger2 = IcclimLogger.get_instance(VerbosityRegistry.HIGH)

        # Then
        assert logger1 is logger2
        # First initialization dictates the initial verbosity if we don't call set_verbosity
        assert logger1.verbosity == VerbosityRegistry.LOW

    def test_init_raises_if_already_exists(self):
        # Given
        IcclimLogger.get_instance(VerbosityRegistry.LOW)

        # When / Then
        with pytest.raises(RuntimeError, match="This class is a singleton"):
            IcclimLogger(VerbosityRegistry.LOW)

    def test_set_verbosity(self):
        # Given
        logger = IcclimLogger.get_instance(VerbosityRegistry.SILENT)
        # We only check the logger attribute, not root level (which needs set_verbosity)
        assert logger.verbosity == VerbosityRegistry.SILENT

        # When
        logger.set_verbosity(VerbosityRegistry.HIGH)

        # Then
        assert logger.verbosity == VerbosityRegistry.HIGH
        assert logging.root.level == logging.INFO

    def test_set_verbosity_from_string(self):
        # Given
        logger = IcclimLogger.get_instance(VerbosityRegistry.LOW)

        # When
        logger.set_verbosity("SILENT")

        # Then
        assert logger.verbosity == VerbosityRegistry.SILENT

    @patch("icclim.logger._logger.info")
    def test_start_message_silent(self, mock_info):
        # Given
        logger = IcclimLogger.get_instance(VerbosityRegistry.SILENT)

        # When
        logger.start_message()

        # Then
        mock_info.assert_not_called()

    @patch("icclim.logger._logger.info")
    def test_start_message_low(self, mock_info):
        # Given
        logger = IcclimLogger.get_instance(VerbosityRegistry.LOW)

        # When
        logger.start_message()

        # Then
        assert mock_info.call_count == 2
        mock_info.assert_any_call("--- BEGIN EXECUTION")

    @patch("icclim.logger._logger.info")
    def test_ending_message_silent(self, mock_info):
        # Given
        logger = IcclimLogger.get_instance(VerbosityRegistry.SILENT)

        # When
        logger.ending_message(10.5)

        # Then
        mock_info.assert_not_called()

    @patch("icclim.logger._logger.info")
    def test_ending_message_low(self, mock_info):
        # Given
        logger = IcclimLogger.get_instance(VerbosityRegistry.LOW)

        # When
        logger.ending_message(10.5)

        # Then
        assert mock_info.call_count == 3
        mock_info.assert_any_call("--- END EXECUTION")
