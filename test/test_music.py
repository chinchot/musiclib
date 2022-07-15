# -*- coding: latin-1 -*-
import unittest
from mock import patch
from app.media.music import ItunesInterface
import subprocess


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

    @patch('app.media.music.ItunesInterface.add_track_art_script')
    def test_add_track_art(self, mock_script):
        mock_script.return_value = (0, b'', b'')
        self.assertEqual(0, self.itunes_interface.add_track_art(track_name='dummy',
                                                                album_name='dummy', image_location='/'))

    @patch('app.media.music.ItunesInterface.add_track_art_script')
    def test_add_track_art_fail(self, mock_script):
        mock_script.return_value = (1, b'', b'ERROR')
        self.assertEqual(1, self.itunes_interface.add_track_art(track_name='dummy',
                                                                album_name='dummy', image_location='/'))


if __name__ == '__main__':
    unittest.main()
