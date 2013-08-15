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
import re
import shutil
import subprocess

from mic import msger
from mic.conf import configmgr
from mic.utils import misc, errors, runner, fs_related, lock

#####################################################################
### GLOBAL CONSTANTS
#####################################################################

chroot_bindmounts = None
chroot_lock = None
BIND_MOUNTS = (
                "/proc",
                "/proc/sys/fs/binfmt_misc",
                "/sys",
                "/dev",
                "/dev/pts",
                "/var/lib/dbus",
                "/var/run/dbus",
                "/var/lock",
                "/lib/modules",
              )

#####################################################################
### GLOBAL ROUTINE
#####################################################################

def ELF_arch(chrootdir):
    """ detect the architecture of an ELF file """
    #FIXME: if chkfiles are symlink, it will be complex
    chkfiles = ('/bin/bash', '/sbin/init')
    # regular expression to arch mapping
    mapping = {
                r"Intel 80[0-9]86": "i686",
                r"x86-64": "x86_64",
                r"ARM": "arm",
              }

    for path in chkfiles:
        cpath = os.path.join(chrootdir, path.lstrip('/'))
        if not os.path.exists(cpath):
            continue

        outs = runner.outs(['file', cpath])
        for ptn in mapping.keys():
            if re.search(ptn, outs):
                return mapping[ptn]

    raise errors.CreatorError("Failed to detect architecture of chroot: %s" %
                              chrootdir)

def get_bindmounts(chrootdir, bindmounts = None):
    """ calculate all bind mount entries for global usage """
    # bindmounts should be a string like '/dev:/dev'
    # FIXME: refine the bindmounts from string to dict
    global chroot_bindmounts

    def totuple(string):
        """ convert string contained ':' to a tuple """
        if ':' in string:
            src, dst = string.split(':', 1)
        else:
            src = string
            dst = None

        return (src or None, dst or None)

    if chroot_bindmounts:
        return chroot_bindmounts

    chroot_bindmounts = []
    bindmounts = bindmounts or ""
    mountlist = []

    for mount in bindmounts.split(";"):
        if not mount:
            continue

        (src, dst) = totuple(mount)

        if src in BIND_MOUNTS or src == '/':
            continue

        if not os.path.exists(src):
            os.makedirs(src)

        if dst and os.path.isdir("%s/%s" % (chrootdir, dst)):
            msger.warning("%s existed in %s , skip it." % (dst, chrootdir))
            continue

        mountlist.append(totuple(mount))

    for mntpoint in BIND_MOUNTS:
        if os.path.isdir(mntpoint):
            mountlist.append(tuple((mntpoint, None)))

    for pair in mountlist:
        if pair[0] == "/lib/modules":
            opt = "ro"
        else:
            opt = None
        bmount = fs_related.BindChrootMount(pair[0], chrootdir, pair[1], opt)
        chroot_bindmounts.append(bmount)

    return chroot_bindmounts

#####################################################################
### SETUP CHROOT ENVIRONMENT
#####################################################################

def bind_mount(chrootmounts):
    """ perform bind mounting """
    for mnt in chrootmounts:
        msger.verbose("bind_mount: %s -> %s" % (mnt.src, mnt.dest))
        mnt.mount()

def setup_resolv(chrootdir):
    """ resolve network """
    try:
        shutil.copyfile("/etc/resolv.conf", chrootdir + "/etc/resolv.conf")
    except (OSError, IOError):
        pass

def setup_mtab(chrootdir):
    """ adjust mount table """
    mtab = "/etc/mtab"
    dstmtab = chrootdir + mtab
    if not os.path.islink(dstmtab):
        shutil.copyfile(mtab, dstmtab)

def setup_chrootenv(chrootdir, bindmounts = None):
    """ setup chroot environment """
    global chroot_lock

    # acquire the lock
    if not chroot_lock:
        lockpath = os.path.join(chrootdir, '.chroot.lock')
        chroot_lock = lock.SimpleLockfile(lockpath)
    chroot_lock.acquire()
    # bind mounting
    bind_mount(get_bindmounts(chrootdir, bindmounts))
    # setup resolv.conf
    setup_resolv(chrootdir)
    # update /etc/mtab
    setup_mtab(chrootdir)

    return None

######################################################################
### CLEANUP CHROOT ENVIRONMENT
######################################################################

def bind_unmount(chrootmounts):
    """ perform bind unmounting """
    for mnt in reversed(chrootmounts):
        msger.verbose("bind_unmount: %s -> %s" % (mnt.src, mnt.dest))
        mnt.unmount()

