import unittest
from resource_finder import ResourceFinder


class TestResourceFinder(unittest.TestCase):
    def test_get_resource(self):
        resource_finder = ResourceFinder()
        self.assertEqual(resource_finder.get_resource(2.50, "color"), "blue")


if __name__ == '__main__':
    unittest.main()
