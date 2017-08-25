"""Part of the service/backend module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators
# Python native libraries.
import io
import os
import sys
import pickle
# import cPickle

import crapi.misc.Utils as Utils


class PickleDB(object):
    pass

    def __init__(self, file):
        self.db = file
        self.lock = Utils.ReentrantRWLock()
        # Touch db file if it doesn't exist.
        if not os.path.exists(self.db):
            with io.open(self.db, 'wb'):
                pass

    def insert(self, explicit_lock=True):
        pass

    def update(self, explicit_lock=True):
        pass

    def delete(self, explicit_lock=True):
        pass
