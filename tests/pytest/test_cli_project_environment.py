from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from testboiler import __main__


def write_project_files(tmp_path):
    (tmp_path / "config.yml").write_text(
        "library: null\nframework:\n  pytest: true\n  unittest: false\n",
        encoding="utf-8",
    )
    (tmp_path / "requirements.txt").write_text("", encoding="utf-8")


def run_main(monkeypatch, *arguments):
    monkeypatch.setattr(__main__.sys, "argv", ["testboiler", *arguments])
    __main__.main()


def test_resolve_project_environment_uses_only_local_dot_venv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VIRTUAL_ENV", "/tmp/external-venv")

    assert __main__.resolve_project_environment() is None

    python_path = Path(__main__._venv_python())
    python_path.parent.mkdir(parents=True)
    python_path.write_text("", encoding="utf-8")

    environment = __main__.resolve_project_environment()

    assert environment == {
        "kind": "local_dot_venv",
        "root": ".venv",
        "python": __main__._venv_python(),
        "label": ".venv",
    }


def test_require_project_environment_requires_local_dot_venv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VIRTUAL_ENV", "/tmp/external-venv")

    with pytest.raises(SystemExit) as exc_info:
        __main__.require_project_environment()

    assert str(exc_info.value) == (
        "Project environment `.venv` was not found. "
        "Run `testboiler install` or `testboiler venv` first."
    )


def test_install_creates_local_dot_venv_even_with_active_virtualenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VIRTUAL_ENV", "/tmp/external-venv")
    write_project_files(tmp_path)

    calls = []

    def fake_check_call(command, **kwargs):
        del kwargs
        calls.append(command)
        if command[:3] == [__main__.sys.executable, "-m", "venv"]:
            python_path = Path(__main__._venv_python())
            python_path.parent.mkdir(parents=True)
            python_path.write_text("", encoding="utf-8")
        return 0

    monkeypatch.setattr(__main__.subprocess, "check_call", fake_check_call)
    monkeypatch.setattr(__main__, "write_install_state", lambda state, environment: None)

    run_main(monkeypatch, "install")

    assert calls[0] == [__main__.sys.executable, "-m", "venv", ".venv"]


def test_venv_creates_local_dot_venv_even_with_active_virtualenv(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VIRTUAL_ENV", "/tmp/external-venv")

    calls = []

    def fake_check_call(command, **kwargs):
        del kwargs
        calls.append(command)
        python_path = Path(__main__._venv_python())
        python_path.parent.mkdir(parents=True)
        python_path.write_text("", encoding="utf-8")
        return 0

    monkeypatch.setattr(__main__.subprocess, "check_call", fake_check_call)

    run_main(monkeypatch, "venv")

    output = capsys.readouterr().out

    assert calls == [[__main__.sys.executable, "-m", "venv", ".venv"]]
    assert "Virtual environment created in .venv" in output


def test_run_fails_without_local_dot_venv_even_with_active_virtualenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VIRTUAL_ENV", "/tmp/external-venv")
    write_project_files(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        run_main(monkeypatch, "run")

    assert str(exc_info.value) == (
        "Project environment `.venv` was not found. "
        "Run `testboiler install` or `testboiler venv` first."
    )
