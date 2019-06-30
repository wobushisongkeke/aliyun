from Crypto.Cipher import AES
from binascii import b2a_hex


class PrpCrypt(object):
    """
    AES encoding and decoding
    """
    def __init__(self, key, iv):
        if type(key) == bytes:
            self.key = key
        elif type(key) == str:
            self.key = key.encode('utf-8')

        if type(iv) == bytes:
            self.iv = iv
        elif type(iv) == str:
            self.iv = iv.encode('utf-8')

        self.mode = AES.MODE_CBC

        self.ciphertext = None

    def encrypt(self, text):
        text = text.encode('utf-8')
        cryptor = AES.new(self.key, self.mode, self.iv)

        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            text = text + ('\0' * add).encode('utf-8')
        elif count > length:
            add = (length - (count % length))
            text = text + ('\0' * add).encode('utf-8')

        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        result = cryptor.decrypt(text)

        return result
