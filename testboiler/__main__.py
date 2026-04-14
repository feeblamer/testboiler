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

