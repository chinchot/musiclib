# -*- coding: latin-1 -*-
import unittest
import json
from mock import patch
from app.media.fm_album import FMAlbum


def get_payload():
    with open('fixtures/file_metadata/buddha_bar-early_years.json', 'r') as json_file:
        content = json.loads(json_file.read())
    return content


class TestAlbum(unittest.TestCase):
    @patch('app.fm_metadata.metadata.FMMetadata.get_payload_from_api')
    def setUp(self, mock_api):
        mock_api.return_value = get_payload()
        self.fm_album = FMAlbum(artist_name='Buddha Bar', album_name='Early Years')
        self.fm_album_multi_disc = FMAlbum(artist_name='Buddha Bar', album_name='Early Years', disc_splits=[10, 11])
        self.fm_album_3_disc = FMAlbum(artist_name='Buddha Bar', album_name='Early Years', disc_splits=[10, 11, 12])

    def test_instance(self):
        self.assertIsInstance(self.fm_album, FMAlbum)

    def test_album_name(self):
        self.assertEqual(self.fm_album.album_name, 'Early Years')

    def test_artist_name(self):
        self.assertEqual(self.fm_album.artist_name, 'Buddha Bar')

    def test_tracks(self):
        self.assertEqual(33, len([track for track in self.fm_album.tracks]))

    def test_track_by_name(self):
        self.assertIsNotNone(self.fm_album.track_by_name('Indra'))

    def test_track_by_name_not_found(self):
        self.assertIsNone(self.fm_album.track_by_name('dummy'))

    def test_track_count(self):
        self.assertEqual(33, self.fm_album.track_count)

    def test_disc_count(self):
        self.assertEqual(1, self.fm_album.disc_count)

    def test_disc_count_with_two_discs(self):
        self.assertEqual(2, self.fm_album_multi_disc.disc_count)

    def test_is_multi_disc(self):
        self.assertFalse(self.fm_album._is_multi_disc())

    def test_is_multi_disc_with_two_discs(self):
        self.assertTrue(self.fm_album_multi_disc._is_multi_disc())

    def test_disc_number(self):
        self.assertEqual(1, self.fm_album.disc_number(1))
        self.assertEqual(1, self.fm_album.disc_number(20))

    def test_disc_number_with_two_discs(self):
        self.assertEqual(1, self.fm_album_multi_disc.disc_number(1))
        self.assertEqual(1, self.fm_album_multi_disc.disc_number(5))
        self.assertEqual(1, self.fm_album_multi_disc.disc_number(10))
        self.assertEqual(2, self.fm_album_multi_disc.disc_number(11))
        self.assertEqual(2, self.fm_album_multi_disc.disc_number(15))
        self.assertEqual(2, self.fm_album_multi_disc.disc_number(21))
        self.assertEqual(2, self.fm_album_multi_disc.disc_number(27))

    def test_disc_total_track_number(self):
        self.assertEqual(33, self.fm_album.disc_total_track_number(10))

    def test_disc_total_track_number_two_discs(self):
        self.assertEqual(11, self.fm_album_multi_disc.disc_total_track_number(11))

    def test_disc_total_track_number_three_discs(self):
        self.assertEqual(10, self.fm_album_3_disc.disc_total_track_number(5))
        self.assertEqual(11, self.fm_album_3_disc.disc_total_track_number(11))
        self.assertEqual(12, self.fm_album_3_disc.disc_total_track_number(22))

    def test_disc_track_number(self):
        self.assertEqual(5, self.fm_album.disc_track_number(5, 1))

    def test_disc_track_number_with_two_discs(self):
        self.assertEqual(1, self.fm_album_multi_disc.disc_track_number(11, 2))

    def test_disc_track_number_with_three_discs(self):
        self.assertEqual(1, self.fm_album_3_disc.disc_track_number(1, 1))
        self.assertEqual(1, self.fm_album_3_disc.disc_track_number(11, 2))
        self.assertEqual(1, self.fm_album_3_disc.disc_track_number(22, 3))


if __name__ == '__main__':
    unittest.main()
