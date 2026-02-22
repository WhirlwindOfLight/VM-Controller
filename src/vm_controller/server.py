import socket
from threading import Thread
from typing import Optional, Literal

from vm_controller.runtime_dir import init_runtime_dir
from vm_controller.keyboard import Keyboard
from vm_controller.mouse import Mouse


type Connection = socket.socket
type ConnMap = dict[Connection, str]

LISTEN_ADDR = "0.0.0.0"
LISTEN_PORT = 19509

MSG_SIZE = {
    b'\x05': 2,  # Keyboard
    b'\x06': 3,  # RelMouse
    b'\x07': 5   # AbsMouse
}


def int_bytes(bytes: bytes, unsigned: bool = False) -> int:
    return int.from_bytes(bytes, "little", signed=(not unsigned))


def read_bit(byte: int) -> bool:
    return bool(byte & 1)


def empty_buffer(conn: Connection) -> None:
    try:
        while True:
            bytes = conn.recv(1024, socket.MSG_DONTWAIT)
            if not bytes:
                return
    except BlockingIOError:
        return


def packet_parser(conn: Connection) -> Optional[Literal[b""]]:
    # Initial bytes need to be processed for an empty byte string
    # to detect a disconnected client
    init_bytes = conn.recv(4)
    if init_bytes == b'':
        return init_bytes

    packet_size = int_bytes(init_bytes, unsigned=True)
    packet_size -= 1  # Ignore the SigByte
    if packet_size < 1:
        print("Err: Empty Packet Recieved!")
        empty_buffer(conn)
        return

    msg_type = conn.recv(1)
    match msg_type:
        case b'\x05':
            # Keyboard Handler
            num_msgs = packet_size // MSG_SIZE[msg_type]
            for _ in range(num_msgs):
                mod_key_byte = int_bytes(conn.recv(1))
                mod_key_states: list[bool] = []
                for _ in range(4):
                    mod_key_states.append(read_bit(mod_key_byte))
                    mod_key_byte >>= 1
                reg_key_byte = int_bytes(conn.recv(1), unsigned=True)
                KEYBOARD.process_events(mod_key_states, reg_key_byte)
        case b'\x06':
            # RelMouse Handler
            num_msgs = packet_size // MSG_SIZE[msg_type]
            for _ in range(num_msgs):
                buttons_byte = int_bytes(conn.recv(1))
                button_states: list[bool] = []
                for _ in range(3):
                    button_states.append(read_bit(buttons_byte))
                    buttons_byte >>= 1
                rel_mouse_pos = (
                    int_bytes(conn.recv(1)),
                    int_bytes(conn.recv(1))
                )
                MOUSE.rel_process_events(button_states, rel_mouse_pos)
        case b'\x07':
            # AbsMouse Handler
            num_msgs = packet_size // MSG_SIZE[msg_type]
            for _ in range(num_msgs):
                abs_mouse_pos = (
                    int_bytes(conn.recv(2)),
                    int_bytes(conn.recv(2))
                )
                wheel_movement = int_bytes(conn.recv(1))
                MOUSE.abs_process_events(abs_mouse_pos, wheel_movement)
        case _:
            print("Invalid SigByte: {}".format(msg_type))
            empty_buffer(conn)
            return


def connection_handler(conn: Connection, connections: ConnMap) -> None:
    while True:
        if packet_parser(conn) == b'':
            # Disconnect detected
            break
    print("{} disconnected!".format(connections[conn]))
    conn.close()
    connections.pop(conn)

def run():
    global KEYBOARD
    global MOUSE
    init_runtime_dir()
    with Keyboard() as KEYBOARD, \
        Mouse() as MOUSE, \
        socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        s.bind((LISTEN_ADDR, LISTEN_PORT))
        s.listen()
        print("vmController - TCP Server Started!")
        connections: ConnMap = {}
        threads: list[Thread] = []
        try:
            while True:
                conn, client_addr = s.accept()
                print("{} connected!".format(client_addr))
                connections[conn] = client_addr
                my_thread = Thread(
                    target=connection_handler,
                    args=(conn, connections,)
                )
                my_thread.start()
                threads.append(my_thread)
        except KeyboardInterrupt:
            print(end='\r')
        finally:
            for conn in connections:
                conn.shutdown(socket.SHUT_RD)
            for my_thread in threads:
                my_thread.join()
            print("Goodbye!")
