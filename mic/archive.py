#
# Copyright (c) 2013 Intel Inc.
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

# Following messages should be disabled in pylint
#  * Used * or ** magic (W0142)
#  * Unused variable (W0612)
#  * Used builtin function (W0141)
#  * Invalid name for type (C0103)
#  * Popen has no '%s' member (E1101)
# pylint: disable=W0142, W0612, W0141, C0103, E1101

""" Compression and Archiving

Utility functions for creating archive files (tarballs, zip files, etc)
and compressing files (gzip, bzip2, lzop, etc)
"""

import os
import shutil
import tempfile
import subprocess

__all__ = [
            "get_compress_formats",
            "compress",
            "decompress",
            "get_archive_formats",
            "get_archive_suffixes",
            "make_archive",
            "extract_archive",
            "compressing",
            "packing",
          ]

def which(binary, path=None):
    """ Find 'binary' in the directories listed in 'path'

    @binary: the executable file to find
    @path: the suposed path to search for, use $PATH if None
    @retval: the absolute path if found, otherwise None
    """
    if path is None:
        path = os.environ["PATH"]
    for apath in path.split(os.pathsep):
        fpath = os.path.join(apath, binary)
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            return fpath
    return None

def _call_external(cmdln_or_args):
    """ Wapper for subprocess calls.

    @cmdln_or_args: command line to be joined before execution.
    @retval: a tuple (returncode, outdata, errdata).
    """
    if isinstance(cmdln_or_args, list):
        shell = False
    else:
        shell = True

    proc = subprocess.Popen(cmdln_or_args, shell=shell,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    (outdata, errdata) = proc.communicate()

    return (proc.returncode, outdata, errdata)

def _do_gzip(input_name, compression=True):
    """ Compress/decompress the file with 'gzip' utility.

    @input_name: the file name to compress/decompress
    @compress: True for compressing, False for decompressing
    @retval: the path of the compressed/decompressed file
    """
    if which("pigz") is not None:
        compressor = "pigz"
    else:
        compressor = "gzip"

    if compression:
        cmdln = [compressor, "-f", input_name]
    else:
        cmdln = [compressor, "-d", "-f", input_name]

    _call_external(cmdln)

    if compression:
        output_name = input_name + ".gz"
    else:
        # suppose that file name is suffixed with ".gz"
        output_name = os.path.splitext(input_name)[0]

    return output_name

def _do_bzip2(input_name, compression=True):
    """ Compress/decompress the file with 'bzip2' utility.

    @input_name: the file name to compress/decompress
    @compress: True for compressing, False for decompressing
    @retval: the path of the compressed/decompressed file
    """
    if which("pbzip2") is not None:
        compressor = "pbzip2"
    else:
        compressor = "bzip2"

    if compression:
        cmdln = [compressor, "-f", input_name]
    else:
        cmdln = [compressor, "-d", "-f", input_name]

    _call_external(cmdln)

    if compression:
        output_name = input_name + ".bz2"
    else:
        # suppose that file name is suffixed with ".bz2"
        output_name = os.path.splitext(input_name)[0]

    return output_name

def _do_lzop(input_name, compression=True):
    """ Compress/decompress the file with 'lzop' utility.

    @input_name: the file name to compress/decompress
    @compress: True for compressing, False for decompressing
    @retval: the path of the compressed/decompressed file
    """
    compressor = "lzop"

    if compression:
        cmdln = [compressor, "-f", "-U", input_name]
    else:
        cmdln = [compressor, "-d", "-f", "-U", input_name]

    _call_external(cmdln)

    if compression:
        output_name = input_name + ".lzo"
    else:
        # suppose that file name is suffixed with ".lzo"
        output_name = os.path.splitext(input_name)[0]

    return output_name

_COMPRESS_SUFFIXES = {
    ".lzo"     : [".lzo"],
    ".gz"      : [".gz"],
    ".bz2"     : [".bz2", ".bz"],
    ".tar.lzo" : [".tar.lzo", ".tzo"],
    ".tar.gz"  : [".tar.gz", ".tgz", ".taz"],
    ".tar.bz2" : [".tar.bz2", ".tbz", ".tbz2", ".tar.bz"],
}

_COMPRESS_FORMATS = {
    "gz" :  _do_gzip,
    "bz2":  _do_bzip2,
    "lzo":  _do_lzop,
}

def get_compress_formats():
    """ Get the list of the supported compression formats

    @retval: a list contained supported compress formats
    """
    return _COMPRESS_FORMATS.keys()

def get_compress_suffixes():
    """ Get the list of the support suffixes

    @retval: a list contained all suffixes
    """
    suffixes = []
    for key in _COMPRESS_SUFFIXES.keys():
        suffix = _COMPRESS_SUFFIXES[key]
        if (suffix):
            suffixes.extend(suffix)

    return suffixes

def compress(file_path, compress_format):
    """ Compress a given file

    @file_path: the path of the file to compress
    @compress_format: the compression format
    @retval: the path of the compressed file
    """
    if not os.path.isfile(file_path):
        raise OSError, "can't compress a file not existed: '%s'" % file_path

    try:
        func = _COMPRESS_FORMATS[compress_format]
    except KeyError:
        raise ValueError, "unknown compress format '%s'" % compress_format
    return func(file_path, True)

def decompress(file_path, decompress_format=None):
    """ Decompess a give file

    @file_path: the path of the file to decompress
    @decompress_format: the format for decompression, None for auto detection
    @retval: the path of the decompressed file
    """
    if not os.path.isfile(file_path):
        raise OSError, "can't decompress a file not existed: '%s'" % file_path

    (file_name, file_ext) = os.path.splitext(file_path)
    for key, suffixes in _COMPRESS_SUFFIXES.iteritems():
        if file_ext in suffixes:
            file_ext = key
            break

    if file_path != (file_name + file_ext):
        shutil.move(file_path, file_name + file_ext)
        file_path  = file_name + file_ext

    if not decompress_format:
        decompress_format = os.path.splitext(file_path)[1].lstrip(".")

    try:
        func = _COMPRESS_FORMATS[decompress_format]
    except KeyError:
        raise ValueError, "unknown decompress format '%s'" % decompress_format
    return func(file_path, False)


def _do_tar(archive_name, target_name):
    """ Archive the directory or the file with 'tar' utility

    @archive_name: the name of the tarball file
    @target_name: the name of the target to tar
    @retval: the path of the archived file
    """
    if os.path.isdir(target_name):
        target_dir = target_name
        target_name = "."
    else:
        target_dir = os.path.dirname(target_name)
        target_name = os.path.basename(target_name)

    cmdln = ["tar", "-S", "-C", target_dir, "-cf", archive_name, target_name]

    _call_external(cmdln)

    return archive_name

def _do_untar(archive_name, target_dir=None):
    """ Unarchive the archived file with 'tar' utility

    @archive_name: the name of the archived file
    @target_dir: the directory which the target locates
    @retval: the target directory
    """
    if not target_dir:
        target_dir = os.getcwd()

    cmdln = ["tar", "-S", "-C", target_dir, "-xf", archive_name]

    _call_external(cmdln)

    return target_dir

def _imp_tarfile(archive_name, target_name):
    """ Archive the directory or the file with tarfile module

    @archive_name: the name of the tarball file
    @target_name: the name of the target to tar
    @retval: the path of the archived file
    """
    import tarfile
    tar = tarfile.open(archive_name, 'w')
    if os.path.isdir(target_name):
        for child in os.listdir(target_name):
            tar.add(os.path.join(target_name, child), child)
    else:
        tar.add(target_name, os.path.basename(target_name))

    tar.close()
    return archive_name

def _make_tarball(archive_name, target_name, compressor=None):
    """ Create a tarball from all the files under 'target_name' or itself.

    @archive_name: the name of the archived file to create
    @target_name: the directory or the file name to archive
    @compressor: callback function to compress the tarball
    @retval: indicate the compressing result
    """
    archive_dir = os.path.dirname(archive_name)

    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    tarball_name = tempfile.mktemp(suffix=".tar", dir=archive_dir)
    if which("tar") is not None:
        _do_tar(tarball_name, target_name)
    else:
        _imp_tarfile(tarball_name, target_name)

    if compressor:
        tarball_name = compressor(tarball_name, True)

    shutil.move(tarball_name, archive_name)

    return os.path.exists(archive_name)

def _extract_tarball(archive_name, target_dir, compressor=None):
    """ Extract a tarball to a target directory

    @archive_name: the name of the archived file to extract
    @target_dir: the directory of the extracted target
    @retval: indicte the untar result
    """

    _do_untar(archive_name, target_dir)

    return not os.path.exists(archive_name)

def _make_zipfile(archive_name, target_name):
    """ Create a zip file from all the files under 'target_name' or itself.

    @archive_name: the name of the archived file
    @target_name: the directory or the file name to archive
    @retval: indicate the archiving result
    """
    archive_dir = os.path.dirname(archive_name)

    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    import zipfile

    arv = zipfile.ZipFile(archive_name, 'w', compression=zipfile.ZIP_DEFLATED)

    if os.path.isdir(target_name):
        for dirpath, dirname, filenames in os.walk(target_name):
            for filename in filenames:
                filepath = os.path.normpath(os.path.join(dirpath, filename))
                arcname = os.path.relpath(filepath, target_name)
                if os.path.isfile(filepath):
                    arv.write(filepath, arcname)
    else:
        arv.write(target_name, os.path.basename(target_name))

    arv.close()

    return os.path.exists(archive_name)

_ARCHIVE_SUFFIXES = {
    "zip"   : [".zip"],
    "tar"   : [".tar"],
    "lzotar": [".tzo", ".tar.lzo"],
    "gztar" : [".tgz", ".taz", ".tar.gz"],
    "bztar" : [".tbz", ".tbz2", ".tar.bz", ".tar.bz2"],
}

_ARCHIVE_FORMATS = {
    "zip"   : ( _make_zipfile, {} ),
    "tar"   : ( _make_tarball, {"compressor" : None} ),
    "lzotar": ( _make_tarball, {"compressor" : _do_lzop} ),
    "gztar" : ( _make_tarball, {"compressor" : _do_gzip} ),
    "bztar" : ( _make_tarball, {"compressor" : _do_bzip2} ),
}

def get_archive_formats():
    """ Get the list of the supported formats for archiving

    @retval: a list contained archive formats
    """
    return _ARCHIVE_FORMATS.keys()

def get_archive_suffixes():
    """ Get the list of the support suffixes

    @retval: a list contained all suffixes
    """
    suffixes = []
    for name in _ARCHIVE_FORMATS.keys():
        suffix = _ARCHIVE_SUFFIXES.get(name, None)
        if (suffix):
            suffixes.extend(suffix)

    return suffixes

def make_archive(archive_name, target_name):
    """ Create an archive file (eg. tar or zip).

    @archive_name: the name of the archived file
    @target_name: the directory or the file to archive
    @retval: the archiving result
    """
    for aformat, suffixes in _ARCHIVE_SUFFIXES.iteritems():
        if filter(archive_name.endswith, suffixes):
            archive_format = aformat
            break
    else:
        raise ValueError, "unknown archive suffix '%s'" % archive_name

    try:
        func, kwargs = _ARCHIVE_FORMATS[archive_format]
    except KeyError:
        raise ValueError, "unknown archive format '%s'" % archive_format

    return func(archive_name, target_name, **kwargs)

def extract_archive(archive_name, target_name):
    """ Extract the given file

    @archive_name: the name of the archived file to extract
    @target_name: the directory name where the target locates
    @retval: the extracting result
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    return _extract_tarball(archive_name, target_name)

packing = make_archive
compressing = compress

