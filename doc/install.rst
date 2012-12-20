MIC Installation
================

.. contents:: Table of Contents

Overview
--------
Many mainstream Linux distributions are supported in Tizen Tools repository, including:

- Ubuntu (12.10, 12.04, 11.10)
- openSUSE (12.2, 12.1)
- Feodra (17, 16)

Ubuntu Installation
-------------------
1. Append Tizen Tools Repository, example: Ubuntu 12.04
::

   $ sudo vi /etc/apt/sources.list

Append this line:
::

   deb http://download.tizen.org/tools/latest-release/Ubuntu_12.04/ /

2. Install or upgrade tools
::

  $ sudo apt-get update
  $ sudo apt-get install mic

OpenSUSE Installation
---------------------
1. Adding Tizen Tools Repository, example: openSUSE12.1
::

  $ sudo zypper addrepo http://download.tizen.org/tools/latest-release/openSUSE_12.1/ tools

2. Install tools
::

  $ sudo zypper refresh
  $ sudo zypper install mic

3. Upgrade tools
::

  $ sudo zypper refresh
  $ sudo zypper update mic

Fedora Installation
-------------------
1. Adding Tizen Tools Repository, example: Fedora17
::

  $ sudo wget -O /etc/yum.repos.d/tools.repo http://download.tizen.org/tools/latest-release/Fedora_17/Tools.repo

2. Install tools
::

  $ sudo yum makecache
  $ sudo yum install mic

3. Upgrade tools
::

  $ sudo yum makecache
  $ sudo yum update mic

Source Installation
-------------------
To make your source insatllation work, you should make sure you have installed all required depends of mic. Then run 'make install' to install MIC from source:
::

  $ cd mic
  $ sudo make install
