from glob import glob
import unittest
import os
import shutil
import logging
import os.path

from fernetfs.filesystem import FileSystem

WORKING_DIR = "/tmp/test_directory"
SECRET = b"secret"
ITERATIONS = 100
SALT = 16

logging.basicConfig(level=logging.DEBUG)

class TestFileSystem(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir(WORKING_DIR)

    def tearDown(self) -> None:
        shutil.rmtree(WORKING_DIR)

    def test_create(self)->dict:
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS)

        fs.create()

    def test_iscreated(self)->dict:
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS)

        fs.create()
        results = fs.iscreated()

        self.assertTrue(results)

    def test_mkdir(self)->dict:
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)

        fs.create()
        fs.mkdir("foobar")

    def test_mkdir_1_child(self)->dict:
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)

        fs.create()
        fs.mkdir("foobar")
        fs.mkdir("/foobar/hhh")

    def test_mkdir_2_child(self)->dict:
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)

        fs.create()
        fs.mkdir("foobar")
        fs.mkdir("/foobar/hhh")
        fs.mkdir("foobar/hhh/aaaa")

    def test_open(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        with fs.open("test.txt", "w") as f:
            f.write("demo")

        with fs.open("test.txt", "r") as f:
            result = f.read()

        expected = "demo"
        self.assertEqual(result, expected)

    def test_open_in_dir(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        fs.mkdir("/foobar")

        with fs.open("/foobar/test.txt", "w") as f:
            f.write("demo")

        with fs.open("/foobar/test.txt", "r") as f:
            result = f.read()

        expected = "demo"
        self.assertEqual(result, expected)

    def test_remove_file(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        with fs.open("test.txt", "w") as f:
            f.write("demo")

        fs.remove_file("test.txt")

    def test_remove_directory(self)->dict:
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)

        fs.create()
        fs.mkdir("foobar")

        fs.remove_directory("foobar")

    def test_is_file_exist(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        with fs.open("test.txt", "w") as f:
            f.write("")

        results = fs.is_file_exist("test.txt")
        self.assertTrue(results)

    def test_is_file_exist_in_dir(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        fs.mkdir("/foobar")
        with fs.open("foobar/test.txt", "w") as f:
            f.write("")
        results = fs.is_file_exist("foobar/test.txt")
        self.assertTrue(results)

    def test_is_file_not_exist(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        results = fs.is_file_exist("test.txt")
        self.assertFalse(results)

    def test_is_directory_exist(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        fs.mkdir("/foobar")

        results = fs.is_directory_exist("foobar")
        self.assertTrue(results)

    def test_is_directory_exist_in_dir(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        fs.mkdir("/foobar")
        fs.mkdir("/foobar/barfoo")
        

        results = fs.is_directory_exist("foobar/barfoo")
        self.assertTrue(results)

    def test_is_directory_not_exist(self):
        fs = FileSystem(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.create()

        results = fs.is_directory_exist("foobar")
        self.assertFalse(results)
