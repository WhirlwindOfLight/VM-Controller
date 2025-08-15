from uinput.ev import *

val = 0x04
myMap = {}

#a-z is 0x04-0x1D
for key in [
    KEY_A, KEY_B, KEY_C, KEY_D, KEY_E,
    KEY_F, KEY_G, KEY_H, KEY_I, KEY_J,
    KEY_K, KEY_L, KEY_M, KEY_N, KEY_O,
    KEY_P, KEY_Q, KEY_R, KEY_S, KEY_T,
    KEY_U, KEY_V, KEY_W, KEY_X, KEY_Y,
    KEY_Z
]:
    myMap[val] = key
    val += 1
#val should now be 0x1E

#1-9 + 0 is 0x1E-0x27
#The key codes are also in order, so a regular for loop can be used
for keyNum in range(KEY_1[1], KEY_0[1] + 1):
    key = (0x01, keyNum)
    myMap[val] = key
    val += 1
#val should now be 0x28

#Special keys in 0x28-0x2C
for key in [
    KEY_ENTER, KEY_ESC, KEY_BACKSPACE,
    KEY_TAB, KEY_SPACE
]:
    myMap[val] = key
    val += 1
#val should now be 0x2D

#Symbols in 0x2D-0x31 and 0x33-0x38
for key in [
    KEY_MINUS, KEY_EQUAL, KEY_LEFTBRACE,
    KEY_RIGHTBRACE, KEY_BACKSLASH
]:
    myMap[val] = key
    val += 1
val += 1 #Skip 0x32
for key in [
    KEY_SEMICOLON, KEY_APOSTROPHE, KEY_GRAVE,
    KEY_COMMA, KEY_DOT, KEY_SLASH
]:
    myMap[val] = key
    val += 1
#val should now be 0x39
myMap[val] = KEY_CAPSLOCK
val += 1

#Function keys in 0x3A-0x45
for key in [
    KEY_F1, KEY_F2, KEY_F3, KEY_F4,
    KEY_F5, KEY_F6, KEY_F7, KEY_F8,
    KEY_F9, KEY_F10, KEY_F11, KEY_F12
]:
    myMap[val] = key
    val += 1
#val should now be 0x46

#Special keys in 0x46-0x53
#KEY_SYSRQ is for [Print Screen] key
for key in [
    KEY_SYSRQ, KEY_SCROLLLOCK,
    KEY_PAUSE, KEY_INSERT, KEY_HOME,
    KEY_PAGEUP, KEY_DELETE, KEY_END,
    KEY_PAGEDOWN, KEY_RIGHT, KEY_LEFT,
    KEY_DOWN, KEY_UP, KEY_NUMLOCK
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
