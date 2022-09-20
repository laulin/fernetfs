# fernetfs
It creates a virtual encrypted file system. 

# Why ?

Native file system with encryption already exist but typically need to be root. Moreover, because they are transparent, you can write en clear sector without any warning. By using this library, it will prevents both problems.

## Understand the behavious

The encryption use the Fernet algorithm ([specification](https://github.com/fernet/spec/blob/master/Spec.md)), which use following strong algorithm :

* AES 128 with CBC mode (encryption)
* HMAC-SHA256 (authentication/integrity)
* IV is created with robust random function (os.getrandom)

It uses a password (symetric algorithm with preshared key). The key derivation function - the way the password is processed to get a key - is the PBKDF2HMAC algorithm with 16 bytes random salt and 480000 iterations.

Currently (15/09/2022), these algorithms are considered safe.

No directory name or file name are stored in plain text; On disk, only sha256 random values are used.

### Install

At first you need to install fernetfs :

* From the repo :
  * git clone https://github.com/laulin/fernetfs.git
  * python3 -m build
  * pip3 install build/fernetfs-*-py3-none-any.whl


