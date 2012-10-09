=====
 mic
=====

Overview
========
MIC means Image Creator and it's used to create images for Tizen. The tool offers three major functions:

- image creation
- image conversion
- chrooting into an image

The tool is derived mainly from MIC2, which is used to create MeeGo images. With great improvements on many features, it has become clear, friendly, and flexible. It provides a python plugin mechanism for developers, to expand image type or image options, and even to hook.

With the MIC tool, users can create different types of images for different verticals, including live CD images, live USB images, raw images for KVM, loop images for IVI platforms, and fs images for chrooting. Also, users can work in a chroot environment, based on an existing live image using MIC's enhanced chrooting. Besides, MIC enables transforming an image to another image format, a very useful function for those sensitive to image format.

Installation
============
MIC runs natively in many mainstream Linux distributions, including:

- Ubuntu (LTS and one latest non-LTS version --- 12.04 and 11.10)
- openSUSE (the latest version --- 12.1)
- Fedora (the latest version --- 17)

Binary Installation
-------------------

To install the MIC package, get the corresponding repository at:
http://download.tizen.org/tools/

If none of the distributions available in the list are the one you want, install MIC from source code.

Ubuntu Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Append repository  source:
::

  $ sudo vi /etc/apt/sources.list

Append the following line:

for Ubuntu 12.04:
::

 deb  http://download.tizen.org/tools/xUbuntu_12.04/

for Ubuntu11.10:
::

 deb  http://download.tizen.org/tools/xUbuntu_11.10/

2. Update repository list:
::

  $ sudo apt-get update

3. Install mic:
::

  $ sudo apt-get install mic

OpenSUSE Installation
~~~~~~~~~~~~~~~~~~~~~
1. Add Tools Building repository:
::

  $ sudo zypper addrepo http://download.tizen.org/tools/openSUSE12.1/ tools-building


2. Update repository list:
::

  $ sudo zypper refresh

3. Install mic:
::

  $ sudo zypper install mic

Fedora Installation
~~~~~~~~~~~~~~~~~~~
1. Add The Tools Building repository:
::

  $ sudo cat  /etc/yum.repos.d/tools-building.repo
  > [Tools]
  > name=Tools project for mic, gbs, etc. (Fedora_17)
  > baseurl=http://download.tizen.org/tools/Fedora_17/
  > enabled=1
  > gpgcheck=0

2. Update repository cache:
::

  $ sudo yum makecache

3. Install Mic:
::

  $ sudo yum install mic --nogpgcheck

Source Installation
-------------------
Before you install MIC from the source, make sure you installed all the MIC's dependencies manually.

Enable Bootstrap Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If your mic is higher than 0.15, it means mic would use bootstrap as default. This is the recommended way to install MIC source. The dependencies are:
::

  - rpm
  - rpm-python
  - python
  - python-xml
  - python-urlgrabber

Take Ubuntu 12.04 as an example, you should install the dependencies with apt-get:
::

   $ sudo apt-get install rpm python-rpm python-urlgrabber

For OpenSUSE, you can install the dependencies with zypper:
::

   $ sudo zypper install rpm-python python-xml python-urlgrabber

Using Native Envionment
~~~~~~~~~~~~~~~~~~~~~~~
If you want MIC to run natively in your host, you should install more dependencies to make it work. For Ubuntu 12.04, you should install these packages with apt-get:
::

  $ sudo apt-get install python-rpm bzip2 dmsetup dosfstools e2fsprogs isomd5sum genisoimage \
   > kpartx parted psmisc sqashfs-tools qemu-user-static extlinux syslinux yum python-m2crypto

To get the MIC source, go `here
<https://github.com/otcshare/mic/downloads>`_  or git clone from github

::

 $ git clone https://github.com/01org/mic

Then go to the MIC source directory, and run 'make install' to install MIC from source:

::

  $ cd mic
  $ sudo make install


Quick Start
============

How to create an image
-----------------------

**Prepare kickstart file**

To create an image, you need a proper ks file.
Here's a simple example:
::

  # filename: tizen-min.ks
  lang en_US.UTF-8
  keyboard us
  timezone --utc America/Los_Angeles

  part / --size 1824 --ondisk sda --fstype=ext3

  rootpw tizen
  bootloader  --timeout=0  --append="rootdelay=5"

  desktop --autologinuser=tizen
  user --name tizen  --groups audio,video --password 'tizen'

  repo --name=Tizen-base --baseurl=http://download.tizen.org/snapshots/trunk/latest/repos/base/ia32/packages/
  repo --name=Tizen-main --baseurl=http://download.tizen.org/snapshots/trunk/latest/repos/main/ia32/packages/

  %packages --ignoremissing
   @tizen-bootstrap
  %end

  %post
  rm -rf /var/lib/rpm/__db*
  rpm --rebuilddb
  %end

  %post --nochroot
  %end

The ks file above can be used to create a minimum Tizen image. For other repositories, you can replace with the appropriate repository url. For example:
::

  repo --name=REPO-NAME --baseurl=https://username:passwd@yourrepo.com/ia32/packages/ --save  --ssl_verify=no

**Create an loop image**

