"""Part of the utilities module."""

from __future__ import absolute_import
from __future__ import print_function
# Python native libraries.
import os
import sys
import threading
import uuid
# Python 3rd party libraries (future module).
import queue as Queue

if sys.platform.startswith('win'):
    import subprocess
else:
    import subprocess32 as subprocess


# TODO: stdout and stderr seperate queues for non-merged output mode
class InteractiveTTY(object):

    """
        An interactive, non-blocking/asynchronous/overlapping, reliable &
        portable background terminal subprocess.
    """

    def __init__(self, environment_variables=os.environ.copy(),
                 is_unix_eol=True, tag_io=False, native_shell=False):
        """Default initialization class method."""
        self.__is_unix_eol__ = is_unix_eol
        if tag_io:
            self.__io_id__ = uuid.uuid4().hex
        else:
            self.__io_id__ = None
        self.__environ_vars__ = environment_variables
        self.__native_shell__ = native_shell
        self.__input__ = Queue.Queue()
        self.__output__ = Queue.Queue()
        if tag_io:
            self.__stdout_id__ = '__' + self.__io_id__ + '_STDOUT__'
            self.__stderr_id__ = '__' + self.__io_id__ + '_STDERR__'

    # Consumer.
    def __consumer__(self):
        """Consumer method."""
        while self.__tty__.poll() is None:
            self.__tty__.stdin.write(
                self.__input__.get(block=True)
            )
            # TODO: This should be removed since command(s) that constantly or
            #       periodically generate(s) output makes our consumer grossly
            #       inefficient. However, we first need to verify that the OS
            #       can detect that is talking to an interactive terminal.
            self.__tty__.stdin.flush()

    # Producer.
    def __producer__(self):
        """Producer method."""
        while self.__tty__.poll() is None:
            for line in iter(self.__tty__.stdout.readline, ''):
                self.__output__.put(item=line, block=True)

    # Consumer (user).
    # TODO: Implement row_limit
    def retrieve(self, batch_mode=False, row_limit=0):
        if self.__io_id__ is not None:
            tag = self.__io_id__ + ': '
        else:
            tag = ''
        try:
            if batch_mode:
                batch = tag + self.__output__.get_nowait()
                while True:
                    try:
                        batch += tag + self.__output__.get_nowait()
                    except Queue.Empty:
                        break
                return batch
            else:
                return tag + self.__output__.get_nowait()
        except Queue.Empty:
            return None

    # Producer (user).
    def send(self, data):
        self.__input__.put_nowait(item=data + '\n')

    def open(self, tty_args=None):
        """Self-explanatory."""
        # See: http://bugs.python.org/issue3907
        #      http://goo.gl/x19GaQ
        #      http://goo.gl/CJs6rq
        #      http://goo.gl/ncYXWx (very nice explanation!)
        # for issues with pipes and workarounds.
        # TODO: Call C function and use setvbuf OR
        #       Call powershell module via a python.py program using the -u
        #       parameter, i.e. python -u subprocess_me.py
        self.__tty__ = subprocess.Popen(
            args=tty_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            # Line-oriented but it does not matter since OS cannot determine if
            # we're talking to an interactive TTY :/.
            bufsize=1,
            universal_newlines=self.__is_unix_eol__,
            env=self.__environ_vars__,
            shell=self.__native_shell__,
            close_fds=False
        )
        self.__thr_consumer__ = threading.Thread(
            target=self.__consumer__,
            name='consumer',
            args=()
        )
        self.__thr_producer__ = threading.Thread(
            target=self.__producer__,
            name='producer',
            args=()
        )
        self.__thr_consumer__.start()
        self.__thr_producer__.start()

        return self.__tty__.pid

    def close(self):
        self.__tty__.terminate()
