# -*- test-case-name: twisted.application.runner.test.test_pidfile -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
PID file.
"""

import errno
from os import getpid, kill

from twisted.python.filepath import IFilePath
from twisted.logger import Logger



class PIDFile(object):
    """
    PID file.

    Manages a file that remembers a process ID.
    """

    _log = Logger()


    def __init__(self, filePath):
        """
        @param filePath: The path to the PID file on disk.
        @type filePath: L{IFilePath}
        """
        self.filePath = IFilePath(filePath)


    def read(self):
        """
        Read the process ID stored in this PID file.

        @raise EnvironmentError: If this PID file cannot be read.
        @raise ValueError: If this PID file's content is invalid.
        """
        pidString = b""
        for pidString in self.filePath.open():
            break

        return int(pidString)


    def write(self, pid=None):
        """
        Store a PID in this PID file.

        @param pid: A PID to store.  If C{None}, store the currently running
            process ID.
        @type pid: L{int}
        """
        if pid is None:
            pid = getpid()
        else:
            pid = int(pid)

        self.filePath.setContent(u"{}\n".format(pid).encode("utf-8"))


    def remove(self):
        """
        Remove this PID file.
        """
        self.filePath.remove()


    def isRunning(self):
        """
        Determine whether there is a running process corresponding to the PID
        in this PID file.

        @return: True if this PID file contains a PID and a process with that
        PID is currently running; false otherwise.
        @rtype: L{bool}

        @raise EnvironmentError: If this PID file cannot be read.
        @raise ValueError: If this PID file's content is invalid.
        """
        pid = self.read()

        try:
            kill(pid, 0)
        except OSError as e:
            if e.errno == errno.ESRCH:  # No such process
                self._log.info("Removing stale PID file: {log_source}")
                self.remove()
                return False
            elif e.errno == errno.EPERM:  # Not permitted to kill
                return True
            else:
                raise
        else:
            return True


    def __enter__(self):
        self.write()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.remove()
