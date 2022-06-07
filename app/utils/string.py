import string
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


class StringUtil:

    def __init__(self):
        pass

    @staticmethod
    def create_slug(string_to_slug):
        """
        create a string that can be used for naming a file
        """
        for character in "?*":
            string_to_slug = string_to_slug.replace(character, "_")
        valid_characters = "-_./()' %s%s" % (string.ascii_letters, string.digits)
        slug_string = ''.join(character for character in string_to_slug if character in valid_characters)
        log.debug("Slug for '%s' is '%s'" % (string_to_slug, slug_string))
        return slug_string
