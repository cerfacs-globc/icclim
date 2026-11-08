"""Checks on the ORCID identifiers of CITATION.cff and .zenodo.json."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
ORCID = r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
ORCID_PATTERN = re.compile(rf"\b{ORCID}\b")
# The value of every "orcid" field, whatever it contains: a malformed identifier is
# found by this pattern and rejected by the format test, instead of being ignored.
ORCID_FIELD_PATTERN = re.compile(r'"?orcid"?\s*:\s*"([^"]*)"', re.IGNORECASE)
URL_PREFIX = "https://orcid.org/"
# File name -> the form of the identifier in this file.
FILES = {"CITATION.cff": URL_PREFIX, ".zenodo.json": ""}


def _text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def _orcid_fields(name: str) -> list[str]:
    return ORCID_FIELD_PATTERN.findall(_text(name))


def _orcids(name: str) -> set[str]:
    """Every ORCID of the file: the identifiers in the text and in the fields."""
    found = set(ORCID_PATTERN.findall(_text(name)))
    for value in _orcid_fields(name):
        found.update(ORCID_PATTERN.findall(value))
    return found


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


@pytest.mark.parametrize(("name", "prefix"), FILES.items())
def test_orcid_fields_are_well_formed(name: str, prefix: str) -> None:
    values = _orcid_fields(name)
    assert values, f"no orcid field found in {name}"
    expected = re.compile(rf"{re.escape(prefix)}{ORCID}")
    malformed = [value for value in values if not expected.fullmatch(value)]
    assert not malformed, f"malformed orcid in {name}: {malformed}"


@pytest.mark.parametrize("name", FILES)
def test_orcids_have_a_valid_checksum(name: str) -> None:
    orcids = _orcids(name)
    assert orcids, f"no ORCID found in {name}"
    invalid = sorted(orcid for orcid in orcids if not _has_valid_checksum(orcid))
    assert not invalid, f"invalid ORCID checksum in {name}: {invalid}"


def test_both_files_list_the_same_orcids() -> None:
    assert _orcids("CITATION.cff") == _orcids(".zenodo.json")


def test_the_checksum_detects_a_wrong_orcid() -> None:
    # The value that Zenodo rejected ("Invalid ORCID identifier") and the right one.
    assert not _has_valid_checksum("0000-0002-4018-4720")
    assert _has_valid_checksum("0000-0001-7743-9570")
    # The example ORCID of the ORCID documentation, whose check digit is X.
    assert _has_valid_checksum("0000-0002-1694-233X")
