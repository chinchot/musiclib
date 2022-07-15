# -*- coding: latin-1 -*-
import unittest
from app.utils.track import TrackList, Track


class TestTrackList(unittest.TestCase):
    def setUp(self):
        self.track_list = TrackList()
        self.track_list.append(Track({'name': 'aaa', 'duration': None}))

    def test_instance(self):
        self.assertIsInstance(self.track_list, TrackList)

    def test_append(self):
        self.assertEqual(1, len(self.track_list))

    def test_lookup_track_name(self):
        self.assertEqual('aaa', self.track_list.lookup_track_name('aaa').name)

    def test_lookup_track_name_not_in(self):
        self.assertIsNone(self.track_list.lookup_track_name('bbb'))

    def test_raises_type_error(self):
        track_list = TrackList()
        self.assertRaises(TypeError, track_list.append, 'aaa')


if __name__ == '__main__':
    unittest.main()
