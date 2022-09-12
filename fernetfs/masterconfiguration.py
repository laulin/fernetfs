import logging
import os
import os.path
import base64

from fernetfs.listing import Listing

class MasterConfiguration:
    FILENAME = ".fernet"
    MASTER_SALT_SIZE = 128
    def __init__(self) -> None:
        self._log = logging.getLogger(f"MasterConfiguration")
        self._listing = None
        self._cache = None

    def exists(self)->bool:
        return self._listing.exists()

    def create(self, secret:bytes, current_working_directory:str, iterations:int=480000, salt_size=16, sub_iterations:int=48000):

        self._listing = Listing(secret, current_working_directory, MasterConfiguration.FILENAME, iterations, salt_size)
        if self.exists():
            raise Exception("Can't overwrite salt file !")
        
        salt = os.getrandom(MasterConfiguration.MASTER_SALT_SIZE)
        safe_salt = base64.urlsafe_b64encode(salt)
        salt_structure = {
            "salt" : str(safe_salt, "utf8"),
            "iterations":iterations,
            "salt_size":salt_size,
            "sub_iterations":sub_iterations

        }
        self._listing.write(salt_structure)
        self._log.debug(f"Create master configuration")

        self._cache = salt_structure
        self._cache["salt"] = salt

        return self._cache

    def get(self)->dict:
        if self._cache is not None:
            return self._cache

        salt_structure = self._listing.read()
        salt_structure["salt"] = base64.urlsafe_b64decode(salt_structure["salt"])

        self._cache = salt_structure

        return self._cache
