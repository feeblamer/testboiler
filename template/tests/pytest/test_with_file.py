import json


def test_create_json_file(tmp_path):
    # tmp_path is a temporary directory created by pytest for this test.
    # The file is created inside that directory and removed by pytest later.
    file_path = tmp_path / "sample.json"
    file_path.write_text('{"value": 123}', encoding="utf-8")

    data = json.loads(file_path.read_text(encoding="utf-8"))
    assert data["value"] == 123
