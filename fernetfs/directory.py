import logging
from hashlib import sha256
import os
import os.path
import json
import shutil

from fernetfs.primitives import Primitives
from fernetfs.listing import ListingDirectory

class Directory:
    def __init__(self, secret:bytes, current_working_directory:str, iterations:int=480000, salt_size=16) -> None:
        self._primitives = Primitives(secret, iterations, salt_size)
        self._log = logging.getLogger(f"{self.__class__.__name__}({current_working_directory})")
        self._current_working_directory = current_working_directory
        self._listing = ListingDirectory(secret, current_working_directory, iterations, salt_size)

    def check_path(self, path:str)->None:
        head, _ = os.path.split(path)

        if head != "" :
            raise Exception("File must be in the current directory")

    def mkdir(self, name:str)->str:
        listing = self._listing.get()

        self.check_path(name)

        if name in listing:
            raise OSError(f"Directory {name} already exists")

        listing = self._listing.add(name, listing)

        hash_name = listing[name]

        full_hash_name = os.path.join(self._current_working_directory, hash_name)
        os.mkdir(full_hash_name)
        self._log.debug(f"Create directory {name} -> {full_hash_name}")
        self._listing.write(listing)
        return hash_name

    def ls(self)->list:
        listing = self._listing.get()

        return list(listing.keys())

    def gethash(self, name:str)->str:
        listing = self._listing.get()

        self.check_path(name)

        if name not in listing:
            raise Exception(f"No directory named {name}")

        hash_name = listing[name]

        return hash_name

    def exists(self, name:str)->bool:
        listing = self._listing.get()

        self.check_path(name)

        if name not in listing:
            return False
        return True

    def rm(self, name, recursive=False)->None:
        listing = self._listing.get()

        self.check_path(name)

        if name not in listing:
            raise Exception(f"No directory named {name}")

        full_path = os.path.join(self._current_working_directory, listing[name])

        if not recursive:
            os.rmdir(full_path)
        else:
            shutil.rmtree(full_path)

        del listing[name]

        if len(listing) > 0:
            self._listing.write(listing)
        else:
            self._listing.remove()

    def cwd(self):
        return self._current_working_directory
        
