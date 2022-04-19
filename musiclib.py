import logging
import os
import re
import sys
import string
import urllib
import requests
import shutil
import json
from config import MusicLibConfig
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging.config

logging.config.fileConfig('logging_config.ini')
logging.getLogger('musiclib')


class FMMetadata:

    def __init__(self):
        self.album = {"name": "", "artist": ""}
        self.fm_response = {"album": self.album}
        self.have_metadata = False
        self.config = MusicLibConfig()
        logging.debug("Init FMMetadata")

    def get_track_info(self, file_metadata):
        logging.info("Obtaining track info for: artist=%s album=%s track=%s"
                   % (file_metadata['artist'], file_metadata['album'], file_metadata['title']))
        result = {"name": ""}
        if not self.is_album_current(file_metadata['artist'], file_metadata['album']):
            logging.debug("Album not current picking up metadata from service")
            self.have_metadata = self.get_metadata_from_api(file_metadata['artist'], file_metadata['album'])
        if self.have_metadata:
            logging.debug("Metadata is already home, we can try to match the track name.")
            result = self.get_track(file_metadata)
        return result

    def is_album_current(self, artist, album):
        logging.debug("Comparing Album '%s' to '%s'" % (self.album.get("name"), album))
        compare_name = self.album.get("name") == album
        logging.debug("Comparing Artist '%s' to '%s'" % (self.album.get("artist"), artist))
        compare_album = self.album.get("artist") == artist
        return compare_name and compare_album

    def get_track(self, file_metadata):
        track_number_found = False
        total_track_count = 0
        result = {"name": file_metadata['title'], "artist": self.album.get("artist")}
        try:
            total_track_count = str(len(self.album["tracks"].get("track")))
            logging.debug("Total track count is %s" % total_track_count)
            result["number"] = "0/%s" % total_track_count
            for cur_track in self.album["tracks"].get("track"):
                current_track = StringUtil.create_slug(cur_track.get("name")).upper().encode('ascii', 'ignore')
                input_track = StringUtil.create_slug(file_metadata['title']).upper()
                logging.debug("Comparing track name '%s' to '%s'" % (current_track, input_track))
                if current_track == input_track:
                    logging.info("Assigning track number %s to track %s" %
                               (cur_track.get("@attr").get("rank").encode('ascii', 'ignore'), file_metadata['title']))
                    result["number"] = "%s/%s" % (cur_track.get("@attr").get("rank"), total_track_count)
                    track_number_found = True
                    break
        except (AttributeError, KeyError):
            pass
        if not track_number_found:
            alt_track_number = self.alternative_track_number(file_metadata['target_directory'])
            result["number"] = "%s/%s" % (alt_track_number, total_track_count)
            logging.info("Assigning alt track number %s to track %s" % (alt_track_number, file_metadata['title']))
        return result

    @staticmethod
    def alternative_track_number(target_directory):
        if os.path.exists(target_directory):
            files = [f for f in os.listdir(target_directory) if re.match(r'.*\.m4a$', f)]
        else:
            raise Exception('Something went terribly wrong, you are trying to check for music files (*.m4a) on a '
                            'directory that doesn\'t exist. This directory is not there: %s'%target_directory)
        return len(files) + 1

    def get_metadata_from_api(self, artist, album):
        result = True
        query = {"format": "json", "method": "album.getinfo", "api_key": self.config.fm_api_key,
                 "artist": artist, "album": album}
        url_query = urllib.parse.urlencode(query)
        provider = self.config.fm_url
        url = provider + "?" + url_query
        try:
            logging.info("Acquiring metadata from: %s" % url)
            payload = requests.get(url)
            logging.debug("Data gotten from service")
            self.fm_response = json.loads(payload.content)
        except requests.exceptions.HTTPError:
            logging.warning("Sadly No metadata available from the provider %s" % provider)
            result = False

        self.album = self.fm_response.get("album")
        if self.album is None:
            result = False
        logging.debug("Album name from service: %s" % self.album)
        return result


