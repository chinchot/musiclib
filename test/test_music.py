# -*- coding: latin-1 -*-
import unittest
import mock
from app.media.music import ItunesInterface
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


if __name__ == '__main__':
    unittest.main()
