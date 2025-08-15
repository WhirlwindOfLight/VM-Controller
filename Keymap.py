from uinput import ev

val = 0x04
myMap = {}

# a-z is 0x04-0x1D
for key in [
    ev.KEY_A, ev.KEY_B, ev.KEY_C, ev.KEY_D, ev.KEY_E,
    ev.KEY_F, ev.KEY_G, ev.KEY_H, ev.KEY_I, ev.KEY_J,
    ev.KEY_K, ev.KEY_L, ev.KEY_M, ev.KEY_N, ev.KEY_O,
    ev.KEY_P, ev.KEY_Q, ev.KEY_R, ev.KEY_S, ev.KEY_T,
    ev.KEY_U, ev.KEY_V, ev.KEY_W, ev.KEY_X, ev.KEY_Y,
    ev.KEY_Z
]:
    myMap[val] = key
    val += 1
# val should now be 0x1E

# 1-9 + 0 is 0x1E-0x27
# The key codes are also in order, so a regular for loop can be used
for keyNum in range(ev.KEY_1[1], ev.KEY_0[1] + 1):
    key = (0x01, keyNum)
    myMap[val] = key
    val += 1
# val should now be 0x28

# Special keys in 0x28-0x2C
for key in [
    ev.KEY_ENTER, ev.KEY_ESC, ev.KEY_BACKSPACE,
    ev.KEY_TAB, ev.KEY_SPACE
]:
    myMap[val] = key
    val += 1
# val should now be 0x2D

# Symbols in 0x2D-0x31 and 0x33-0x38
for key in [
    ev.KEY_MINUS, ev.KEY_EQUAL, ev.KEY_LEFTBRACE,
    ev.KEY_RIGHTBRACE, ev.KEY_BACKSLASH
]:
    myMap[val] = key
    val += 1
val += 1  # Skip 0x32
for key in [
    ev.KEY_SEMICOLON, ev.KEY_APOSTROPHE, ev.KEY_GRAVE,
    ev.KEY_COMMA, ev.KEY_DOT, ev.KEY_SLASH
]:
    myMap[val] = key
    val += 1
# val should now be 0x39
myMap[val] = ev.KEY_CAPSLOCK
val += 1

# Function keys in 0x3A-0x45
for key in [
    ev.KEY_F1, ev.KEY_F2, ev.KEY_F3, ev.KEY_F4,
    ev.KEY_F5, ev.KEY_F6, ev.KEY_F7, ev.KEY_F8,
    ev.KEY_F9, ev.KEY_F10, ev.KEY_F11, ev.KEY_F12
]:
    myMap[val] = key
    val += 1
# val should now be 0x46

# Special keys in 0x46-0x53
# ev.KEY_SYSRQ is for [Print Screen] key
for key in [
    ev.KEY_SYSRQ, ev.KEY_SCROLLLOCK,
    ev.KEY_PAUSE, ev.KEY_INSERT, ev.KEY_HOME,
    ev.KEY_PAGEUP, ev.KEY_DELETE, ev.KEY_END,
    ev.KEY_PAGEDOWN, ev.KEY_RIGHT, ev.KEY_LEFT,
    ev.KEY_DOWN, ev.KEY_UP, ev.KEY_NUMLOCK
]:
    myMap[val] = key
    val += 1


def Keymap(byte):
    if byte in myMap:
        return myMap[byte]
    else:
        return None


def KeymapEvents():
    return list(myMap.values())
