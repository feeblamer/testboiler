## TESTBOILER — MVP бойлерплейта для быстрого тестирования Python-библиотек

### 1. Текущее состояние

`testboiler` — это CLI-пакет, который быстро разворачивает каталог для тестирования сторонней Python-библиотеки или встроенных модулей Python.

В текущем MVP уже есть:
- CLI-команды `init`, `install`, `run`, `venv`;
- шаблон проекта с `pytest` и `unittest`;
- конфиг `config.yml`;
- установка зависимостей только в локальное проектное виртуальное окружение `.venv`;
- idempotent-поведение `install` через state-файл внутри локального `.venv`.

### 2. Структура репозитория

```text
repo/
├─ src/testboiler/
├─ template/
├─ tests/
├─ examples/
├─ docs/
├─ README.md
├─ pyproject.toml
└─ setup.py
```

Назначение каталогов:
- `src/testboiler/` — код CLI;
- `template/` — единственный источник шаблонных файлов для `testboiler init`;
- `tests/` — тесты самого инструмента;
- `examples/` — готовые sample projects;
- `docs/` — проектная документация и аналитические заметки.

### 3. Структура создаваемого проекта

```text
my_project/
├─ tests/
│  ├─ pytest/
│  │  ├─ test_1.py
│  │  └─ test_with_file.py
│  └─ unittest/
│     ├─ test_1.py
│     └─ test_with_file.py
├─ config.yml
└─ requirements.txt
```

Шаблонные тесты не привязаны к конкретной библиотеке. Это заготовки, в которые пользователь добавляет свои проверки.

### 4. Конфиг `config.yml`

```yaml
library:
  distribution: beautifulsoup4
  import_name: bs4

framework:
  pytest: true
  unittest: true
```

Для встроенных модулей Python:

```yaml
library: null

framework:
  pytest: true
  unittest: false
```

Правила:
- `library` задаётся либо как mapping с `distribution` и `import_name`, либо как `null`;
- `distribution` используется для `pip install`;
- `import_name` используется для runtime-проверки импорта перед запуском тестов;
- хотя бы один раннер в `framework` должен быть включён.

### 5. Проектное виртуальное окружение

`testboiler` жёстко разделяет:

1. `tool environment` — окружение, из которого запускается сам CLI.
2. `project environment` — локальный `.venv` в корне текущего boilerplate-проекта.

Правила:
- `tool environment` никогда не используется как окружение проекта;
- active virtualenv, системный Python и `pipx`-окружение игнорируются при выборе project environment;
- единственное поддерживаемое project environment — `.venv` в корне проекта;
- если `.venv` ещё нет, `testboiler install` или `testboiler venv` создаёт его.

State-файл `install` всегда хранится в локальном project environment:
- `.venv/.testboiler-install-state.json`.

### 6. Поведение команд

`testboiler init`:
- копирует шаблон в текущий каталог;
- работает в полностью пустом каталоге;
- также работает в каталоге, где уже существует только `.venv`;
- `testboiler init <dir>` создаёт новую папку и разворачивает шаблон в ней, если такой папки ещё нет.

`testboiler install`:
- работает только с локальным `.venv`;
- создаёт локальный `.venv`, если его ещё нет;
- устанавливает зависимости из `requirements.txt`;
- устанавливает пакет из `config.yml`, если `library` задана;
- записывает state-файл и не повторяет установку без необходимости;
- `testboiler install --force` принудительно переустанавливает зависимости.

`testboiler run`:
- ничего не устанавливает;
- требует существующий локальный `.venv` и актуальный state;
- проверяет, что `pytest` и библиотека из `config.yml` действительно доступны в локальном `.venv`;
- запускает только включённые раннеры.

`testboiler venv`:
- создаёт локальный `.venv`, если его ещё нет;
- не взаимодействует с внешними virtualenv и не зависит от них.

Также доступен запуск через:

```bash
python -m testboiler
```

### 7. Минимальные сценарии

Сценарий с локальным `.venv`:

```bash
python -m pip install -e .
testboiler init my_project
cd my_project
testboiler install
testboiler run
```

Сценарий с явным созданием project environment:

```bash
python -m venv .venv
source .venv/bin/activate
testboiler init
testboiler install
testboiler run
```

### 8. Границы текущего MVP

В этот MVP не входят:
- Docker и `dockerize`;
- CI-интеграция;
- поддержка нескольких библиотек в одном конфиге;
- автогенерация `requirements.txt`;
- выбор между несколькими project environments через отдельный флаг CLI.

### 9. Примеры

В каталоге `examples/` лежат готовые примеры проектов.

Текущий пример:
- `examples/builtin_stdlib/` — проект для встроенных модулей Python с `library: null`.

Для примеров нужно подготовить локальный `.venv` в каталоге самого примера через `testboiler install` или `testboiler venv`.
