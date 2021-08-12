class IcclimError(Exception):
    """Base class for exceptions in this module."""

    pass


class InvalidIcclimArgumentError(IcclimError):
    """Exceptions raised erreonous input arguments.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, arg, msg):
        self.arg = arg
        self.msg = msg

    def __str__(self):
        return repr(self.arg + ": " + self.msg)


class MissingIcclimInputError(IcclimError):
    """Exceptions raised erreonous input arguments.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
