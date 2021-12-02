class IcclimError(Exception):
    """Base class for exceptions in this module."""

    pass


class InvalidIcclimArgumentError(IcclimError):
    """Exceptions raised erroneous input arguments.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class MissingIcclimInputError(IcclimError):
    """Exceptions raised erreonous input arguments.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class InvalidIcclimOutputError(IcclimError):
    """Exceptions raised erreonous input arguments.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