def cleanup_resolv(chrootdir):
    """ clear resolv.conf """
    try:
        fdes = open(chrootdir + "/etc/resolv.conf", "w")
        fdes.truncate(0)
        fdes.close()
    except (OSError, IOError):
        pass

def kill_proc_inchroot(chrootdir):
    """ kill all processes running inside chrootdir """
    import glob
    for fpath in glob.glob("/proc/*/root"):
        try:
            if os.readlink(fpath) == chrootdir:
                pid = int(fpath.split("/")[2])
                os.kill(pid, 9)
        except (OSError, ValueError):
            pass

def cleanup_mtab(chrootdir):
    """ remove mtab file """
    if os.path.exists(chrootdir + "/etc/mtab"):
        os.unlink(chrootdir + "/etc/mtab")

def cleanup_mounts(chrootdir):
    """ clean up all mount entries owned by chrootdir """
    umountcmd = misc.find_binary_path("umount")
    mounts = open('/proc/mounts').readlines()
    for line in reversed(mounts):
        if chrootdir not in line:
            continue

        point = line.split()[1]

        # '/' to avoid common name prefix
        if chrootdir == point or point.startswith(chrootdir + '/'):
            args = [ umountcmd, "-l", point ]
            ret = runner.quiet(args)
            if ret != 0:
                msger.warning("failed to unmount %s" % point)
            if os.path.isdir(point) and len(os.listdir(point)) == 0:
                shutil.rmtree(point)
            else:
                msger.warning("%s is not directory or is not empty" % point)

def cleanup_chrootenv(chrootdir, bindmounts=None, globalmounts=()):
    """ clean up chroot environment """
    global chroot_lock

    # kill processes
    kill_proc_inchroot(chrootdir)
    # clean mtab
    cleanup_mtab(chrootdir)
    # clean resolv.conf
    cleanup_resolv(chrootdir)
    # bind umounting
    bind_unmount(get_bindmounts(chrootdir, bindmounts))
    # clean up mounts
    cleanup_mounts(chrootdir)
    # release the lock
    if chroot_lock:
        chroot_lock.release()
        chroot_lock = None

    return None

#####################################################################
### CHROOT STUFF
#####################################################################

def savefs_before_chroot(chrootdir, saveto = None):
    """ backup chrootdir to another directory before chrooting in """
    if configmgr.chroot['saveto']:
        savefs = True
        saveto = configmgr.chroot['saveto']
        wrnmsg = "Can't save chroot fs for dir %s exists" % saveto
        if saveto == chrootdir:
            savefs = False
            wrnmsg = "Dir %s is being used to chroot" % saveto
        elif os.path.exists(saveto):
            if msger.ask("Dir %s already exists, cleanup and continue?" %
                         saveto):
                shutil.rmtree(saveto, ignore_errors = True)
                savefs = True
            else:
                savefs = False

        if savefs:
            msger.info("Saving image to directory %s" % saveto)
            fs_related.makedirs(os.path.dirname(os.path.abspath(saveto)))
            runner.quiet("cp -af %s %s" % (chrootdir, saveto))
            devs = ['dev/fd',
                    'dev/stdin',
                    'dev/stdout',
                    'dev/stderr',
                    'etc/mtab']
            ignlst = [os.path.join(saveto, x) for x in devs]
            map(os.unlink, filter(os.path.exists, ignlst))
        else:
            msger.warning(wrnmsg)

def cleanup_after_chroot(targettype, imgmount, tmpdir, tmpmnt):
    """ clean up all temporary directories after chrooting """
    if imgmount and targettype == "img":
        imgmount.cleanup()

    if tmpdir:
        shutil.rmtree(tmpdir, ignore_errors = True)

    if tmpmnt:
        shutil.rmtree(tmpmnt, ignore_errors = True)

def chroot(chrootdir, bindmounts = None, execute = "/bin/bash"):
    """ chroot the chrootdir and execute the command """
    def mychroot():
        """ pre-execute function """
        os.chroot(chrootdir)
        os.chdir("/")

    arch = ELF_arch(chrootdir)
    if arch == "arm":
        qemu_emulator = misc.setup_qemu_emulator(chrootdir, "arm")
    else:
        qemu_emulator = None

    savefs_before_chroot(chrootdir, None)

    try:
        msger.info("Launching shell. Exit to continue.\n"
                   "----------------------------------")
        globalmounts = setup_chrootenv(chrootdir, bindmounts)
        subprocess.call(execute, preexec_fn = mychroot, shell=True)

    except OSError, err:
        raise errors.CreatorError("chroot err: %s" % str(err))

    finally:
        cleanup_chrootenv(chrootdir, bindmounts, globalmounts)
        if qemu_emulator:
            os.unlink(chrootdir + qemu_emulator)
