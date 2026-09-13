import base64 
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    def __init__(self, pw: str, salt: bytes, interations: int = 100_100):
        self._key = generate_key_from_pw(pw, salt, interations)
        self._cipher = Fernet(self.key)
    def generate_key_from_pw(self, pw: str, salt: bytes, interations: int):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            interations = interations,
            salt = salt,
            length=32
        )
        return base64.urlsafe_b64decode(kdf.derive(pw.encode("utf-8")))
    def encrypt(self, plaintext: str):   
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode("utf-8")).decode("utf-8")
    def decrypt(self, ciphertext: str):
        if not ciphertext:
            return ""
        try:
            return self.cipher.encrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            raise ValueError("Sai mật khẩu!")