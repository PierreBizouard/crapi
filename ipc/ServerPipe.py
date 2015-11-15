# Copyright (C) 2014/15 - Iraklis Diakos (hdiakos@outlook.com)
# Pilavidis Kriton (kriton_pilavidis@outlook.com)
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the ASF 2.0 license.
#

"""Part of the ipc module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
# Python native libraries.
from enum import Enum

import crapi.ipc.Pipe as Pipe
from crapi.ipc.PipeError import PipeError


class ServerPipe(Pipe.Pipe):

    def __init__(self, name='', ptype=Pipe.Pipe.Type.NAMED,
                 mode=Pipe.Pipe.Mode.DUPLEX, channel=Pipe.Pipe.Channel.MESSAGE,
                 transport=Pipe.Pipe.Transport.ASYNCHRONOUS, instances=0,
                 buf_sz=[0, 0]):

        super(ServerPipe, self).__init__(
            name=name, ptype=ptype, mode=mode, channel=channel,
            transport=transport, view=Pipe.Pipe.View.SERVER,
            instances=instances, buf_sz=buf_sz
        )

    #TODO: Implement policy strategy.
    class POLICY(Enum):
        RW = 'rw'
        WR = 'wr'
        RO = 'ro'
        WO = 'wo'

    #TODO: Add a signal handler that allows processing of RW events.
    def _listen(self, policy=POLICY.RW):
        status_code = self.connect()
        if status_code == 0:
            status_code, written_bytes = self.write("Hello CRAPI client! :)")
            print("Payload status code (W): ", end="")
            print(status_code)
            print("# of bytes written (W): ", end="")
            print(written_bytes)
            pipe_status, pipe_bytes, pipe_content = self.read()
            self.close()
        else:
            raise PipeError(
                'Pipe encountered an error while attempting a connection!',
                'status_code',
                status_code
            )
        return status_code, pipe_status, pipe_bytes, pipe_content

    def listen(self):
        return self._listen()
