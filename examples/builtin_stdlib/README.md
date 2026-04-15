# builtin_stdlib

Пример проекта для тестирования встроенных модулей Python.

Этот пример не создаёт собственный `.venv` и рассчитан на использование корневого
окружения репозитория.

Примеры запуска из корня репозитория:

```bash
./.venv/bin/python -m pytest examples/builtin_stdlib/tests/pytest
./.venv/bin/python -m unittest discover -s examples/builtin_stdlib/tests/unittest
```
