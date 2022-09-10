from glob import glob
import unittest
import os
import shutil
import logging
import os.path

from fernetfs.file import File

WORKING_DIR = "/tmp/test_directory"
SECRET = b"secret"
ITERATIONS = 100

logging.basicConfig(level=logging.DEBUG)

class TestFile(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir(WORKING_DIR)

    def tearDown(self) -> None:
        shutil.rmtree(WORKING_DIR)

    def test_ls(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        with file.open("foobar.txt", "w") as f:
            f.write("test")
        
        result = file.ls()

        expected = ["foobar.txt"]
        self.assertEqual(result, expected)

    def test_ls_append(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        with file.open("foobar.txt", "a") as f:
            f.write("test")
        
        result = file.ls()

        expected = ["foobar.txt"]
        self.assertEqual(result, expected)

    def test_write_read(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        with file.open("foobar.txt", "w") as f:
            f.write("test")
       
        with file.open("foobar.txt", "r") as f:
            result = f.read()

        expected = "test"
        self.assertEqual(result, expected)

    def test_remove(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        with file.open("foobar.txt", "w") as f:
            f.write("test")
        
        file.rm("foobar.txt")

        result = file.ls()

        expected = []
        self.assertEqual(result, expected)

    def test_exists(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        with file.open("foobar.txt", "w") as f:
            f.write("test")

        result = file.exists("foobar.txt")

        self.assertTrue(result)

    def test_not_exists(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        result = file.exists("foobar.txt")

        self.assertFalse(result)

    def test_remove(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        with file.open("foobar.txt", "w") as f:
            f.write("test")

        file.rm("foobar.txt")

        result = file.exists("foobar.txt")

        self.assertFalse(result)

    def test_remove_fail(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        try:
            file.rm("foobar.txt")
            self.assertTrue(False)
        except:
            pass

    def test_remove_listing(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        with file.open("foobar.txt", "w") as f:
            f.write("test")

        file.rm("foobar.txt")

        result = list(glob(WORKING_DIR + "/*"))

        self.assertEqual(result, [])

    def test_open_in_ram_echo(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        file.open_in_ram("foobar.txt", 'echo "test" >')

        with file.open("foobar.txt", "r") as f:
            result = f.read()

        expected = "test\n"

        self.assertEqual(result, expected)

    def test_open_in_ram_sed(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        with file.open("foobar.txt", "w") as f:
            f.write("read_ko")

        file.open_in_ram("foobar.txt", 'sed -i s/ko/ok/g')

        with file.open("foobar.txt", "r") as f:
            result = f.read()

        expected = "read_ok"

        self.assertEqual(result, expected)
        
    def test_write_read_in_dir(self)->dict:
        file = File(SECRET, WORKING_DIR, ITERATIONS)

        new_path = os.path.join(WORKING_DIR, "my_dir")
        os.mkdir(new_path)

        try:
            with file.open("my_dir/foobar.txt", "w") as f:
                f.write("test")
            self.assertTrue(False)
        except Exception:
            pass

        


    