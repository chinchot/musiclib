import unittest
from musiclib import FileUtility

class TestFileUtility(unittest.TestCase):
    def setUp(self):
        self.file_utility = FileUtility()

    def test_instance(self):
        self.assertIsInstance(self.file_utility, FileUtility)


if __name__ == '__main__':
    unittest.main()
