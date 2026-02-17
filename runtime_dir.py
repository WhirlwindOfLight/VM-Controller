from os import path, makedirs
from os.path import expanduser


RUNTIME_DIR = path.join(expanduser("~/.local/state"), "vmController")


def init_runtime_dir() -> None:
    makedirs(path.join(RUNTIME_DIR, "devices"), exist_ok=True)
