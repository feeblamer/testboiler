import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

import yaml


STATE_FILE_NAME = ".testboiler-install-state.json"


def _normalize_scalar_none(value):
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None

    if normalized.lower() in {"none", "null", "~"}:
        return None

    return normalized


def _load_library_config(config, config_path):
    if "library" not in config:
        return None

    library = config["library"]
    if library is None:
        return None

    scalar_library = _normalize_scalar_none(library)
    if scalar_library is None:
        return None

    if not isinstance(library, dict):
        raise SystemExit(
            f"`library` in {config_path} must be null or a mapping with "
            "`distribution` and `import_name`."
        )

    allowed_keys = {"distribution", "import_name"}
    unknown_keys = set(library) - allowed_keys
    if unknown_keys:
        unknown = ", ".join(sorted(unknown_keys))
        raise SystemExit(f"Unknown keys in `library` section of {config_path}: {unknown}")

    distribution = str(library.get("distribution", "")).strip()
    import_name = str(library.get("import_name", "")).strip()

    if not distribution:
        raise SystemExit(f"`library.distribution` in {config_path} must be a non-empty string.")
    if not import_name:
        raise SystemExit(f"`library.import_name` in {config_path} must be a non-empty string.")

    return {
        "distribution": distribution,
        "import_name": import_name,
    }


def load_config(config_path="config.yml"):
    if not os.path.exists(config_path):
        raise SystemExit(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            loaded = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise SystemExit(f"Invalid YAML in configuration file: {config_path}") from exc
    except OSError as exc:
        raise SystemExit(f"Failed to read configuration file: {config_path}") from exc

    if loaded is None:
        raise SystemExit(f"Configuration file is empty: {config_path}")

    config = loaded

    if not isinstance(config, dict):
        raise SystemExit(f"Configuration file must contain a YAML mapping: {config_path}")

    allowed_keys = {"library", "framework"}
    unknown_keys = set(config) - allowed_keys
    if unknown_keys:
        unknown = ", ".join(sorted(unknown_keys))
        raise SystemExit(f"Unknown top-level keys in {config_path}: {unknown}")

    library = _load_library_config(config, config_path)
    framework = config.get("framework") or {}
    if not isinstance(framework, dict):
        raise SystemExit(f"`framework` in {config_path} must be a mapping.")

    pytest_enabled = bool(framework.get("pytest", False))
    unittest_enabled = bool(framework.get("unittest", False))
    if not pytest_enabled and not unittest_enabled:
        raise SystemExit(f"Enable at least one test runner in {config_path}.")

    return {
        "library": library,
        "pytest": pytest_enabled,
        "unittest": unittest_enabled,
    }


def resolve_template_root():
    repo_template = Path(__file__).resolve().parents[2] / "template"
    installed_template = Path(sysconfig.get_path("data")) / "share" / "testboiler" / "template"
    fallback_template = Path(sys.prefix) / "share" / "testboiler" / "template"

    for candidate in (repo_template, installed_template, fallback_template):
        if candidate.is_dir():
            return candidate

    raise SystemExit("Template directory was not found in this installation.")


def _hash_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        digest.update(file.read())
    return digest.hexdigest()


def _build_install_state(config, config_path="config.yml", requirements_path="requirements.txt"):
    state = {
        "version": 1,
        "config_hash": _hash_file(config_path),
        "requirements_hash": None,
        "library_distribution": None,
    }

    if os.path.exists(requirements_path):
        state["requirements_hash"] = _hash_file(requirements_path)

    if config["library"]:
        state["library_distribution"] = config["library"]["distribution"]

    return state


def copy_template(dst):
    if os.listdir(dst):
        raise SystemExit("`testboiler init` only works in an empty directory.")

    template_root = resolve_template_root()
    for item in template_root.iterdir():
        target = os.path.join(dst, item.name)
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def _venv_python(venv_dir=".venv"):
    venv_path = Path(venv_dir)
    if os.name == "nt":
        return str(venv_path / "Scripts" / "python.exe")
    return str(venv_path / "bin" / "python")


def _state_file_path(venv_dir=".venv"):
    return str(Path(venv_dir) / STATE_FILE_NAME)


def ensure_project_venv(venv_dir=".venv"):
    python_path = _venv_python(venv_dir)
    if not os.path.exists(python_path):
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
    return python_path


def require_project_venv(venv_dir=".venv"):
    python_path = _venv_python(venv_dir)
    if not os.path.exists(python_path):
        raise SystemExit("Project .venv was not found. Run `testboiler install` first.")
    return python_path


def load_install_state(venv_dir=".venv"):
    state_path = _state_file_path(venv_dir)
    if not os.path.exists(state_path):
        return None

    try:
        with open(state_path, "r", encoding="utf-8") as file:
            state = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "Project install state is invalid. Run `testboiler install`."
        ) from exc

    if not isinstance(state, dict):
        raise SystemExit("Project install state is invalid. Run `testboiler install`.")

    return state


