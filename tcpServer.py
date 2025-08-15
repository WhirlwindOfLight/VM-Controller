#!/opt/vmController/venv/bin/python3

import socket
from threading import Thread
from RuntimeDir import initRuntimeDir
from Keyboard import Keyboard
from Mouse import Mouse


listenAddr = "0.0.0.0"
listenPort = 19509


def intBytes(bytes):
    return int.from_bytes(bytes, "little", signed=True)


def unsignedIntBytes(bytes):
    return int.from_bytes(bytes, "little")


def readBit(byte):
    return bool(byte & 1)


def emptyBuffer(conn):
    try:
        while True:
            bytes = conn.recv(1024, socket.MSG_DONTWAIT)
            if not bytes:
                return
    except BlockingIOError:
        return


def packetParser(conn):
    global myKeyboard
    global myMouse

    # Initial bytes need to be processed for an empty byte string
    # to detect a disconnected client
    initBytes = conn.recv(4)
    if initBytes == b'':
        return initBytes

    packetSize = unsignedIntBytes(initBytes)
    packetSize -= 1  # Ignore the SigByte
    if packetSize < 1:
        print("Err: Empty Packet Recieved!")
        emptyBuffer(conn)
        return

    msgType = conn.recv(1)
    if msgType == b'\x05':
        # Keyboard Handler
        msgSize = 2
        numMsgs = packetSize // msgSize
        for i in range(numMsgs):
            modKeyByte = intBytes(conn.recv(1))
            modKeyStates = []
            for i in range(4):
                modKeyStates.append(readBit(modKeyByte))
                modKeyByte >>= 1
            regKeyByte = unsignedIntBytes(conn.recv(1))
            myKeyboard.processEvents(modKeyStates, regKeyByte)
    elif msgType == b'\x06':
        # RelMouse Handler
        msgSize = 3
        numMsgs = packetSize // msgSize
        for i in range(numMsgs):
            buttonsByte = intBytes(conn.recv(1))
            buttonStates = []
            for i in range(3):
                buttonStates.append(readBit(buttonsByte))
                buttonsByte >>= 1
            relMousePos = (
                intBytes(conn.recv(1)),
                intBytes(conn.recv(1))
            )
            myMouse.relProcessEvents(buttonStates, relMousePos)
    elif msgType == b'\x07':
        # AbsMouse Handler
        msgSize = 5
        numMsgs = packetSize // msgSize
        for i in range(numMsgs):
            absMousePos = (
                intBytes(conn.recv(2)),
                intBytes(conn.recv(2))
            )
            wheelMovement = intBytes(conn.recv(1))
            myMouse.absProcessEvents(absMousePos, wheelMovement)
    else:
        print("Invalid SigByte: {}".format(msgType))
        emptyBuffer(conn)
        return


def connectionHandler(conn, connections):
    while True:
        if packetParser(conn) == b'':
            # Disconnect detected
            break
    print("{} disconnected!".format(connections[conn]))
    conn.close()
    connections.pop(conn)


initRuntimeDir()
with Keyboard() as myKeyboard, Mouse() as myMouse, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((listenAddr, listenPort))
    s.listen()
    print("vmController - TCP Server Started!")
    connections = {}
    threads = []
    try:
        while True:
            conn, client_addr = s.accept()
            print("{} connected!".format(client_addr))
            connections[conn] = client_addr
            myThread = Thread(
                target=connectionHandler,
                args=(conn, connections,)
            )
            myThread.start()
            threads.append(myThread)
    except KeyboardInterrupt:
        print(end='\r')
    finally:
        for conn in connections:
            conn.shutdown(socket.SHUT_RD)
        for myThread in threads:
            myThread.join()
        print("Goodbye!")
