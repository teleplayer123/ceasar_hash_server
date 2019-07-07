import os
import hashlib
import base64
import struct
import pickle
import socket 
import console
import sys

Address = ["localhost", 6000]

class SocketManager:

    def __init__(self, address):
        self.address = address

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.address)
        return self.sock

    def __exit__(self, *ignore):
        self.sock.close()
    

def main():
    if len(sys.argv) > 1:
        Address[1] = sys.argv[1]
    call = dict(r=register_id, l=login_mimic,g=get_hash, s=stop_server)
    menu = "(R)egister  (L)ogin mimic (G)et hash (S)top server"
    valid = frozenset("rRlLgGsS")
    while True:
        action = console.get_menu_choice(menu, valid, "r")
        call[action]()

def get_hash():
    identity = console.get_string("enter id", "id")
    ok, *data = handle_request("GET_HASH", identity)
    if not ok:  
        print("id does not exist")
    else:
        print("{0}".format(data))

def login_mimic():
    identity = console.get_string("enter username", "username")
    password = console.get_string("enter password", "password")
    ok, *data = handle_request("LOGIN_MIMIC", identity, password)
    if not ok:
        print("Error", data[0])
    else:
        print(f"{identity}: ", data[0])

def register_id():
    identity = console.get_string("enter id", "id")
    password = console.get_string("enter password", "password")
    ok, *data = handle_request("REGISTER_ID", identity, password)
    if not ok:
        print("Error", data)
    else:
        print(data)

def stop_server():
    handle_request("STOP_SERVER", wait_reply=False)
    sys.exit()

def handle_request(*items, wait_reply=True):
    size_struct = struct.Struct("!I")
    data = pickle.dumps(items, 3)
    try:
        with SocketManager(tuple(Address)) as sock:
            sock.sendall(size_struct.pack(len(data)))
            sock.sendall(data)
            if not wait_reply:
                return

            size_data = sock.recv(size_struct.size)
            size = size_struct.unpack(size_data)[0]
            res = bytearray()
            while True:
                data = sock.recv(1000)
                if not data:
                    break
                res.extend(data)
                if len(res) >= size:
                    break
        return pickle.loads(data)
    except socket.error as err:
        print("Error, check server: ", err)

main()