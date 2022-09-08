import unittest
import os
from contextlib import suppress
import logging

from fernetfs.basicfile import BasicFile
from fernetfs.tmpfile import TmpFile

WORKING_FILE = "/tmp/test.x"
SECRET = b"secret"
ITERATIONS = 100

#logging.basicConfig(level=logging.DEBUG)

class TestTmpFile(unittest.TestCase):


    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)
        pass

    def test_write_utf8(self):
        with BasicFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("test_write_utf8")

        tmp = TmpFile(SECRET,WORKING_FILE, "cat", ITERATIONS)
        tmp.run()

    def test_read_utf8(self):
        with BasicFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("test_read_utf8")

        tmp = TmpFile(SECRET,WORKING_FILE, "sed -i s/read/test/g", ITERATIONS)
        tmp.run()

        with BasicFile(WORKING_FILE, SECRET, "r", ITERATIONS) as f:
            result = f.read()

        print(result)