To create an image, run MIC in the terminal:
::

 $ sudo mic create loop tizen-min.ks

How to add/remove packages
--------------------------

You can specific the packages you plan to install in the '%packages' section in ks file. Packages can be specified by group/pattern or by individual package name. The definition of the groups/pattern can be referred to in the repodata/\*comps.xml or repodata/pattern.xml file at the download server. For example: http://download.tizen.org/snapshots/latest/repos/base/ia32/packages/repodata/_.

The %packages section is required to end with '%end'. Also, multiple '%packages' sections are allowed. Additionally, individual packages may be specified using globs. For example:
::

  %packages
  ...
  @Tizen Core            # add a group named Tizen Core, and all the packages in this group would be added
  e17-*                  # add all the packages with name starting with "e17-"
  kernel                 # add kernel package
  nss-server.armv7hl     # add nss-server with arch armv7hl
  -passwd                # remove the package passwd
  ...
  %end

Use local rpm package
---------------------

"How can I install my own rpm into the image, so I can test my package with the image?"
In such a case, using local package path would be very helpful. For example, if your rpm 'hello.rpm' is under directory 'localpath', run MIC like below:

::

    $ sudo mic create loop test.ks --local-pkgs-path=localpath

From the output, MIC will tell you "Marked 'hellop.rpm' as installed", and it will install hello.rpm in the image. Be sure your rpm is not in the repo of ks file and that your rpm's version is newer or equal to the repo rpm version.

How to set proxy
----------------

**Proxy variable in bash**

It's common to use the proxy variable in bash. In general, you can set the following environment variables to enable proxy support:

::

  export http_proxy=http://proxy.com:port
  export https_proxy=http://proxy.com:port
  export ftp_proxy=http://proxy.com:port
  export no_proxy=localhost,127.0.0.0/8,.company.com

You don't need all the variables. Check what you do need. When your repo url in your ks file starts with 'https', MIC will use https_proxy. Be especially aware of when you set no_proxy (it indicates which domain should be accessed directly). Don't leave blank space in the string.

Because MIC needs sudo privilege, set /etc/sudoers, to keep the proxy environment, and add those proxy variables to "env_keep":

::

   Defaults        env_keep += "http_proxy https_proxy ftp_proxy no_proxy"

Note: Use "visudo" to modify /etc/sudoers

However, if you don't want to change your /etc/sudoers, there is an alternative for you to set the proxy in mic.conf. See the next section.

**Proxy setting in mic.conf**

The proxy environment variables may disturb other program, so if you would like to enable proxy support only for MIC, set the proxy in /etc/mic/mic.conf like this:

::

  [create]
   ; settings for create subcommand
   tmpdir= /var/tmp/mic
   cachedir= /var/tmp/mic/cache
   outdir= .
   pkgmgr = zypp
   proxy = http://proxy.yourcompany.com:8080/
   no_proxy = localhost,127.0.0.0/8,.yourcompany.com

**Proxy setting in ks file**

It's likely that you will need to enable proxy support only for a special repo url, and other things would remain at their existing proxy setting.
Here's how to handle that case:

::

  repo --name=oss --baseurl=http://www.example.com/repos/oss/packages --proxy=http://host:port

Chroot an image
----------------

When you want to run commands inside an image, just chroot it first. Be sure your image has bash installed inside:

::

    $ sudo mic chroot tizen-min.img

Convert an image to another format
----------------------------------

**Convert livecd to liveusb**

To convert a livecd image to liveusb:

::

  $ sudo mic convert test.iso liveusb

**Convert liveusb to livecd**

To convert a liveusb to livecd:

::

  $ sudo mic convert test.usbimg livecd

Basic Usage
============
MIC is used to create and manipulate images for Linux distributions. It is composed of three subcommands: create, convert, and chroot.

Create
-------------------

This command is used to create various images, including live CD, live USB, loop, and raw.

**Usage:**

::

  mic create(cr) SUBCOMMAND <ksfile> [OPTION]

**Sub-commands:**

::

   help(?)            give detailed help on a specific sub-command
   fs                 create fs image, which is also chroot directory
   livecd             create live CD image, used for CD booting
   liveusb            create live USB image, used for USB booting
   loop               create loop image, including multi-partitions
   raw                create raw image, containing multi-partitions

**Options:**

::

   -h, --help          Show this help message and exit
   --logfile=LOGFILE   Path of logfile
   -c CONFIG, --config=CONFIG
                       Specify config file for MIC
   -k CACHEDIR, --cachedir=CACHEDIR
                       Cache directory to store downloaded files
   -o OUTDIR, --outdir=OUTDIR
                       Output directory
   -A ARCH, --arch=ARCH
                       Specify repo architecture
   --release=RID       Generate a release of RID with all necessary files.
                       When @BUILD_ID@ is contained in kickstart file, it
                       will be replaced by RID.
   --record-pkgs=RECORD_PKGS
                       Record the info of installed packages. Multiple values
                       can be specified which joined by ",", valid values:
                       "name", "content", "license".
   --pkgmgr=PKGMGR     Specify backend package manager
   --local-pkgs-path=LOCAL_PKGS_PATH
                       Path for local pkgs(rpms) to be installed
   --compress-disk-image=COMPRESS_DISK_IMAGE
                       Sets the disk image compression. Note: The available
                       values might depend on the used filesystem type.
   --copy-kernel       Copy kernel files from image /boot directory to the
                       image output directory.

