import string
import logging.config
from fuzzywuzzy import fuzz

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
        valid_characters = "-_./' %s%s" % (string.ascii_letters, string.digits)
        slug_string = ''.join(character for character in string_to_slug if character in valid_characters)
        log.debug("Slug for '%s' is '%s'" % (string_to_slug, slug_string))
        return slug_string

    @staticmethod
    def fuzzy_match(string1, string2, match_ratio=100):
        string_one = StringUtil.create_slug(string1.upper())
        string_two = StringUtil.create_slug(string2.upper())
        if string_one == string_two or string_one.startswith(string_two) or string_two.startswith(string_one):
            return True
        ratio = fuzz.ratio(string1, string2)
        ratio_limit = 50
        if ratio > ratio_limit:
            log.info(f'The comparison between "{string1}" and "{string2}" came down to fuzzy matching with'
                     f' a ratio of {ratio}. This was only reported for ratio above {ratio_limit}')
        return ratio >= match_ratio
