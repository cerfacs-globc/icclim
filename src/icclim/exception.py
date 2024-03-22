"""Contain icclim-specific exceptions."""

from __future__ import annotations


class InvalidIcclimArgumentError(ValueError):
    """
    Exception raised for erroneous input arguments.

    Attributes
    ----------
    msg : str
        Error description.
    source_err : Exception or None, optional
        The source of the error, if any.

    Methods
    -------
    __str__()
        Returns a string representation of the error message.
    """

    def __init__(self, msg: str, source_err: Exception | None = None) -> None:
        self.msg = msg
        self.source = source_err

    def __str__(self) -> str:
        """Return a string representation of the error message."""
        return repr(self.msg)
