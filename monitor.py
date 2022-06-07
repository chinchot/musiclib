#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from musiclib import MusicLib
import time
import sys
import re
import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('monitor')


class MyEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.music = MusicLib()

    def catch_created_handler(self, event):
        log.debug(f"New file has been created: {event.src_path}")
        if re.match(r'.*\.m4a$', event.src_path):
            exit_code = self.music.do_file(event.src_path)
            log.debug(f"Created File Processed: {event.src_path}. Exit Code {exit_code}")

    def catch_moved_handler(self, event):
        log.debug(f"Files are being moved from {event.dest_path} to {event.src_path}")
        if os.path.dirname(event.src_path) == os.path.dirname(event.dest_path):
            log.debug(f"File moved in same directory {os.path.dirname(event.dest_path)}")
            if re.match(r'.*\.m4a$', event.dest_path):
                log.debug(f"New File: {event.dest_path}")
                exit_code = self.music.do_file(event.dest_path)
                log.debug(f"File Processed: {event.dest_path}. Exit Code {exit_code}")

    @staticmethod
    def catch_all_handler(event):
        log.debug(event)

    def on_moved(self, event):
        self.catch_moved_handler(event)

    def on_created(self, event):
        self.catch_created_handler(event)

    def on_deleted(self, event):
        MyEventHandler.catch_all_handler(event)

    def on_modified(self, event):
        MyEventHandler.catch_all_handler(event)


def main():
    path = '.'
    if len(sys.argv) == 2:
        path = sys.argv[1]
    log.info(f"Watching directory {path}")
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        log.info('End monitoring')
    observer.join()


if __name__ == "__main__":
    main()
