#
# Copyright (c) 2014 Intel, Inc.
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

import os
import shutil

from mic import msger, rt_util
from mic.conf import configmgr
from mic.plugin import pluginmgr
from mic.pluginbase import ImagerPlugin
from mic.imager.loop import LoopImageCreator
from mic.utils import errors, fs_related, runner

class QcowImageCreator(LoopImageCreator):
    img_format = 'qcow'

    def __init__(self, creatoropts=None, pkgmgr=None):
        LoopImageCreator.__init__(self, creatoropts, pkgmgr) 
        self.cmd_qemuimg = 'qemu-img'

    def _stage_final_image(self):
        try:
            self.cmd_qemuimg = fs_related.find_binary_path('qemu-img')
        except errors.CreatorError:
            return LoopImageCreator._stage_final_image(self)

        self._resparse()

        imgfile = None
        for item in self._instloops:
            if item['mountpoint'] == '/':
                if item['fstype'] == "ext4":
                    runner.show('/sbin/tune2fs -O ^huge_file,extents,uninit_bg %s'
                                % imgfile)
                self.image_files.setdefault('partitions', {}).update(
                         {item['mountpoint']: item['label']})
                imgfile = os.path.join(self._imgdir, item['name'])

        if imgfile:
            qemuimage = imgfile + ".x86"
            runner.show("%s convert -O qcow2 %s %s"
                        % (self.cmd_qemuimg, imgfile, qemuimage))
            os.unlink(imgfile)
            os.rename(qemuimage, imgfile)

        for item in os.listdir(self._imgdir):
            shutil.move(os.path.join(self._imgdir, item),
                        os.path.join(self._outdir, item))

class QcowPlugin(ImagerPlugin):
    name = 'qcow'

    @classmethod
    def do_create(cls, subcmd, opts, *args):
        """${cmd_name}: create qcow image

        Usage:
            ${name} ${cmd_name} <ksfile> [OPTS]

        ${cmd_option_list}
        """
        if len(args) != 1:
            raise errors.Usage("Extra arguments given")

        creatoropts = configmgr.create
        ksconf = args[0]

        if creatoropts['runtime'] == "bootstrap":
            configmgr._ksconf = ksconf
            rt_util.bootstrap_mic()
        elif not rt_util.inbootstrap():
            try:
                fs_related.find_binary_path('mic-native')
            except errors.CreatorError:
                if not msger.ask("Subpackage \"mic-native\" has not been "
                                 "installed in your host system, still "
                                 "continue with \"native\" running mode?",
                                 False):
                    raise errors.Abort("Abort because subpackage 'mic-native' "
                                       "has not been installed")

        recording_pkgs = []
        if len(creatoropts['record_pkgs']) > 0:
            recording_pkgs = creatoropts['record_pkgs']

        if creatoropts['release'] is not None:
            if 'name' not in recording_pkgs:
                recording_pkgs.append('name')
            if 'vcs' not in recording_pkgs:
                recording_pkgs.append('vcs')

        configmgr._ksconf = ksconf

        # try to find the pkgmgr
        pkgmgr = None
        backends = pluginmgr.get_plugins('backend')
        if 'auto' == creatoropts['pkgmgr']:
            for key in configmgr.prefer_backends:
                if key in backends:
                    pkgmgr = backends[key]
                    break
        else:
            for key in backends.keys():
                if key == creatoropts['pkgmgr']:
                    pkgmgr = backends[key]
                    break

        if not pkgmgr:
            raise errors.CreatorError("Can't find backend: %s, "
                                      "available choices: %s" %
                                      (creatoropts['pkgmgr'],
                                       ','.join(backends.keys())))

        creator = QcowImageCreator(creatoropts,
                                   pkgmgr)

        if len(recording_pkgs) > 0:
            creator._recording_pkgs = recording_pkgs

        image_names = [creator.name + ".img"]
        image_names.extend(creator.get_image_names())
        cls.check_image_exists(creator.destdir,
                                creator.pack_to,
                                image_names,
                                creatoropts['release'])

        try:
            creator.check_depend_tools()
            creator.mount(None, creatoropts["cachedir"])
            creator.install()
            creator.configure(creatoropts["repomd"])
            creator.copy_kernel()
            creator.unmount()
            creator.package(creatoropts["destdir"])
            creator.create_manifest()

            if creatoropts['release'] is not None:
                creator.release_output(ksconf,
                                       creatoropts['destdir'],
                                       creatoropts['release'])
            creator.print_outimage_info()

        except errors.CreatorError:
            raise
        finally:
            creator.cleanup()

        msger.info("Finished.")
        return 0

    @classmethod
    def do_chroot(cls, target, cmd=[]):
        pass

    @classmethod
    def do_unpack(cls, srcimg):
        pass
