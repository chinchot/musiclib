import subprocess
from subprocess import PIPE
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


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
        log.debug("Executed command: %s" % command_executed)
        error_code = process.returncode
        log.debug("Error Code from %s = %s" % (command, error_code))
        if error_code == 0:
            log.info("Added file '%s' to iTunes" % file_name)
        else:
            log.debug("STD OUT")
            log.debug(stdout_data)
            log.error("STD ERR")
            log.error(stderr_data)
            raise ErrorExecuteAppleScript(f'Error while executing: {command_executed}')

    @staticmethod
    def add_track_art(track_name, album_name, image_location):
        command = 'osascript'
        process = subprocess.Popen([command, 'add image.scpt', album_name, track_name, image_location],
                                   stdout=PIPE, stderr=PIPE, shell=False)
        stdout_data, stderr_data = process.communicate()
        log.debug("Executed command:")
        error_code = process.returncode
        log.debug("Error Code from %s = %s" % (command, error_code))
        if error_code == 0:
            log.debug("image added")
        else:
            log.debug("STD OUT")
            log.debug(stdout_data)
            log.error("STD ERR")
            log.error(stderr_data)
        return error_code


class ErrorExecuteAppleScript(Exception):
    pass
