import os
import shutil
import subprocess
from subprocess import PIPE, STDOUT
from app.utils.string import StringUtil
from app.utils.file import FileUtility
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


class MediaFile:

    def __init__(self):
        self.ffmpeg_command = "ffmpeg"
        self.metadata = {}
        self.file_util = FileUtility()
        log.debug("MediaFile initialized")

    def get_metadata(self, file_name):
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
        return self.metadata

    def valid_metadata(self):
        return self.metadata["exit_code"] == 0

    def check_before_move(self):
        log.debug("check_before_move (%s, %s)" % (self.metadata["source_file"], self.metadata["target_directory"]))
        if not os.path.isfile(self.metadata["source_file"]):
            log.error("The source file %s does not exists." % self.metadata["source_file"])
            return False
        return self.file_util.create_directory(self.metadata["target_directory"])

    @staticmethod
    def target_file(source_file_name, target_directory):
        return os.path.join(target_directory, os.path.basename(source_file_name))

    def move(self):
        error_code = 0
        log.debug("Moving file without adding metadata.")
        if not self.check_before_move():
            error_code = -1
            return error_code
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

    def _build_add_metadata_command(self, track_info, album_compilation_indicator):
        command = list()
        command.extend([self.ffmpeg_command, '-y'])
        command.extend(['-i', f'{self.metadata["source_file"]}'])
        command.extend(['-codec', 'copy'])
        command.extend(['-metadata', f'track={track_info["number"]}']),
        command.extend(['-metadata', 'disc=1/1'])
        if album_compilation_indicator:
            command.extend(['-metadata', 'compilation=1'])
        command.append(self.metadata["target_file"])
        log.debug(f"Executing command:\n{' '.join(command)}")
        return command

    def move_with_new_metadata(self, track_info, album_compilation_indicator=False):
        error_code = -1
        log.debug("Moving file adding metadata.")
        if not self.check_before_move():
            return error_code
        command = self._build_add_metadata_command(track_info, album_compilation_indicator)
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

