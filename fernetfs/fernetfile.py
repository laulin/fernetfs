import io
import logging

from fernetfs.fileprimitive import FilePrimitive

class FernetFile:
    def __init__(self, filename:str, secret:bytes, mode:str, iterations:int=480000, salt_size=16):
        self._filename = filename
        self._mode = mode
        self._primitives = FilePrimitive(secret, iterations, salt_size)
        self._log = logging.getLogger(f"FernetFile({filename})")
        self._data = None

    def __enter__(self):
        self._log.debug("__enter__")
        self._open_file()
        return self._data
     
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._log.debug("__exit__")
        self._close_file()

    def _open_file(self):
        if "r" in self._mode :
            self._log.debug("Open with r")
            return self._open_file_read()
        elif "w" in self._mode :
            self._log.debug("Open with w")
            return self._open_file_write()
        elif "a" in self._mode :
            self._log.debug("Open with a")
            return self._open_file_read()

    def _open_file_read(self):
        if "b" in self._mode:
            buffer = io.BytesIO
        else:
            buffer = io.StringIO

        with open(self._filename, f"r") as f:
            container_data = f.read()
            
            plain = self._primitives.decrypt(container_data)

            if "b" not in self._mode:
                plain = str(plain, "utf8")

            self._data = buffer(plain)

    def _open_file_write(self):
        if "b" in self._mode:
            self._data = io.BytesIO()
        else:
            self._data = io.StringIO()

    def _close_file(self):
        if "a" in self._mode or "w" in self._mode:
            self._close_write_file()

        self._data.close()
        self._data = None

    def _close_write_file(self):
        data = self._data.getvalue()
        self._log.debug(f"Data len : {len(data)}")

        if "b" not in self._mode:
            data = bytes(data, "utf8")

        container_data = self._primitives.encrypt(data)

        with open(self._filename, f"w") as f:
            f.write(container_data)
