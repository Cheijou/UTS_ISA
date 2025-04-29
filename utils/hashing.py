import bcrypt

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()  # Ubah hasil hash ke string untuk disimpan

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception as e:
        print("Verifikasi gagal:", e)
        return False
