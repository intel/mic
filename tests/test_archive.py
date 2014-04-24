"""
It is used to test mic/archive.py
"""


import os
import shutil
import unittest

from mic import archive


class ArchiveTest(unittest.TestCase):
    """
        test pulic methods in archive.py
    """
    def setUp(self):
        """Create files and directories for later use"""
        self.relative_file = './sdfb.gxdf.bzws.zzz'
        abs_file = '/tmp/adsdfb.gxdf.bzws.zzz'
        bare_file = 'abc.def.bz.zzz'
        self.relative_dir = './sdf.zzz'
        abs_dir = '/tmp/asdf.zzz'
        bare_dir = 'abd.zzz'
        self.wrong_format_file = './sdbs.werxdf.bz.zzz'

        self.files = [self.relative_file, abs_file, bare_file]
        self.dirs = [self.relative_dir, abs_dir, bare_dir]
        for file_item in self.files:
            os.system('touch %s' % file_item)

        for dir_item in self.dirs:
            self.create_dir(dir_item)
            shutil.copy(self.relative_file, '%s/1.txt' % dir_item)
            shutil.copy(self.relative_file, '%s/2.txt' % dir_item)
            self.create_dir('%s/dir1' % dir_item)
            self.create_dir('%s/dir2' % dir_item)

    def tearDown(self):
        """Clean up unuseful file and directory """
        try:
            for file_item in self.files:
                os.remove(file_item)
            for dir_item in self.dirs:
                shutil.rmtree(dir_item, ignore_errors=True)
        except OSError:
            pass

    def create_dir(self, dir_name):
        """Create directories and ignore any erros """
        try:
            os.makedirs(dir_name)
        except OSError:
            pass

    def test_get_compress_formats(self):
        """Test get compress format """
        compress_list = archive.get_compress_formats()
        compress_list.sort()
        self.assertEqual(compress_list, ['bz2', 'gz', 'lzo'])

    def test_compress_negtive_file_path_is_required(self):
        """Test if the first parameter: file path is empty"""
        with self.assertRaises(OSError):
            archive.compress('', 'bz2')

    def test_compress_negtive_compress_format_is_required(self):
        """Test if the second parameter: compress format is empty"""
        with self.assertRaises(ValueError):
            archive.compress(self.relative_file, '')

    def test_compress_negtive_parameters_are_all_required(self):
        """Test if two parameters are both empty"""
        with self.assertRaises(OSError):
            archive.compress('', '')

    def test_compress_negtive_file_not_exist(self):
        """Test target file does not exist"""
        with self.assertRaises(OSError):
            archive.compress('a.py', 'bz2')

    def test_compress_negtive_file_is_dir(self):
        """Test target is one direcoty, which is not supported"""
        with self.assertRaises(OSError):
            archive.compress(self.relative_dir, 'bz2')

    def test_compress_negtive_wrong_compress_format(self):
        """Test wrong compress format"""
        with self.assertRaises(ValueError):
            archive.compress(self.relative_file, 'bzip2')

    def _compress_negtive_gz_command_not_exists(self):
        #TODO: test if command like 'pigz', 'gzip' does not exist
        pass

    def _compress_negtive_lzo_command_not_exists(self):
        #TODO: test if command 'lzop' does not exist
        pass

    def _compress_negtive_bz2_command_not_exists(self):
        #TODO: test if command like 'pbzip2', 'bzip2' does not exist
        pass

    def test_compress_gz(self):
        """Test compress format: gz"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'gz')
            self.assertEqual('%s.gz' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            os.remove(output_name)

    def test_compress_bz2(self):
        """Test compress format: bz2"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'bz2')
            self.assertEqual('%s.bz2' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            os.remove(output_name)

    def _test_compress_lzo(self):
        """Test compress format: lzo"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'lzo')
            self.assertEqual('%s.lzo' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            os.remove(output_name)

    def test_decompress_negtive_file_path_is_required(self):
        """Test if the first parameter: file to be uncompressed is empty"""
        with self.assertRaises(OSError):
            archive.decompress('', 'bz')

    def test_decompress_compress_format_is_empty(self):
        """Test if the second parameter: compress format is empty string"""
        output_name = archive.compress(self.relative_file, 'gz')
        self.assertEqual('%s.gz' % self.relative_file, output_name)
        self.assertTrue(os.path.exists(output_name))
        self.assertFalse(os.path.exists(self.relative_file))
        archive.decompress(output_name, '')
        self.assertTrue(os.path.exists(self.relative_file))

    def test_decompress_negtive_parameters_are_empty(self):
        """Test if two parameters are both empty string"""
        with self.assertRaises(OSError):
            archive.decompress('', '')

    def test_decompress_negtive_file_not_exist(self):
        """Test decompress target does not exist"""
        with self.assertRaises(OSError):
            archive.decompress('tresa.py', 'bz2')

    def test_decompress_negtive_path_is_dir(self):
        """Test decompress target is a directory"""
        with self.assertRaises(OSError):
            archive.decompress(self.relative_dir, 'bz2')

    def _decompress_negtive_not_corresponding(self):
        # TODO: test if path is .lzo, but given format is bz2
        pass

    def test_decompress_negtive_wrong_compress_format(self):
        """Test wrong decompress format"""
        with self.assertRaises(ValueError):
            archive.decompress(self.relative_file, 'bzip2')

    def test_decompress_negtive_wrong_file_format(self):
        """Test wrong target format"""
        with self.assertRaises(Exception):
            archive.decompress(self.wrong_format_file, 'bz2')

    def test_decompress_gz(self):
        """Test decompress
            Format: gz
            both two parameters are given, one is target file,
            the other is corresponding compress format"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'gz')
            self.assertEqual('%s.gz' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            self.assertFalse(os.path.exists(file_item))
            archive.decompress(output_name, 'gz')
            self.assertTrue(os.path.exists(file_item))

    def test_decompress_gz_no_compress_format(self):
        """Test decompress
            Format: gz
            one parameters is given, only target file"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'gz')
            self.assertEqual('%s.gz' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            self.assertFalse(os.path.exists(file_item))
            archive.decompress(output_name)
            self.assertTrue(os.path.exists(file_item))

    def test_decompress_bz2(self):
        """Test decompress
            Format: bz2
            both two parameters are given, one is target file,
            the other is corresponding compress format"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'bz2')
            self.assertEqual('%s.bz2' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            self.assertFalse(os.path.exists(file_item))
            archive.decompress(output_name, 'bz2')
            self.assertTrue(os.path.exists(file_item))

    def test_decompress_bz2_no_compress_format(self):
        """Test decompress
            Format: bz2
            one parameters is given, only target file"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'bz2')
            self.assertEqual('%s.bz2' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            self.assertFalse(os.path.exists(file_item))
            archive.decompress(output_name)
            self.assertTrue(os.path.exists(file_item))

    def _test_decompress_lzo(self):
        """Test decompress
            Format: lzo
            both two parameters are given, one is target file,
            the other is corresponding compress format"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'lzo')
            self.assertEqual('%s.lzo' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            self.assertFalse(os.path.exists(file_item))
            archive.decompress(output_name, 'lzo')
            self.assertTrue(os.path.exists(file_item))

    def _test_decompress_lzo_no_compress_format(self):
        """Test decompress
            Format: lzo
            one parameters is given, only target file"""
        for file_item in self.files:
            output_name = archive.compress(file_item, 'lzo')
            self.assertEqual('%s.lzo' % file_item, output_name)
            self.assertTrue(os.path.exists(output_name))
            self.assertFalse(os.path.exists(file_item))
            archive.decompress(output_name)
            self.assertTrue(os.path.exists(file_item))

    def test_get_archive_formats(self):
        """Test get archive format"""
        archive_formats = archive.get_archive_formats()
        archive_formats.sort()
        self.assertEqual(archive_formats,
                        ["bztar", "gztar", "lzotar", "tar", 'zip'])

    def test_get_archive_suffixes(self):
        """Test get archive suffixes"""
        archive_suffixes = archive.get_archive_suffixes()
        archive_suffixes.sort()

        self.assertEqual(archive_suffixes,
                         ['.tar', '.tar.bz', '.tar.bz2', '.tar.gz', '.tar.lzo',
                         '.taz', '.tbz', '.tbz2', '.tgz', '.tzo', '.zip'])

    def test_make_archive_negtive_archive_name_is_required(self):
        """Test if first parameter: file path is empty"""
        with self.assertRaises(Exception):
            archive.make_archive('', self.relative_dir)

    def test_extract_archive_negtive_archive_name_is_required(self):
        """Test if first parameter: file path is empty"""
        with self.assertRaises(Exception):
            archive.extract_archive('', self.relative_dir)

    def test_make_archive_negtive_target_name_is_required(self):
        """Test if second parameter: target name is empty"""
        with self.assertRaises(Exception):
            archive.make_archive('a.zip', '')

    def _extract_archive_negtive_target_name_is_required(self):
        # Not sure if the current dir will be used ?
        # TODO:
        pass

    def test_make_archive_negtive_parameters_are_empty(self):
        """Test if both parameters are empty"""
        with self.assertRaises(Exception):
            archive.make_archive('', '')

    def test_extract_archive_negtive_parameters_are_empty(self):
        """Test if both parameters are empty"""
        with self.assertRaises(Exception):
            archive.extract_archive('', '')

    def test_make_archive_negtive_target_path_not_exists(self):
        """Test if file path does not exist"""
        fake_file = 'abcdfsdf'
        with self.assertRaises(Exception):
            archive.make_archive('a.tar', fake_file)

        with self.assertRaises(Exception):
            archive.make_archive('a.zip', fake_file)

    def test_extract_archive_negtive_path_not_exists(self):
        """Test if file path does not exist"""
        fake_file = 'abcdfsdf'
        with self.assertRaises(Exception):
            archive.extract_archive(fake_file, self.relative_dir)

    def test_extract_archive_negtive_target_is_file(self):
        """Test if the extract target is file"""
        out_file = '%s.tar' % self.relative_dir
        self.assertTrue(archive.make_archive(out_file, self.relative_dir))
        self.assertTrue(os.path.exists(out_file))
        with self.assertRaises(Exception):
            archive.extract_archive(out_file, self.relative_file)
        os.remove(out_file)

    def test_make_archive_wrong_format(self):
        """Test wrong make_archive format"""
        with self.assertRaises(Exception):
            archive.make_archive('a.sfsfrwe', self.relative_dir)

    def test_make_archive_tar_with_different_name(self):
        """ Test make_archive format: tar
            It packs the source with another name"""
        for item in self.files + self.dirs:
            out_file = 'abcd.tar'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_tar(self):
        """ Test make_archive format: tar"""
        for item in self.files + self.dirs:
            out_file = '%s.tar' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_extract_archive_tar(self):
        """ Test extract format: tar"""
        for item in self.files:
            out_file = '%s.tar' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(
                                           out_dir,
                                           os.path.basename(item))))
            shutil.rmtree(out_dir)

        for item in self.dirs:
            out_file = '%s.tar' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, '1.txt')))
            self.assertTrue(os.path.exists(os.path.join(out_dir, '2.txt')))
            self.assertTrue(os.path.exists(os.path.join(out_dir, 'dir1')))
            self.assertTrue(os.path.exists(os.path.join(out_dir, 'dir2')))
            shutil.rmtree(out_dir)

    def test_make_archive_zip_with_different_name(self):
        """ Test make_archive format: zip
            It packs the source with another name"""
        for item in self.files + self.dirs:
            out_file = 'a.zip'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_zip(self):
        """ Test make_archive format: zip"""
        for item in self.files + self.dirs:
            out_file = '%s.zip' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_zip(self):
        """ Test extract archive format: zip"""
        for item in self.files + self.dirs:
            out_file = '%s.zip' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def _test_make_archive_tzo_with_different_name(self):
        """ Test make_archive format: tzo
            It packs the source with another name"""
        for item in self.files + self.dirs:
            out_file = 'abc.tzo'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _test_make_archive_tzo(self):
        """ Test make_archive format: tzo"""
        for item in self.files + self.dirs:
            out_file = '%s.tzo' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_tzo(self):
        """ Test extract format: tzo"""
        for item in self.files + self.dirs:
            out_file = '%s.tzo' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def _test_make_archive_tar_lzo_with_different_name(self):
        """ Test make_archive format: lzo
            It packs the source with another name"""
        for item in self.files + self.dirs:
            out_file = 'abc.tar.lzo'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _test_make_archive_tar_lzo(self):
        """ Test make_archive format: lzo"""
        for item in self.files + self.dirs:
            out_file = '%s.tar.lzo' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_tar_lzo(self):
        """ Test extract_archive format: lzo"""
        for item in self.files + self.dirs:
            out_file = '%s.tar.lzo' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def test_make_archive_taz_with_different_name(self):
        """ Test make_archive format: taz
            It packs the source with another name"""
        for item in self.files + self.dirs:
            out_file = 'abcd.taz'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_taz(self):
        """ Test make_archive format: taz"""
        for item in self.files + self.dirs:
            out_file = '%s.taz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_taz(self):
        """ Test extract archive format: taz"""
        for item in self.files + self.dirs:
            out_file = '%s.taz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def test_make_archive_tgz_with_different_name(self):
        """ Test make_archive format: tgz
            It packs the source with anotehr name"""
        for item in self.files + self.dirs:
            out_file = 'abc.tgz'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_tgz(self):
        """ Test make_archive format: tgz"""
        for item in self.files + self.dirs:
            out_file = '%s.tgz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_tgz(self):
        """ Test extract archive format: tgz"""
        for item in self.files + self.dirs:
            out_file = '%s.tgz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def test_make_archive_tar_gz_with_different_name(self):
        """ Test make_archive format: tar.gz
            It packs the source with another name"""
        for item in self.files + self.dirs:
            out_file = 'erwe.tar.gz'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_tar_gz(self):
        """ Test make_archive format: tar.gz"""
        for item in self.files + self.dirs:
            out_file = '%s.tar.gz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_tar_gz(self):
        """ Test extract archive format: tar.gz"""
        for item in self.files + self.dirs:
            out_file = '%s.tar.gz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def test_make_archive_tbz_with_different_name(self):
        """ Test make_archive format: tbz
            It packs the source with another name"""
        for item in self.files + self.dirs:
            out_file = 'sdfsd.tbz'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_tbz(self):
        """ Test make_archive format: tbz"""
        for item in self.files + self.dirs:
            out_file = '%s.tbz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_tbz(self):
        """ Test extract format: tbz"""
        for item in self.files + self.dirs:
            out_file = '%s.tbz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def test_make_archive_tbz2_with_different_name(self):
        """ Test make_archive format: tbz2
            It packs source with another name"""
        for item in self.files + self.dirs:
            out_file = 'sfsfd.tbz2'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_tbz2(self):
        """ Test make_archive format: tbz2"""
        for item in self.files + self.dirs:
            out_file = '%s.tbz2' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_tbz2(self):
        """ Test extract format: tbz2"""
        for item in self.files + self.dirs:
            out_file = '%s.tbz2' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def test_make_archive_tar_bz_with_different_name(self):
        """ Test make_archive format: tar.bz
            It packs source with antoher name"""
        for item in self.files + self.dirs:
            out_file = 'sdf.tar.bz'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_tar_bz(self):
        """ Test make_archive format: tar.bz"""
        for item in self.files + self.dirs:
            out_file = '%s.tar.bz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_tar_bz(self):
        """ Test extract format: tar.bz"""
        for item in self.files + self.dirs:
            out_file = '%s.tar.bz' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

    def test_make_archive_tar_bz2_with_different_name(self):
        """ Test make_archive format: tar.bz2
            it packs the source with another name """
        for item in self.files + self.dirs:
            out_file = 'df.tar.bz2'
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def test_make_archive_tar_bz2(self):
        """ Test make_archive format: tar.bz2"""
        for item in self.files + self.dirs:
            out_file = '%s.tar.bz2' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))
            os.remove(out_file)

    def _extract_archive_tar_bz2(self):
        """ Test extract format: tar.bz2"""
        for item in self.files + self.dirs:
            out_file = '%s.tar.bz2' % item
            self.assertTrue(archive.make_archive(out_file, item))
            self.assertTrue(os.path.exists(out_file))

            out_dir = 'un_tar_dir'
            archive.extract_archive(out_file, out_dir)
            self.assertTrue(os.path.exists(os.path.join(out_dir, item)))
            shutil.rmtree(out_dir)

if __name__ == "__main__":
    unittest.main()
