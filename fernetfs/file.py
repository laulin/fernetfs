import logging
import os.path
import os

from fernetfs.basicfile import BasicFile
from fernetfs.primitives import Primitives
from fernetfs.listing import ListingFile
from fernetfs.tmpfile import TmpFile


class File():
    def __init__(self, secret: bytes, root_path: str, iterations: int = 480000, salt_size=16):
        self._root_path = root_path
        self._primitives = Primitives(secret, iterations, salt_size)
        self._log = logging.getLogger(f"File({root_path})")
        self._listing = ListingFile(secret, root_path, iterations, salt_size)

        self._secret = secret
        self._iterations = iterations
        self._salt_size = salt_size

    def check_path(self, path:str)->None:
        head, _ = os.path.split(path)

        if head != "" :
            raise Exception("File must be in the current directory")

    def open(self, filename:str, mode:str)->BasicFile:
        listing = self._listing.get()

        self.check_path(filename)

        if filename not in listing:
            if "r" in mode:
                raise Exception(f"No file named {filename}")
            else:
                listing = self._listing.add(filename, listing)

        hash_name = listing[filename]
        path = os.path.join(self._root_path, hash_name)
        self._log.debug(f"Opening {filename} ({path}) in '{mode}' mode")

        if "r" in mode and not self.exists(filename):
            raise Exception(f"No file named {filename} ({path})")

        file = BasicFile(path, self._secret, mode, self._iterations, self._salt_size)
        self._listing.write(listing)
        
        return file

    def open_in_ram(self, filename:str, command:str)->TmpFile:
        listing = self._listing.get()

        self.check_path(filename)

        if filename not in listing:
            self._log.debug("Creating empty file of RAM file")
            with self.open(filename, "wb") as f:
                f.write(b"")
            listing = self._listing.get()
            
        hash_name = listing[filename]
        path = os.path.join(self._root_path, hash_name)
        file = TmpFile(self._secret, path, command, self._iterations, self._salt_size)
        file.run()

    def ls(self)->list:
        listing = self._listing.get()
        return list(listing.keys())

    def exists(self, filename:str)->bool:
        listing = self._listing.get()

        self.check_path(filename)

        if filename not in listing:
            self._log.debug(f"File {filename} in not in listing")
            return False
        
        hash_name = listing[filename]
        path = os.path.join(self._root_path, hash_name)

        # prevent Inconsistent between listinges and files
        if not os.path.exists(path):
            self._log.debug(f"File {path} in in fs")
            del listing[filename]
            self._listing.write(listing)
            return False

        self._log.debug(f"File {path} exists")

        return True

    def rm(self, filename:str)->None:
        listing = self._listing.get()

        self.check_path(filename)

        if not self.exists(filename):
            raise Exception(f"No file named {filename}")

        hash_name = listing[filename]
        path = os.path.join(self._root_path, hash_name)

        os.remove(path)

        del listing[filename]

        if len(listing) > 0:
            self._listing.write(listing)
        else:
            self._listing.remove()

