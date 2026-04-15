# testboiler

`testboiler` — это небольшой CLI-бойлерплейт для быстрого создания окружения тестирования Python-библиотеки.

Структура репозитория теперь разделена на:
- `src/testboiler/` — код CLI;
- `template/` — единственный источник файлов шаблона;
- `tests/` — тесты самого проекта;
- `examples/` — примеры готовых проектов;
- `docs/` — внутренняя документация и аналитические заметки.

## Команды

- `testboiler init` копирует файлы шаблона в текущую директорию, если она пустая или содержит только `.venv`.
- `testboiler init <dir>` создаёт новую директорию и инициализирует шаблон в ней. Если директория уже существует, команда завершается с ошибкой.
- `testboiler install` работает только с локальным `.venv` в корне проекта. Если `.venv` ещё нет, команда создаёт его автоматически.
- `testboiler install --force` принудительно переустанавливает зависимости, даже если `config.yml` и `requirements.txt` не изменились.
- `testboiler run` запускает включённые наборы тестов из `config.yml`.
- `testboiler venv` создаёт локальный `.venv` в корне проекта.

## Быстрый старт

```bash
python -m pip install -e .
testboiler init my_project
cd my_project
```

После этого отредактируйте `config.yml`, добавьте свои тесты в `tests/pytest/` или `tests/unittest/` и выполните:

```bash
testboiler install
testboiler run
```

Примечания:
- `testboiler` жёстко разделяет `tool environment` и `project environment`.
- Окружение, из которого запущен сам CLI, включая `pipx`, не используется как окружение проекта.
- Единственное поддерживаемое project environment — локальный `.venv` в корне проекта.
- `testboiler install` создаёт `.venv`, если нужно, и устанавливает пакеты из локального `requirements.txt` только туда.
- `testboiler install` также устанавливает пакет из `config.yml` в тот же локальный `.venv`, если `library` задана.
- `testboiler install` повторно ничего не ставит, если `config.yml` и `requirements.txt` не менялись.
- `testboiler run` не устанавливает пакеты. Он использует только уже подготовленный локальный `.venv` и требует повторный `testboiler install`, если конфиг или зависимости изменились.
- Укажите `library: null` в `config.yml`, если тестируете только встроенные модули Python.

Структура `library` в `config.yml`:

```yaml
library:
  distribution: requests==2.32.0
  import_name: requests
```

## Примеры

- `examples/builtin_stdlib/` — пример проекта для встроенных модулей Python.
- Для работы с примером сначала создайте локальный `.venv` в каталоге примера или выполните `testboiler install`, чтобы он был создан автоматически.
