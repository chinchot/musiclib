import os
import re
import sys
import string
import urllib2
import urllib
import shutil
import json
from config import Config
from log_set import B
from subprocess import Popen, PIPE, STDOUT


class FMMetadata:

    def __init__(self):
        self.album = {"name": "", "artist": ""}
        self.fm_response = {"album": self.album}
        self.have_metadata = False
        B.log.debug("Init FMMetadata")

    def get_track_info(self, file_metadata):
        B.log.info("Obtaining track info for: artist=%s album=%s track=%s"
                   % (file_metadata['artist'], file_metadata['album'], file_metadata['title']))
        result = {"name": ""}
        if not self.is_album_current(file_metadata['artist'], file_metadata['album']):
            B.log.debug("Album not current picking up metadata from service")
            self.have_metadata = self.get_metadata_from_api(file_metadata['artist'], file_metadata['album'])
        if self.have_metadata:
            B.log.debug("Metadata is already home, we can try to match the track name.")
            result = self.get_track(file_metadata)
        return result

    def is_album_current(self, artist, album):
        B.log.debug("Comparing Album '%s' to '%s'" % (self.album.get("name"), album.decode('UTF-8', 'ignore')))
        compare_name = self.album.get("name") == album.decode('UTF-8', 'ignore')
        B.log.debug("Comparing Artist '%s' to '%s'" % (self.album.get("artist"), artist.decode('UTF-8', 'ignore')))
        compare_album = self.album.get("artist") == artist.decode('UTF-8', 'ignore')
        return compare_name and compare_album

    def get_track(self, file_metadata):
        total_track_count = str(len(self.album["tracks"].get("track")))
        track_number_found = False
        B.log.debug("Total track count is %s" % total_track_count)
        result = {"name": file_metadata['title'], "number": "0/%s" % total_track_count,
                  "artist": self.album.get("artist")}
        for cur_track in self.album["tracks"].get("track"):
            current_track = StringUtil.create_slug(cur_track.get("name")).upper().encode('ascii', 'ignore')
            input_track = StringUtil.create_slug(file_metadata['title']).upper()
            B.log.debug("Comparing track name '%s' to '%s'" % (current_track, input_track))
            if current_track == input_track:
                B.log.info("Assigning track number %s to track %s" %
                           (cur_track.get("@attr").get("rank").encode('ascii', 'ignore'), file_metadata['title']))
                result["number"] = "%s/%s" % (cur_track.get("@attr").get("rank"), total_track_count)
                track_number_found = True
                break
        if not track_number_found:
            alt_track_number = self.alternative_track_number(file_metadata['target_directory'])
            result["number"] = "%s/%s" % (alt_track_number, total_track_count)
            B.log.info("Assigning alt track number %s to track %s" % (alt_track_number, file_metadata['title']))
        return result

    @staticmethod
    def alternative_track_number( target_directory):
        files = [f for f in os.listdir(target_directory) if re.match(r'.*\.m4a$', f)]
        return len(files) + 1

    def get_metadata_from_api(self, artist, album):
        result = True
        query = {"format": "json", "method": "album.getinfo", "api_key": Config.getvalue("general", "FM.APIKEY"),
                 "artist": artist, "album": album}
        url_query = urllib.urlencode(query)
        provider = Config.getvalue("general", "FM.URL")
        url = provider + "?" + url_query
        try:
            B.log.info("Acquiring metadata from: %s" % url)
            payload = urllib2.urlopen(url)
            B.log.debug("Data gotten from service")
            B.log.debug(payload)
            self.fm_response = json.load(payload)
        except urllib2.HTTPError:
            B.log.warning("Sadly No metadata available from the provider %s" % provider)
            result = False
            pass

        self.album = self.fm_response.get("album")
        if self.album is None:
            result = False
        B.log.debug("Album name from service: %s" % self.album)
        return result


