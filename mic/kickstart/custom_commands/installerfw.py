#!/usr/bin/python -tt
#
# Copyright (c) 2013 Intel, Inc.
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

from pykickstart.base import *
from pykickstart.options import *
from mic import msger

class Mic_installerfw(KickstartCommand):
    """ This class implements the "installerfw_plugins" KS option. The argument
    of the option is a comman-separated list of MIC features which have to be
    disabled and instead, will be done in the installer. For example,
    "installerfw_plugins=bootloader" disables all the MIC code which installs
    the bootloader to the target images, and instead, the bootlodaer will be
    installed by the installer framework plugin.

    The plugin is a program which is external to MIC, it comes from the
    installation repositories and can be executed by MIC in order to perform
    various configuration actions. The main point here is to make sure MIC has
    no hard-wired knoledge about the target OS configuration. """

    removedKeywords = KickstartCommand.removedKeywords
    removedAttrs = KickstartCommand.removedAttrs

    def __init__(self, *args, **kwargs):
        KickstartCommand.__init__(self, *args, **kwargs)
        self.op = self._getParser()
        self.features = None

    def __str__(self):
        retval = KickstartCommand.__str__(self)

        if self.features:
            retval += "# Enable installer framework plugins\ninstallerfw_plugins\n"

        return retval

    def _getParser(self):
        op = KSOptionParser()
        return op

    def parse(self, args):
        (_, extra) = self.op.parse_args(args=args, lineno=self.lineno)

        if len(extra) != 1:
            msg = "Kickstart command \"%s\" requires one " \
                  "argumet - a list of legacy features to disable" % self.currentCmd
            raise KickstartValueError, formatErrorMsg(self.lineno, msg = msg)

        self.features = extra[0].split(",")

        return self
