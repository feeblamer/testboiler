import unittest

class TestImport(unittest.TestCase):
    def test_import(self):
        import requests
        self.assertEqual(requests.__name__, "requests")

if __name__ == "__main__":
    unittest.main()

