import os
from os import path
from typing import Self

import uinput
from uinput import ev

from vm_controller import RUNTIME_DIR
from vm_controller.helper_functions import EventStruct, Event, get_dev_path


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
    def __init__(self, dev_name: str = "vmController - Mouse") -> None:
        self.dev_name = dev_name
        self.button_states = [False, False, False]
        self.abs_mode = False  # False -> RelMouse; True -> AbsMouse
        self.abs_pos = [1, 1]
        self.virt_abs_mouse = uinput.Device(
            events=(MOUSE_BUTTONS + MOUSE_WHEEL_EVENTS
                    + list(map(lambda x: x + ABS_RANGE, MOUSE_ABS_EVENTS))),
            name=(dev_name + ABSMOUSE_SUFFIX)
        )
        self.virt_rel_mouse = uinput.Device(
            events=(MOUSE_BUTTONS + MOUSE_WHEEL_EVENTS + MOUSE_REL_EVENTS),
            name=(dev_name + RELMOUSE_SUFFIX)
        )
        for link in [ABSMOUSE_LINK, RELMOUSE_LINK]:
            if path.islink(link):
                os.unlink(link)
        os.symlink(get_dev_path(dev_name + ABSMOUSE_SUFFIX), ABSMOUSE_LINK)
        os.symlink(get_dev_path(dev_name + RELMOUSE_SUFFIX), RELMOUSE_LINK)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> bool:
        os.unlink(ABSMOUSE_LINK)
        os.unlink(RELMOUSE_LINK)
        self.virt_abs_mouse.destroy()
        self.virt_rel_mouse.destroy()
        return False

    def abs_to_events(self, abs_mouse_pos: IntPair, wheel_movement: int) -> list[EventStruct]:  # noqa: E501
        events: list[EventStruct] = []

        for i in range(2):
            if abs_mouse_pos[i] != 0 and abs_mouse_pos[i] != self.abs_pos[i]:
                self.abs_mode = True
                self.abs_pos[i] = abs_mouse_pos[i]
                events.append(
                    EventStruct(MOUSE_ABS_EVENTS[i], abs_mouse_pos[i])
                )
        if wheel_movement != 0:
            events.append(EventStruct(MOUSE_WHEEL_EVENTS[0], wheel_movement))
            events.append(
                EventStruct(
                    MOUSE_WHEEL_EVENTS[1],
                    wheel_movement * HI_RES_MULT
                )
            )

        return events

    def rel_to_events(self, button_states: list[bool], rel_mouse_pos: IntPair) -> list[EventStruct]:  # noqa: E501
        events: list[EventStruct] = []

        if button_states != self.button_states:
            state_num = 0
            for button in MOUSE_BUTTONS:
                if button_states[state_num] ^ self.button_states[state_num]:
                    events.append(
                        EventStruct(button, button_states[state_num])
                    )
                state_num += 1
            self.button_states = button_states
        for i in range(2):
            if rel_mouse_pos[i] != 0:
                self.abs_mode = False
                events.append(
                    EventStruct(MOUSE_REL_EVENTS[i], rel_mouse_pos[i])
                )

        return events

    def print_events(self, events: list[EventStruct]) -> None:
        if self.abs_mode:
            mouse_name = self.dev_name + ABSMOUSE_SUFFIX
        else:
            mouse_name = self.dev_name + RELMOUSE_SUFFIX
        for ev_obj in events:
            print("[{}] - ({}, {})".format(
                mouse_name, ev_obj.event, ev_obj.value)
            )

    def process_events(self, events: list[EventStruct]) -> None:
        if self.abs_mode:
            my_virt_mouse = self.virt_abs_mouse
        else:
            my_virt_mouse = self.virt_rel_mouse
        for ev_obj in events:
            my_virt_mouse.emit(ev_obj.event, ev_obj.value, syn=False)
        my_virt_mouse.syn()

    def abs_print_events(self, abs_mouse_pos: IntPair, wheel_movement: int) -> None:  # noqa: E501
        self.print_events(self.abs_to_events(abs_mouse_pos, wheel_movement))

    def rel_print_events(self, button_states: list[bool], rel_mouse_pos: IntPair) -> None:  # noqa: E501
        self.print_events(self.rel_to_events(button_states, rel_mouse_pos))

    def abs_process_events(self, abs_mouse_pos: IntPair, wheelMovement: int) -> None:  # noqa: E501
        self.process_events(self.abs_to_events(abs_mouse_pos, wheelMovement))

    def rel_process_events(self, button_states: list[bool], rel_mouse_pos: IntPair) -> None:  # noqa: E501
        self.process_events(self.rel_to_events(button_states, rel_mouse_pos))
