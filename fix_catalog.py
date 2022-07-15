#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging.config
from app.media.fm_album import FMAlbum, NoImageError
from app.media.album import Album
from app.media.file import MediaFile
from app.media.music import ItunesInterface, ErrorExecuteAppleScript
from app.utils.argument_parser import parse_args
logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('catalog')


class FixCatalog(object):
    """Fixes the metadata of al album/artist set of files contained in a single directory.
    """
    def __init__(self, arguments):
        self._input_path = arguments.input_path
        self._album_name = arguments.album_name
        self._artist_name = arguments.artist_name
        self._disc_splits = arguments.disc_splits
        self._album_compilation_indicator = arguments.album_compilation
        self._match_ratio = arguments.match_ratio

    def set_album(self, album_name):
        if album_name is not None and self._album_name is None:
            self._album_name = album_name
        elif self._album_name is None:
            raise ErrorValueNotDetermined('No Album name could be determined, and no override was provided '
                                          'in argument --album')

    def set_artist(self, artist_name):
        if artist_name is not None and self._artist_name is None:
            self._artist_name = artist_name
        elif self._artist_name is None:
            raise ErrorValueNotDetermined('No Artist name could be determined, and no override was provided '
                                          'in argument --artist')

    def set_catalog_values_from_media(self, file_media):
        try:
            self.set_album(file_media.album_name)
            self.set_artist(file_media.artist_name)
        except ErrorValueNotDetermined as e:
            log.error(e)
            exit(1)

    def run(self):
        media_file = MediaFile()
        file_media = Album(self._input_path)
        music = ItunesInterface()
        self.set_catalog_values_from_media(file_media)
        fm_album = FMAlbum(album_name=self._album_name, artist_name=self._artist_name, disc_splits=self._disc_splits)
        for track in fm_album.tracks:
            track_in_file = file_media.track_by_name(track.name, match_ratio=self._match_ratio)
            if track_in_file is None:
                log.warning(f'Track name "{track.name}" not found in path')
            else:
                media_file.add_metadata(input_file=track_in_file.location,
                                        track_number=f'{fm_album.disc_track_number(track.number, fm_album.disc_number(track.number))}/{fm_album.disc_total_track_number(track.number)}',
                                        disc=f'{fm_album.disc_number(track.number)}/{fm_album.disc_count}',
                                        album_compilation_indicator=self._album_compilation_indicator,
                                        album_artist=fm_album.artist_name)
                try:
                    music.add_file(track_in_file.location)
                    image_location = fm_album.image_location()
                    music.add_track_art(track_name=track.name, album_name=fm_album.album_name,
                                        image_location=image_location)
                except ErrorExecuteAppleScript as e:
                    log.error(e)
                    exit(1)
                except NoImageError:
                    log.warning('No image added')


class ErrorValueNotDetermined(Exception):
    pass


def main():
    arguments = parse_args()
    fix_catalog = FixCatalog(arguments)
    fix_catalog.run()


if __name__ == "__main__":
    main()
