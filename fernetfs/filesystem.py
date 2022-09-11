from ast import Str
import logging
import os.path
import os
import glob

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from fernetfs.file import File
from fernetfs.directory import Directory
from fernetfs.mastersalt import MasterSalt
from fernetfs.tmpfile import TmpFile


class FileSystem():
    KEY_LENGTH = 256
    SALT_LENGTH = 256
    def __init__(self, secret:bytes, root_path:str, iterations:int = 480000, salt_size=16, sub_iterations:int = 48000):
        self._secret = secret
        self._root_path = root_path
        self._iterations = iterations
        self._salt_size = salt_size
        self._sub_iterations = sub_iterations

        self._log = logging.getLogger(f"FileSystem({root_path})")

        self._key = None
        self._salt = MasterSalt(secret, root_path, iterations, FileSystem.SALT_LENGTH)

    def iscreated(self)->bool:
        return self._salt.exists()

    def create(self)->None:
        path = os.path.join(self._root_path, "*")
        ls_destination = list(glob.glob(path))

        if len(ls_destination) > 0:
            raise Exception("Mounting point is not empty")

        self._salt.create()
        self.mount()

    def mount(self)->None:
        if not self.iscreated():
            raise Exception(f"File system at {self._root_path} doesn't exist")

        salt = self._salt.get()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=FileSystem.KEY_LENGTH,
            salt=salt,
            iterations=self._iterations,
        )
        self._key = kdf.derive(self._secret)

    def _split_path(self, path:str)->list:
        if path.startswith("/"):
            path = path[1:]

        return list(path.split("/"))

    def _get_directory(self, relative_path:Str)->Directory:
        path = self._root_path
        directory = Directory(self._key, self._root_path, self._sub_iterations, self._salt_size)

        sub_dirs = self._split_path(relative_path)
        for sub_dir in sub_dirs[:-1]:
            hash_name = directory.gethash(sub_dir)
            path = os.path.join(path, hash_name)
            directory = Directory(self._key, path, self._sub_iterations, self._salt_size)

        return directory, sub_dirs[-1]

    def mkdir(self, path:str)->None:
        directory, last_dir = self._get_directory(path)
        directory.mkdir(last_dir)

    def open(self, path:str, mode:str)->File:
        directory, filename = self._get_directory(path)
        file = directory.get_file()
        return file.open(filename, mode)

    def open_as_tmpfile(self, path:str, command:str):
        directory, filename = self._get_directory(path)
        cwd = directory.cwd()
        file = directory.get_file()
        hashname = file.get_hash(filename)
        full_path = os.path.join(cwd, hashname)
        tmpfile = TmpFile(self._key, full_path, command, self._sub_iterations, self._salt_size)
        return tmpfile

    def remove_file(self, path:str)->None:
        directory, filename = self._get_directory(path)
        file = directory.get_file()
        file.rm(filename)

    def remove_directory(self, path:str, recursive:bool=False)->None:
        directory, directory_name = self._get_directory(path)
        directory.rm(directory_name, recursive)

    def is_file_exist(self, path:str)->bool:
        directory, filename = self._get_directory(path)
        file = directory.get_file()
        return file.exists(filename)

    def is_directory_exist(self, path:str)->bool:
        directory, directoryname = self._get_directory(path)
        return directory.exists(directoryname)

    def ls(self, path:str)->dict:
        directory, _ = self._get_directory(path)
        file = directory.get_file()
        output = {}
        for d in directory.ls():
            output[d] = "d"

        for f in file.ls():
            output[f] = "f"

        return output