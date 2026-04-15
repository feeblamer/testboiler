## TESTBOILER — MVP бойлерплейта для быстрого тестирования Python-библиотек

### 1. Что уже реализовано

`testboiler` — это CLI-пакет, который помогает быстро подготовить каталог для проверки сторонней Python-библиотеки.

В текущем MVP есть:
- шаблон проекта с `pytest` и `unittest`;
- конфиг `config.yml`;
- локальный `.venv` для запуска тестов;
- CLI-команды `init`, `install`, `run`, `venv`.

Структура репозитория организована так:
- `src/testboiler/` — код CLI;
- `template/` — источник файлов шаблона;
- `tests/` — тесты самого CLI;
- `examples/` — готовые примерные проекты;
- `docs/` — проектная документация.

### 2. Структура шаблона

```text
my_project/
├─ tests/
│  ├─ pytest/
│  │   └─ test_1.py
│  └─ unittest/
│      └─ test_1.py
├─ requirements.txt
└─ config.yml
```

Шаблонные тесты не содержат кода под конкретную библиотеку. Это заготовки, в которые пользователь добавляет свои проверки.
Источник этого шаблона в репозитории: `template/`.

### 3. Конфиг `config.yml`

```yaml
library:
  distribution: requests==2.32.0
  import_name: requests

framework:
  pytest: true
  unittest: true
```

Правила:
- `library` можно задать как mapping с `distribution` и `import_name` или как `null`, если тестируются только встроенные модули Python;
- если указан реальный пакет, `distribution` используется для установки в локальный `.venv`, а `import_name` — для проверки импорта;
- если `pytest: true`, запускается `pytest tests/pytest`;
- если `unittest: true`, запускается `python -m unittest discover -s tests/unittest`;
- хотя бы один раннер должен быть включён.

### 4. Локальное окружение проекта

`testboiler install` и `testboiler run` работают через `.venv` внутри boilerplate-проекта.

Команда `testboiler install`:
- создаёт `.venv`, если его ещё нет;
- устанавливает зависимости из `requirements.txt` именно в `.venv`;
- устанавливает зависимость из `config.yml` тоже в `.venv`, если `library` задана.

Команда `testboiler run`:
- использует уже существующий `.venv`;
- не выполняет установку пакетов повторно;
- запускает тесты через Python из `.venv`.

Это позволяет запускать `testboiler` из `pipx`, не засоряя окружение самого CLI.

### 5. Команды CLI

После `pip install -e .` доступны:

- `testboiler init` — копирует шаблон в текущий пустой каталог;
- `testboiler init <dir>` — создаёт новую папку и разворачивает шаблон в ней;
- `testboiler install` — создаёт/использует локальный `.venv` и ставит туда зависимости из `requirements.txt` и `config.yml`;
- `testboiler run` — использует локальный `.venv` и запускает только те тестовые наборы, которые включены в конфиге;
- `testboiler venv` — создаёт `.venv`.

Также доступен запуск через:

```bash
python -m testboiler
```

### 6. Минимальный рабочий сценарий

```bash
python -m pip install -e .
testboiler init my_project
cd my_project
```

Дальше:
1. Открыть `config.yml` и указать реальную библиотеку.
2. Указать нужные зависимости в `requirements.txt`.

```bash
echo "pytest" >> requirements.txt
```

3. Добавить свои тесты в `tests/pytest/` или `tests/unittest/`.
4. Выполнить:

```bash
testboiler install
testboiler run
```

### 7. Границы текущего MVP

В этот MVP не входят:
- Docker и `dockerize`;
- CI-интеграция;
- поддержка нескольких библиотек в одном конфиге;
- автогенерация `requirements.txt`.

### 8. Примеры

В каталоге `examples/` лежат готовые примеры проектов.

Текущий пример:
- `examples/builtin_stdlib/` — проект для встроенных модулей Python с `library: null`.
 - `examples/builtin_stdlib/` — проект для встроенных модулей Python с `library: null`.

Примеры не создают собственный `.venv` и рассчитаны на использование корневого виртуального окружения репозитория.
