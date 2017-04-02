import os
import string
import urllib2
import urllib
import shutil
import json
import sys
from config import Config
from log_set import B
from subprocess import Popen, PIPE, STDOUT


class FMMetadata:

    def __init__(self):
        self.album = {"name": "", "artist": ""}
        self.fm_response = {"album": self.album}
        self.have_metadata = False

    def get_track_info(self, artist, album, track):
        B.log.info("Obtaining track info for: artist=%s album=%s track=%s" % (artist, album, track))
        result = {"name": ""}
        if not self.is_album_current(artist, album):
            self.have_metadata = self.get_metadata_from_api(artist, album)
        if self.have_metadata:
            result = self.get_track(track)
        return result

    def is_album_current(self, artist, album):
        compare_name = self.album.get("name") == album.decode('UTF-8', 'ignore')
        compare_album = self.album.get("artist") == artist.decode('UTF-8', 'ignore')
        return compare_name and compare_album

    def get_track(self, track):
        total_track_count = str(len(self.album["tracks"].get("track")))
        result = {"name": track, "number": "0/%s" % total_track_count, "artist": self.album.get("artist")}
        for cur_track in self.album["tracks"].get("track"):
            current_track = StringUtil.create_slug(cur_track.get("name")).upper().encode('ascii', 'ignore')
            input_track = StringUtil.create_slug(track).upper()
            if current_track == input_track:
                B.log.info("Assigning track number %s to metadata" % cur_track.get("@attr").get("rank"))
                result["number"] = "%s/%s" % (cur_track.get("@attr").get("rank"), total_track_count)
                return result
        return result

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
            self.fm_response = json.load(payload)
        except urllib2.HTTPError:
            B.log.warning("Sadly No metadata avilable from the provider %s" % provider)
            result = False
            pass

        self.album = self.fm_response.get("album")
        if self.album is None:
            result = False
        return result


class MediaFile:

    def __init__(self):
        self.metadata = {}
        self.file_util = FileUtility()
        return

    def get_metadata(self, file_name):
        B.log.info("Getting metadata from file.")
        self.metadata = {}
        process = Popen(["ffmpeg", "-y", "-i", file_name, "-f", "ffmetadata", "/dev/null"], stdout=PIPE, stderr=STDOUT)
        stream_data = process.communicate()[0]
        exitcode = process.returncode
        stdout_iterator = stream_data.split("\n")
        for line in stdout_iterator:
            if line.find(" album ") > 0:
                self.metadata["album"] = line.split(":")[1].strip(b" ")
            if line.find(" artist ") > 0:
                self.metadata["artist"] = line.split(":")[1].strip(b" ")
            if line.find(" title ") > 0:
                self.metadata["title"] = line.split(":")[1].strip(b" ")
        self.metadata["exit_code"] = exitcode
        if exitcode == 0:
            self.metadata["alt_album"] = StringUtil.create_slug(self.metadata["album"])
            self.metadata["alt_artist"] = StringUtil.create_slug(self.metadata["artist"])
            self.metadata["alt_title"] = StringUtil.create_slug(self.metadata["title"])
        return self.metadata

    def valid_metadata(self):
        return self.metadata["exit_code"] == 0

    def check_before_move(self, source_file_name, target_directory):
        if not os.path.isfile(source_file_name):
            B.log.error("The source file %s does not exists." % source_file_name)
            return False
        return self.file_util.create_directory(target_directory)

    @staticmethod
    def target_file(source_file_name, target_directory):
        return os.path.join(target_directory, os.path.basename(source_file_name))

    def move(self, source_file_name, target_directory):
        error_code = 0
        B.log.info("Moving file without adding metadata.")
        if not self.check_before_move(source_file_name, target_directory):
            error_code = -1
            return error_code
        target_file_name = self.target_file(source_file_name, target_directory)
        # copy the file with the same metadata to the right directory
        try:
            shutil.move(source_file_name, target_file_name)
        except IOError:
            B.log.warning("Sorry but was not able to move the file %s to %s" % (source_file_name, target_file_name))
            error_code = -1
            pass
        return error_code

    def move_with_new_metadata(self, source_file_name, target_directory, track_info):
        error_code = -1
        B.log.info("Moving file adding metadata.")
        if not self.check_before_move(source_file_name, target_directory):
            return error_code
        target_file_name = self.target_file(source_file_name, target_directory)
        process = Popen(['ffmpeg', '-y', '-i', r'%s' % source_file_name, '-c:a', 'copy',
                         '-metadata', 'track=%s' % track_info['number'],
                         '-metadata', 'album_artist=%s' % track_info["artist"],
                         '-metadata', 'disc=1/1',
                         r'%s' % target_file_name],
                        stdout=PIPE, stderr=PIPE, shell=False)
        stdout_data, stderr_data = process.communicate()
        command_executed = ' '.join(('ffmpeg', '-y', '-i', r'%s' % source_file_name, '-c:a', 'copy',
                                     '-metadata', 'track=%s' % track_info['number'],
                                     '-metadata', 'album_artist=%s' % track_info["artist"],
                                     '-metadata', 'disc=1/1',
                                     r'%s' % target_file_name))
        B.log.info("Executed command: %s" % command_executed)
        error_code = process.returncode
        if error_code == 0:
            try:
                os.remove(source_file_name)
            except IOError:
                B.log.warning("Sorry but was not able to delete file %s" % source_file_name)
                pass
        else:
            B.log.info("STD OUT")
            B.log.info(stdout_data)
            B.log.error("STD ERR")
            B.log.error(stderr_data)
        return error_code


class FileUtility:

    def __init__(self):
        return

    @staticmethod
    def create_directory(dir_name="."):
        if os.path.exists(dir_name):
            if not os.path.isdir(dir_name):
                B.log.error("trying to create a directory where a file name with the same exists already: %s"
                            % dir_name)
                return False
        else:
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
        return slug_string


class MusicLib:

    def __init__(self):
        B.log.info("Initializing MusicLib")
        self.fm_metadata = {}
        self.fm_album = {}
        self.fm_metadata = FMMetadata()
        self.media_file = MediaFile()
        self.music_file = FileUtility()

    def process_file(self, file_name):
        file_name = file_name.decode('UTF-8', 'ignore')
        if not os.path.isfile(file_name):
            B.log.error("File %s does not exists" % file_name)
            return False
        file_metadata = self.media_file.get_metadata(file_name)
        if not self.media_file.valid_metadata():
            B.log.error("Couldn't get the metadata from file: %s" % file_name)
            return False
        track_info = self.fm_metadata.get_track_info(
            artist=file_metadata["artist"],
            album=file_metadata["album"],
            track=file_metadata["title"])
        target_directory = os.path.join(os.path.dirname(file_name),
                                        "Processed",
                                        file_metadata["alt_artist"],
                                        file_metadata["alt_album"])
        B.log.info("Moving %s to %s" % (file_name, target_directory))
        if track_info.get("name") == "":
            self.media_file.move(file_name, target_directory)
        else:
            self.media_file.move_with_new_metadata(file_name, target_directory, track_info)
        return True

    def do_file(self, file_name):
        error_code = 1
        if self.process_file(file_name):
            B.log.info("Everything worked as expected. Congratulations!")
            error_code = 0
        else:
            B.log.error("Something went wrong. Check your logs")
        return error_code


def main():
    music = MusicLib()
    error_code = music.do_file(sys.argv[1])
    B.log.info('Finished')
    return error_code

if __name__ == '__main__':
    exit(main())
