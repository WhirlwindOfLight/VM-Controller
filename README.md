# VM-Controller
This program is designed to create virtual input devices to control physical or virtual machines that take TCP input and convert it into keyboard and mouse signals. It was originally designed to respond to packets sent from [HardwareVNC](https://github.com/WhirlwindOfLight/HardwareVNC), but it can also be used in combination with [VM-HardwareForwarder](https://github.com/WhirlwindOfLight/VM-HardwareForwarder) to forward physical keyboard and mouse signals from one machine to another. This program is only designed for use on Linux, so instructions will assume you are on Linux.

## Usage
This program is not designed to be compiled or installed, but some stuff does need to be done on the first run that doesn't need to be done on every run.
### Initial Run
1. Download the dependencies with your system package manager:
    * make
    * python ~3.12
2. Navigate to where you want to store the program
3. Clone the repository with `git clone https://github.com/WhirlwindOfLight/VM-Controller`
4. Enter the directory with `cd VM-Controller`
5. Build the [virtual environment](https://peps.python.org/pep-0405/) with `make`
    * NOTE: If your Python version ever updates, you may need to rebuild your virtual environment! To do this, navigate back to this repository directory and run `make clean; make`
### Normal Use
Run the program either directly or using a systemd service by running `vm-controller`. If this program is installed on the VM Host, then while the program is running there are hooks stored in `~/.local/state/vmController` to connect the virtual input devices to the VMs. This program does need permission to create virtual uinput devices, so it needs to be run either as root, with the `input` group, or with a custom udev rule.
### Security Note
This program was designed with the assumption that the machine has a firewall protecting port TCP/19509 for all networks, and as such, **THIS PROGRAM DOES NOT ENCRYPT THE TCP TRAFFIC, NOR DOES IT BIND TO LOCALHOST-ONLY BY DEFAULT!!!** This program should only be used in an environment where the port is properly protected by a system firewall and/or an encrypted tunnel (such as a VPN), or there is a risk an attacker could take control of your machine and/or spy on your input!

## Licensing
All current and prior code in this repository is licensed under the terms of the GNU General Public License v3.0 (GPL-3.0-only) as of February 18, 2026, and all future changes will be released under the same terms unless otherwise stated (see [LICENSE](LICENSE) for more details). In addition, when run, the code depends on and imports the following libraries with their associated licenses:
* [pyudev](https://github.com/pyudev/pyudev/tree/master) (LGPL-2.1)
* [python-uinput](https://github.com/pyinput/python-uinput) (GPL-3.0-or-later)