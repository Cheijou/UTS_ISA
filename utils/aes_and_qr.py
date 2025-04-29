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

    def encrypt(self, raw):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(raw.encode('utf-8'))
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

    def decrypt(self, data):
        try:
            enc = base64.b64decode(data.encode('utf-8'))
            if len(enc) < 32:
                raise ValueError("Data terlalu pendek untuk didekripsi")

            nonce = enc[:16]  # Ambil nonce dari data yang telah didecode
            tag = enc[16:32]  # Ambil tag
            ciphertext = enc[32:]  # Ambil ciphertext
            
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

    # Generate QR Code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(encrypted_data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    nama_file = f"resi_pengiriman_{resi}.png"
    img.save(nama_file)
    return nama_file

def read_qr_and_decrypt(path):
    img = Image.open(path)
    decoded_objects = decode(img)
    cipher = AESCipher("rahasia123")
    
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        
        # Decrypt QR Code content
        decrypted_data = cipher.decrypt(data)
        if decrypted_data:
            return decrypted_data
        else:
            print("Failed to decrypt or invalid data.")

def encrypt_data(plaintext):
    cipher = AESCipher("rahasia123")

    encrypted_text = cipher.encrypt(plaintext)

    return encrypted_text

def decrypt_data(ciphertext):
    cipher = AESCipher("rahasia123")

    decrypted_text = cipher.decrypt(ciphertext)

    return decrypted_text
