from ast import Str
import logging
import os.path
import os
import glob

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import InvalidToken

from fernetfs.file import File
from fernetfs.directory import Directory
from fernetfs.masterconfiguration import MasterConfiguration
from fernetfs.tmpfile import TmpFile


class FileSystem():
    KEY_LENGTH = 256
    SALT_LENGTH = 256
    def __init__(self):
        self._current_working_directory = None
        self._salt_size = None
        self._sub_iterations = None
        self._key = None

        self._master_conf = MasterConfiguration(FileSystem.SALT_LENGTH)

        self._log = logging.getLogger(f"FileSystem(unmounted)")

    def create(self, secret:bytes, current_working_directory:str, iterations:int=480000, salt_size=16, sub_iterations:int=48000)->None:
        path = os.path.join(current_working_directory, "*")
        ls_destination = list(glob.glob(path))

        if len(ls_destination) > 0:
            raise Exception("Mounting point is not empty")

        self._master_conf.create(secret, current_working_directory, iterations, salt_size, sub_iterations)

    def mount(self, secret:bytes, current_working_directory:str, iterations:int=480000)->None:
        
        try:
            conf = self._master_conf.get(secret, current_working_directory, iterations)
        except FileNotFoundError as e:
            self._log.error(f"{current_working_directory} is not a valid fs ! ")
            raise e
        except InvalidToken as e:
            self._log.error(f"Password is invalid !")
            raise e
        
        self._current_working_directory = current_working_directory
        self._salt_size = conf["salt_size"]
        self._sub_iterations = conf["sub_iterations"]
        salt = conf["salt"]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=FileSystem.KEY_LENGTH,
            salt=salt,
            iterations=iterations,
        )
        self._key = kdf.derive(secret)

        self._log = logging.getLogger(f"FileSystem({current_working_directory})")

    def _split_path(self, path:str)->list:
        if path.startswith("/"):
            path = path[1:]

        return list(path.split("/"))

    def _get_directory(self, relative_path:Str)->Directory:
        path = self._current_working_directory
        directory = Directory(self._key, self._current_working_directory, self._sub_iterations, self._salt_size)

        sub_dirs = self._split_path(relative_path)
        for sub_dir in sub_dirs[:-1]:
            hash_name = directory.gethash(sub_dir)
            path = os.path.join(path, hash_name)
            directory = Directory(self._key, path, self._sub_iterations, self._salt_size)

        return directory, sub_dirs[-1]

    def _get_file(self, directory:Directory)->File:
        cwd = directory.cwd()
        return File(self._key, cwd, self._sub_iterations, self._salt_size)

    def mkdir(self, path:str)->None:
        directory, last_dir = self._get_directory(path)
        directory.mkdir(last_dir)

    def open(self, path:str, mode:str)->File:
        directory, filename = self._get_directory(path)
        file = self._get_file(directory)
        return file.open(filename, mode)

    def open_as_tmpfile(self, path:str, command:str):
        directory, filename = self._get_directory(path)
        cwd = directory.cwd()
        file = self._get_file(directory)
        hashname = file.get_hash(filename)
        full_path = os.path.join(cwd, hashname)
        tmpfile = TmpFile(self._key, full_path, command, self._sub_iterations, self._salt_size)
        return tmpfile

    def remove_file(self, path:str)->None:
        directory, filename = self._get_directory(path)
        file = self._get_file(directory)
        file.rm(filename)

    def remove_directory(self, path:str, recursive:bool=False)->None:
        directory, directory_name = self._get_directory(path)
        directory.rm(directory_name, recursive)

    def is_file_exist(self, path:str)->bool:
        directory, filename = self._get_directory(path)
        file = self._get_file(directory)
        return file.exists(filename)

    def is_directory_exist(self, path:str)->bool:
        directory, directoryname = self._get_directory(path)
        return directory.exists(directoryname)

    def ls(self, path:str)->dict:
        directory, _ = self._get_directory(path)
        file = self._get_file(directory)
        output = {}
        for d in directory.ls():
            output[d] = "d"

        for f in file.ls():
            output[f] = "f"

        return output