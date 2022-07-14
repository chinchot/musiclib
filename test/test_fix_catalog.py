# -*- coding: latin-1 -*-
import unittest
from fix_catalog import FixCatalog, ErrorValueNotDetermined
from argparse import Namespace


class TestFixCatalog(unittest.TestCase):
    def setUp(self):
        arguments = Namespace(input_path='test/fixtures/music_file/Processed/Muse/Drones',
                              album_name=None, artist_name=None, disc_splits=None, album_compilation=False,
                              match_ratio=100)
        self.fix_catalog = FixCatalog(arguments)
        self.arguments_multi_disc = Namespace(input_path='/', album_name='album', artist_name='artist',
                                              disc_splits=[10, 11], album_compilation=False, match_ratio=100)
        self.arguments_3_discs = Namespace(input_path='/', album_name='album', artist_name='artist',
                                           disc_splits=[10, 11, 12], album_compilation=False, match_ratio=100)

    def test_instance(self):
        self.assertIsInstance(self.fix_catalog, FixCatalog)

    def test_init(self):
        arguments = Namespace(input_path='/', album_name='album', artist_name='artist',  disc_splits=None,
                              album_compilation=False, match_ratio=100)
        self.assertIsInstance(FixCatalog(arguments), FixCatalog)

    def test_set_artist(self):
        self.fix_catalog.set_artist('Muse')
        self.assertEqual(self.fix_catalog._artist_name, 'Muse')

    def test_set_album(self):
        self.fix_catalog.set_album('Drones')
        self.assertEqual(self.fix_catalog._album_name, 'Drones')

    def test_set_album_is_none_and_argument_not_provided(self):
        self.assertRaises(ErrorValueNotDetermined, self.fix_catalog.set_album, None)

    def test_set_artist_is_none_and_argument_not_provided(self):
        self.assertRaises(ErrorValueNotDetermined, self.fix_catalog.set_artist, None)

    def test_set_album_is_none(self):
        arguments = Namespace(input_path='/', album_name='album', artist_name='artist',  disc_splits=None,
                              album_compilation=False, match_ratio=100)
        fix_catalog = FixCatalog(arguments)
        fix_catalog.set_album(None)
        self.assertEqual(fix_catalog._album_name, 'album')

    def test_set_artist_is_none(self):
        arguments = Namespace(input_path='/', album_name='album', artist_name='artist',  disc_splits=None,
                              album_compilation=False, match_ratio=100)
        fix_catalog = FixCatalog(arguments)
        fix_catalog.set_artist(None)
        self.assertEqual(fix_catalog._artist_name, 'artist')


if __name__ == '__main__':
    unittest.main()
