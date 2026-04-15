import argparse
import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

import yaml


def _normalize_library_value(value):
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None

    if normalized.lower() in {"none", "null", "~"}:
        return None

    if "<" in normalized or ">" in normalized:
        return None

    return normalized


def load_config(config_path="quickboiler.cfg"):
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

    library = _normalize_library_value(config.get("library"))
    framework = config.get("framework") or {}
    if not isinstance(framework, dict):
        raise SystemExit(f"`framework` in {config_path} must be a mapping.")

    pytest_enabled = bool(framework.get("pytest", False))
    unittest_enabled = bool(framework.get("unittest", False))
    if not pytest_enabled and not unittest_enabled:
        raise SystemExit("Enable at least one test runner in quickboiler.cfg.")

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


def run_pytest(python_executable):
    subprocess.check_call([python_executable, "-m", "pytest", "tests/pytest"])


def run_unittest(python_executable):
    subprocess.check_call(
        [python_executable, "-m", "unittest", "discover", "-s", "tests/unittest"]
    )


def _extract_import_name(requirement):
    package_name = requirement
    for separator in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        package_name = package_name.split(separator, 1)[0]
    package_name = package_name.split("[", 1)[0].strip()
    return package_name.replace("-", "_")


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
        subprocess.check_call([python_executable, "-m", "pip", "install", library])
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"Failed to install library `{library}` into the project .venv."
        ) from exc


def ensure_test_dependencies(config, python_executable):
    install_requirements(python_executable)
    install_library(python_executable, config["library"])


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
        import_name = _extract_import_name(config["library"])
        try:
            subprocess.check_call(
                [python_executable, "-c", f"import {import_name}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                f"Library `{config['library']}` is not installed in project .venv. "
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
    sub.add_parser(
        "install",
        help="Install requirements.txt and quickboiler.cfg library into the project .venv.",
    )
    sub.add_parser("run", help="Run enabled test suites from quickboiler.cfg.")
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
        venv_python = ensure_project_venv()
        ensure_test_dependencies(config, venv_python)
        print("Dependencies installed into .venv")
    elif args.cmd == "run":
        config = load_config()
        venv_python = require_project_venv()
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
