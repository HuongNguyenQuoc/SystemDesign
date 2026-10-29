from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path

# File khóa nằm cùng thư mục với security.py.
KEYFILE = Path(__file__).resolve().parent / ".encryption.key"

class Encryptor:
    def __init__(self, key: bytes):
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()

def load_key() -> bytes:
    try:
        # "xb": tạo file mới; nếu đã tồn tại thì không ghi đè.
        with KEYFILE.open("xb") as f:
            f.write(Fernet.generate_key())
        KEYFILE.chmod(0o600)  # Chỉ owner có quyền đọc/ghi

    except FileExistsError:
        pass  # File đã tồn tại, không làm gì cả

    return KEYFILE.read_bytes().strip()

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
