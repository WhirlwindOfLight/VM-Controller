from os import path, makedirs

RUNTIME_DIR = path.join("/run","vmController")

def initRuntimeDir():
    makedirs(path.join(RUNTIME_DIR, "devices"), exist_ok=True)
