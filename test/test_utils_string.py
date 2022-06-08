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


if __name__ == '__main__':
    unittest.main()
