#!/usr/bin/python -tt
#
# Copyright (c) 2009, 2010, 2011 Intel, Inc.
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

from __future__ import with_statement
import os
import sys
import glob
import re
import shutil
import subprocess
import ctypes

from mic import bootstrap, msger
from mic.conf import configmgr
from mic.utils import errors, proxy
from mic.utils.fs_related import find_binary_path, makedirs
from mic.chroot import setup_chrootenv, cleanup_chrootenv, ELF_arch

_libc = ctypes.cdll.LoadLibrary(None)
_errno = ctypes.c_int.in_dll(_libc, "errno")
_libc.personality.argtypes = [ctypes.c_ulong]
_libc.personality.restype = ctypes.c_int
_libc.unshare.argtypes = [ctypes.c_int,]
_libc.unshare.restype = ctypes.c_int

expath = lambda p: os.path.abspath(os.path.expanduser(p))

PER_LINUX32=0x0008
PER_LINUX=0x0000
personality_defs = {
    'x86_64': PER_LINUX, 'ppc64': PER_LINUX, 'sparc64': PER_LINUX,
    'i386': PER_LINUX32, 'i586': PER_LINUX32, 'i686': PER_LINUX32,
    'ppc': PER_LINUX32, 'sparc': PER_LINUX32, 'sparcv9': PER_LINUX32,
    'ia64' : PER_LINUX, 'alpha' : PER_LINUX,
    's390' : PER_LINUX32, 's390x' : PER_LINUX,
}

def condPersonality(per=None):
    if per is None or per in ('noarch',):
        return
    if personality_defs.get(per, None) is None:
        return
    res = _libc.personality(personality_defs[per])
    if res == -1:
        raise OSError(_errno.value, os.strerror(_errno.value))

def inbootstrap():
    if os.path.exists(os.path.join("/", ".chroot.lock")):
        return True
    return (os.stat("/").st_ino != 2)

def bootstrap_mic(argv=None):


    def mychroot():
        os.chroot(rootdir)
        os.chdir(cwd)

    # by default, sys.argv is used to run mic in bootstrap
    if not argv:
        argv = sys.argv
    if argv[0] not in ('/usr/bin/mic', 'mic'):
        argv[0] = '/usr/bin/mic'

    cropts = configmgr.create
    bsopts = configmgr.bootstrap
    distro = bsopts['distro_name'].lower()

    rootdir = bsopts['rootdir']
    pkglist = bsopts['packages']
    cwd = os.getcwd()

    # create bootstrap and run mic in bootstrap
    bsenv = bootstrap.Bootstrap(rootdir, distro, cropts['arch'])
    bsenv.logfile = cropts['logfile']
    # rootdir is regenerated as a temp dir
    rootdir = bsenv.rootdir

    if 'optional' in bsopts:
        optlist = bsopts['optional']
    else:
        optlist = []

    try:
        msger.info("Creating %s bootstrap ..." % distro)
        bsenv.create(cropts['repomd'], pkglist, optlist)

        # bootstrap is relocated under "bootstrap"
        if os.path.exists(os.path.join(rootdir, "bootstrap")):
            rootdir = os.path.join(rootdir, "bootstrap")

        bsenv.dirsetup(rootdir)
        sync_mic(rootdir, plugin=cropts['plugin_dir'])

        #FIXME: sync the ks file to bootstrap
        if "/" == os.path.dirname(os.path.abspath(configmgr._ksconf)):
            safecopy(configmgr._ksconf, rootdir)

        msger.info("Start mic in bootstrap: %s\n" % rootdir)
        bsarch = ELF_arch(rootdir)
        if bsarch in personality_defs:
            condPersonality(bsarch)
        bindmounts = get_bindmounts(cropts)
        ret = bsenv.run(argv, cwd, rootdir, bindmounts)

    except errors.BootstrapError, err:
        raise errors.CreatorError("Failed to download/install bootstrap package " \
                                  "or the package is in bad format: %s" % err)
    except RuntimeError, err:
        #change exception type but keep the trace back
        value, tb = sys.exc_info()[1:]
        raise errors.CreatorError, value, tb
    else:
        sys.exit(ret)
    finally:
        bsenv.cleanup()

