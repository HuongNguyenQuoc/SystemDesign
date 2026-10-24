import os
from cryptography.fernet import Fernet, InvalidToken

class Encryptor:
    def __init__(self, key: bytes):
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()

def load_key() -> bytes:
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY environment variable is not set.")
    return key.encode()

if __name__ == "__main__":
    enc = Encryptor(load_key())
    plaintext = "huongquoc1"

    encrypted = enc.encrypt(plaintext)
    print(f"Encrypted: {encrypted}")

    encrypted2 = enc.encrypt(plaintext)
    print(f"Encrypted2: {encrypted2}")

    decrypted = enc.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")

    decrypted2 = enc.decrypt(encrypted2)
    print(f"Decrypted2: {decrypted2}")

    enc2 = Encryptor(Fernet.generate_key())
    try:
        decrypted_invalid = enc2.decrypt(encrypted)
        print(f"Decrypted with invalid key: {decrypted_invalid}")
    except InvalidToken:
        print("Failed to decrypt with invalid key.")
