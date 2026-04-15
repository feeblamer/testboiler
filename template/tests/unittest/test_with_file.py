import json
import tempfile
import unittest
from pathlib import Path


class TestWithTemporaryFile(unittest.TestCase):
    def test_create_json_file(self):
        # TemporaryDirectory creates a real temporary folder in the system temp area.
        # The file is created inside that folder and removed after the `with` block ends.
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "sample.json"
            file_path.write_text('{"value": 123}', encoding="utf-8")

            data = json.loads(file_path.read_text(encoding="utf-8"))
            self.assertEqual(data["value"], 123)
