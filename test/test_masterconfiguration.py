import unittest
import os
import shutil
import logging
import os.path

from fernetfs.masterconfiguration import MasterConfiguration

WORKING_DIR = "/tmp/test_directory"
SECRET = b"secret"
ITERATIONS = 100

logging.basicConfig(level=logging.DEBUG)

class TestMasterConfiguration(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir(WORKING_DIR)

    def tearDown(self) -> None:
        shutil.rmtree(WORKING_DIR)

    def test_create_directory_listing(self):
        conf = MasterConfiguration()

        conf.create(SECRET, WORKING_DIR, ITERATIONS)

    def test_get(self)->dict:
        conf = MasterConfiguration()

        conf.create(SECRET, WORKING_DIR, ITERATIONS)
        results = list(conf.get(SECRET, WORKING_DIR, ITERATIONS).keys())
        expected = ["salt", "salt_size", "sub_iterations"]

        self.assertListEqual(results, expected)

    def test_create_directory_listing(self):
        conf = MasterConfiguration()

        conf.create(SECRET, WORKING_DIR, ITERATIONS)    
        try:
            conf.create(SECRET, WORKING_DIR, ITERATIONS)    
            self.assertTrue(False)
        except:
            pass
