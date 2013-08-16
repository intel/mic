# Copyright (c) 2011 Intel, Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or any later version.

import os
import errno

class LockfileError(Exception):
    """ Lockfile Exception"""
    pass

class SimpleLockfile(object):
    """ Simple implementation of lockfile """
    def __init__(self, fpath):
        self.fpath = fpath
        self.lockf = None

    def acquire(self):
        """ acquire the lock """
        try:
            self.lockf = os.open(self.fpath,
                                 os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except OSError as err:
            if err.errno == errno.EEXIST:
                raise LockfileError("File %s is locked already" % self.fpath)
            raise
        finally:
            if self.lockf:
                os.close(self.lockf)

    def release(self):
        """ release the lock """
        try:
            os.remove(self.fpath)
        except OSError as err:
            if err.errno == errno.ENOENT:
                pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()

    def __del__(self):
        self.release()
