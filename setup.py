#!/usr/bin/env python
"""
    Main for installing mic
"""


import os, sys
import glob
from distutils.core import setup


MOD_NAME = 'mic'


def check_debian():
    """--install-layout is recognized after 2.5"""
    if sys.version_info[:2] > (2, 5):
        if len(sys.argv) > 1 and 'install' in sys.argv:
            try:
                import platform
                (dist, _, _) = platform.linux_distribution()
                # for debian-like distros, mods will be installed to
                # ${PYTHONLIB}/dist-packages
                if dist in ('debian', 'Ubuntu'):
                    sys.argv.append('--install-layout=deb')
            except AttributeError:
                pass


def create_conf_file():
    """Apply prefix to mic.conf.in to generate actual mic.conf"""
    with open('etc/mic.conf.in') as source_file:
        conf_str = source_file.read()
        conf_str = conf_str.replace('@PREFIX@', PREFIX)
        with open(CONF_FILE, 'w') as conf_file:
            conf_file.write(conf_str)


try:
    import mic
    VERSION = mic.__version__
except (ImportError, AttributeError):
    VERSION = "dev"

check_debian()

PACKAGES = [MOD_NAME,
            MOD_NAME + '/utils',
            MOD_NAME + '/imager',
            MOD_NAME + '/kickstart',
            MOD_NAME + '/kickstart/custom_commands',
            MOD_NAME + '/3rdparty/pykickstart',
            MOD_NAME + '/3rdparty/pykickstart/commands',
            MOD_NAME + '/3rdparty/pykickstart/handlers',
            MOD_NAME + '/3rdparty/pykickstart/urlgrabber',
           ]

IMAGER_PLUGINS = glob.glob(os.path.join("plugins", "imager", "*.py"))
BACKEND_PLUGINS = glob.glob(os.path.join("plugins", "backend", "*.py"))

PREFIX = sys.prefix
# if real_prefix, it must be in virtualenv, use prefix as root
ROOT = sys.prefix if hasattr(sys, 'real_prefix') else ''

CONF_FILE = 'etc/mic.conf'
create_conf_file()

setup(name=MOD_NAME,
  version = VERSION,
  description = 'Image Creator for Linux Distributions',
  author='Jian-feng Ding, Qiang Zhang, Gui Chen',
  author_email='jian-feng.ding@intel.com, qiang.z.zhang@intel.com,\
                gui.chen@intel.com',
  url='https://github.com/01org/mic',
  scripts=[
      'tools/mic',
      ],
  packages = PACKAGES,
  data_files = [("%s/lib/mic/plugins/imager" % PREFIX, IMAGER_PLUGINS),
                ("%s/lib/mic/plugins/backend" % PREFIX, BACKEND_PLUGINS),
                ("%s/etc/mic" % ROOT, [CONF_FILE])]
)
