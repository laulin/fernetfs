import base64
import os
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class FilePrimitive:
    def __init__(self, secret:bytes, iteration:int=480000, salt_length:int=16) -> None:
        self._iteration = iteration
        self._salt_length = salt_length
        self._secret = secret

    def secret_2_key(self, salt:bytes, secret:bytes)->bytes:
        """
        It takes a salt and a secret and returns a key
        
        :param salt: a random string of bytes
        :type salt: bytes
        :param secret: The secret key that you want to use to encrypt the data
        :type secret: bytes
        :return: The key is being returned.
        """
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._iteration,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret))

        return key

    def create_salt(self, _rand=os.getrandom)->bytes:
        """
        It generates a random string of bytes of length `self._salt_length` and then encodes it using
        `base64.urlsafe_b64encode`
        
        :param _rand: This is the random number generator. It's a function that takes an integer and
        returns a string of random bytes
        :return: A random string of bytes.
        """

        salt = _rand(self._salt_length)
        return base64.urlsafe_b64encode(salt)

    def encrypt(self, data:bytes)->str:
        """
        The function takes a string of data, creates a salt, uses the salt and the secret to create a
        key, uses the key to encrypt the data, and returns the encrypted data in a JSON object
        
        :param data: The data to encrypt
        :type data: bytes
        :return: A JSON string containing the salt and the encrypted data.
        """
        
        salt = self.create_salt()
        key = self.secret_2_key(salt, self._secret)
        
        f = Fernet(key)
        encrypted = f.encrypt(data)

        container = {
            "salt" : str(salt, "utf8"),
            "data" : str(encrypted, "utf8")
        }
        return json.dumps(container, indent=4)


    def decrypt(self, container_data:str)->str:
        """
        It takes a string of JSON data, converts it to a dictionary, extracts the data and salt, uses
        the salt to generate a key, uses the key to decrypt the data, and returns the decrypted data
        
        :param container_data: The encrypted data in JSON format
        :type container_data: str
        :return: The decrypted data.
        """
        
        container = json.loads(container_data)
        data = bytes(container["data"], "utf8")
        salt = bytes(container["salt"], "utf8")

        key = self.secret_2_key(salt, self._secret)
        f = Fernet(key)
        plain = f.decrypt(data)

        return plain

    def encrypt_file(self, infilename:str, outfilename:str)->None:
        """
        Read the contents of the file, encrypt it, and write the encrypted contents to a file
        
        :param infilename: The name of the file to encrypt
        :type infilename: str
        :param outfilename: The name of the file to write the encrypted data to. If this is None, the
        encrypted data is printed to the console
        :type outfilename: str
        """
        
        with open(infilename, "rb") as f:
            plain = f.read()

        container = self.encrypt(plain)

        if outfilename is None:
            print(container)
        else:
            with open(outfilename, "w") as f:
                f.write(container)

    def decrypt_file(self, infilename:str, outfilename:str)->None:
        """
        Read the contents of the file, decrypt it, and write the decrypted contents to a file
        
        :param infilename: The name of the file to be decrypted
        :type infilename: str
        :param outfilename: The name of the file to write the decrypted data to. If this is None, the
        decrypted data will be printed to the console
        :type outfilename: str
        """
        
        with open(infilename, "r") as f:
            container = f.read()

        plain = self.decrypt(container)

        if outfilename is None:
            print(plain)
        else:
            with open(outfilename, "wb") as f:
                f.write(plain)

    def verify_file(self, infilename:str)->bool:
        """
        If the file can be decrypted, then it was encrypted with the same key
        
        :param infilename: the name of the file to be encrypted
        :type infilename: str
        :return: The decrypted file.
        """
        
        with open(infilename, "rb") as f:
            container = f.read()
        try:
            plain = self.decrypt(container)
            return True
        except:
            return False