class MediaFile:

    def __init__(self):
        self.ffmpeg_command = "ffmpeg"
        self.metadata = {}
        self.file_util = FileUtility()
        logging.warning("Init MediaFile")

    def get_metadata(self, file_name):
        logging.info("Getting metadata from file %s." % file_name)
        self.metadata = {}
        process = subprocess.Popen([self.ffmpeg_command, "-y", "-i", file_name, "-f", "ffmetadata", "/dev/null"],
                                   stdout=PIPE, stderr=STDOUT)
        command_executed = ' '.join((self.ffmpeg_command, "-y", "-i", file_name, "-f", "ffmetadata", "/dev/null"))
        logging.debug("Executed command: %s" % command_executed)
        stream_data = process.communicate()[0]
        exitcode = process.returncode
        stdout_iterator = str(stream_data).split("\\n")
        for line in stdout_iterator:
            logging.debug(line)
            if line.find(" album ") > 0:
                self.metadata["album"] = line.split(":")[1].strip(" ")
            if line.find(" artist ") > 0:
                self.metadata["artist"] = line.split(":")[1].strip(" ")
            if line.find(" title ") > 0:
                self.metadata["title"] = line.split(":")[1].strip(" ")
        self.metadata["exit_code"] = exitcode
        self.metadata["source_file"] = file_name
        logging.debug("Exit Code from ffmpeg = %s" % exitcode)
        if exitcode == 0:
            self.metadata["alt_album"] = StringUtil.create_slug(self.metadata["album"])
            self.metadata["alt_artist"] = StringUtil.create_slug(self.metadata["artist"])
            self.metadata["alt_title"] = StringUtil.create_slug(self.metadata["title"])
            self.metadata["target_directory"] = os.path.join(os.path.dirname(file_name), "..",
                                                             "Processed", self.metadata["alt_artist"],
                                                             self.metadata["alt_album"])
            self.metadata["target_file"] = os.path.join(self.metadata["target_directory"], os.path.basename(file_name))
        logging.debug("get_metadata = %s" % self.metadata)
        return self.metadata

    def valid_metadata(self):
        return self.metadata["exit_code"] == 0

    def check_before_move(self):
        logging.debug("check_before_move (%s, %s)" % (self.metadata["source_file"], self.metadata["target_directory"]))
        if not os.path.isfile(self.metadata["source_file"]):
            logging.error("The source file %s does not exists." % self.metadata["source_file"])
            return False
        return self.file_util.create_directory(self.metadata["target_directory"])

    @staticmethod
    def target_file(source_file_name, target_directory):
        return os.path.join(target_directory, os.path.basename(source_file_name))

    def move(self):
        error_code = 0
        logging.info("Moving file without adding metadata.")
        if not self.check_before_move():
            error_code = -1
            return error_code
        logging.debug("target_file = %s" % self.metadata["target_file"])
        # copy the file with the same metadata to the right directory
        try:
            logging.debug("Moving File %s to %s" % (self.metadata["source_file"], self.metadata["target_file"]))
            shutil.move(self.metadata["source_file"], self.metadata["target_file"])
        except IOError:
            logging.warning("Sorry but was not able to move the file %s to %s" %
                          (self.metadata["source_file"], self.metadata["target_file"]))
            error_code = -1
            pass
        logging.debug("move error code = %s" % error_code)
        return error_code

    def move_with_new_metadata(self, track_info):
        error_code = -1
        logging.info("Moving file adding metadata.")
        if not self.check_before_move():
            return error_code
        process = subprocess.Popen([self.ffmpeg_command, '-y', '-i', r'%s' % self.metadata["source_file"],
                                    '-codec', 'copy', '-metadata', 'track=%s' % track_info['number'],
                                    '-metadata', 'album_artist=%s' % track_info["artist"], '-metadata', 'disc=1/1',
                                    r'%s' % self.metadata["target_file"]], stdout=PIPE, stderr=PIPE, shell=False)
        stdout_data, stderr_data = process.communicate()
        command_executed = ' '.join((self.ffmpeg_command, '-y', '-i', r'%s' % self.metadata["source_file"], '-codec', 'copy',
                                     '-metadata', 'track=%s' % track_info['number'],
                                     '-metadata', 'album_artist=%s' % track_info["artist"],
                                     '-metadata', 'disc=1/1',
                                     r'%s' % self.metadata["target_file"]))
        logging.info("Executed command: %s" % command_executed)
        error_code = process.returncode
        logging.debug("Error Code from %s = %s" % (self.ffmpeg_command, error_code))
        if error_code == 0:
            try:
                logging.debug("Deleting file %s" % self.metadata["source_file"])
                os.remove(self.metadata["source_file"])
            except IOError:
                logging.warning("Sorry but was not able to delete file %s" % self.metadata["source_file"])
                pass
        else:
            logging.info("STD OUT")
            logging.info(stdout_data)
            logging.error("STD ERR")
            logging.error(stderr_data)
        return error_code


