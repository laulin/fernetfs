from tempfile import mkstemp
import os
from threading import Thread, Lock
import logging 
import time

import inotify.adapters

from fernetfs.fernetfile import FilePrimitive

RAMFS = "/dev/shm"

class FernetTmpFSFile:
    def __init__(self, secret:bytes, filename:str, editor:str, iterations:int=480000, salt_size=16):
        """
        `__init__` is a function that takes in a secret, a filename, an editor, and two optional
        arguments (iterations and salt_size) and sets the values of the class variables `_primitives`,
        `_filename`, `_editor`, and `_running`.
        
        :param secret: The secret key used to encrypt and decrypt the file
        :type secret: bytes
        :param filename: The name of the file to be encrypted
        :type filename: str
        :param editor: The editor to use
        :type editor: str
        :param iterations: The number of iterations to use when generating the key, defaults to 480000
        :type iterations: int (optional)
        :param salt_size: The size of the salt to use. The default is 16 bytes, which is 128 bits,
        defaults to 16 (optional)
        """
        
        self._primitives = FilePrimitive(secret, iterations, salt_size)
        self._filename = filename
        self._editor = editor
        self._log = logging.getLogger(f"FernetTmpFSFile({filename})")

        self._running = False


    def decrypt(self):
        """
        > It opens the file, reads the contents, and then decrypts the contents.
        :return: The decrypted data.
        """

        self._log.debug("decrypt")
        
        with open(self._filename, "rb") as f:
            container = f.read()
    
        return self._primitives.decrypt(container)


    def encrypt(self, path:str):
        """
        > It reads the file at the given path, encrypts it, and writes the encrypted data to the file at
        the path stored in the `_filename` attribute
        
        :param path: the path to the file you want to encrypt
        :type path: str
        """
        
        self._log.debug("encrypt")

        with open(path, "rb") as f:
            plain = f.read()

        encrypted = self._primitives.encrypt(plain)

        with open(self._filename, "w") as f:
            f.write(encrypted)


    def write_back(self, watch_path:str):
        """
        It watches the RAMFS directory for changes, and when a file is closed after being written to, it
        encrypts it
        
        :param watch_path: The path to the file to watch
        :type watch_path: str
        :return: The event is being returned.
        """
        
        i = inotify.adapters.Inotify()

        i.add_watch(RAMFS)

        for event in i.event_gen():

            if not self._running:
                self._log.debug(f"leave")
                return

            if event is not None:
                (_, type_names, path, filename) = event

                if os.path.join(path, filename) == watch_path:
                    if "IN_CLOSE_WRITE" in type_names:
                        self._log.debug(f"Write back {watch_path}")
                        self.encrypt(watch_path)


    def run(self):
        """
        It creates a temporary file in RAMFS, write the decrypted content of the file, run the editor
        on it, and when the editor is closed, it re-encrypt the file and delete the temporary file
        """
        
        decrypted = self.decrypt()

        try:
            fd, path = mkstemp(dir=RAMFS, suffix=".plain")
            with os.fdopen(fd, 'wb') as f:
                f.write(decrypted)
                f.flush()

                # Run a thread that monitor file change.
                # This way, modification are automatically write back to the encrypted file
                self._running = True
                write_back_thread = Thread(target=self.write_back, args=(path,))
                write_back_thread.start()

                self._log.debug(f"{self._editor} {path}")
                print(f"{self._editor} {path}")
                os.system(f"{self._editor} {path}")
                # stopping the write back thread
                self._running = False

            self.encrypt(path)
            
        except Exception as e:
            print(f"Something failed : {e}")
        finally:
            os.unlink(path)