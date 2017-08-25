"""Part of the service module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class DaemonTimeoutError(Exception):

    """A class for raising daemon timeout errors."""

    """
        This class efficiently communicates to the user when a daemon timeout
        condition has occured.
    """

    def __init__(self, message, attribute_key, attribute_value, *args):
        """Default initialization class method."""
        """
            Sets the required parameters when throwing a daemon timeout error.
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
        super(DaemonTimeoutError, self).__init__(
            message, attribute_key, attribute_value, *args
        )
