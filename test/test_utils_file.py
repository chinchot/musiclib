import unittest
import mock
import os
from app.utils.file import FileUtility, ErrorNotAbleToCreateDir


class TestFileUtility(unittest.TestCase):
    def setUp(self):
        self.file_utility = FileUtility()

    def test_instance(self):
        self.assertIsInstance(self.file_utility, FileUtility)

    def test_create_directory(self):
        dir_name = 'fixtures/dummy_dir'
        try:
            os.removedirs(dir_name)
        except OSError:
            pass
        self.file_utility.create_directory(dir_name=dir_name)
        self.assertTrue(os.path.exists(dir_name))

    def test_create_existing_directory(self):
        dir_name = 'fixtures/copy'
        self.file_utility.create_directory(dir_name=dir_name)
        self.assertTrue(os.path.exists(dir_name))

    @mock.patch('os.makedirs')
    def test_create_directory_io_error(self, mock_makedir):
        dir_name = 'fixtures/non_existent'
        mock_makedir.side_effect = IOError
        self.assertRaises(ErrorNotAbleToCreateDir, self.file_utility.create_directory, dir_name=dir_name)

    def test_create_directory_over_file(self):
        dir_name = 'fixtures/dummy_music/dummy1.m4a'
        self.assertRaises(ErrorNotAbleToCreateDir, self.file_utility.create_directory, dir_name=dir_name)


if __name__ == '__main__':
    unittest.main()
