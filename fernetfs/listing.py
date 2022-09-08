import logging
import os
import os.path
import json
from hashlib import sha256

from fernetfs.primitives import Primitives

class Listing:
    HASH_RANDOM_SIZE = 32
    def __init__(self, secret:bytes, root_path:str, name:str, iterations:int=480000, salt_size=16) -> None:
        self._primitives = Primitives(secret, iterations, salt_size)
        self._log = logging.getLogger(f"Listing({name} @ {root_path})")
        self._root_path = root_path
        self._path = os.path.join(self._root_path, name)

    def exists(self)->bool:
        return os.path.exists(self._path)

    def create(self):
        self.write({})

    def read(self):
        
        with open(self._path, "r") as f:
            encrypted_listing = f.read()

        listing = self._primitives.decrypt(encrypted_listing)
        output = json.loads(listing)

        self._log.debug(f"Read from {self._path} with {len(output)} entries")
        return output

    def write(self, listing:dict):
        json_listing = bytes(json.dumps(listing), "utf8")
        encrypted_listing = self._primitives.encrypt(json_listing)

        with open(self._path, "w") as f:
            f.write(encrypted_listing)

        self._log.debug(f"Write to {self._path} with {len(listing)} entries")

    def get(self)->dict:
        if self.exists():
            listing = self.read()
        else:
            listing = {}

        return listing

    def add(self, key:str, source:dict)->dict:
        hash_name = sha256(os.getrandom(Listing.HASH_RANDOM_SIZE)).hexdigest()
        source[key] = hash_name
        self._log.debug(f"Add to {key} as {hash_name}")

        return source

    def remove(self):
        os.remove(self._path)

class ListingDirectory(Listing):
    def __init__(self, secret: bytes, root_path: str, iterations: int = 480000, salt_size=16) -> None:
        super().__init__(secret, root_path, ".directories", iterations, salt_size)

class ListingFile(Listing):
    def __init__(self, secret: bytes, root_path: str, iterations: int = 480000, salt_size=16) -> None:
        super().__init__(secret, root_path, ".files", iterations, salt_size)