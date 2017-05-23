import os
import struct

from Crypto.Cipher import AES
from io import BytesIO


def encrypt(key, data, size, size_of_chunk=64*1024):
    # initial vector
    iv = os.urandom(16)

    encryptor = AES.new(key, AES.MODE_CBC, iv)
    new_data = struct.pack('<Q', size)
    new_data += iv

    while True:
        chunk = data.read(size_of_chunk)
        if len(chunk) == 0:
            break
        elif len(chunk) % 16 != 0:
            # PAD
            chunk += b' ' * (16 - len(chunk) % 16)
        new_data += encryptor.encrypt(chunk)

    return BytesIO(new_data)


def decrypt(key, data, size_of_chunk=24*1024):
    origin_size = struct.unpack('<Q', data.read(struct.calcsize('Q')))[0]
    iv = data.read(16)
    decryptor = AES.new(key, AES.MODE_CBC, iv)
    origin_data = b''

    while True:
        chunk = data.read(size_of_chunk)
        if len(chunk) == 0:
            break
        origin_data += decryptor.decrypt(chunk)

    return (BytesIO(origin_data), origin_size)
