#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import requests
import os
from requests.exceptions import MissingSchema
from app.fm_metadata.metadata import FMMetadata
from app.utils.track import TrackList, Track
logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('root')


class FMAlbum(object):
    def __init__(self, album_name, artist_name, disc_splits=None):
        self._album_name = album_name
        self._artist_name = artist_name
        self._track_list = TrackList()
        self._disc_splits = disc_splits
        self._image_location = None
        self._get_metadata()

    def _get_metadata(self):
        fm_metadata = FMMetadata()
        payload = fm_metadata.get_payload_from_api(artist=self._artist_name, album=self._album_name)
        for track in payload['album']['tracks']['track']:
            self._track_list.append(Track(track))
        self._image_location = FMAlbum._get_art(payload)

    def image_location(self):
        if self._image_location is not None:
            return self._image_location
        raise NoImageError('The current album has no art.')

    @staticmethod
    def _get_art(payload):
        image_location = None
        image_list = payload['album'].get('image')
        if image_list:
            for image_size in ['mega', 'extralarge', 'large', 'medium', 'small']:
                image_location = FMAlbum._get_image(image_list, image_size)
                if image_location is not None:
                    break
        return image_location

    @staticmethod
    def _get_image_by_size(image_list, size):
        for image in image_list:
            if image.get('size') == size:
                return image
        return {'#text': ''}

    @staticmethod
    def _get_image(image_list, image_size):
        image = FMAlbum._get_image_by_size(image_list, image_size)
        image_url = image.get('#text')
        if image_url is None or image_url == '':
            return None
        log.debug(f'Getting image from {image_url}')
        try:
            response = requests.get(image_url)
        except MissingSchema as e:
            log.error(e)
            return None
        image_location = os.path.join(os.getcwd(), 'image.jpg')
        with open(image_location, "wb") as file:
            file.write(response.content)
        return image_location

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
        return self._track_list.lookup_track_name(track_name)

    @property
    def disc_count(self):
        if self._disc_splits is None or len(self._disc_splits) == 1:
            return 1
        else:
            return len(self._disc_splits)

    def _is_multi_disc(self):
        return self.disc_count > 1

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


class NoImageError(Exception):
    pass


if __name__ == "__main__":
    album = FMAlbum(album_name='Drones', artist_name='Muse')
    print(album)
