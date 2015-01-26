#!/usr/bin/python -tt
#
# Marko Saukko <marko.saukko@cybercom.com>
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
#
# This copyrighted material is made available to anyone wishing to use, modify,
# copy, or redistribute it subject to the terms and conditions of the GNU
# General Public License v.2. This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from pykickstart.commands.partition import *

class Mic_PartData(FC4_PartData):
    removedKeywords = FC4_PartData.removedKeywords
    removedAttrs = FC4_PartData.removedAttrs

    def __init__(self, *args, **kwargs):
        FC4_PartData.__init__(self, *args, **kwargs)
        self.deleteRemovedAttrs()
        self.align = kwargs.get("align", None)
        self.extopts = kwargs.get("extopts", None)
        self.part_type = kwargs.get("part_type", None)
        self.uuid = kwargs.get("uuid", None)
        self.exclude_image = kwargs.get("exclude_from_image", False)

    def _getArgsAsStr(self):
        retval = FC4_PartData._getArgsAsStr(self)

        if self.align:
            retval += " --align"
        if self.extopts:
            retval += " --extoptions=%s" % self.extopts
        if self.part_type:
            retval += " --part-type=%s" % self.part_type
        if self.uuid:
            retval += " --uuid=%s" % self.uuid
        if self.exclude_image:
            retval += " --exclude-from-image"

        return retval

class Mic_Partition(FC4_Partition):
    removedKeywords = FC4_Partition.removedKeywords
    removedAttrs = FC4_Partition.removedAttrs

    def _getParser(self):
        op = FC4_Partition._getParser(self)
        # The alignment value is given in kBytes. e.g., value 8 means that
        # the partition is aligned to start from 8096 byte boundary.
        op.add_option("--align", type="int", action="store", dest="align",
                      default=None)
        op.add_option("--extoptions", type="string", action="store", dest="extopts",
                      default=None)
        op.add_option("--part-type", type="string", action="store", dest="part_type",
                      default=None)
        op.add_option("--uuid", dest="uuid", action="store", type="string")
        op.add_option("--exclude-from-image", action="store_true", dest="exclude_image",
                      default=False)
        return op
