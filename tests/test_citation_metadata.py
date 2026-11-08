"""Checks on the ORCID identifiers of CITATION.cff and .zenodo.json."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
ORCID_PATTERN = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b")
FILES = ["CITATION.cff", ".zenodo.json"]


def _orcids(name: str) -> list[str]:
    text = (ROOT / name).read_text(encoding="utf-8")
    return ORCID_PATTERN.findall(text)


def _check_digit(base_digits: str) -> str:
    """Check digit of the first 15 digits of an ORCID (ISO 7064 mod 11-2)."""
    total = 0
    for digit in base_digits:
        total = (total + int(digit)) * 2
    result = (12 - total % 11) % 11
    return "X" if result == 10 else str(result)


def _has_valid_checksum(orcid: str) -> bool:
    digits = orcid.replace("-", "")
    return digits[-1] == _check_digit(digits[:-1])


@pytest.mark.parametrize("name", FILES)
def test_orcids_have_a_valid_checksum(name: str) -> None:
    orcids = _orcids(name)
    assert orcids, f"no ORCID found in {name}"
    invalid = [orcid for orcid in orcids if not _has_valid_checksum(orcid)]
    assert not invalid, f"invalid ORCID checksum in {name}: {invalid}"


def test_both_files_list_the_same_orcids() -> None:
    assert sorted(_orcids("CITATION.cff")) == sorted(_orcids(".zenodo.json"))


def test_the_checksum_detects_a_wrong_orcid() -> None:
    # The value that Zenodo rejected ("Invalid ORCID identifier") and the right one.
    assert not _has_valid_checksum("0000-0002-4018-4720")
    assert _has_valid_checksum("0000-0001-7743-9570")
    # The example ORCID of the ORCID documentation, whose check digit is X.
    assert _has_valid_checksum("0000-0002-1694-233X")
