# -*- coding: latin-1 -*-
import unittest
from app.utils.string import StringUtil


class TestStringUtility(unittest.TestCase):
    def setUp(self):
        self.string_utility = StringUtil()

    def test_instance(self):
        self.assertIsInstance(self.string_utility, StringUtil)

    def test_no_change_in_file_name(self):
        self.assertEqual(self.string_utility.create_slug('file_name.txt'), 'file_name.txt')

    def test_change_in_file_name(self):
        self.assertEqual(self.string_utility.create_slug('file#name.txt'), 'filename.txt')

    def test_fuzzy_match_with_ratio(self):
        string_one = 'I Put a Spell on You (feat. Brigitte Wickens) [Extended Mix]'
        string_two = 'I Put a Spell on You (Extended Mix)'
        self.assertTrue(self.string_utility.fuzzy_match(string_one, string_two, 72))
        self.assertFalse(self.string_utility.fuzzy_match(string_one, string_two, 73))

    def test_fuzzy_match_exact(self):
        string_one = 'I Put a Spell on You'
        string_two = 'I Put a Spell on You'
        self.assertTrue(self.string_utility.fuzzy_match(string_one, string_two))
        string_two = 'I Put a Spell on You (Extended Mix)'
        self.assertTrue(self.string_utility.fuzzy_match(string_one, string_two))
        self.assertTrue(self.string_utility.fuzzy_match(string_two, string_one))


if __name__ == '__main__':
    unittest.main()
