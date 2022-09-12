import logging
import os
import os.path
import base64

from fernetfs.listing import Listing

class MasterConfiguration:
    FILENAME = ".fernet"
   
    def __init__(self, salt_size:int=128) -> None:
        self._log = logging.getLogger(f"MasterConfiguration")
        self._salt_size = salt_size

    def exists(self, path)->bool:
        full_path = os.path.join(path, MasterConfiguration.FILENAME)
        return os.path.exists(full_path)

    def create(self, secret:bytes, current_working_directory:str, iterations:int=480000, salt_size=16, sub_iterations:int=48000):

        listing = Listing(secret, current_working_directory, MasterConfiguration.FILENAME, iterations, salt_size)
        if self.exists(current_working_directory):
            raise Exception("Can't overwrite salt file !")
        
        salt = os.getrandom(self._salt_size)
        safe_salt = base64.urlsafe_b64encode(salt)
        salt_structure = {
            "salt" : str(safe_salt, "utf8"),
            "salt_size":salt_size,
            "sub_iterations":sub_iterations

        }
        listing.write(salt_structure)
        self._log.debug(f"Create master configuration")


    def get(self, secret:bytes, current_working_directory:str, iterations:int=480000, salt_size=16)->dict:
        listing = Listing(secret, current_working_directory, MasterConfiguration.FILENAME, iterations, salt_size)
        salt_structure = listing.read()
        salt_structure["salt"] = base64.urlsafe_b64decode(salt_structure["salt"])

        return salt_structure
