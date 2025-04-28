from cryptography.fernet import Fernet
import os

KEY_FILE = "key.key"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

KEY = load_key()
cipher = Fernet(KEY)

def encrypt(password):
    return cipher.encrypt(password.encode()).decode()

def verify_password(plain, encrypted):
    try:
        return cipher.decrypt(encrypted.encode()).decode() == plain
    except Exception as e:
        print("Verifikasi gagal:", e)
        return False
    
def decrypt(encrypted):
    return cipher.decrypt(encrypted.encode()).decode()
