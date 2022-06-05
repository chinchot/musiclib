# -*- coding: latin-1 -*-
import unittest
import mock
import os
from musiclib import FileUtility
from musiclib import StringUtil
from musiclib import ItunesInterface
from musiclib import MusicLib
from musiclib import MediaFile
import subprocess


@mock.patch.object(subprocess, 'Popen', autospec=True)
class TestItunesInterface(unittest.TestCase):
    def setUp(self):
        self.itunes_interface = ItunesInterface()

    def test_instance(self, mock_popen):
        self.assertIsInstance(self.itunes_interface, ItunesInterface)

    def test_file_has_been_added(self, mock_popen):
        self.add_file_error_code(mock_popen, 0)

    def test_file_added_error(self, mock_popen):
        self.add_file_error_code(mock_popen, 1)

    def add_file_error_code(self, mock_popen, error_code):
        process_mock = mock.Mock()
        attrs = {'returncode': error_code, 'communicate.return_value': ('output', 'error')}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        error_code = self.itunes_interface.add_file('file_name')
        self.assertEqual(error_code, error_code)


class TestStringUtility(unittest.TestCase):
    def setUp(self):
        self.string_utility = StringUtil()

    def test_instance(self):
        self.assertIsInstance(self.string_utility, StringUtil)

    def test_no_change_in_file_name(self):
        self.assertEqual(self.string_utility.create_slug('file_name.txt'), 'file_name.txt')

    def test_change_in_file_name(self):
        self.assertEqual(self.string_utility.create_slug('file#name.txt'), 'filename.txt')


class TestFileUtility(unittest.TestCase):
    def setUp(self):
        self.file_utility = FileUtility()

    def test_instance(self):
        self.assertIsInstance(self.file_utility, FileUtility)

    def test_create_new_directory(self):
        try:
            os.rmdir('new_dir_test')
        except OSError:
            pass
        self.assertTrue(self.file_utility.create_directory('new_dir_test'))

    def test_create_existing_directory(self):
        try:
            os.mkdir('existing_dir')
        except OSError:
            pass
        self.assertTrue(self.file_utility.create_directory('existing_dir'))

    def test_try_create_directory_on_existing_file_name(self):
        try:
            with open('existing_file_name', 'w') as file_handler:
                file_handler.write('')
        except IOError:
            pass
        self.assertFalse(self.file_utility.create_directory('existing_file_name'))


class TestMusicLib(unittest.TestCase):
    def setUp(self):
        self.music_lib = MusicLib()

    def test_instance(self):
        self.assertIsInstance(self.music_lib, MusicLib)


class TestMediaFile(unittest.TestCase):
    def setUp(self):
        self.media_file = MediaFile()

    def test_instance(self):
        self.assertIsInstance(self.media_file, MediaFile)

    def test_build_add_metadata_command(self):
        track_info = {'number': 1}
        self.media_file.metadata['source_file'] = 'dummy'
        self.media_file.metadata['target_file'] = 'dummy'
        command = self.media_file._build_add_metadata_command(track_info, False)
        self.assertEqual(11, len(command))
        command = self.media_file._build_add_metadata_command(track_info, True)
        self.assertEqual(13, len(command))


if __name__ == '__main__':
    unittest.main()
