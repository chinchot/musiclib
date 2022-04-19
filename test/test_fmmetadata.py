# -*- coding: latin-1 -*-
import unittest
import mock
from musiclib import FMMetadata
from musiclib import MediaFile
import ConfigParser
import requests


class PopenMock:
    def __init__(self):
        pass


class TestFMMetadata(unittest.TestCase):
    def setUp(self):
        self.fm_metadata = FMMetadata()
        self.metadata = self.set_fm_metadata()

    @staticmethod
    def set_fm_metadata():
        media_file = MediaFile()
        metadata = media_file.get_metadata('/Users/manolo/Documents/python/musiclib/test/fixtures/music_file/'
                                           'CafeTacvba-BarTacuba.m4a')
        return metadata

    def musiclib_config_side_effect(*args, **kwargs):
        config = ConfigParser.ConfigParser()
        config.read('../musiclib.dev.ini')
        return config.get(section=args[1], option=args[2])

    def test_instance(self):
        self.assertIsInstance(self.fm_metadata, FMMetadata)

    # Test alternative_track_number()
    def test_alternative_track_number(self):
        self.assertEqual(3, self.fm_metadata.alternative_track_number('fixtures/dummy_music'))

    def test_empty_alternative_track_number(self):
        self.assertEqual(1, self.fm_metadata.alternative_track_number('fixtures/empty_dir'))

    def test_alternative_track_number_non_existent_path(self):
        self.assertRaises(Exception, self.fm_metadata.alternative_track_number, 'fixtures/nonthere')

    # Test get_track()
    @mock.patch('config.Config.getvalue')
    @mock.patch('requests.get')
    def test_get_track(self, mock_requests, mock_config):
        process_mock = mock.Mock()
        attrs = {'content': '{"album": {"name":"Bar Tacuba", "artist":"Cafe Tacvba","tracks":'
                            '{"track":[{"name":"Bar Tacuba","@attr":{"rank":"1"}}]}}}'}
        process_mock.configure_mock(**attrs)
        mock_requests.return_value = process_mock
        mock_config.side_effect = self.musiclib_config_side_effect
        self.fm_metadata.get_metadata_from_api(artist='Cafe Tacvba', album='Bar Tacuba')
        result = {"name": 'Bar Tacuba', "number": u'1/1', "artist": u'Cafe Tacvba'}
        self.assertEqual(result, self.fm_metadata.get_track(self.metadata))

    @mock.patch('config.Config.getvalue')
    @mock.patch('requests.get')
    def test_get_track_not_found_in_metadata(self, mock_requests, mock_config):
        process_mock = mock.Mock()
        attrs = {'content': '{"album": {"name":"Bar Tacuba", "artist":"Cafe Tacvba","tracks":'
                            '{"track":[{"name":"Bar Tacuba","@attr":"None"}]}}}'}
        process_mock.configure_mock(**attrs)
        mock_requests.return_value = process_mock
        mock_config.side_effect = self.musiclib_config_side_effect
        self.fm_metadata.get_metadata_from_api(artist='Cafe Tacvba', album='Bar Tacuba')
        result = {"name": 'Bar Tacuba', "number": u'1/1', "artist": u'Cafe Tacvba'}
        self.assertEqual(result, self.fm_metadata.get_track(self.metadata))

    @mock.patch('config.Config.getvalue')
    @mock.patch('requests.get')
    def test_get_tracks_not_found_in_metadata(self, mock_requests, mock_config):
        process_mock = mock.Mock()
        attrs = {'content': '{"album": {"name":"Bar Tacuba", "artist":"Cafe Tacvba"}}'}
        process_mock.configure_mock(**attrs)
        mock_requests.return_value = process_mock
        mock_config.side_effect = self.musiclib_config_side_effect
        self.fm_metadata.get_metadata_from_api(artist='Cafe Tacvba', album='Bar Tacuba')
        result = {"name": 'Bar Tacuba', "number": u'1/0', "artist": u'Cafe Tacvba'}
        self.assertEqual(result, self.fm_metadata.get_track(self.metadata))

    # Test get_metadata_from_api()
    @mock.patch('config.Config.getvalue')
    @mock.patch('requests.get')
    def test_get_metadata_from_api(self, mock_requests, mock_config):
        process_mock = mock.Mock()
        attrs = {'content': '{"album": {"name":"The Wall", "artist":"Pink Floyd"}}'}
        process_mock.configure_mock(**attrs)
        mock_requests.return_value = process_mock
        mock_config.side_effect = self.musiclib_config_side_effect
        return_value = self.fm_metadata.get_metadata_from_api(artist='Pink Floyd', album='The Wall')
        self.assertTrue(return_value)

    @mock.patch('config.Config.getvalue')
    @mock.patch('requests.get')
    def test_no_metadata_provider(self, mock_requests, mock_config):
        http_error = requests.exceptions.HTTPError()
        mock_requests.raise_for_status = mock.Mock(side_effect=http_error)
        mock_requests.side_effect = http_error
        mock_config.side_effect = self.musiclib_config_side_effect
        return_value = self.fm_metadata.get_metadata_from_api(artist='Pink Floyd', album='The Wall')
        self.assertFalse(return_value)

    @mock.patch('config.Config.getvalue')
    @mock.patch('requests.get')
    def test_get_metadata_from_api_album_not_found(self, mock_requests, mock_config):
        process_mock = mock.Mock()
        attrs = {'content': '{"message": "Album not found", "links": [], "error": 6}'}
        process_mock.configure_mock(**attrs)
        mock_requests.return_value = process_mock
        mock_config.side_effect = self.musiclib_config_side_effect
        return_value = self.fm_metadata.get_metadata_from_api(artist='Pink Floyd', album='Wrong Album')
        self.assertFalse(return_value)

    # Test get_track_info()
    @mock.patch('config.Config.getvalue')
    def test_get_track_info(self, mock_config):
        mock_config.side_effect = self.musiclib_config_side_effect
        result = {'artist': u'Caf\xe9 Tacvba', 'name': 'Bar Tacuba', 'number': '1/12'}
        self.assertEqual(result, self.fm_metadata.get_track_info(self.metadata))

    @mock.patch('config.Config.getvalue')
    @mock.patch('requests.get')
    def test_get_track_info_no_metadata(self, mock_requests, mock_config):
        process_mock = mock.Mock()
        attrs = {'content': '{"message": "Album not found", "links": [], "error": 6}'}
        process_mock.configure_mock(**attrs)
        mock_requests.return_value = process_mock
        mock_config.side_effect = self.musiclib_config_side_effect
        result = {"name": ""}
        self.assertEqual(result, self.fm_metadata.get_track_info(self.metadata))

    # Test is_album_current()
    def test_is_album_not_current(self):
        self.assertEqual(False, self.fm_metadata.is_album_current(album='MTV Unplugged', artist='Café Tacvba'))

    @mock.patch('config.Config.getvalue')
    @mock.patch('requests.get')
    def test_is_album_current(self, mock_requests, mock_config):
        process_mock = mock.Mock()
        attrs = {'content': '{"album": {"name":"The Wall", "artist":"Pink Floyd"}}'}
        process_mock.configure_mock(**attrs)
        mock_requests.return_value = process_mock
        mock_config.side_effect = self.musiclib_config_side_effect
        self.fm_metadata.get_metadata_from_api(artist='Pink Floyd', album='The Wall')
        self.assertEqual(True, self.fm_metadata.is_album_current(artist='Pink Floyd', album='The Wall'))


if __name__ == '__main__':
    unittest.main()
