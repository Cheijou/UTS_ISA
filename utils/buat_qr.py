from Crypto.Cipher import AES
import base64
import qrcode
import random
import string
import json

# AES Encryption Helper
class AESCipher:
    def __init__(self, key):
        self.key = key.ljust(32).encode('utf-8')  # Pastikan key 32 bytes untuk AES-256

    def encrypt(self, raw):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(raw.encode('utf-8'))
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        nonce = enc[:16]
        tag = enc[16:32]
        ciphertext = enc[32:]
        cipher = AES.new(self.key, AES.MODE_EAX, nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

def generate_random_resi(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_resi_qr(secret_key="rahasia123", resi = ""):
    
    data_detail = {
        "resi": resi,
    }

    # Encrypt the data
    cipher = AESCipher(secret_key)
    encrypted_data = cipher.encrypt(json.dumps(data_detail))

    # Generate QR Code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(encrypted_data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(f"resi_{resi}.png")
