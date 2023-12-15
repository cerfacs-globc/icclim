from __future__ import annotations


class InvalidIcclimArgumentError(ValueError):
    """Exceptions raised erroneous input arguments.

    Parameters
    ----------
        msg: str
            Error description.
        source_err: Exception | None
            The source of the error if any.
    """

    def __init__(self, msg: str, source_err: Exception = None):
        self.msg = msg
        self.source = source_err

    def __str__(self):
        return repr(self.msg)
