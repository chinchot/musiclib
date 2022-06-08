import os
import sys
from app.fm_metadata.metadata import FMMetadata, NoImageError
from app.media.file import MediaFile
from app.media.music import ItunesInterface
from app.utils.file import FileUtility, ErrorNotAbleToCreateDir
from config import MusicLibConfig
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


class MusicLib:

    def __init__(self):
        log.info("Initializing MusicLib")
        self.fm_metadata = {}
        self.fm_album = {}
        self.config = MusicLibConfig()
        self.fm_metadata = FMMetadata(api_key=self.config.fm_api_key, url=self.config.fm_url)
        self.media_file = MediaFile()
        self.music_file = FileUtility()
        self.itunes = ItunesInterface()
        log.debug("MusicLib has been initialized")

    @staticmethod
    def check_file_exists(file_name):
        if not os.path.isfile(file_name):
            raise ErrorDuringProcessFile(f'File {file_name} does not exists.')

    def get_metadata(self, file_name):
        file_metadata = self.media_file.get_metadata(file_name)
        if not self.media_file.valid_metadata:
            raise ErrorDuringProcessFile(f'Could not get the metadata from file: {file_name}')
        return file_metadata

    def process_file(self, file_name) -> None:
        log.debug("Process File: %s" % file_name)
        MusicLib.check_file_exists(file_name)
        file_metadata = self.get_metadata(file_name)
        FileUtility.create_directory(dir_name=file_metadata["target_directory"])
        track_info = self.fm_metadata.get_track_info(file_metadata)
        log.debug("Moving %s to %s" % (file_name, file_metadata["target_directory"]))
        if track_info.get("name") == "":
            if self.media_file.move() != 0:
                raise ErrorDuringProcessFile('Error while trying to move the file to new location.')
        else:
            if self.media_file.move_with_new_metadata(track_info, self.config.album_compilation_indicator) != 0:
                raise ErrorDuringProcessFile('Error while trying to move the file with metadata to new location.')
        if self.config.add_music_indicator:
            if self.itunes.add_file(file_metadata["target_file"]) == 0:
                log.debug("Added file Track %s - '%s' to iTunes" % (track_info["number"],
                                                                    os.path.basename(file_metadata["target_file"])))
                try:
                    art_location = self.fm_metadata.get_art()
                    self.itunes.add_track_art(track_name=track_info.get('name'),
                                              album_name=self.fm_metadata.album.get('name'),
                                              image_location=art_location)
                except NoImageError:
                    log.error('No image to be added')
            else:
                raise ErrorDuringProcessFile("Song '%s'no added to iTunes" % os.path.basename(file_metadata["target_file"]))
        else:
            log.warning("Add song indicator is off. Song '%s'no added to iTunes" % os.path.basename(file_metadata["target_file"]))

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
