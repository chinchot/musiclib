import os
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


class FileUtility:

    def __init__(self):
        pass

    @staticmethod
    def create_directory(dir_name=".") -> None:
        if os.path.exists(dir_name):
            log.debug(f"Directory %s already exists {dir_name}")
            if not os.path.isdir(dir_name):
                raise ErrorNotAbleToCreateDir(f"Trying to create a directory where a file name with the same exists"
                                              f" already: {dir_name}")
        else:
            log.debug("Creating directory: %s" % dir_name)
            try:
                os.makedirs(dir_name)
            except IOError:
                raise ErrorNotAbleToCreateDir(f"Were not able to create directory {dir_name}")


class ErrorNotAbleToCreateDir(Exception):
    pass
