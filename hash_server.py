import socketserver
import os
import threading
import struct
import pickle
import gzip
import hashlib
import base64
import uuid
import copy

class Finish(Exception): pass
class HashServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

class Storage:

    def __init__(self, identity, password):
        self.__id = identity
        self.__password = password

    @property
    def identity(self):
        return self.__id

    @identity.setter 
    def identity(self, identity):
        self.__id = identity 

    @property
    def password(self):
        return self.__password

    @password.setter 
    def password(self, password):
        self.__password = password 


class RequestHandler(socketserver.StreamRequestHandler):

    storage = {}
    salt_key_storage = {}
    StorageLock = threading.Lock()
    CallLock = threading.Lock()
    call = dict(
            REGISTER_ID = lambda self, i, p: self.register_id(i, p),
            GET_HASH = lambda self, i: self.get_hash(i),
            LOGIN_MIMIC = lambda self, i, p: self.login_mimic(i, p),
            STOP_SERVER = lambda self, *args: self.stop_server(*args))

    def handle(self):
        size_struct = struct.Struct("!I")
        size_data = self.rfile.read(size_struct.size)
        size = size_struct.unpack(size_data)[0]
        data = pickle.loads(self.rfile.read(size))
        reply = None
        try:
            with self.CallLock:
                function = self.call[data[0]]
            reply = function(self, *data[1:])
        except Finish as err:
            print(err)
        data = pickle.dumps(reply, 3)
        self.wfile.write(size_struct.pack(len(data)))
        self.wfile.write(data)

    def register_id(self, identity, password):
        if identity not in self.storage:
            with self.StorageLock:
                hashed_password = encrypt(password)
                self.storage[identity] = Storage(identity, hashed_password)
                return (True, "id successfully stored")
        else:
            return (False, "id already exists")
        return (False, "error trying to store hash")

    def get_hash(self, identity):
        with self.StorageLock:
            password = self.storage.get(identity)
            if password is not None:
                return(True, password.password)
        return (False, "id does not exist")

    def login_mimic(self, identity, password):
        if identity in self.storage:
            secret = load("salts.dat")
            self.salt_key_storage = secret
            comb = self.salt_key_storage[password]
            salt = comb[:16]
            key = comb[16:]
            comp_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf8"), salt, 100000)
            if comp_key == key:
                return (True, "login successful")
            else:
                return (False, "wrong password")

    def stop_server(self, *ignore):
        self.server.shutdown()
        raise Finish()
        
def encrypt(password):
    keys = None
    try:
        block_size = 16
        salt = os.urandom(block_size)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf8"), salt, 100000)
        RequestHandler.salt_key_storage[password] = salt + key
        keys = RequestHandler.salt_key_storage
    finally:
        save("salts.dat", keys)
    return key

def load(filename):
    try:
        with gzip.open(filename, "rb") as fh:
            return pickle.load(fh)
    except EnvironmentError as err:
        print(err)

def save(filename, data):
    try:
        with gzip.open(filename, "wb") as fh:
            pickle.dump(data, fh)
    except (EnvironmentError, pickle.PicklingError) as err:
        print(err)

def main():
    filename = os.path.join(os.path.dirname(__file__), "hashed_passwords.dat")
    print("server running")
    hashes = None
    server = None
    if not os.path.exists(filename):
        hashes = RequestHandler.storage
    else:
        hashes = load(filename)
        RequestHandler.storage = hashes
    try:
        server = HashServer(("", 6000), RequestHandler)
        server.serve_forever()
    except Exception as err:
        print(err)
    finally:
        if server is not None:
            server.shutdown()
            save(filename, hashes)

main()