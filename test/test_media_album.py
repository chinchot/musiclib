# -*- coding: latin-1 -*-
import unittest
from app.media.album import Album


class TestAlbum(unittest.TestCase):
    def setUp(self):
        self.album = Album('fixtures/music_file/Processed/Muse/Drones')

    def test_instance(self):
        self.assertIsInstance(self.album, Album)

    def test_process_files(self):
        self.assertEqual(self.album._artist_name, 'Muse')
        self.assertEqual(self.album._album_name, 'Drones')
        self.assertEqual(self.album._track_list, ['Drones'])

    def test_album_name(self):
        self.assertEqual(self.album.album_name, 'Drones')

    def test_artist_name(self):
        self.assertEqual(self.album.artist_name, 'Muse')

    def test_album_name_not_consistent(self):
        album = Album('fixtures/music_file/Processed')
        self.assertIsNone(album.album_name)

    def test_artist_name_not_consistent(self):
        album = Album('fixtures/music_file/Processed')
        self.assertIsNone(album.artist_name)

    def test_track_by_name(self):
        self.assertIsNotNone(self.album.track_by_name('Drones'))

    def test_track_by_name_not_found(self):
        self.assertIsNone(self.album.track_by_name('dummy'))


if __name__ == '__main__':
    unittest.main()