def get_bindmounts(cropts):
    binddirs =  [
                  os.getcwd(),
                  cropts['tmpdir'],
                  cropts['cachedir'],
                  cropts['outdir'],
                  cropts['local_pkgs_path'],
                ]
    bindfiles = [
                  cropts['logfile'],
                  configmgr._ksconf,
                ]

    for lrepo in cropts['localrepos']:
        binddirs.append(lrepo)

    bindlist = map(expath, filter(None, binddirs))
    bindlist += map(os.path.dirname, map(expath, filter(None, bindfiles)))
    bindlist = sorted(set(bindlist))
    bindmounts = ';'.join(bindlist)
    return bindmounts


def get_mic_binpath():
    fp = None
    try:
        import pkg_resources # depends on 'setuptools'
        dist = pkg_resources.get_distribution('mic')
        # the real script is under EGG_INFO/scripts
        if dist.has_metadata('scripts/mic'):
            fp = os.path.join(dist.egg_info, "scripts/mic")
    except ImportError:
        pass
    except pkg_resources.DistributionNotFound:
        pass


    if fp:
        return fp

    # not found script if 'flat' egg installed
    try:
        return find_binary_path('mic')
    except errors.CreatorError:
        raise errors.BootstrapError("Can't find mic binary in host OS")


def get_mic_modpath():
    try:
        import mic
    except ImportError:
        raise errors.BootstrapError("Can't find mic module in host OS")
    path = os.path.abspath(mic.__file__)
    return os.path.dirname(path)

def get_mic_libpath():
    return os.getenv("MIC_LIBRARY_PATH", "/usr/lib/mic")

# the hard code path is prepared for bootstrap
def sync_mic(bootstrap, binpth = '/usr/bin/mic',
             libpth='/usr/lib',
             plugin='/usr/lib/mic/plugins',
             pylib = '/usr/lib/python2.7/site-packages',
             conf = '/etc/mic/mic.conf'):
    _path = lambda p: os.path.join(bootstrap, p.lstrip('/'))

    micpaths = {
                 'binpth': get_mic_binpath(),
                 'libpth': get_mic_libpath(),
                 'plugin': plugin,
                 'pylib': get_mic_modpath(),
                 'conf': '/etc/mic/mic.conf',
               }

    if not os.path.exists(_path(pylib)):
        pyptn = '/usr/lib/python?.?/site-packages'
        pylibs = glob.glob(_path(pyptn))
        if pylibs:
            pylib = pylibs[0].replace(bootstrap, '')
        else:
            raise errors.BootstrapError("Can't find python site dir in: %s" %
                                        bootstrap)

    for key, value in micpaths.items():
        try:
            safecopy(value, _path(eval(key)), False, ["*.pyc", "*.pyo"])
        except (OSError, IOError), err:
            raise errors.BootstrapError(err)

    # auto select backend
    conf_str = file(_path(conf)).read()
    conf_str = re.sub("pkgmgr\s*=\s*.*", "pkgmgr=auto", conf_str)
    with open(_path(conf), 'w') as wf:
        wf.write(conf_str)

    # chmod +x /usr/bin/mic
    os.chmod(_path(binpth), 0777)

    # correct python interpreter
    mic_cont = file(_path(binpth)).read()
    mic_cont = "#!/usr/bin/python\n" + mic_cont
    with open(_path(binpth), 'w') as wf:
        wf.write(mic_cont)


def safecopy(src, dst, symlinks=False, ignore_ptns=()):
    if os.path.isdir(src):
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        if os.path.exists(dst):
            shutil.rmtree(dst, ignore_errors=True)

        src = src.rstrip('/')
        # check common prefix to ignore copying itself
        if dst.startswith(src + '/'):
            ignore_ptns = list(ignore_ptns) + [ os.path.basename(src) ]

        ignores = shutil.ignore_patterns(*ignore_ptns)
        try:
            shutil.copytree(src, dst, symlinks, ignores)
        except (OSError, IOError):
            shutil.rmtree(dst, ignore_errors=True)
            raise
    else:
        if not os.path.isdir(dst):
            makedirs(os.path.dirname(dst))

        shutil.copy2(src, dst)