def write_install_state(state, venv_dir=".venv"):
    state_path = _state_file_path(venv_dir)
    with open(state_path, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, sort_keys=True)
        file.write("\n")


def run_pytest(python_executable):
    subprocess.check_call([python_executable, "-m", "pytest", "tests/pytest"])


def run_unittest(python_executable):
    subprocess.check_call(
        [python_executable, "-m", "unittest", "discover", "-s", "tests/unittest"]
    )


def install_requirements(python_executable, requirements_path="requirements.txt"):
    if not os.path.exists(requirements_path):
        return

    with open(requirements_path, "r", encoding="utf-8") as file:
        requirements = [
            line.strip()
            for line in file
            if line.strip() and not line.lstrip().startswith("#")
        ]

    if not requirements:
        return

    try:
        subprocess.check_call(
            [python_executable, "-m", "pip", "install", "-r", requirements_path]
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "Failed to install dependencies into the project .venv from requirements.txt."
        ) from exc


def install_library(python_executable, library):
    if not library:
        return

    try:
        subprocess.check_call(
            [python_executable, "-m", "pip", "install", library["distribution"]]
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"Failed to install library `{library['distribution']}` into the project .venv."
        ) from exc


def ensure_test_dependencies(config, python_executable):
    install_requirements(python_executable)
    install_library(python_executable, config["library"])


def is_install_state_current(config, venv_dir=".venv", config_path="config.yml", requirements_path="requirements.txt"):
    stored_state = load_install_state(venv_dir)
    if stored_state is None:
        return False

    current_state = _build_install_state(config, config_path, requirements_path)
    return stored_state == current_state


def require_fresh_install_state(config, venv_dir=".venv", config_path="config.yml", requirements_path="requirements.txt"):
    state = load_install_state(venv_dir)
    if state is None:
        raise SystemExit("Project dependencies were not installed. Run `testboiler install`.")

    current_state = _build_install_state(config, config_path, requirements_path)

    if state.get("config_hash") != current_state["config_hash"]:
        raise SystemExit("config.yml changed after the last install. Run `testboiler install`.")

    if state.get("requirements_hash") != current_state["requirements_hash"]:
        raise SystemExit(
            "requirements.txt changed after the last install. Run `testboiler install`."
        )

    if state.get("library_distribution") != current_state["library_distribution"]:
        raise SystemExit("Library configuration changed after the last install. Run `testboiler install`.")


def ensure_runtime_requirements(config, python_executable):
    if config["pytest"]:
        try:
            subprocess.check_call(
                [python_executable, "-c", "import pytest"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                "pytest is not installed in project .venv. Run `testboiler install`."
            ) from exc

    if config["library"]:
        try:
            subprocess.check_call(
                [python_executable, "-c", f"import {config['library']['import_name']}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                f"Library `{config['library']['distribution']}` is not installed in project .venv. "
                "Run `testboiler install`."
            ) from exc


def main():
    parser = argparse.ArgumentParser(prog="testboiler")
    sub = parser.add_subparsers(dest="cmd")
    init_parser = sub.add_parser(
        "init",
        help="Copy the template files into the current directory or create a new project directory.",
    )
    init_parser.add_argument(
        "dir",
        nargs="?",
        help="Create this directory and initialize the template inside it.",
    )
    install_parser = sub.add_parser(
        "install",
        help="Install requirements.txt and config.yml library into the project .venv.",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstall dependencies even if config.yml and requirements.txt did not change.",
    )
    sub.add_parser("run", help="Run enabled test suites from config.yml.")
    sub.add_parser("venv", help="Create a local virtual environment in .venv.")
    args = parser.parse_args()

    if args.cmd == "init":
        if args.dir:
            target_dir = os.path.abspath(args.dir)
            if os.path.exists(target_dir):
                raise SystemExit(f"Directory already exists: {target_dir}")
            os.makedirs(target_dir)
            copy_template(target_dir)
        else:
            copy_template(os.getcwd())
    elif args.cmd == "install":
        config = load_config()
        venv_dir = ".venv"
        venv_python = ensure_project_venv(venv_dir)
        if not args.force and is_install_state_current(config, venv_dir):
            print("Dependencies are already installed in .venv")
        else:
            ensure_test_dependencies(config, venv_python)
            write_install_state(_build_install_state(config), venv_dir)
            print("Dependencies installed into .venv")
    elif args.cmd == "run":
        config = load_config()
        venv_python = require_project_venv()
        require_fresh_install_state(config)
        ensure_runtime_requirements(config, venv_python)
        if config["pytest"]:
            run_pytest(venv_python)
        if config["unittest"]:
            run_unittest(venv_python)
    elif args.cmd == "venv":
        ensure_project_venv()
        print("Virtual environment created in .venv\nActivate with:\n  source .venv/bin/activate")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
