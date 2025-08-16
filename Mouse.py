import os
from os import path
from typing import Self

import uinput
from uinput import ev

from RuntimeDir import RUNTIME_DIR
from HelperFunctions import EventStruct, Event, getDevPath


type IntPair = tuple[int, int]

ABSMOUSE_LINK = path.join(RUNTIME_DIR, "devices", "AbsMouse")
RELMOUSE_LINK = path.join(RUNTIME_DIR, "devices", "RelMouse")
ABSMOUSE_SUFFIX = " (Absolute)"
RELMOUSE_SUFFIX = " (Relative)"
MOUSE_BUTTONS: list[Event] = [ev.BTN_LEFT, ev.BTN_RIGHT, ev.BTN_MIDDLE]
MOUSE_REL_EVENTS: list[Event] = [ev.REL_X, ev.REL_Y]
MOUSE_ABS_EVENTS: list[Event] = [ev.ABS_X, ev.ABS_Y]
MOUSE_WHEEL_EVENTS: list[Event] = [ev.REL_WHEEL, ev.REL_WHEEL_HI_RES]
HI_RES_MULT = 120
ABS_RANGE = (1, 32767, 0, 0)


class Mouse:
    def __init__(self, devName: str = "vmController - Mouse") -> None:
        self.devName = devName
        self.buttonStates = [False, False, False]
        self.absMode = False  # False -> RelMouse; True -> AbsMouse
        self.absPos = [1, 1]
        self.virtAbsMouse = uinput.Device(
            events=(MOUSE_BUTTONS + MOUSE_WHEEL_EVENTS
                    + list(map(lambda x: x + ABS_RANGE, MOUSE_ABS_EVENTS))),
            name=(devName + ABSMOUSE_SUFFIX)
        )
        self.virtRelMouse = uinput.Device(
            events=(MOUSE_BUTTONS + MOUSE_WHEEL_EVENTS + MOUSE_REL_EVENTS),
            name=(devName + RELMOUSE_SUFFIX)
        )
        os.symlink(getDevPath(devName + ABSMOUSE_SUFFIX), ABSMOUSE_LINK)
        os.symlink(getDevPath(devName + RELMOUSE_SUFFIX), RELMOUSE_LINK)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> bool:
        os.unlink(ABSMOUSE_LINK)
        os.unlink(RELMOUSE_LINK)
        self.virtAbsMouse.destroy()
        self.virtRelMouse.destroy()
        return False

    def absToEvents(self, absMousePos: IntPair, wheelMovement: int) -> list[EventStruct]:  # noqa: E501
        events: list[EventStruct] = []

        for i in range(2):
            if absMousePos[i] != 0 and absMousePos[i] != self.absPos[i]:
                self.absMode = True
                self.absPos[i] = absMousePos[i]
                events.append(EventStruct(MOUSE_ABS_EVENTS[i], absMousePos[i]))
        if wheelMovement != 0:
            events.append(EventStruct(MOUSE_WHEEL_EVENTS[0], wheelMovement))
            events.append(
                EventStruct(MOUSE_WHEEL_EVENTS[1], wheelMovement * HI_RES_MULT)
            )

        return events

    def relToEvents(self, buttonStates: list[bool], relMousePos: IntPair) -> list[EventStruct]:  # noqa: E501
        events: list[EventStruct] = []

        if buttonStates != self.buttonStates:
            stateNum = 0
            for button in MOUSE_BUTTONS:
                if buttonStates[stateNum] ^ self.buttonStates[stateNum]:
                    events.append(EventStruct(button, buttonStates[stateNum]))
                stateNum += 1
            self.buttonStates = buttonStates
        for i in range(2):
            if relMousePos[i] != 0:
                self.absMode = False
                events.append(EventStruct(MOUSE_REL_EVENTS[i], relMousePos[i]))

        return events

    def printEvents(self, events: list[EventStruct]) -> None:
        if self.absMode:
            mouseName = self.devName + ABSMOUSE_SUFFIX
        else:
            mouseName = self.devName + RELMOUSE_SUFFIX
        for ev_obj in events:
            print("[{}] - ({}, {})".format(
                mouseName, ev_obj.event, ev_obj.value)
            )

    def processEvents(self, events: list[EventStruct]) -> None:
        if self.absMode:
            myVirtMouse = self.virtAbsMouse
        else:
            myVirtMouse = self.virtRelMouse
        for ev_obj in events:
            myVirtMouse.emit(ev_obj.event, ev_obj.value, syn=False)
        myVirtMouse.syn()

    def absPrintEvents(self, absMousePos: IntPair, wheelMovement: int) -> None:
        self.printEvents(self.absToEvents(absMousePos, wheelMovement))

    def relPrintEvents(self, buttonStates: list[bool], relMousePos: IntPair) -> None:  # noqa: E501
        self.printEvents(self.relToEvents(buttonStates, relMousePos))

    def absProcessEvents(self, absMousePos: IntPair, wheelMovement: int) -> None:  # noqa: E501
        self.processEvents(self.absToEvents(absMousePos, wheelMovement))

    def relProcessEvents(self, buttonStates: list[bool], relMousePos: IntPair) -> None:  # noqa: E501
        self.processEvents(self.relToEvents(buttonStates, relMousePos))
