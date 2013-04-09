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

""" This module implements a simple GPT partitions parser which can read the
GPT header and the GPT partition table. """

import struct
import uuid
from mic.utils.errors import MountError

_GPT_HEADER_FORMAT = "<8sIIIIQQQQ16sQIII420x"
_GPT_ENTRY_FORMAT = "<16s16sQQQ72s"

def _stringify_uuid(binary_uuid):
    """ A small helper function to transform a binary UUID into a string
    format. """

    uuid_str = str(uuid.UUID(bytes_le = binary_uuid))

    return uuid_str.upper()

class GptParser:
    """ GPT partition table parser. The current implementation is simplified
    and it assumes that the partition table is correct, so it does not check
    the CRC-32 checksums and does not handle the backup GPT partition table.
    But this implementation can be extended in the future, if needed. """

    def __init__(self, disk_path, sector_size = 512):
        """ The class construcor which accepts the following parameters:
            * disk_path - full path to the disk image or device node
            * sector_size - size of a disk sector in bytes """

        self.sector_size = sector_size
        self.disk_path = disk_path

        try:
            self.disk_obj = open(disk_path, 'rb')
        except IOError as err:
            raise MountError("Cannot open file '%s' for reading GPT " \
                             "partitions: %s" % (disk_path, err))

    def __del__(self):
        """ The class destructor. """

        self.disk_obj.close()

    def read_header(self):
        """ Read and verify the GPT header and return a tuple containing the
        following elements:

        (Signature, Revision, Header size in bytes, header CRC32, Current LBA,
        Backup LBA, First usable LBA for partitions, Last usable LBA, Disk GUID,
        Starting LBA of array of partition entries, Number of partition entries,
        Size of a single partition entry, CRC32 of partition array)

        This tuple corresponds to the GPT header format. Please, see the UEFI
        standard for the description of these fields. """

        # The header sits at LBA 1 - read it
        self.disk_obj.seek(self.sector_size)
        try:
            header = self.disk_obj.read(struct.calcsize(_GPT_HEADER_FORMAT))
        except IOError as err:
            raise MountError("cannot read from file '%s': %s" % \
                             (self.disk_path, err))

        header = struct.unpack(_GPT_HEADER_FORMAT, header)

        # Perform a simple validation
        if header[0] != 'EFI PART':
            raise MountError("GPT paritition table on disk '%s' not found" % \
                             self.disk_path)

        return (header[0], # 0. Signature
                header[1], # 1. Revision
                header[2], # 2. Header size in bytes
                header[3], # 3. Header CRC32
                header[5], # 4. Current LBA
                header[6], # 5. Backup LBA
                header[7], # 6. First usable LBA for partitions
                header[8], # 7. Last usable LBA
                _stringify_uuid(header[9]), # 8. Disk GUID
                header[10], # 9. Starting LBA of array of partition entries
                header[11], # 10. Number of partition entries
                header[12], # 11. Size of a single partition entry
                header[13]) # 12. CRC32 of partition array

    def get_partitions(self):
        """ This is a generator which parses teh GPT partition table and
        generates the following tupes for each partition:

        (Partition type GUID, Partition GUID, First LBA, Last LBA,
        Attribute flags, Partition name)

        This tuple corresponds to the GPT partition record format. Please, see the
        UEFI standard for the description of these fields. """

        gpt_header = self.read_header()
        entries_start = gpt_header[9] * self.sector_size
        entries_count = gpt_header[10]

        self.disk_obj.seek(entries_start)

        for _ in xrange(0, entries_count):
            entry = self.disk_obj.read(struct.calcsize(_GPT_ENTRY_FORMAT))
            entry = struct.unpack(_GPT_ENTRY_FORMAT, entry)

            if entry[2] == 0 or entry[3] == 0:
                continue

            part_name = str(entry[5].decode('UTF-16').split('\0', 1)[0])

            yield (_stringify_uuid(entry[0]), # 0. Partition type GUID
                   _stringify_uuid(entry[1]), # 1. Partition GUID
                   entry[2],                  # 2. First LBA
                   entry[3],                  # 3. Last LBA
                   entry[4],                  # 4. Attribute flags
                   part_name)                 # 5. Partition name
