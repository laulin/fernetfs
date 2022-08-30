import unittest
import os
from contextlib import suppress
import logging 

from fernetfs.fileprimitive import FilePrimitive

WORKING_FILE = "/tmp/test.x"
PLAIN_FILE = "/tmp/test.bin"
SECRET = b"secret"
ITERATIONS = 100

#logging.basicConfig(level=logging.DEBUG)

class TestFilePrimitive(unittest.TestCase):
    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)
        with suppress(FileNotFoundError):
            os.remove(PLAIN_FILE)

    def test_encrypt_decrypt(self):
        fp = FilePrimitive(ITERATIONS)
        encrypted = fp.encrypt(SECRET, b"hello")
        result = fp.decrypt(SECRET, encrypted)
        expected = b"hello"

        self.assertEqual(result, expected)

    def test_encrypt_decrypt_file(self):
        with open(PLAIN_FILE, "wb") as f:
            f.write(b"hello")

        fp = FilePrimitive(ITERATIONS)
        fp.encrypt_file(SECRET, PLAIN_FILE, WORKING_FILE)
        os.remove(PLAIN_FILE)
        fp.decrypt_file(SECRET, WORKING_FILE, PLAIN_FILE)

        with open(PLAIN_FILE, "rb") as f:
            result = f.read()

        expected = b"hello"

        self.assertEqual(result, expected)



    