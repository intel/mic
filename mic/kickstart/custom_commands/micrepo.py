#
# Copyright (c) 2008, 2009, 2010 Intel, Inc.
#
# Yi Yang <yi.y.yang@intel.com>
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

from pykickstart.commands.repo import F14_RepoData, F14_Repo


class Mic_RepoData(F14_RepoData):
    "Mic customized repo data"

    def __init__(self, *args, **kw):
        F14_RepoData.__init__(self, *args, **kw)
        for field in ('save', 'proxyuser', 'proxypasswd', 'debuginfo',
                      'disable', 'source', 'gpgkey', 'ssl_verify', 'priority',
                      'nocache', 'user', 'passwd'):
            setattr(self, field, kw.get(field))

        if hasattr(self, 'proxy') and not self.proxy:
            # TODO: remove this code, since it only for back-compatible.
            # Some code behind only accept None but not empty string
            # for default proxy
            self.proxy = None

    def _getArgsAsStr(self):
        retval = F14_RepoData._getArgsAsStr(self)

        for field in ('proxyuser', 'proxypasswd', 'user', 'passwd',
                      'gpgkey', 'ssl_verify', 'priority',
                      ):
            if hasattr(self, field) and getattr(self, field):
                retval += ' --%s="%s"' % (field, getattr(self, field))

        for field in ('save', 'diable', 'nocache', 'source', 'debuginfo'):
            if hasattr(self, field) and getattr(self, field):
                retval += ' --%s' % field

        return retval


class Mic_Repo(F14_Repo):
    "Mic customized repo command"

    def _getParser(self):
        op = F14_Repo._getParser(self)
        op.add_option('--user')
        op.add_option('--passwd')
        op.add_option("--proxyuser")
        op.add_option("--proxypasswd")

        op.add_option("--save", action="store_true", default=False)
        op.add_option("--debuginfo", action="store_true", default=False)
        op.add_option("--source", action="store_true", default=False)
        op.add_option("--disable", action="store_true", default=False)
        op.add_option("--nocache", action="store_true", default=False)

        op.add_option("--gpgkey")
        op.add_option("--priority", type="int")
        op.add_option("--ssl_verify", default=None)
        return op
