import base64
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from backend.config import settings

# AES_KEY와 AES_IV를 환경 변수에서 읽어옵니다.
AES_KEY = base64.urlsafe_b64decode(settings.aes_key)
AES_IV = base64.urlsafe_b64decode(settings.aes_iv)

# AES_KEY와 IV의 길이 확인
AES_KEY_LENGTH = 32
AES_IV_LENGTH = 16

if len(AES_KEY) != AES_KEY_LENGTH:
    raise ValueError(f"AES_KEY must be {AES_KEY_LENGTH} bytes long.")
elif len(AES_IV) != AES_IV_LENGTH:
    raise ValueError(f"AES_IV must be {AES_IV_LENGTH} bytes long.")

cipher_backend = default_backend()


# 암호화 함수
def encrypt_password(password: str) -> str:
    padder = padding.PKCS7(128).padder()
    padded_password = padder.update(password.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=cipher_backend)
    encryptor = cipher.encryptor()
    encrypted_password = encryptor.update(padded_password) + encryptor.finalize()

    encrypted_password_base64 = base64.urlsafe_b64encode(encrypted_password).decode()
    return encrypted_password_base64


# 복호화 함수
def decrypt_password(encrypted_password_str: str) -> str:
    try:
        encrypted_password_bytes = base64.urlsafe_b64decode(encrypted_password_str)

        cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=cipher_backend)
        decryptor = cipher.decryptor()
        decrypted_password = decryptor.update(encrypted_password_bytes) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        decrypted_password = unpadder.update(decrypted_password) + unpadder.finalize()

        return decrypted_password.decode()
    except Exception as e:
        print(f"Error in decrypt_password: {e}")
        return None
