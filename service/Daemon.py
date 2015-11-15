# Copyright (C) 2014/15 - Iraklis Diakos (hdiakos@outlook.com)
# Pilavidis Kriton (kriton_pilavidis@outlook.com)
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the ASF 2.0 license.
#

"""Part of the service module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators
# Python native libraries.
#from abc import ABCMeta
#from abc import abstractmethod
import sys
import time

import crapi.service.WindowsDaemonFactory as WindowsDaemonFactory
import crapi.ipc.ClientPipe as ClientPipe
from crapi.service.DaemonTimeoutError import DaemonTimeoutError

# Python 3rd party libraries.
if sys.platform.startswith('win'):
    import win32serviceutil as w32scu
    import win32service as w32svc
    import pywintypes as WinT
    import winerror as werr


    # FIXME: Inherit WindowsDaemonTemplate and override abstract classes.
    #        Finalize created file by injecting overriden code to created
    #        template.
class Daemon(object):

    #__metaclass__ = ABCMeta

    def __init__(
        self, name='crapi', display_name='CRAPI: Common Range API',
        description='Dynamic runtime templating engine of Windows Services.',
        timeout=0
    ):
        dm_md, dm_py_cl = WindowsDaemonFactory.instantiate(
            name, display_name, description, timeout
        )
        self.name = name
        self.display_name = display_name
        self.description = description
        self.timeout = timeout
        self.module = dm_md
        self.python_class = dm_py_cl
        # FIXME: If the service is already installed reload its signature via
        #        the registry.
        # FIXME: If the service is deleted from sc.exe then add this file to
        #        folder (i.e. removed - check rt folder).
        try:
            svc_codes = w32scu.QueryServiceStatus(name)
            if svc_codes[1] == w32svc.SERVICE_STOPPED:
                w32scu.StartService(serviceName=self.name)
                self.__wait_for_svc_to_start()
        except WinT.error, e:
            if e.args[0] == werr.ERROR_SERVICE_DOES_NOT_EXIST:
                try:
                    w32scu.InstallService(
                        pythonClassString=self.python_class,
                        serviceName=self.name,
                        displayName=self.display_name,
                        description=self.description,
                        startType=w32svc.SERVICE_AUTO_START
                    )
                except:
                    raise
                w32scu.StartService(serviceName=self.name)
                self.__wait_for_svc_to_start()
            else:
                raise
        finally:
            self.pipe = ClientPipe.ClientPipe(name=self.name)

    # FIXME: Retries code.
    def __wait_for_svc_to_start(self, timeout=1, retries=30):
        svc_codes = w32scu.QueryServiceStatus(
            serviceName=self.name
        )
        while svc_codes[1] != w32svc.SERVICE_RUNNING:
            time.sleep(timeout)
            if retries < 0:
                raise DaemonTimeoutError('Failed')
            svc_codes = w32scu.QueryServiceStatus(
                serviceName=self.name
            )

    def send(self, msg, timeout=0):
        return self.pipe.write(payload=msg.encode('ascii'), timeout=timeout)

    def receive(self, timeout=0):
        return self.pipe.read(timeout=timeout)

    def close(self):
        self.pipe.close()
