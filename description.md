## TESTBOILER — MVP бойлерплейта для быстрого тестирования Python-библиотек

### 1. Что уже реализовано

`testboiler` — это CLI-пакет, который помогает быстро подготовить каталог для проверки сторонней Python-библиотеки.

В текущем MVP есть:
- шаблон проекта с `pytest` и `unittest`;
- конфиг `quickboiler.cfg`;
- локальный `.venv` для запуска тестов;
- CLI-команды `init`, `install`, `run`, `venv`.

### 2. Структура шаблона

```text
my_project/
├─ tests/
│  ├─ pytest/
│  │   └─ test_1.py
│  └─ unittest/
│      └─ test_1.py
├─ requirements.txt
└─ quickboiler.cfg
```

Шаблонные тесты не содержат кода под конкретную библиотеку. Это заготовки, в которые пользователь добавляет свои проверки.

### 3. Конфиг `quickboiler.cfg`

```yaml
# Укажите библиотеку, которую хотите тестировать.
# Это шаблон: замените значение ниже на реальный пакет.
library: <lib==2.0.1>

framework:
  pytest: true
  unittest: true
```

Правила:
- `library` можно задать как реальный пакет или как `None`, если тестируются только встроенные модули Python;
- если указан реальный пакет, он устанавливается в локальный `.venv` проекта;
- если `pytest: true`, запускается `pytest tests/pytest`;
- если `unittest: true`, запускается `python -m unittest discover -s tests/unittest`;
- хотя бы один раннер должен быть включён.

### 4. Локальное окружение проекта

`testboiler install` и `testboiler run` работают через `.venv` внутри boilerplate-проекта.

Команда `testboiler install`:
- создаёт `.venv`, если его ещё нет;
- устанавливает зависимости из `requirements.txt` именно в `.venv`;
- устанавливает зависимость из `quickboiler.cfg` тоже в `.venv`, если `library` задана.

Команда `testboiler run`:
- использует уже существующий `.venv`;
- не выполняет установку пакетов повторно;
- запускает тесты через Python из `.venv`.

Это позволяет запускать `testboiler` из `pipx`, не засоряя окружение самого CLI.

### 5. Команды CLI

После `pip install -e .` доступны:

- `testboiler init` — копирует шаблон в текущий пустой каталог;
- `testboiler init <dir>` — создаёт новую папку и разворачивает шаблон в ней;
- `testboiler install` — создаёт/использует локальный `.venv` и ставит туда зависимости из `requirements.txt` и `quickboiler.cfg`;
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
1. Открыть `quickboiler.cfg` и указать реальную библиотеку.
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
