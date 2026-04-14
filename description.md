## QUICKBOILER — Бойлерплейт для мгновенного тестирования любой Python‑библиотеки  

### 1️⃣ Структура готового проекта  

```
my_project/
├─ src/                       # место для кода (можно оставить пустым)
├─ tests/
│  ├─ pytest/
│  │   └─ test_example.py     # шаблонный pytest‑тест
│  └─ unittest/
│      └─ test_example.py     # шаблонный unittest‑тест
├─ .venv/                     # (опционально) локальное virtualenv
├─ requirements.txt           # будет заполнен автоматически
├─ quickboiler.cfg            # конфиг проекта
├─ sitecustomize.py           # авто‑установка зависимости
└─ quickboiler/               # исполняемый пакет CLI
   ├─ __init__.py
   └─ __main__.py             # entry‑point: quickboiler <command>
```

### 2️⃣ Файл `quickboiler.cfg` (YAML)

```yaml
# Укажите библиотеку, которую нужно тестировать
library: requests==2.31.0

# Какие наборы тестов включать (можно отключить один из блоков)
framework:
  pytest: true
  unittest: true
```

*Если версия не важна – просто `library: requests`.*

### 3️⃣ Авто‑установка зависимости – `sitecustomize.py`

```python
import importlib, subprocess, sys, os, yaml

cfg_path = os.path.join(os.path.dirname(__file__), "quickboiler.cfg")
if os.path.exists(cfg_path):
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    lib = cfg.get("library")
    if lib:
        pkg_name = lib.split("==")[0]          # имя без версии
        try:
            importlib.import_module(pkg_name)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
```

*Python ищет `sitecustomize.py` автоматически при старте интерпретатора, поэтому любой импорт в тестах сначала выполнит проверку и, при необходимости, установит требуемый пакет.*

### 4️⃣ Шаблонные тесты  

**pytest (`tests/pytest/test_example.py`)**  

```python
def test_import():
    import requests          # проверка, что библиотека импортируется
    assert requests.__name__ == "requests"
```

**unittest (`tests/unittest/test_example.py`)**  

```python
import unittest

class TestImport(unittest.TestCase):
    def test_import(self):
        import requests
        self.assertEqual(requests.__name__, "requests")

if __name__ == "__main__":
    unittest.main()
```

Можно добавить свои тесты рядом с этими шаблонами – они будут автоматически обнаружены.

### 5️⃣ CLI‑утилита `quickboiler`  

`quickboiler` — пакет, установленный в окружении (`pip install -e .` из корня проекта). Основные команды:

| Команда | Описание |
|--------|----------|
| `quickboiler init` | Копирует шаблонную структуру в текущий каталог (если ещё нет). |
| `quickboiler run` | Запускает **оба** набора тестов: `pytest tests/pytest` и `python -m unittest discover -s tests/unittest`. |
| `quickboiler venv` | Создаёт локальное виртуальное окружение `.venv` и выводит инструкцию по активации. |
| `quickboiler dockerize` | Генерирует `Dockerfile` и `docker-compose.yml` для изолированного CI‑контейнера. |

#### Минимальная реализация `quickboiler/__main__.py`

```python
import argparse, subprocess, sys, os, shutil

def copy_template(dst):
    src = os.path.join(os.path.dirname(__file__), "..", "quickboiler_template")
    shutil.copytree(src, dst, dirs_exist_ok=True)

def run_pytest():
    subprocess.check_call([sys.executable, "-m", "pytest", "tests/pytest"])

def run_unittest():
    subprocess.check_call([sys.executable, "-m", "unittest", "discover", "-s", "tests/unittest"])

def main():
    parser = argparse.ArgumentParser(prog="quickboiler")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("init")
    sub.add_parser("run")
    sub.add_parser("venv")
    args = parser.parse_args()

    if args.cmd == "init":
        copy_template(os.getcwd())
    elif args.cmd == "run":
        run_pytest()
        run_unittest()
    elif args.cmd == "venv":
        subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
        print("Виртуальное окружение создано в .venv. Активировать:\n  source .venv/bin/activate")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

> **Примечание:** при упаковке проекта добавить в `setup.cfg`/`pyproject.toml` entry‑point `console_scripts = ["quickboiler=quickboiler.__main__:main"]`.

### 6️⃣ Быстрый старт (полный цикл)

1. **Инициализация**  

   ```bash
   mkdir my_project && cd my_project
   python -m quickboiler init      # скопирует шаблон
   ```

2. **Настройка библиотеки**  

   Откройте `quickboiler.cfg` и укажите нужный пакет, например `library: numpy`.

3. **Установка зависимостей**  

   ```bash
   python -m pip install -r requirements.txt pyyaml pytest
   ```

4. **Создание/добавление тестов** в `tests/pytest/` или `tests/unittest/`.

5. **Запуск**  

   ```bash
   python -m quickboiler run
   ```

   - При первом запуске `sitecustomize.py` проверит наличие `numpy`.  
   - Если пакет отсутствует, автоматически выполнит `pip install numpy`.  
   - После установки тесты продолжают выполняться.

### 7️⃣ Расширения (по желанию)

| Расширение | Что добавляет |
|-----------|----------------|
| **Docker‑support** | `quickboiler dockerize` → `Dockerfile` с `FROM python:3.12-slim`, копирует проект, `pip install -r requirements.txt`, затем `ENTRYPOINT ["python","-m","quickboiler","run"]`. |
| **CI‑Hook** | `.github/workflows/quickboiler.yml` вызывает `quickboiler run` в CI‑pipeline. |
| **Pre‑commit** | Скрипт, проверяющий, что `library` установлена перед каждым коммитом. |
| **Multiple libraries** | В `quickboiler.cfg` добавить список `libraries: [requests==2.31.0, numpy]` и модифицировать `sitecustomize.py` для итерации. |

---  

**Итого:**  
* Быстрое развёртывание проекта (`quickboiler init`).  
* Автоматическая установка недостающих зависимостей при первом импорте.  
* Поддержка одновременно `pytest` и `unittest` с возможностью переключения через конфиг.  
* Готов к дальнейшему расширению (Docker, CI, несколько зависимостей).
