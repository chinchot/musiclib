import os
import re
import urllib
import requests
import json
from requests.exceptions import MissingSchema
from app.utils.string import StringUtil
import logging.config

log = logging.getLogger('music')


class FMMetadata:

    def __init__(self, api_key, url):
        self.album = {"name": "", "artist": ""}
        self.fm_response = {"album": self.album}
        self.have_metadata = False
        self.have_metadata = False
        self.api_key = api_key
        self.url = url
        log.debug("Init FMMetadata")

    def get_track_info(self, file_metadata):
        log.info("Obtaining track info for: artist=%s album=%s track=%s"
                   % (file_metadata['artist'], file_metadata['album'], file_metadata['title']))
        result = {"name": ""}
        if not self.is_album_current(file_metadata['artist'], file_metadata['album']):
            log.debug("Album not current picking up metadata from service")
            self.have_metadata = self.get_metadata_from_api(file_metadata['artist'], file_metadata['album'])
        if self.have_metadata:
            log.debug("Metadata is already home, we can try to match the track name.")
            result = self.get_track(file_metadata)
        return result

    def is_album_current(self, artist, album):
        log.debug("Comparing Album '%s' to '%s'" % (self.album.get("name"), album))
        compare_name = self.album.get("name") == album
        log.debug("Comparing Artist '%s' to '%s'" % (self.album.get("artist"), artist))
        compare_album = self.album.get("artist") == artist
        return compare_name and compare_album

    def get_art(self):
        image_location = None
        image_list = self.album.get('image')
        if image_list:
            for image in image_list:
                if image.get('size') == 'mega':
                    image_url = image.get('#text')
                    log.debug(f'Getting image from {image_url}')
                    try:
                        response = requests.get(image_url)
                    except MissingSchema as e:
                        log.error(e)
                        raise NoImageError
                    image_location = "/users/manolo/Downloads/sample_image.jpg"
                    file = open(image_location, "wb")
                    file.write(response.content)
                    file.close()
        if not image_location:
            raise NoImageError
        return image_location

    def get_track(self, file_metadata):
        track_number_found = False
        total_track_count = 0
        result = {"name": file_metadata['title'], "artist": self.album.get("artist")}
        try:
            total_track_count = str(len(self.album["tracks"].get("track")))
            log.debug("Total track count is %s" % total_track_count)
            result["number"] = "0/%s" % total_track_count
            for cur_track in self.album["tracks"].get("track"):
                current_track = StringUtil.create_slug(cur_track.get("name")).upper()
                input_track = StringUtil.create_slug(file_metadata['title']).upper()
                log.debug("Comparing track name '%s' to '%s'" % (current_track, input_track))
                if current_track == input_track:
                    log.debug("Assigning track number %s to track %s" %
                               (cur_track.get("@attr").get("rank"), file_metadata['title']))
                    result["number"] = "%s/%s" % (cur_track.get("@attr").get("rank"), total_track_count)
                    track_number_found = True
                    break
        except (AttributeError, KeyError):
            pass
        if not track_number_found:
            alt_track_number = self.alternative_track_number(file_metadata['target_directory'])
            result["number"] = "%s/%s" % (alt_track_number, total_track_count)
            log.debug("Assigning alt track number %s to track %s" % (alt_track_number, file_metadata['title']))
        return result

    @staticmethod
    def alternative_track_number(target_directory):
        if os.path.exists(target_directory):
            files = [f for f in os.listdir(target_directory) if re.match(r'.*\.m4a$', f)]
        else:
            raise Exception('Something went terribly wrong, you are trying to check for music files (*.m4a) on a '
                            'directory that doesn\'t exist. This directory is not there: %s'%target_directory)
        return len(files) + 1

    def get_metadata_from_api(self, artist, album):
        result = True
        query = {"format": "json", "method": "album.getinfo", "api_key": self.api_key,
                 "artist": artist, "album": str(album)}
        url_query = urllib.parse.urlencode(query)
        provider = self.url
        url = provider + "?" + url_query
        try:
            log.debug("Acquiring metadata from: %s" % url)
            payload = requests.get(url)
            log.debug("Data gotten from service")
            self.fm_response = json.loads(payload.content)
        except requests.exceptions.HTTPError:
            log.warning("Sadly No metadata available from the provider %s" % provider)
            result = False

        self.album = self.fm_response.get("album")
        if self.album is None:
            result = False
        log.debug("Album name from service: %s" % self.album)
        return result


class NoImageError(Exception):
    pass
