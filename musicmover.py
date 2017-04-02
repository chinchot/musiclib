import os
import sys
import re
from musiclib import MusicLib
from log_set import B


class MusicMover:

    def add_metadata_to_files(self, path):
        B.log.info('Starting the Music Mover')
        music = MusicLib()
        files = [f for f in os.listdir(path) if re.match(r'.*\.m4a$', f)]
        B.log.info('Found all these files to be moved:')
        B.log.info(','.join(files))
        for media_file in files:
            music.process_file(os.path.join(path, media_file))


def main():
    path = '.'
    if len(sys.argv) == 2:
        path = sys.argv[1]
    B.log.info("Moving files from directory %s" % path)
    MusicMover().add_metadata_to_files(path)
    B.log.info('Mover has finished')

if __name__ == "__main__":
    main()
