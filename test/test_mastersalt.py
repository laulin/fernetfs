from glob import glob
import unittest
import os
import shutil
import logging
import os.path
from venv import create

from fernetfs.mastersalt import MasterSalt

WORKING_DIR = "/tmp/test_directory"
SECRET = b"secret"
ITERATIONS = 100

logging.basicConfig(level=logging.DEBUG)

class TestMasterSalt(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir(WORKING_DIR)

    def tearDown(self) -> None:
        shutil.rmtree(WORKING_DIR)

    def test_create(self)->dict:
        salt = MasterSalt(SECRET, WORKING_DIR, ITERATIONS)

        result = salt.create()
        #print(result)

    def test_create_twice(self)->dict:
        salt = MasterSalt(SECRET, WORKING_DIR, ITERATIONS)

        salt.create()
        try:
            salt.create()
            self.assertTrue(False)
        except:
            pass

    def test_get(self)->dict:
        salt = MasterSalt(SECRET, WORKING_DIR, ITERATIONS)

        salt.get()

    def test_create_twice(self)->dict:
        salt = MasterSalt(SECRET, WORKING_DIR, ITERATIONS)

        salt.get()
        salt.get()
        
    
