import logging
import os
import os.path
import base64

from fernetfs.listing import Listing

class MasterSalt:
    FILENAME = ".salt"
    MASTER_SALT_SIZE = 128
    def __init__(self, secret:bytes, root_path:str, iterations:int=480000, salt_size=16) -> None:
        self._log = logging.getLogger(f"MasterSalt({root_path})")
        self._listing = Listing(secret, root_path, MasterSalt.FILENAME, iterations, salt_size)

        self._cache = None

    def exists(self)->bool:
        return self._listing.exists()

    def create(self):
        if self.exists():
            raise Exception("Can't overwrite salt file !")
        
        salt = os.getrandom(MasterSalt.MASTER_SALT_SIZE)
        safe_salt = base64.urlsafe_b64encode(salt)
        salt_structure = {"salt" : str(safe_salt, "utf8")}

        self._listing.write(salt_structure)
        self._log.debug(f"Create salt : {salt_structure['salt']}")

        self._cache = salt

        return salt_structure

    def get(self)->dict:
        if self._cache is not None:
            return self._cache

        if self.exists():
            salt_structure = self._listing.read()
            self._log.debug(f"Read existing salt : {salt_structure['salt']}")
        else:
            salt_structure = self.create()
            self._log.debug(f"Read created salt : {salt_structure['salt']}")

        self._cache = base64.urlsafe_b64decode(salt_structure["salt"])

        return self._cache
