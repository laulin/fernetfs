import logging
from hashlib import sha256
import os
import os.path
import json
import shutil

from fernetfs.file import FilePrimitive

class Directory:
    HASH_RANDOM_SIZE = 32

    def __init__(self, secret:bytes, root_path:str, iterations:int=480000, salt_size=16) -> None:
        self._primitives = FilePrimitive(secret, iterations, salt_size)
        self._log = logging.getLogger(f"Directory({root_path})")
        self._root_path = root_path

    def is_directories_list(self)->bool:
        path = os.path.join(self._root_path, ".directory")
        return os.path.exists(path)

    def create_directories_list(self):
        self.write_directories_list({})

    def read_directories_list(self):
        path = os.path.join(self._root_path, ".directory")
        with open(path, "r") as f:
            encrypted_listing = f.read()

        listing = self._primitives.decrypt(encrypted_listing)
        return json.loads(listing)

    def write_directories_list(self, listing:dict):
        json_listing = bytes(json.dumps(listing), "utf8")
        encrypted_listing = self._primitives.encrypt(json_listing)
        path = os.path.join(self._root_path, ".directory")

        with open(path, "w") as f:
            f.write(encrypted_listing)

    def get_directories_list(self)->dict:
        if self.is_directories_list():
            listing = self.read_directories_list()
        else:
            listing = {}

        return listing

    def mkdir(self, name:str)->str:
        listing = self.get_directories_list()

        if name in listing:
            raise OSError(f"Directory {name} already exists")

        hash_name = sha256(os.getrandom(Directory.HASH_RANDOM_SIZE)).hexdigest()

        listing[name] = hash_name

        full_hash_name = os.path.join(self._root_path, hash_name)
        os.mkdir(full_hash_name)
        self._log.debug(f"Create directory {name} -> {full_hash_name}")
        self.write_directories_list(listing)
        return hash_name

    def lsdir(self)->list:
        listing = self.get_directories_list()

        return list(listing.keys())

    def gethash(self, name:str)->str:
        listing = self.get_directories_list()

        if name not in listing:
            raise Exception(f"No directory named {name}")

        hash_name = listing[name]

        return hash_name

    def exists(self, name:str)->bool:
        listing = self.get_directories_list()

        if name not in listing:
            return False
        return True

    def rm(self, name, recursive=False)->None:
        listing = self.get_directories_list()

        if name not in listing:
            raise Exception(f"No directory named {name}")

        full_path = os.path.join(self._root_path, listing[name])

        if not recursive:
            os.rmdir(full_path)
        else:
            shutil.rmtree(full_path)

        del listing[name]

        if len(listing) > 0:
            self.write_directories_list(listing)
        else:
            self._log.debug(f"Remove .directory in {self._root_path}")
            path = os.path.join(self._root_path, ".directory")
            os.remove(path)
        