class MediaFile:

    def __init__(self):
        self.ffmpeg_command = "ffmpeg"
        self.metadata = {}
        self.file_util = FileUtility()
        B.log.warning("Init MediaFile")

    def get_metadata(self, file_name):
        B.log.info("Getting metadata from file %s." % file_name)
        self.metadata = {}
        process = Popen([self.ffmpeg_command, "-y", "-i", file_name, "-f", "ffmetadata", "/dev/null"], stdout=PIPE, stderr=STDOUT)
        command_executed = ' '.join((self.ffmpeg_command, "-y", "-i", file_name, "-f", "ffmetadata", "/dev/null"))
        B.log.debug("Executed command: %s" % command_executed)
        stream_data = process.communicate()[0]
        exitcode = process.returncode
        stdout_iterator = stream_data.split("\n")
        for line in stdout_iterator:
            B.log.debug(line)
            if line.find(" album ") > 0:
                self.metadata["album"] = line.split(":")[1].strip(b" ")
            if line.find(" artist ") > 0:
                self.metadata["artist"] = line.split(":")[1].strip(b" ")
            if line.find(" title ") > 0:
                self.metadata["title"] = line.split(":")[1].strip(b" ")
        self.metadata["exit_code"] = exitcode
        self.metadata["source_file"] = file_name
        B.log.debug("Exit Code from ffmpeg = %s" % exitcode)
        if exitcode == 0:
            self.metadata["alt_album"] = StringUtil.create_slug(self.metadata["album"])
            self.metadata["alt_artist"] = StringUtil.create_slug(self.metadata["artist"])
            self.metadata["alt_title"] = StringUtil.create_slug(self.metadata["title"])
            self.metadata["target_directory"] = os.path.join(os.path.dirname(file_name),
                                                             "Processed", self.metadata["alt_artist"],
                                                             self.metadata["alt_album"])
            self.metadata["target_file"] = os.path.join(self.metadata["target_directory"], os.path.basename(file_name))
        B.log.debug("get_metadata = %s" % self.metadata)
        return self.metadata

    def valid_metadata(self):
        return self.metadata["exit_code"] == 0

    def check_before_move(self):
        B.log.debug("check_before_move (%s, %s)" % (self.metadata["source_file"], self.metadata["target_directory"]))
        if not os.path.isfile(self.metadata["source_file"]):
            B.log.error("The source file %s does not exists." % self.metadata["source_file"])
            return False
        return self.file_util.create_directory(self.metadata["target_directory"])

    @staticmethod
    def target_file(source_file_name, target_directory):
        return os.path.join(target_directory, os.path.basename(source_file_name))

    def move(self):
        error_code = 0
        B.log.info("Moving file without adding metadata.")
        if not self.check_before_move():
            error_code = -1
            return error_code
        B.log.debug("target_file = %s" % self.metadata["target_file"])
        # copy the file with the same metadata to the right directory
        try:
            B.log.debug("Moving File %s to %s" % (self.metadata["source_file"], self.metadata["target_file"]))
            shutil.move(self.metadata["source_file"], self.metadata["target_file"])
        except IOError:
            B.log.warning("Sorry but was not able to move the file %s to %s" %
                          (self.metadata["source_file"], self.metadata["target_file"]))
            error_code = -1
            pass
        B.log.debug("move error code = %s" % error_code)
        return error_code

    def move_with_new_metadata(self, track_info):
        error_code = -1
        B.log.info("Moving file adding metadata.")
        if not self.check_before_move():
            return error_code
        process = Popen([self.ffmpeg_command, '-y', '-i', r'%s' % self.metadata["source_file"], '-c:a', 'copy',
                         '-metadata', 'track=%s' % track_info['number'],
                         '-metadata', 'album_artist=%s' % track_info["artist"],
                         '-metadata', 'disc=1/1',
                         r'%s' % self.metadata["target_file"]],
                        stdout=PIPE, stderr=PIPE, shell=False)
        stdout_data, stderr_data = process.communicate()
        command_executed = ' '.join((self.ffmpeg_command, '-y', '-i', r'%s' % self.metadata["source_file"], '-c:a', 'copy',
                                     '-metadata', 'track=%s' % track_info['number'],
                                     '-metadata', 'album_artist=%s' % track_info["artist"],
                                     '-metadata', 'disc=1/1',
                                     r'%s' % self.metadata["target_file"]))
        B.log.info("Executed command: %s" % command_executed)
        error_code = process.returncode
        B.log.debug("Error Code from %s = %s" % (self.ffmpeg_command, error_code))
        if error_code == 0:
            try:
                B.log.debug("Deleting file %s" % self.metadata["source_file"])
                os.remove(self.metadata["source_file"])
            except IOError:
                B.log.warning("Sorry but was not able to delete file %s" % self.metadata["source_file"])
                pass
        else:
            B.log.info("STD OUT")
            B.log.info(stdout_data)
            B.log.error("STD ERR")
            B.log.error(stderr_data)
        return error_code


