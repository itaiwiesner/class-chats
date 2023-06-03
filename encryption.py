from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib



def encrypt(decrypted_data, key):
    """ encrypts data using the given key and AES protocol"""
    cipher = AES.new(key, AES.MODE_CBC)
    padded_data = pad(decrypted_data.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return cipher.iv + encrypted_data


def decrypt(encrypted_data, key):
    """ decrypts data using the given key and AES protocol"""
    iv = encrypted_data[:AES.block_size]
    encrypted_data = encrypted_data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    decrypted_data = cipher.decrypt(encrypted_data)
    unpadded_data = unpad(decrypted_data, AES.block_size)
    return unpadded_data.decode()


def encrypt_password(password):
    """ gets password and encrypts it using md5 hash """
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode('utf-8'))
    return md5_hash.hexdigest()


