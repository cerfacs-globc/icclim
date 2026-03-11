from datetime import datetime, timezone

import pytest

from icclim._core.utils import read_date
from icclim.exception import InvalidIcclimArgumentError


class TestReadDate:
    def test_read_date_from_datetime(self):
        # Given
        dt = datetime(2000, 1, 1, tzinfo=timezone.utc)

        # When
        result = read_date(dt)

        # Then
        assert result == dt

    @pytest.mark.parametrize(
        ("in_date", "expected_year", "expected_month", "expected_day"),
        [
            ("2000-01-01", 2000, 1, 1),
            ("1994-12-02", 1994, 12, 2),
            (
                "2 december",
                datetime.now(timezone.utc).year,
                12,
                2,
            ),  # dateparser uses current year if missing
        ],
    )
    def test_read_date_from_string(
        self, in_date, expected_year, expected_month, expected_day
    ):
        # When
        result = read_date(in_date)

        # Then
        assert result.year == expected_year
        assert result.month == expected_month
        assert result.day == expected_day

    def test_read_date_invalid_string(self):
        # When / Then
        with pytest.raises(
            InvalidIcclimArgumentError, match="does not have a valid format"
        ):
            read_date("not a real date string")
