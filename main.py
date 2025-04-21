
import mysql.connector
import os
from cryptography.fernet import Fernet
from utils.encryption import encrypt_password,verify_password
from utils.pdf_generator import generate_resi_pdf

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="projek_isa"
)

cursor = db.cursor(dictionary=True)
def login():
          
    username = input("Username: ")
    password = input("Password: ")

    cursor.execute("SELECT * FROM tUsers WHERE username = %s", (username,))
    user = cursor.fetchone()
    print(type(user['password']))

    if user:
        print("User ditemukan:", user['username'])
    print(user['password'])
    if user and verify_password(password, user['password']):
        print(f"Login berhasil sebagai {user['role']}")
        return user
    else:
        print("Login gagal.")
        return None

def register():
    username = input("Username: ")
    password = encrypt_password(input("Password: "))
    role = input("Anda adalah? (kurir/pengirim): ")
    cursor.execute("INSERT INTO tUsers (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
    db.commit()
    print("Registrasi berhasil.")

def dashboard(user):
    print(f"Selamat datang, {user['username']} ({user['role']})")
    if user['role'] == 'Pengirim':
        print("1. Cetak Resi")
        print("2. Lihat Detail Pengiriman")
        print("0. Keluar")
        pilihan = input("Pilih menu: ")
        if pilihan == '1':
            data = {
                "Nama Pengirim": user['username'],
                "Alamat Tujuan": "Jl. Mawar No.10",
                "Kurir": "Kurir1",
                "Status": "Dalam Perjalanan"
            }
            generate_resi_pdf(data)
            print("Resi berhasil dicetak ke file 'resi.pdf'")
        elif pilihan == '2':
            print("Nanti dulu")
    elif user['role'] == 'Admin':
        print("Fitur role ini belum tersedia.")
    else:
        print("Masih belum")

def main():
    while True:
        print("=== Sistem Informasi Pengiriman Barang ===")
        print("1. Login")
        print("2. Register")
        print("0. Keluar")
        pilihan = input("Pilih menu: ")
        if pilihan == '1':
            user = login()
            if user:
                dashboard(user)
        elif pilihan == '2':
            register()
        elif pilihan == '0':
            break

if __name__ == '__main__':
    main()





