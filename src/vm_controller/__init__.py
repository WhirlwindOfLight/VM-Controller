from os import path, makedirs

from platformdirs import user_runtime_dir


RUNTIME_DIR = user_runtime_dir(
    appname="vm-controller",
    ensure_exists=True
)


def main():
    # Function level import needed to prevent circular import
    from vm_controller import server

    # Initialize "devices" directory
    devices_dir = path.join(RUNTIME_DIR, "devices")
    makedirs(devices_dir, exist_ok=True)
    print(f'Virtual Device links wil be stored here: {devices_dir}')

    server.run()