class ItunesInterface:

    def __init__(self):
        B.log.debug("Init ItunesInterface")

    @staticmethod
    def add_file(file_name):
        command = 'osascript'
        process = Popen([command, '-e', 'set foo to posix file "%s" as alias' % file_name,
                         '-e', 'tell application "iTunes" to add foo'],
                         stdout=PIPE, stderr=PIPE, shell=False)
        stdout_data, stderr_data = process.communicate()
        command_executed = ' '.join((command, '-e', 'tell application "iTunes" to add POSIX file "%s"' % file_name))
        B.log.info("Executed command: %s" % command_executed)
        error_code = process.returncode
        B.log.debug("Error Code from %s = %s" % (command, error_code))
        if error_code == 0:
            B.log.info("Added file '%s' to iTunes" % file_name)
        else:
            B.log.info("STD OUT")
            B.log.info(stdout_data)
            B.log.error("STD ERR")
            B.log.error(stderr_data)
        return error_code


class FileUtility:

    def __init__(self):
        B.log.debug("Init FileUtility")

    @staticmethod
    def create_directory(dir_name="."):
        if os.path.exists(dir_name):
            B.log.debug("Directory %s already exists" % dir_name)
            if not os.path.isdir(dir_name):
                B.log.error("trying to create a directory where a file name with the same exists already: %s"
                            % dir_name)
                return False
        else:
            B.log.debug("Creating directory: %s" % dir_name)
            try:
                os.makedirs(dir_name)
            except IOError:
                B.log.error("Were not able to create directory %s" % dir_name)
                return False
        return True


class StringUtil:

    def __init__(self):
        return

    @staticmethod
    def create_slug(string_to_slug):
        """
        create a string that can be used for naming a file
        """
        for character in "?*":
            string_to_slug = string_to_slug.replace(character, "_")
        valid_characters = "-_./()' %s%s" % (string.ascii_letters, string.digits)
        slug_string = ''.join(character for character in string_to_slug if character in valid_characters)
        B.log.debug("Slug for '%s' is '%s'" % (string_to_slug, slug_string))
        return slug_string


class MusicLib:

    def __init__(self):
        B.log.info("Initializing MusicLib")
        self.fm_metadata = {}
        self.fm_album = {}
        self.fm_metadata = FMMetadata()
        self.media_file = MediaFile()
        self.music_file = FileUtility()
        self.itunes = ItunesInterface()
        B.log.debug("Init MusicLib")

    def process_file(self, file_name):
        file_name = file_name.decode('UTF-8', 'ignore')
        B.log.debug("Process File: %s" % file_name)
        if not os.path.isfile(file_name):
            B.log.error("File %s does not exists" % file_name)
            return False
        file_metadata = self.media_file.get_metadata(file_name)
        if not self.media_file.valid_metadata():
            B.log.error("Couldn't get the metadata from file: %s" % file_name)
            return False
        FileUtility.create_directory(dir_name=file_metadata["target_directory"])
        track_info = self.fm_metadata.get_track_info(file_metadata)
        B.log.info("Moving %s to %s" % (file_name, file_metadata["target_directory"]))
        if track_info.get("name") == "":
            if self.media_file.move() != 0:
                return False
        else:
            if self.media_file.move_with_new_metadata( track_info) != 0:
                return False
        if self.itunes.add_file(file_metadata["target_file"]) == 0:
            B.log.info("Added file Track %s - '%s' to iTunes" % (track_info["number"],
                                                                 os.path.basename(file_metadata["target_file"])))
        else:
            B.log.warning("Song '%s'no added  to iTunes" % os.path.basename(file_metadata["target_file"]))
            return False
        return True

    def do_file(self, file_name):
        error_code = 1
        B.log.debug("do_file %s" % file_name)
        if self.process_file(file_name):
            B.log.info("Everything worked as expected. Congratulations!")
            error_code = 0
        else:
            B.log.error("Something went wrong. Check your logs")
        return error_code


def main():
    B.log.debug("Main")
    music = MusicLib()
    B.log.debug("argv[1] = %s" % sys.argv[1])
    error_code = music.do_file(sys.argv[1])
    B.log.info('Finished')
    return error_code

if __name__ == '__main__':
    exit(main())