class ItunesInterface:

    def __init__(self):
        pass

    @staticmethod
    def add_file(file_name):
        command = 'osascript'
        process = subprocess.Popen([command, '-e', 'set foo to posix file "%s" as alias' % file_name,
                                    '-e', 'tell application "Music" to add foo'],
                                    stdout=PIPE, stderr=PIPE, shell=False)
        stdout_data, stderr_data = process.communicate()
        command_executed = ' '.join((command, '-e', 'tell application "Music" to add POSIX file "%s"' % file_name))
        logging.info("Executed command: %s" % command_executed)
        error_code = process.returncode
        logging.debug("Error Code from %s = %s" % (command, error_code))
        if error_code == 0:
            logging.info("Added file '%s' to iTunes" % file_name)
        else:
            logging.info("STD OUT")
            logging.info(stdout_data)
            logging.error("STD ERR")
            logging.error(stderr_data)
        return error_code


class FileUtility:

    def __init__(self):
        pass

    @staticmethod
    def create_directory(dir_name="."):
        if os.path.exists(dir_name):
            logging.info("Directory %s already exists" % dir_name)
            if not os.path.isdir(dir_name):
                logging.error("trying to create a directory where a file name with the same exists already: %s"
                            % dir_name)
                return False
        else:
            logging.info("Creating directory: %s" % dir_name)
            try:
                os.makedirs(dir_name)
            except IOError:
                logging.error("Were not able to create directory %s" % dir_name)
                return False
        return True


class StringUtil:

    def __init__(self):
        pass

    @staticmethod
    def create_slug(string_to_slug):
        """
        create a string that can be used for naming a file
        """
        for character in "?*":
            string_to_slug = string_to_slug.replace(character, "_")
        valid_characters = "-_./()' %s%s" % (string.ascii_letters, string.digits)
        slug_string = ''.join(character for character in string_to_slug if character in valid_characters)
        logging.debug("Slug for '%s' is '%s'" % (string_to_slug, slug_string))
        return slug_string


class MusicLib:

    def __init__(self):
        logging.info("Initializing MusicLib")
        self.fm_metadata = {}
        self.fm_album = {}
        self.fm_metadata = FMMetadata()
        self.media_file = MediaFile()
        self.music_file = FileUtility()
        self.itunes = ItunesInterface()
        logging.debug("Init MusicLib")

    def process_file(self, file_name):
        logging.debug("Process File: %s" % file_name)
        if not os.path.isfile(file_name):
            logging.error("File %s does not exists" % file_name)
            return False
        file_metadata = self.media_file.get_metadata(file_name)
        if not self.media_file.valid_metadata():
            logging.error("Couldn't get the metadata from file: %s" % file_name)
            return False
        FileUtility.create_directory(dir_name=file_metadata["target_directory"])
        track_info = self.fm_metadata.get_track_info(file_metadata)
        logging.info("Moving %s to %s" % (file_name, file_metadata["target_directory"]))
        if track_info.get("name") == "":
            if self.media_file.move() != 0:
                return False
        else:
            if self.media_file.move_with_new_metadata( track_info) != 0:
                return False
        if self.itunes.add_file(file_metadata["target_file"]) == 0:
            logging.info("Added file Track %s - '%s' to iTunes" % (track_info["number"],
                                                                   os.path.basename(file_metadata["target_file"])))
        else:
            logging.warning("Song '%s'no added to iTunes" % os.path.basename(file_metadata["target_file"]))
            return False
        return True

    def do_file(self, file_name):
        error_code = 1
        logging.debug("do_file %s" % file_name)
        if self.process_file(file_name):
            logging.info("Everything worked as expected. Congratulations!")
            error_code = 0
        else:
            logging.error("Something went wrong. Check your logs")
        return error_code


def main():
    logging.debug("Main")
    music = MusicLib()
    logging.debug("argv[1] = %s" % sys.argv[1])
    error_code = music.do_file(sys.argv[1])
    logging.info('Finished')
    return error_code


if __name__ == '__main__':
    exit(main())
