#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from app.media.file import MediaFile
from app.utils.string import StringUtil
logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('root')


class Album(object):
    def __init__(self, album_path):
        self._album_path = album_path
        self._media_file = MediaFile()
        self._album_name = None
        self._artist_name = None
        self._track_list = list()
        self._artist_name_is_same_in_all_tracks = True
        self._album_name_is_same_in_all_tracks = True
        self._process_files()

    def _process_files(self):
        for file in os.listdir(self._album_path):
            track_location = os.path.join(self._album_path, file)
            self._media_file.get_metadata_from_file(track_location)
            if self._media_file.valid_metadata:
                self._album_name = self._media_file.metadata_album_name
                self._set_artist_name()
                track = dict()
                track['track_name'] = self._media_file.metadata_track_name
                track['track_location'] = track_location
                self._track_list.append(track)

    def _set_artist_name(self):
        if self._artist_name is None:
            self._artist_name = self._media_file.metadata_artist_name
        elif self._artist_name != self._media_file.metadata_artist_name:
            self._artist_name_is_same_in_all_tracks = False

    def _set_album_name(self):
        if self._album_name is None:
            self._album_name = self._media_file.metadata_album_name
        elif self._album_name != self._media_file.metadata_album_name:
            self._album_name_is_same_in_all_tracks = False

    @property
    def album_name(self):
        if self._album_name_is_same_in_all_tracks:
            return self._album_name
        log.warning('Album name is not consistent in all tracks')
        return None

    @property
    def artist_name(self):
        if self._artist_name_is_same_in_all_tracks:
            return self._artist_name
        log.warning('Artist name is not consistent in all tracks')
        return None

    def track_by_name(self, track_name, match_ratio=100):
        return self._lookup_track_by_name(track_name=track_name, return_token='track_name', match_ratio=match_ratio)

    def track_location_by_name(self, track_name, match_ratio=100):
        return self._lookup_track_by_name(track_name=track_name, return_token='track_location', match_ratio=match_ratio)

    def _lookup_track_by_name(self, track_name, return_token, match_ratio=100):
        for track in self._track_list:
            result_track_name = track.get('track_name')
            if StringUtil.fuzzy_match(result_track_name, track_name, match_ratio=match_ratio):
                return track.get(return_token)
        return None
