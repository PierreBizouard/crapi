"""Part of the ipc module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class PipeError(Exception):

    """A class for raising pipe errors."""

    """
        This class efficiently communicates to the user when a common or
        uncommon pipe situation has occured.
    """

    def __init__(self, message, attribute_key, attribute_value, *args):
        """Default initialization class method."""
        """
            Sets the required parameters when throwing a pipe error.
            Apart from the exception message (string), parameters are pairs of
            (attribute key, attribute value) aka pairs of (string, object)
            values.
        """
        self.message = message
        self.attribute_key = attribute_key
        self.attribute_value = attribute_value
        self.arglist = []
        for arg in args:
            self.arglist.append(arg)
        super(PipeError, self).__init__(
            message, attribute_key, attribute_value, *args
        )
