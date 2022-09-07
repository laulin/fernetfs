import unittest
import os
import shutil
import logging
import os.path
from unittest import result

from fernetfs.listing import ListingDirectory

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
        listing = ListingDirectory(SECRET, WORKING_DIR, ITERATIONS)

        listing.create()

    def test_read_directory_listing(self)->dict:
        listing = ListingDirectory(SECRET, WORKING_DIR, ITERATIONS)

        listing.create()
        result = listing.read()
        expected = {}

        self.assertEqual(result, expected)

    def test_write_read_directory_listing(self)->dict:
        listing = ListingDirectory(SECRET, WORKING_DIR, ITERATIONS)

        listing.write({"key":"value"})
        result = listing.read()
        expected = {"key":"value"}

        self.assertEqual(result, expected)

    def test_remove(self)->dict:
        listing = ListingDirectory(SECRET, WORKING_DIR, ITERATIONS)

        listing.write({"key":"value"})
        listing.remove()

    def test_add(self)->dict:
        listing = ListingDirectory(SECRET, WORKING_DIR, ITERATIONS)

        listing.write({"key":"value"})
        l = listing.get()
        l = listing.add("foobar", l)
        listing.write(l)

        result = list(listing.get().keys())
        expected = ["key", "foobar"]
        self.assertListEqual(result, expected)
    
