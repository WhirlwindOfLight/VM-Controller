import os
from os import path
from typing import Self

import uinput
from uinput import ev

from vm_controller.runtime_dir import RUNTIME_DIR
from vm_controller.keymap import KEYMAP
from vm_controller.helper_functions import EventStruct, Event, get_dev_path


KEYBOARD_LINK = path.join(RUNTIME_DIR, "devices", "Keyboard")
KEYBOARD_MODKEYS: list[Event] = [
    ev.KEY_LEFTCTRL, ev.KEY_LEFTSHIFT, ev.KEY_LEFTALT, ev.KEY_LEFTMETA
]


class Keyboard:
    def __init__(self, dev_name: str = "vmController - Keyboard") -> None:
        self.dev_name = dev_name
        self.mod_key_states = [False, False, False, False]
        self.reg_key = None
        self.virt_keyboard = uinput.Device(
            events=(KEYMAP.events + KEYBOARD_MODKEYS),
            name=dev_name
        )
        if path.islink(KEYBOARD_LINK):
            os.unlink(KEYBOARD_LINK)
        os.symlink(get_dev_path(dev_name), KEYBOARD_LINK)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> bool:
        os.unlink(KEYBOARD_LINK)
        self.virt_keyboard.destroy()
        return False

    def to_events(self, mod_key_states: list[bool], reg_key_byte: int) -> list[EventStruct]:  # noqa: E501
        events: list[EventStruct] = []

        if mod_key_states != self.mod_key_states:
            state_num = 0
            for key in KEYBOARD_MODKEYS:
                if mod_key_states[state_num] ^ self.mod_key_states[state_num]:
                    events.append(EventStruct(key, mod_key_states[state_num]))
                state_num += 1
        self.mod_key_states = mod_key_states

        reg_key = KEYMAP(reg_key_byte)
        if reg_key != self.reg_key:
            if self.reg_key is not None:
                events.append(EventStruct(self.reg_key, False))
            if reg_key is not None:
                events.append(EventStruct(reg_key, True))
        self.reg_key = reg_key

        return events

    def print_events(self, mod_key_states: list[bool], reg_key_byte: int) -> None:  # noqa: E501
        for ev_obj in self.to_events(mod_key_states, reg_key_byte):
            print("[{}] - ({}, {})".format(
                self.dev_name, ev_obj.event[1], ev_obj.value)
            )

    def process_events(self, mod_key_states: list[bool], reg_key_byte: int) -> None:  # noqa: E501
        for ev_obj in self.to_events(mod_key_states, reg_key_byte):
            self.virt_keyboard.emit(ev_obj.event, ev_obj.value, syn=False)
        self.virt_keyboard.syn()
