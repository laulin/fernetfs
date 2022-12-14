import unittest
import os
from contextlib import suppress
import logging

from fernetfs.basicfile import BasicFile
from fernetfs.tmpfile import TmpFile

WORKING_FILE = "/tmp/test.x"
SECRET = b"secret"
ITERATIONS = 100

logging.basicConfig(level=logging.DEBUG)

class TestTmpFile(unittest.TestCase):


    def tearDown(self) -> None:
        with suppress(FileNotFoundError):
            os.remove(WORKING_FILE)
        pass

    def test_write_utf8(self):
        with BasicFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("test_write_utf8")

        tmp = TmpFile(SECRET,WORKING_FILE, ITERATIONS)
        tmp.run("cat")

    def test_read_utf8(self):
        with BasicFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("test_read_utf8")

        tmp = TmpFile(SECRET,WORKING_FILE, ITERATIONS)
        tmp.run("sed -i s/read/test/g")

        with BasicFile(WORKING_FILE, SECRET, "r", ITERATIONS) as f:
            result = f.read()

        print(result)

    def test_read_with(self):
        with BasicFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("test_read_utf8")

        tmp = TmpFile(SECRET,WORKING_FILE, ITERATIONS)

        with tmp as filename:
            with open(filename, "r") as f:
                results = f.read()

        expected = "test_read_utf8"

        self.assertEqual(results, expected)

    def test_write_with(self):
        with BasicFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("")

        tmp = TmpFile(SECRET,WORKING_FILE, ITERATIONS)

        with tmp as filename:
            with open(filename, "w") as f:
                f.write("test_read_utf8")

        with BasicFile(WORKING_FILE, SECRET, "r", ITERATIONS) as f:
            results = f.read()

        expected = "test_read_utf8"

        self.assertEqual(results, expected)

    def test_write_with_exception(self):
        with BasicFile(WORKING_FILE, SECRET, "w", ITERATIONS) as f:
            f.write("")

        tmp = TmpFile(SECRET,WORKING_FILE, ITERATIONS)

        try:
            with tmp as filename:
                with open(filename, "w") as f:
                    f.write("test_read_utf8")

                raise Exception("Bad stuff here")
        except:
            print("something happen here")

        with BasicFile(WORKING_FILE, SECRET, "r", ITERATIONS) as f:
            results = f.read()

        expected = "test_read_utf8"

        self.assertEqual(results, expected)


