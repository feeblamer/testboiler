def test_import():
    import requests          # проверка, что библиотека импортируется
    assert requests.__name__ == "requests"