**Examples:**

::

   mic cr loop tizen.ks
   mic cr livecd tizen.ks --release=latest
   mic cr fs tizen.ks --local-pkgs-path=localrpm


Chroot
-------------------

This command is used to chroot inside the image. It's a great enhancement of the chroot command in the Linux system.

**Usage:**

::

  mic chroot(ch) <imgfile>

**Options:**

::

   -h, --help          show this help message and exit
   -s SAVETO, --saveto=SAVETO
                       Save the unpacked image to specified dir

**Examples:**

::

   mic ch loop.img
   mic ch tizen.iso
   mic ch -s tizenfs tizen.usbimg

Convert
-------------------

This command is used for converting an image to another format.

**Usage:**

::

   mic convert(cv) <imagefile> <destformat>

**Options:**

::

   -h, --help   Show this help message and exit
   -S, --shell  Launch shell before packaging the converted image

**Examples:**

::

   mic cv tizen.iso liveusb
   mic cv tizen.usbimg livecd
   mic cv --shell tizen.iso liveusb

What's BootStrap?
=================
When some important packages (like rpm) of the distribution (Tizen) is much different with native environment, the image created by native environment may be not bootable. Then a bootstrap environment will be required to create the image.

To create an image of one distribution (Tizen), MIC will create a bootstrap for this distribution (Tizen) at first, and then create the image by chrooting this bootstrap. This way is called "Bootstrap Mode" for MIC. And from 0.15 on, MIC will use this mode by default.

Advanced Usage
==============
The advanced usage is exclusively for bootstrap. Please skip it if you don't care about it.

The major reason for using bootstrap is if some important packages (like rpm) are customized a lot in the repo in which you want to create image, and mic must use the customized rpm to create images, or the images can't be booted. So MIC will create a bootstrap using the repo in the ks file at first, then create the image through chrooting, which can make MIC use the chroot environment with the customized rpm.

Now MIC will use bootstrap mode to create an image by default. To meet your requirement, you can also change the bootstrap settings (/etc/mic/bootstrap.conf):

::

  [main]
  distro_name = tizen  # which distro will be used for creating bootstrap
  rootdir = /var/tmp/mic-bootstrap  # which dir will be located when creating bootstrap
  enable = true # whether to enable the bootstrap mode
  [tizen] # the supported distro for creating bootstrap
  optional:  # which packages will be optional when creating bootstrap for this distro
  packages:  # which packages will be required when creating bootstrap for this distro


FAQ
============

Q: When creating an image, MIC shows "Error <creator>: URLGrabber error: http://www.example.com/latest/repos/oss/ia32/packages/repodata/repomd.xml"

A: Perhaps your network has some issues, or your proxy doesn't work. Try another proxy or find out the network issue.

Q: MIC complains "Error <repo>: found 1 resolver problem, abort!"

A: This is not an issue with MIC, but with the repo you used. Make sure the packages in the repo you used have proper dependencies.

Q: I used '-A i586' to create an i586 image, but it showed "nothing provided ....". What's wrong with it?

A: Use '-A i686'. i586 is lower than i686, so many packages will be missing from the installation.

Q: MIC shows in the log: "file /usr/share/whatever conflicts between attempted installs of somepackageA and somepackageB"

A: There are conflicts between some packages in the repo you used, but this is not an issue with MIC. Please make sure you are using a proper repo.

Q: Error shows: Command 'modprobe' is not available in Fedora 17.

A: In Fedora 17, when you use sudo, the PATH variable will be changed and you will lose some important paths. Run 'export PATH=/sbin:$PATH' before running MIC.

Known Issues
============

Nonsupport zypp backend in Fedora 17
------------------------------------
As libsat-solver changed to libsolv in Fedora 17, zypp backend can't work well for some dependency issues. Use yum as the backend in Fedora 17 distribution.

Unable to install syslinux bootloader
--------------------------------------

In some new Linux distributions, the "syslinux" package in their official software repositories is version 4.04. It causes a segfault, which is a fatal bug, and MIC will fail with syslinux installation errors.

The solution is to install the patched "syslinux" package in MeeGo or Tizen's tools repos, until the official released one has been fixed

Failed to create btrfs image in OpenSUSE
----------------------------------------

When creating a btrfs image in OpenSUSE, it hangs, showing image kernel panic. This issue impacts OpenSUSE distributions: 12.1, etc.

Failed to create an image (and the password in the repo URL contains "@")
--------------------------------------------------------------------------

MIC cannot support passwords that contain the char "@", but this will be fixed soon. Example:

::

  repo --name=Tizen-base --baseurl=https://username:passwd@example.com/arch/packages/ --save  --ssl_verify=no


Bug report and Contacts
=========================
The source code is tracked at github.com: https://github.com/01org/mic

Report issues for bugs or feature requests at JIRA: https://bugs.tizen.org, or at the github page directly.
