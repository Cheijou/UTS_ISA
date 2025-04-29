from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from pyzbar.pyzbar import decode
from PIL import Image
import base64
import qrcode
import json
from Crypto.Random import get_random_bytes

# Fungsi padding & unpadding agar data bisa di-enkripsi dalam AES CBC (16-byte blocks)
def pad(data):
    pad_len = 16 - len(data) % 16
    return data + chr(pad_len) * pad_len

def unpad(data):
    pad_len = ord(data[-1])
    return data[:-pad_len]

# Buat kunci dari username dan password (gunakan sebagai salt juga)
def derive_key_from_username_password(username, password):
    salt = username.encode('utf-8')
    return PBKDF2(password, salt, dkLen=32, count=100000)

# AES CBC Encryption/Decryption helper
class AESCipher:
    def __init__(self, username, password):
        self.key = derive_key_from_username_password(username, password)

    def encrypt(self, raw):
        raw_padded = pad(raw)
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(raw_padded.encode())
        combined = iv + ciphertext  # Hanya IV + data terenkripsi
        return base64.b64encode(combined).decode()

    def decrypt(self, enc_data):
        try:
            enc = base64.b64decode(enc_data.encode())
            iv = enc[:16]
            ciphertext = enc[16:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext).decode('utf-8')
            return unpad(decrypted)
        except Exception as e:
            print("Error decrypting data:", e)
            return None

# Buat QR berisi data terenkripsi dari nomor resi
def create_resi_qr(resi="", username="", password=""):
    data_detail = {
        "resi": resi,
    }

    cipher = AESCipher(username, password)
    encrypted_data = cipher.encrypt(json.dumps(data_detail))

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(encrypted_data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    nama_file = f"resi_pengiriman_{resi}.png"
    img.save(nama_file)
    return nama_file

# Baca QR dan dekripsi isinya
def read_qr_and_decrypt(path, username, password):
    img = Image.open(path)
    decoded_objects = decode(img)

    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        cipher = AESCipher(username, password)
        decrypted = cipher.decrypt(data)
        return decrypted

# Encrypt dan decrypt manual (jika tidak lewat QR)
def encrypt_data(plaintext, username, password):
    cipher = AESCipher(username, password)
    return cipher.encrypt(plaintext)

def decrypt_data(ciphertext, username, password):
    cipher = AESCipher(username, password)
    return cipher.decrypt(ciphertext)
