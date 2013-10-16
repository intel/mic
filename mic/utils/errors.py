#
# Copyright (c) 2011~2013 Intel, Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place - Suite 330, Boston, MA 02111-1307, USA.

""" Collection of all error class """

class CreatorError(Exception):
    """ Based class for all mic creator errors """
    keyword = None

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        if isinstance(self.msg, unicode):
            self.msg = self.msg.encode('utf-8', 'ignore')
        else:
            self.msg = str(self.msg)
        return self.msg

    def __repr__(self):
        if not hasattr(self, 'keyword') or not self.keyword:
            self.keyword = self.__class__.__name__
        return "<%s> %s" % (self.keyword, str(self))

class Usage(CreatorError):
    """ Error class for Usage """
    pass

class Abort(CreatorError):
    """ Error class for Abort """
    pass

class ConfigError(CreatorError):
    """ Error class for Config file """
    keyword = 'Config'

class KsError(CreatorError):
    """ Error class for Kickstart module """
    keyword = 'Kickstart'

class RepoError(CreatorError):
    """ Error class for Repository related """
    keyword = 'Repository'

class RpmError(CreatorError):
    """ Error class for RPM related """
    keyword = 'RPM'

class MountError(CreatorError):
    """ Error class for Mount related """
    keyword = 'Mount'

class SnapshotError(CreatorError):
    """ Error class for Snapshot related """
    keyword = 'Snapshot'

class SquashfsError(CreatorError):
    """ Error class for Squashfs related """
    keyword = 'Squashfs'

class BootstrapError(CreatorError):
    """ Error class for Bootstrap related """
    keyword = 'Bootstrap'

