import unittest
import os
import shutil
import logging
import os.path

from fernetfs.directory import Directory

WORKING_DIR = "/tmp/test_directory"
SECRET = b"secret"
ITERATIONS = 100

logging.basicConfig(level=logging.DEBUG)

class TestFile(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir(WORKING_DIR)

    def tearDown(self) -> None:
        shutil.rmtree(WORKING_DIR)

    def test_create_directory_listing(self):
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        directory.create_directories_list()

    def test_read_directory_listing(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        directory.create_directories_list()
        result = directory.read_directories_list()
        expected = {}

        self.assertEqual(result, expected)

    def test_write_read_directory_listing(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        directory.write_directories_list({"key":"value"})
        result = directory.read_directories_list()
        expected = {"key":"value"}

        self.assertEqual(result, expected)

    def test_mkdir(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        directory.mkdir("foobar")

    def test_lsdir(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        directory.mkdir("foobar")
        result = directory.lsdir()

        expected = ["foobar"]
        self.assertEqual(result, expected)

    def test_gethash(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        expected = directory.mkdir("foobar")
        result = directory.gethash("foobar")

        self.assertEqual(result, expected)

    def test_exists(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        directory.mkdir("foobar")
        result = directory.exists("foobar")

        self.assertTrue(result)

    def test_not_exists(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        result = directory.exists("foobar")

        self.assertFalse(result)

    def test_rm(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        directory.mkdir("foobar")
        directory.rm("foobar")

        result = directory.lsdir()

        expected = []
        self.assertEqual(result, expected)

    def test_rm_not_empty(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        new_dir = directory.mkdir("foobar")
        full_path = os.path.join(WORKING_DIR, new_dir, "not_empty.txt")
        with open(full_path, "w") as f:
            f.write("...")
        
        try:
            directory.rm("foobar")
            self.assertTrue(False)
        except:
            pass

    def test_rm_recursive(self)->dict:
        directory = Directory(SECRET, WORKING_DIR, ITERATIONS)

        new_dir = directory.mkdir("foobar")
        full_path = os.path.join(WORKING_DIR, new_dir, "not_empty.txt")
        with open(full_path, "w") as f:
            f.write("...")
        
        directory.rm("foobar", True)


    