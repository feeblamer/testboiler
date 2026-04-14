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

