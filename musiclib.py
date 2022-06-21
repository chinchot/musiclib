import os
import sys
from app.media.file import MediaFile
from app.media.music import ItunesInterface
from app.media.file import NoImageError
from config import MusicLibConfig
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


class MusicLib:

    def __init__(self):
        log.info("Initializing Music Library")
        self.fm_album = {}
        self.config = MusicLibConfig()
        self.media_file = MediaFile(api_key=self.config.fm_api_key, url=self.config.fm_url)
        self.itunes = ItunesInterface()
        log.debug("Music Library has been initialized")

    @staticmethod
    def check_file_exists(file_name):
        if not os.path.isfile(file_name):
            raise ErrorDuringProcessFile(f'File {file_name} does not exists.')

    def get_metadata(self, file_name) -> None:
        self.media_file.get_metadata(file_name)
        if not self.media_file.valid_metadata:
            raise ErrorDuringProcessFile(f'Could not get the metadata from file: {file_name}')

    def add_album_art(self):
        try:
            art_location = self.media_file.get_art()
            self.itunes.add_track_art(track_name=self.media_file.track_name,
                                      album_name=self.media_file.album_name,
                                      image_location=art_location)
        except NoImageError:
            log.error('No image to be added')

    def add_file_to_music(self):
        if self.config.add_music_indicator:
            if self.itunes.add_file(self.media_file.target_file) == 0:
                log.debug(f"Added file Track {self.media_file.track_number} - '{self.media_file.target_file}' to Music")
                self.add_album_art()
            else:
                raise ErrorDuringProcessFile(f"Song '{os.path.basename(self.media_file.target_file)}' not added to"
                                             f" Music")
        else:
            log.warning(f"Add song indicator is off. Song '{os.path.basename(self.media_file.target_file)}' "
                        f"not added to Music")

    def process_file(self, file_name) -> None:
        log.debug("Process File: %s" % file_name)
        MusicLib.check_file_exists(file_name)
        self.get_metadata(file_name)
        self.media_file.move_file(self.config.album_compilation_indicator)
        self.add_file_to_music()

    def do_file(self, file_name):
        log.debug("do_file %s" % file_name)
        try:
            self.process_file(file_name)
            log.info("Everything worked as expected. Congratulations!")
            error_code = 0
        except (ErrorDuringProcessFile, Exception) as e:
            log.error(e)
            log.error("Something went wrong. Check your logs")
            error_code = 1
        return error_code


class ErrorDuringProcessFile(Exception):
    pass


def main():
    log.debug("Main")
    music = MusicLib()
    log.debug("argv[1] = %s" % sys.argv[1])
    error_code = music.do_file(sys.argv[1])
    log.info('Finished')
    return error_code


if __name__ == '__main__':
    exit(main())
