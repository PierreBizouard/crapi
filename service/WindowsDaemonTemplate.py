# Copyright (C) 2014/15 - Iraklis Diakos (hdiakos@outlook.com)
# Pilavidis Kriton (kriton_pilavidis@outlook.com)
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the ASF 2.0 license.
#

"""Part of the service module."""

# NOTE: unicode_literals causes problems when using instantiation with 'type'
# so use str which is a no-op in Python 3.x and converts arguments properly
# in Python 2.x
# TODO: This is a nested daemon factory class. Maybe we can enhance it?
#       This is also known as CRTP: Curiously recurring template pattern.
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators
# Python native libraries.
import sys

import crapi.ipc.ServerPipe as ServerPipe

# Python 3rd party libraries.
if sys.platform.startswith('win'):
    import servicemanager as scm
    import win32service as w32svc
    import win32serviceutil as w32scu
    #FIXME: UAC elevation?
#    import win32con as w32con
#    import win32com.shell.shell as w32sh_sh
#    import win32com.shell.shellcon as w32shcon
    import win32event as w32ev


class WindowsDaemonTemplate(object, w32scu.ServiceFramework):

    """A class that enables implementation of Windows services."""

    _svc_name_ = 'crapi'
    _svc_display_name_ = 'CRAPI: Common Range API'
    _svc_description_ = 'Dynamic runtime templating engine of Windows Services.'
    _svc_timeout_ = 0
    _svc_package_ = str(sys.modules[__name__]) + '.' + __name__

    def __init__(self, args):

        self.name = self._svc_name_
        self.display_name = self._svc_display_name_
        self.description = self._svc_description_

        w32scu.ServiceFramework.__init__(self, args)
        self.__hStop = w32ev.CreateEvent(None, False, False, None)
        self.__hShutdown = w32ev.CreateEvent(None, False, False, None)
        self.pipe = ServerPipe.ServerPipe(name=self.name)
        self.stream = self.pipe._getOverlappedStruct()
        if self._svc_timeout_ == 0:
            self.__timeout = w32ev.INFINITE
        else:
            self.__timeout = self._svc_timeout_
        self.__event = w32ev.QS_ALLEVENTS

    def SvcDoRun(self):
        self.start()

    def SvcStop(self):
        self.stop()

    def SvcShutdown(self):
        self.shutdown()

    #TODO: Add linux service entry points!

    def _start(self):
        scm.LogInfoMsg(
            self.display_name + ": Starting service..."
        )
        self.ReportServiceStatus(w32svc.SERVICE_RUNNING)
        self._run()

    def _stop(self):
        scm.LogInfoMsg(
            self.display_name + ": Stopping service..."
        )
        self.ReportServiceStatus(w32svc.SERVICE_STOP_PENDING)
        self.pipe.close()
        self.pipe.shutdown()
        w32ev.SetEvent(self.__hStop)

    def _shutdown(self):
        scm.LogInfoMsg(
            self.display_name + ": Shutting down service..."
        )
        self.ReportServiceStatus(w32svc.SERVICE_CONTROL_PRESHUTDOWN)
        self.pipe.close()
        self.pipe.shutdown()
        w32ev.SetEvent(self.__hShutdown)

    def _run(self):

        self.__hEvents = self.__hStop, self.__hShutdown, self.stream.hEvent
        #FIXME: Add pre-initialization code (like change pipe type etc)

        while True:

            scm.LogInfoMsg(
                self.display_name + ": Connecting..."
            )
            self.pipe.connect()
            scm.LogInfoMsg(
                self.display_name + ": Connected!"
            )
            w32ev.SetEvent(self.stream.hEvent)
            rc = w32ev.MsgWaitForMultipleObjects(
                self.__hEvents,
                False,
                self.__timeout,
                self.__event
            )

            if rc == w32ev.WAIT_OBJECT_0:
                scm.LogInfoMsg(
                    self.display_name + ": Received stop event..."
                )
                break
            elif rc == w32ev.WAIT_OBJECT_0+1:
                scm.LogInfoMsg(
                    self.display_name + ": Received shutdown event..."
                )
            elif rc == w32ev.WAIT_OBJECT_0+2:
                scm.LogInfoMsg(
                    self.display_name + ": Received pipe event..."
                )

                self.advance()

                scm.LogInfoMsg(
                    self.display_name + ": Finished processing pipe event..."
                )
            elif rc == w32ev.WAIT_OBJECT_0+len(self.__hEvents):
                scm.LogInfoMsg(self.display_name + ": All events...")
            elif rc == w32ev.WAIT_TIMEOUT:
                scm.LogInfoMsg(
                    self.display_name + ": Event timeout expired..."
                )
            else:
                raise RuntimeError("What is this? Quack quack!")

        scm.LogInfoMsg(self.display_name + ": Exiting service...")

    #FIXME: Add abstracts or define methods in client and replace in
    # implemented file.

    #@abstractmethod
    def start(self):
        self._start()

    #@abstractmethod
    def stop(self):
        self._stop()

    #@abstractmethod
    def shutdown(self):
        self._shutdown()

    #@abstractmethod
    def advance(self):
        pipe_status, pipe_bytes, pipe_content = self.pipe.read()
        scm.LogInfoMsg(
            self.display_name + " (Pipe status): " + str(pipe_status)
        )
        scm.LogInfoMsg(
            self.display_name + " (Pipe bytes): " + str(pipe_bytes)
        )
        scm.LogInfoMsg(
            self.display_name + " (Pipe content): " + pipe_content
        )
        self.pipe.close()
