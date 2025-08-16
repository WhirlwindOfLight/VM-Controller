import os
from os import path
from typing import Self

import uinput
from uinput import ev

from RuntimeDir import RUNTIME_DIR
from Keymap import Keymap, KeymapEvents
from HelperFunctions import EventStruct, Event, getDevPath


KEYBOARD_LINK = path.join(RUNTIME_DIR, "devices", "Keyboard")
KEYBOARD_MODKEYS: list[Event] = [
    ev.KEY_LEFTCTRL, ev.KEY_LEFTSHIFT, ev.KEY_LEFTALT, ev.KEY_LEFTMETA
]


class Keyboard:
    def __init__(self, devName: str = "vmController - Keyboard") -> None:
        self.devName = devName
        self.modKeyStates = [False, False, False, False]
        self.regKey = None
        self.virtKeyboard = uinput.Device(
            events=(KeymapEvents() + KEYBOARD_MODKEYS),
            name=devName
        )
        os.symlink(getDevPath(devName), KEYBOARD_LINK)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> bool:
        os.unlink(KEYBOARD_LINK)
        self.virtKeyboard.destroy()
        return False

    def toEvents(self, modKeyStates: list[bool], regKeyByte: int) -> list[EventStruct]:  # noqa: E501
        events: list[EventStruct] = []

        if modKeyStates != self.modKeyStates:
            stateNum = 0
            for key in KEYBOARD_MODKEYS:
                if modKeyStates[stateNum] ^ self.modKeyStates[stateNum]:
                    events.append(EventStruct(key, modKeyStates[stateNum]))
                stateNum += 1
        self.modKeyStates = modKeyStates

        regKey = Keymap(regKeyByte)
        if regKey != self.regKey:
            if self.regKey is not None:
                events.append(EventStruct(self.regKey, False))
            if regKey is not None:
                events.append(EventStruct(regKey, True))
        self.regKey = regKey

        return events

    def printEvents(self, modKeyStates: list[bool], regKeyByte: int) -> None:
        for ev_obj in self.toEvents(modKeyStates, regKeyByte):
            print("[{}] - ({}, {})".format(
                self.devName, ev_obj.event[1], ev_obj.value)
            )

    def processEvents(self, modKeyStates: list[bool], regKeyByte: int) -> None:
        for ev_obj in self.toEvents(modKeyStates, regKeyByte):
            self.virtKeyboard.emit(ev_obj.event, ev_obj.value, syn=False)
        self.virtKeyboard.syn()
