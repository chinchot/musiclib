# -*- coding: latin-1 -*-
import unittest
import mock
from musiclib import MusicLib, ErrorDuringProcessFile


class TestMusicLib(unittest.TestCase):
    def setUp(self):
        self.music_lib = MusicLib()

    def test_instance(self):
        self.assertIsInstance(self.music_lib, MusicLib)

    @mock.patch('musiclib.MusicLib.process_file')
    def test_do_file_ok(self, mock_process):
        mock_process.return_value = None
        self.assertEqual(self.music_lib.do_file('dummy_file.m4a'), 0)

    @mock.patch('musiclib.MusicLib.process_file')
    def test_do_file_error(self, mock_process):
        mock_process.side_effect = ErrorDuringProcessFile
        self.assertNotEqual(self.music_lib.do_file('dummy_file.m4a'), 0)

    @mock.patch('app.media.music.ItunesInterface.add_file')
    @mock.patch('app.media.file.MediaFile.move_with_new_metadata')
    @mock.patch('app.fm_metadata.metadata.FMMetadata.get_track_info')
    def test_process_file(self, mock_track_info, mock_media_file, mock_itunes):
        mock_track_info.return_value = {"name": "Drones", "number": 1}
        mock_media_file.return_value = 0
        mock_itunes.return_value = 0
        self.assertIsNone(self.music_lib.process_file(file_name='fixtures/music_file/Muse - Drones.m4a'))

    def test_check_file_exists(self):
        self.assertIsNone(MusicLib.check_file_exists(file_name='fixtures/music_file/Muse - Drones.m4a'))

    def test_check_file_does_not_exists(self):
        self.assertRaises(ErrorDuringProcessFile, MusicLib.check_file_exists,
                          file_name='fixtures/music_file/Muse - Drones.tmp')

    def test_get_metadata(self):
        expected_metadata = {'title': 'Drones', 'artist': 'Muse', 'album': 'Drones', 'exit_code': 0,
                             'source_file': 'fixtures/music_file/Muse - Drones.m4a', 'alt_album': 'Drones',
                             'alt_artist': 'Muse', 'alt_title': 'Drones',
                             'target_directory': 'fixtures/music_file/../Processed/Drones',
                             'target_file': 'fixtures/music_file/../Processed/Drones/Muse - Drones.m4a'}
        self.assertEqual(expected_metadata, self.music_lib.get_metadata(
            file_name='fixtures/music_file/Muse - Drones.m4a'))

    def test_get_metadata_file_do_not_exists(self):
        self.assertRaises(ErrorDuringProcessFile, self.music_lib.get_metadata,
                          file_name='fixtures/music_file/Muse - Drones.tmp')


if __name__ == '__main__':
    unittest.main()
