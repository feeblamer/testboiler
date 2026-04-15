import json


def test_json_roundtrip():
    payload = {"value": 123, "name": "stdlib"}
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded == payload
