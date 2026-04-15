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
- `testboiler install` использует локальный `.venv`, а если его нет — активированное виртуальное окружение. Если нет ни того, ни другого, команда создаёт локальный `.venv`.
- `testboiler install --force` принудительно переустанавливает зависимости, даже если `config.yml` и `requirements.txt` не изменились.
- `testboiler run` запускает включённые наборы тестов из `config.yml`.
- `testboiler venv` создаёт локальный `.venv`, но не делает этого, если проект уже использует активированное внешнее окружение.

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
- `testboiler install` использует project environment: локальный `.venv` или уже активированное внешнее виртуальное окружение.
- `testboiler install` устанавливает пакеты из локального `requirements.txt` в используемое окружение.
- `testboiler install` также устанавливает пакет из `config.yml` в то же окружение, если `library` задана.
- `testboiler install` повторно ничего не ставит, если `config.yml` и `requirements.txt` не менялись.
- `testboiler run` не устанавливает пакеты. Он использует уже подготовленное project environment и требует повторный `testboiler install`, если конфиг или зависимости изменились.
- Укажите `library: null` в `config.yml`, если тестируете только встроенные модули Python.

Структура `library` в `config.yml`:

```yaml
library:
  distribution: requests==2.32.0
  import_name: requests
```

## Примеры

- `examples/builtin_stdlib/` — пример проекта для встроенных модулей Python.
- Этот пример использует корневой `.venv` текущего репозитория и не создаёт собственное виртуальное окружение.
