from RuntimeDir import RUNTIME_DIR
from Keymap import Keymap, KeymapEvents
from HelperFunctions import *
from uinput.ev import *
import uinput
from os import path
import os

KEYBOARD_LINK = path.join(RUNTIME_DIR,"devices","Keyboard")
KEYBOARD_MODKEYS = [KEY_LEFTCTRL, KEY_LEFTSHIFT, KEY_LEFTALT, KEY_LEFTMETA]

class Keyboard:
    def __init__(self, devName="vmController - Keyboard"):
        self.devName = devName
        self.modKeyStates = [False, False, False, False]
        self.regKey = None
        self.virtKeyboard = uinput.Device(KeymapEvents() + KEYBOARD_MODKEYS, devName)
        os.symlink(getDevPath(devName), KEYBOARD_LINK)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        os.unlink(KEYBOARD_LINK)
        self.virtKeyboard.destroy()
        return False

    def toEvents(self, modKeyStates, regKeyByte):
        events = []

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

    def printEvents(self, modKeyStates, regKeyByte):
        for ev in self.toEvents(modKeyStates, regKeyByte):
            print("[{}] - ({}, {})".format(self.devName, ev["event"][1], ev["value"]))

    def processEvents(self, modKeyStates, regKeyByte):
        for ev in self.toEvents(modKeyStates, regKeyByte):
            self.virtKeyboard.emit(ev["event"], ev["value"], syn=False)
        self.virtKeyboard.syn()
