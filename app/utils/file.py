import os
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


class FileUtility:

    def __init__(self):
        pass

    @staticmethod
    def create_directory(dir_name="."):
        if os.path.exists(dir_name):
            log.debug("Directory %s already exists" % dir_name)
            if not os.path.isdir(dir_name):
                log.error(f"trying to create a directory where a file name with the same exists already: {dir_name}")
                return False
        else:
            log.debug("Creating directory: %s" % dir_name)
            try:
                os.makedirs(dir_name)
            except IOError:
                log.error("Were not able to create directory %s" % dir_name)
                return False
        return True

