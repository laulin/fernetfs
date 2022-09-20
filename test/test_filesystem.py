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
        fs = FileSystem()

        fs.create(SECRET, WORKING_DIR, ITERATIONS)

    def test_mount(self)->dict:
        fs = FileSystem()

        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

    def test_miss_mount(self)->dict:
        fs = FileSystem()

        try:
            fs.mount(SECRET, WORKING_DIR, ITERATIONS)
            self.assertTrue(False)
        except:
            pass

    def test_mount_bad_secret(self)->dict:
        fs = FileSystem()

        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        try:
            fs.mount(b"SECRET", WORKING_DIR, ITERATIONS)
            self.assertTrue(False)
        except:
            pass

    def test_mkdir(self)->dict:
        fs = FileSystem()

        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)
        fs.mkdir("foobar")

    def test_mkdir_1_child(self)->dict:
        fs = FileSystem()

        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)
        fs.mkdir("foobar")
        fs.mkdir("/foobar/hhh")

    def test_mkdir_2_child(self)->dict:
        fs = FileSystem()

        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)
        fs.mkdir("foobar")
        fs.mkdir("/foobar/hhh")
        fs.mkdir("foobar/hhh/aaaa")

    def test_open(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        with fs.open("test.txt", "w") as f:
            f.write("demo")

        with fs.open("test.txt", "r") as f:
            result = f.read()

        expected = "demo"
        self.assertEqual(result, expected)

    def test_open_in_dir(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        fs.mkdir("/foobar")

        with fs.open("/foobar/test.txt", "w") as f:
            f.write("demo")

        with fs.open("/foobar/test.txt", "r") as f:
            result = f.read()

        expected = "demo"
        self.assertEqual(result, expected)

    def test_remove_file(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        with fs.open("test.txt", "w") as f:
            f.write("demo")

        fs.remove_file("test.txt")

    def test_remove_directory(self)->dict:
        fs = FileSystem()

        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)
        fs.mkdir("foobar")

        fs.remove_directory("foobar")

    def test_remove_directory_2(self)->dict:
        fs = FileSystem()

        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)
        fs.mkdir("foobar")

        fs.remove_directory("foobar/")

    def test_is_file_exist(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        with fs.open("test.txt", "w") as f:
            f.write("")

        results = fs.is_file_exist("test.txt")
        self.assertTrue(results)

    def test_is_file_exist_in_dir(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        fs.mkdir("/foobar")
        with fs.open("foobar/test.txt", "w") as f:
            f.write("")
        results = fs.is_file_exist("foobar/test.txt")
        self.assertTrue(results)

    def test_is_file_not_exist(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        results = fs.is_file_exist("test.txt")
        self.assertFalse(results)

    def test_is_directory_exist(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        fs.mkdir("/foobar")

        results = fs.is_directory_exist("foobar")
        self.assertTrue(results)

    def test_is_directory_exist_in_dir(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        fs.mkdir("/foobar")
        fs.mkdir("/foobar/barfoo")
        

        results = fs.is_directory_exist("foobar/barfoo")
        self.assertTrue(results)

    def test_is_directory_not_exist(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        results = fs.is_directory_exist("foobar")
        self.assertFalse(results)

    def test_ls(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        fs.mkdir("/foobar")
        fs.mkdir("/barfoo")

        with fs.open("test.txt", "w") as f:
            f.write("")

        with fs.open("demo.txt", "w") as f:
            f.write("")

        results = fs.ls("/")
        expected = {'foobar': 'd', 'barfoo': 'd', 'test.txt': 'f', 'demo.txt': 'f'}
        self.assertDictEqual(results, expected)

    def test_open_as_tmpfile(self):
        fs = FileSystem()
        fs.create(SECRET, WORKING_DIR, ITERATIONS, SALT, ITERATIONS)
        fs.mount(SECRET, WORKING_DIR, ITERATIONS)

        fs.mkdir("/foobar")
        with fs.open("/foobar/test.txt", "w") as f:
            f.write("read")

        tmpfs = fs.open_as_tmpfile("/foobar/test.txt")
        tmpfs.run("sed -i s/read/test/g")

        with fs.open("/foobar/test.txt", "r") as f:
            results = f.read()

        expected = "test"
        self.assertEqual(results, expected)
