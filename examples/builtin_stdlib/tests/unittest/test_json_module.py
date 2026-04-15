import json
import unittest


class TestJsonModule(unittest.TestCase):
    def test_json_roundtrip(self):
        payload = {"value": 123, "name": "stdlib"}
        encoded = json.dumps(payload)
        decoded = json.loads(encoded)
        self.assertEqual(decoded, payload)
