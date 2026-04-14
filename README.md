# testboiler

`testboiler` — это небольшой CLI-бойлерплейт для быстрого создания окружения тестирования Python-библиотеки.

## Команды

- `testboiler init` копирует файлы шаблона в текущую директорию, но только если она пустая.
- `testboiler init <dir>` создаёт новую директорию и инициализирует шаблон в ней. Если директория уже существует, команда завершается с ошибкой.
- `testboiler install` создаёт `.venv`, если его ещё нет, и устанавливает зависимости из `requirements.txt`, а также пакет из `quickboiler.cfg`.
- `testboiler run` запускает включённые наборы тестов из `quickboiler.cfg`.
- `testboiler venv` создаёт локальный `.venv`.

## Быстрый старт

```bash
python -m pip install -e .
testboiler init my_project
cd my_project
```

После этого отредактируйте `quickboiler.cfg`, добавьте свои тесты в `tests/pytest/` или `tests/unittest/` и выполните:

```bash
testboiler install
testboiler run
```

Примечания:
- `testboiler install` создаёт и использует локальный `.venv` проекта.
- `testboiler install` устанавливает пакеты из локального `requirements.txt` в этот `.venv`.
- `testboiler install` также устанавливает пакет из `quickboiler.cfg` в тот же `.venv`, если `library` задана.
- `testboiler run` не устанавливает пакеты. Он только запускает тесты, используя уже существующий `.venv`.
- Укажите `library: None` в `quickboiler.cfg`, если тестируете только встроенные модули Python.
