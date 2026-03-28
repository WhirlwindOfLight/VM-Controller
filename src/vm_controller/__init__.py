from os import path, makedirs
from ipaddress import IPv4Address
from argparse import ArgumentParser

from platformdirs import user_runtime_dir


RUNTIME_DIR = user_runtime_dir(
    appname="vm-controller",
    ensure_exists=True
)


def main():
    # Function level import needed to prevent circular import
    from vm_controller import server

    arg_parser = ArgumentParser()
    arg_parser.add_argument("-a", "--address", default="0.0.0.0", type=IPv4Address)
    arg_parser.add_argument("-p", "--port", default=19509, type=int)
    args = arg_parser.parse_args()

    # Initialize "devices" directory
    devices_dir = path.join(RUNTIME_DIR, "devices")
    makedirs(devices_dir, exist_ok=True)
    print(f'Virtual Device links wil be stored here: {devices_dir}')

    print(f"Starting server listening at {args.address}:{args.port}")
    server.run(str(args.address), args.port)
