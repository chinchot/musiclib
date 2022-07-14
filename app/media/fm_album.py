#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from app.fm_metadata.metadata import FMMetadata
logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('root')


class FMAlbum(object):
    def __init__(self, album_name, artist_name, disc_splits=None):
        self._album_name = album_name
        self._artist_name = artist_name
        self._track_list = list()
        self._disc_splits = disc_splits
        self._get_metadata()

    def _get_metadata(self):
        fm_metadata = FMMetadata()
        payload = fm_metadata.get_payload_from_api(artist=self._artist_name, album=self._album_name)
        for track in payload['album']['tracks']['track']:
            self._track_list.append(Track(track))

    @property
    def album_name(self):
        return self._album_name

    @property
    def artist_name(self):
        return self._artist_name

    @property
    def tracks(self):
        for track in self._track_list:
            yield track

    @property
    def track_count(self):
        return len(self._track_list)

    def track_by_name(self, track_name):
        for track in self._track_list:
            if track.name.upper() == track_name.upper():
                return track
        return None

    @property
    def disc_count(self):
        if self._disc_splits is None or len(self._disc_splits) == 1:
            return 1
        else:
            return len(self._disc_splits)

    def _is_multi_disc(self):
        return self.disc_count > 1

    def disc_total_track_number(self, track_number, default_total_track_number):
        if self._is_multi_disc():
            return self._disc_splits[self.disc_number(track_number)-1]
        else:
            return default_total_track_number

    def disc_number(self, track_number):
        disc_number = 0
        track_number_start = 1
        if self._is_multi_disc():
            for track_count in self._disc_splits:
                if track_number_start <= track_number:
                    disc_number += 1
                track_number_start = track_number_start + track_count
        else:
            disc_number += 1
        return disc_number

    def disc_track_number(self, track_number, disc_number):
        if self._is_multi_disc():
            previous_disc_track_count = 0
            for track_count in self._disc_splits[:disc_number-1]:
                previous_disc_track_count += track_count
            return track_number - previous_disc_track_count
        else:
            return track_number

    def disc_total_track_number(self, track_number):
        if self._is_multi_disc():
            return self._disc_splits[self.disc_number(track_number)-1]
        else:
            return self.track_count


class Track(object):
    def __init__(self, fm_track):
        self._set_track_values(fm_track)

    def _set_track_values(self, fm_track):
        self._name = fm_track.get('name')
        self._duration = fm_track.get('duration')
        self._rank = fm_track.get('@attr').get('rank')
        self._artist = fm_track.get('artist').get('name')

    @property
    def artist_name(self):
        return self._artist

    @property
    def name(self):
        return self._name

    @property
    def duration(self):
        return self._duration

    @property
    def number(self):
        return self._rank

    def __repr__(self):
        track = dict()
        track['name'] = self.name
        track['artist_name'] = self.artist_name
        track['number'] = self.number
        track['duration'] = self.duration
        return str(track)


if __name__ == "__main__":
    album = FMAlbum(album_name='Buddha Bar XI', artist_name='Buddha Bar')
    print(album)