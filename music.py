import os
import re
from musiclib import MusicLib

def add_metadata_to_files():
    music = MusicLib()
    files = [f for f in os.listdir('.') if re.match(r'.*\.m4a$', f)]
    for media_file in files:
        music.process_file(media_file)

add_metadata_to_files()
