import ConfigParser
import os
import sys

def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


@singleton
class Config:

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        config_file = "%s.dev.ini" % os.path.basename(sys.argv[0]).replace(".py", "")
        self.config.read(config_file)
        return

    def getvalue(self, section, key):
        return self.config.get(section=section, option=key)
