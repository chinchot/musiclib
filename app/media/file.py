import os
import shutil
import subprocess
from subprocess import PIPE, STDOUT
from app.utils.string import StringUtil
from app.fm_metadata.metadata import FMMetadata
from app.utils.file import FileUtility, ErrorNotAbleToCreateDir
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


class MediaFile:

    def __init__(self):
        self.ffmpeg_command = "ffmpeg"
        self.metadata = dict()
        self.track_info = dict()
        self.file_util = FileUtility()
        self.fm_metadata = FMMetadata()
        log.debug("MediaFile initialized")

    def get_track_info(self):
        self.track_info = self.fm_metadata.get_track_info(self.metadata)

    def get_metadata_from_file(self, file_name):
        log.info("Getting metadata from file %s." % file_name)
        self.metadata = {}
        process = subprocess.Popen([self.ffmpeg_command, "-y", "-i", file_name, "-f", "ffmetadata", "/dev/null"],
                                   stdout=PIPE, stderr=STDOUT)
        command_executed = ' '.join((self.ffmpeg_command, "-y", "-i", file_name, "-f", "ffmetadata", "/dev/null"))
        log.debug("Executed command: %s" % command_executed)
        stream_data = process.communicate()[0]
        exitcode = process.returncode
        stdout_iterator = stream_data.decode('utf-8').split("\n")
        for line in stdout_iterator:
            log.debug(line)
            if line.find(" album ") > 0:
                self.metadata["album"] = line.split(":")[1].strip(" ")
            if line.find(" artist ") > 0:
                self.metadata["artist"] = line.split(":")[1].strip(" ")
            if line.find(" title ") > 0:
                self.metadata["title"] = line.split(":")[1].strip(" ")
        self.metadata["exit_code"] = exitcode
        self.metadata["source_file"] = file_name
        log.debug("Exit Code from ffmpeg = %s" % exitcode)
        if exitcode == 0:
            self.metadata["alt_album"] = StringUtil.create_slug(self.metadata["album"])
            self.metadata["alt_artist"] = StringUtil.create_slug(self.metadata["artist"])
            self.metadata["alt_title"] = StringUtil.create_slug(self.metadata["title"])
            self.metadata["target_directory"] = os.path.join(os.path.dirname(file_name), "..",
                                                             "Processed", self.metadata["alt_album"])
            self.metadata["target_file"] = os.path.join(self.metadata["target_directory"], os.path.basename(file_name))
        log.debug("get_metadata = %s" % self.metadata)

    def get_metadata(self, file_name):
        self.get_metadata_from_file(file_name)
        if self.target_directory:
            FileUtility.create_directory(dir_name=self.target_directory)
            self.get_track_info()

    @property
    def valid_metadata(self):
        return self.metadata["exit_code"] == 0

    @property
    def extra_track_info_available(self):
        return not self.track_info.get('name') == ""

    @property
    def target_file(self):
        return self.metadata.get('target_file')

    @property
    def track_number(self):
        return self.track_info.get('number')

    @property
    def track_name(self):
        return self.track_info.get('name')

    @property
    def album_name(self):
        return self.fm_metadata.album.get('name')

    @property
    def metadata_album_name(self):
        return self.metadata.get('album')

    @property
    def metadata_artist_name(self):
        return self.metadata.get('artist')

    @property
    def metadata_track_name(self):
        return self.metadata.get('title')

    @property
    def target_directory(self):
        return self.metadata.get('target_directory')

    def check_before_move(self):
        log.debug(f'Checking file exists to move from'
                  f' \'{self.metadata["source_file"]}\' to \'{self.metadata["target_directory"]}\'')
        if not os.path.isfile(self.metadata["source_file"]):
            raise ErrorFileMissing(f'The source file {self.metadata["source_file"]} does not exists.')

    def get_art(self):
        return self.fm_metadata.get_art()

    def move_file(self, album_compilation_indicator):
        if self.extra_track_info_available:
            if self.move_with_new_metadata(album_compilation_indicator) != 0:
                raise ErrorMovingFile('Error while trying to move the file with metadata to new location.')
        else:
            if self.move_without_additional_metadata() != 0:
                raise ErrorMovingFile('Error while trying to move the file to new location.')

    def move_without_additional_metadata(self):
        error_code = 0
        log.debug("Moving file without adding metadata.")
        try:
            self.check_before_move()
        except (ErrorFileMissing, ErrorNotAbleToCreateDir) as e:
            log.error(e)
            error_code = -1
            return error_code
        self.file_util.create_directory(self.metadata["target_directory"])
        log.debug("target_file = %s" % self.metadata["target_file"])
        # copy the file with the same metadata to the right directory
        try:
            log.debug("Moving File %s to %s" % (self.metadata["source_file"], self.metadata["target_file"]))
            shutil.move(self.metadata["source_file"], self.metadata["target_file"])
        except IOError:
            log.warning("Sorry but was not able to move the file %s to %s" %
                        (self.metadata["source_file"], self.metadata["target_file"]))
            error_code = -1
            pass
        log.debug("move error code = %s" % error_code)
        return error_code

    def _build_add_metadata_command(self, input_file, track_number, disc, output_file, album_compilation_indicator,
                                    album_artist=None):
        command = list()
        command.extend([self.ffmpeg_command, '-y'])
        command.extend(['-i', f'{input_file}'])
        command.extend(['-codec', 'copy'])
        command.extend(['-metadata', f'track={track_number}']),
        command.extend(['-metadata', f'disc={disc}'])
        if album_artist is not None:
            command.extend(['-metadata', f'album_artist={album_artist}'])
        if album_compilation_indicator:
            command.extend(['-metadata', 'compilation=1'])
        command.append(output_file)
        log.debug(f"Executing command:\n{' '.join(command)}")
        return command

    def _execute(self, command):
        process = subprocess.Popen(command, stdout=PIPE, stderr=PIPE, shell=False)
        stdout_data, stderr_data = process.communicate()
        error_code = process.returncode
        log.debug("Error Code from %s = %s" % (self.ffmpeg_command, error_code))
        log.debug("STD OUT")
        log.debug(stdout_data)
        if error_code != 0:
            log.error("STD ERR")
            log.error(stderr_data)
            raise ErrorExecuteCommand(stderr_data)

    def add_metadata(self, input_file, track_number, disc, album_compilation_indicator, album_artist=None):
        output_file = os.path.join(os.path.dirname(input_file), 'temp.m4a')
        command = self._build_add_metadata_command(input_file=input_file,
                                                   track_number=track_number,
                                                   disc=disc, output_file=output_file,
                                                   album_compilation_indicator=album_compilation_indicator,
                                                   album_artist=album_artist)
        self._execute(command=command)
        shutil.move(output_file, input_file)

    def move_with_new_metadata(self, album_compilation_indicator):
        error_code = -1
        log.debug("Moving file adding metadata.")
        try:
            self.check_before_move()
            self.file_util.create_directory(self.metadata["target_directory"])
        except (ErrorFileMissing, ErrorNotAbleToCreateDir) as e:
            log.error(e)
            return error_code
        command = self._build_add_metadata_command(input_file=self.metadata["source_file"],
                                                   track_number=self.track_info.get("number"),
                                                   disc='1/1', output_file=self.metadata["target_file"],
                                                   album_compilation_indicator=album_compilation_indicator)
        process = subprocess.Popen(command, stdout=PIPE, stderr=PIPE, shell=False)
        stdout_data, stderr_data = process.communicate()
        error_code = process.returncode
        log.debug("Error Code from %s = %s" % (self.ffmpeg_command, error_code))
        if error_code == 0:
            try:
                log.debug("Deleting file %s" % self.metadata["source_file"])
                os.remove(self.metadata["source_file"])
            except IOError:
                log.warning("Sorry but was not able to delete file %s" % self.metadata["source_file"])
                pass
        else:
            log.debug("STD OUT")
            log.debug(stdout_data)
            log.error("STD ERR")
            log.error(stderr_data)
        return error_code


class ErrorFileMissing(Exception):
    pass


class ErrorMovingFile(Exception):
    pass


class ErrorExecuteCommand(Exception):
    pass
