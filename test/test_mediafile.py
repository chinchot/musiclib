import unittest
import mock
import subprocess
from app.media.file import MediaFile

expected_metadata = {'title': 'Drones', 'artist': 'Muse', 'album': 'Drones', 'exit_code': 0,
                     'source_file': 'fixtures/music_file/Muse - Drones.m4a', 'alt_album': 'Drones',
                     'alt_artist': 'Muse', 'alt_title': 'Drones',
                     'target_directory': 'fixtures/music_file/../Processed/Drones',
                     'target_file': 'fixtures/music_file/../Processed/Drones/Muse - Drones.m4a'}


class TestMediaFile(unittest.TestCase):
    def setUp(self):
        self.media_file = MediaFile()

    def test_instance(self):
        self.assertIsInstance(self.media_file, MediaFile)

    # test get_metadata
    @mock.patch.object(subprocess, 'Popen', autospec=True)
    def test_get_metadata(self, mock_popen):
        process_mock = mock.Mock()
        attrs = {'returncode': 0,
                 'communicate.return_value':
                     [b'    title           : Drones\n    artist          : Muse\n    album           : Drones\n']}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        result = {'album': 'Drones', 'alt_album': 'Drones', 'alt_title': 'Drones',
                  'target_directory': 'fixtures/music_file/../Processed/Drones', 'artist': 'Muse',
                  'title': 'Drones', 'exit_code': 0, 'alt_artist': 'Muse',
                  'target_file': 'fixtures/music_file/../Processed/Drones/Muse-Drones copy.m4a',
                  'source_file': 'fixtures/music_file/Muse-Drones copy.m4a'}
        self.assertEqual(result, self.media_file.get_metadata('fixtures/music_file/Muse-Drones copy.m4a'))

    # test valid_metadata
    @mock.patch.object(subprocess, 'Popen', autospec=True)
    def test_valid_metadata(self, mock_popen):
        process_mock = mock.Mock()
        attrs = {'returncode': 0,
                 'communicate.return_value':
                     [b'    title           : Drones\n    artist          : Muse\n    album           : Drones\n']}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        self.media_file.get_metadata('fixtures/music_file/Muse-Drones copy.m4a')
        self.assertTrue(self.media_file.valid_metadata)

    @mock.patch.object(subprocess, 'Popen', autospec=True)
    def test_invalid_metadata(self, mock_popen):
        process_mock = mock.Mock()
        attrs = {'returncode': 1,
                 'communicate.return_value':
                     [b'    title           : Drones\n    artist          : Muse\n    album           : Drones\n']}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock
        self.media_file.get_metadata('fixtures/music_file/Muse-Drones copy.m4a')
        self.assertFalse(self.media_file.valid_metadata)

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
