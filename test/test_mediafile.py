import unittest
import mock
import subprocess
from musiclib import MediaFile


class TestMediaFile(unittest.TestCase):
    def setUp(self):
        self.media_file = MediaFile()

    def test_instance(self):
        self.assertIsInstance(self.media_file, MediaFile)

    # test get_metadata
    @mock.patch.object(subprocess, 'Popen', autospec=True)
    def test_get_metadata(self, mock_popen):
        process_mock = mock.Mock()
        attrs = {'returncode': 0, 'communicate.return_value':
            ['    title           : Drones\n    artist          : Muse\n    album           : Drones\n']}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        result = {'album': 'Drones', 'alt_album': 'Drones', 'alt_title': 'Drones',
                  'target_directory': 'fixtures/music_file/Processed/Muse/Drones', 'artist': 'Muse',
                  'title': 'Drones', 'exit_code': 0, 'alt_artist': 'Muse',
                  'target_file': 'fixtures/music_file/Processed/Muse/Drones/Muse-Drones copy.m4a',
                  'source_file': 'fixtures/music_file/Muse-Drones copy.m4a'}
        self.assertEqual(result, self.media_file.get_metadata('fixtures/music_file/Muse-Drones copy.m4a'))

    # test valid_metadata
    @mock.patch.object(subprocess, 'Popen', autospec=True)
    def test_valid_metadata(self, mock_popen):
        process_mock = mock.Mock()
        attrs = {'returncode': 0, 'communicate.return_value':
            ['    title           : Drones\n    artist          : Muse\n    album           : Drones\n']}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        self.media_file.get_metadata('fixtures/music_file/Muse-Drones copy.m4a')
        self.assertTrue(self.media_file.valid_metadata())

    @mock.patch.object(subprocess, 'Popen', autospec=True)
    def test_invalid_metadata(self, mock_popen):
        process_mock = mock.Mock()
        attrs = {'returncode': 1, 'communicate.return_value':
            ['    title           : Drones\n    artist          : Muse\n    album           : Drones\n']}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        self.media_file.get_metadata('fixtures/music_file/Muse-Drones copy.m4a')
        self.assertFalse(self.media_file.valid_metadata())


if __name__ == '__main__':
    unittest.main()
