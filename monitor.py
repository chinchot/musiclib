#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from musiclib import MusicLib, FileUtility
import time
import sys
import re
import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
logging.config.fileConfig('logging_config.ini')
logging.getLogger('root')

class MyEventHandler(FileSystemEventHandler):

    def __init__(self):
        self.music = MusicLib()

    def catch_created_handler(self, event):
        logging.info("New File: %s" % event.src_path)
        if re.match(r'.*\.m4a$', event.src_path):
            exit_code = self.music.do_file(event.src_path)
            logging.info("File Processed: %s. Exit Code %s" % (event.src_path, exit_code))

    def catch_moved_handler(self, event):
        logging.info("New File: %s" % event.dest_path)
        logging.info("Old File: %s" % event.src_path)
        logging.info("New Path: %s" % os.path.dirname(event.dest_path))
        logging.info("Old Path: %s" % os.path.dirname(event.src_path))
        if os.path.dirname(event.src_path) == os.path.dirname(event.dest_path):
            logging.info("File moved in same directory")
            if re.match(r'.*\.m4a$', event.dest_path):
                logging.info("New File: %s" % event.dest_path)
                exit_code = self.music.do_file(event.dest_path)
                logging.info("File Processed: %s. Exit Code %s" % (event.dest_path, exit_code))

    def catch_all_handler(self, event):
        logging.info(event)

    def on_moved(self, event):
        self.catch_moved_handler(event)

    def on_created(self, event):
        self.catch_created_handler(event)

    def on_deleted(self, event):
        self.catch_all_handler(event)

    def on_modified(self, event):
        self.catch_all_handler(event)


def main():
    path = '.'
    if len(sys.argv) == 2:
        path = sys.argv[1]
    logging.info("Watching directory %s" % path)
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info('Finished')
    observer.join()

if __name__ == "__main__":
    main()
