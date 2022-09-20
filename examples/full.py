import os
import shutil
import logging

from fernetfs.filesystem import FileSystem

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    PASSWORD = b"my_password"
    ENTRYPOINT = "/tmp/secret"

    fs = FileSystem()

    # creating the secet location
    os.mkdir(ENTRYPOINT)
    fs.create(PASSWORD, ENTRYPOINT, 48000)

    # After this call, the FS is ready
    fs.mount(PASSWORD, ENTRYPOINT, 48000)

    fs.mkdir("foo")
    with fs.open("foo/bar.txt", "w") as f:
        f.write("Hello, u\n")

    tmpfile = fs.open_as_tmpfile("foo/bar.txt", "cat ")

    with tmpfile as filename:
        print(f"Opening {tmpfile}")
        os.system(f"nano {tmpfile}")

    print("New content : ")
    tmpfile.run()

    print(f"ls / : {fs.ls('')}")
    print(f"ls /foo : {fs.ls('foo')}")

    os.system(f"tree {ENTRYPOINT}")

    
    fs.remove_file("foo/bar.txt")
    fs.remove_directory("foo")

    shutil.rmtree(ENTRYPOINT)
    
