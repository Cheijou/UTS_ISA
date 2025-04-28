from Crypto.Cipher import AES 
from pyzbar.pyzbar import decode
from PIL import Image
import base64
import qrcode
import random
import string
import json

def fix_key(key):
    key = key.encode('utf-8')
    if len(key) > 32:
        return key[:32]  # Potong
    elif len(key) < 32:
        return key.ljust(32, b'\0')  # Isi null byte, bukan space
    return key

# AES Encryption Helper
class AESCipher:
    def __init__(self, key):
        self.key = fix_key(key)
        print(f"[INIT] Key: {self.key.hex()}")  # Pastikan key 32 bytes untuk AES-256

    def encrypt(self, raw):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(raw.encode('utf-8'))
        print(f"[ENCRYPT] Nonce: {cipher.nonce.hex()}")
        print(f"[ENCRYPT] Tag: {tag.hex()}")
        print(f"[ENCRYPT] Ciphertext (first 64 bytes): {ciphertext[:64].hex()}")
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

    def decrypt(self, data):
        try:
            enc = base64.b64decode(data.encode('utf-8'))
            if len(enc) < 32:
                raise ValueError("Data terlalu pendek untuk didekripsi")
            print(f"[DECRYPT] Data setelah base64 decode, panjang: {len(enc)} bytes")

            nonce = enc[:16]  # Ambil nonce dari data yang telah didecode
            tag = enc[16:32]  # Ambil tag
            ciphertext = enc[32:]  # Ambil ciphertext
            print(f"[DECRYPT] Nonce: {nonce.hex()}")
            print(f"[DECRYPT] Tag: {tag.hex()}")
            print(f"[DECRYPT] Ciphertext (first 64 bytes): {ciphertext[:64].hex()}")
            
            # Dekripsi dengan AES.MODE_EAX
            cipher = AES.new(self.key, AES.MODE_EAX, nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
        except Exception as e:
            print("Error decrypting data:", e)
            return None

def create_resi_qr(resi = ""):
    
    data_detail = {
        "resi": resi,
    }

    # Encrypt the data
    cipher = AESCipher("rahasia123")
    encrypted_data = cipher.encrypt(json.dumps(data_detail))
    print(encrypted_data)

    # Generate QR Code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(encrypted_data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(f"resi_{resi}.png")

def read_qr_and_decrypt(path):
    img = Image.open(path)
    decoded_objects = decode(img)
    print(decoded_objects)
    cipher = AESCipher("rahasia123")
    
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        print (data)  # Ambil isi QR Code
        # print("Isi QR Code:", data)
        
        # Decrypt QR Code content
        decrypted_data = cipher.decrypt(data)
        if decrypted_data:
            return decrypted_data
        else:
            print("Failed to decrypt or invalid data.")
