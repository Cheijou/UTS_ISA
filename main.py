
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
    print()
    username = input("Username: ")
    password = input("Password: ")
    print()

    cursor.execute("SELECT * FROM tUsers WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and verify_password(password, user['password']):
        print(f"Login berhasil sebagai {user['role']}", "\n")
        return user
    else:
        print("Login gagal.", "\n")
        return None

def register():
    print()
    username = input("Username: ")
    password = encrypt_password(input("Password: "))
    role = input("Anda adalah? (kurir/pengirim): ")
    print()
    cursor.execute("INSERT INTO tUsers (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
    db.commit()
    print("Registrasi berhasil.", "\n")

def dashboard(user):
    if user['role'] == 'Pengirim':
        print("1. Cetak Resi")
        print("2. Lihat Detail Pengiriman")
        print("0. Keluar")
        pilihan = input("Pilih menu: ")
        print()
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
            print("=== Daftar Pengiriman Anda ===", "\n")
            cursor.execute("SELECT * FROM tPengiriman WHERE pengirim = %s", (user['username'],))
            all_pengiriman = cursor.fetchall()

            for i in range(0, len(all_pengiriman)):
                print((i+1), ". Pengiriman ", all_pengiriman[i]['barang'], " kepada ", all_pengiriman[i]['penerima'])
            print()
            
            pilihan = int(input("Data pengiriman mana yang ingin anda periksa? : "))
            id_pengiriman = pilihan

            cursor.execute("SELECT * FROM tPengiriman WHERE id = %s", (id_pengiriman,))
            data_pengiriman = cursor.fetchone()

            print("\n", "=== Berikut merupakan detail pengirimannya ===", "\n")

            print("Barang yang Dikirim : ", data_pengiriman['barang'])
            print("Tanggal Pengiriman : ", data_pengiriman['tanggal_pengiriman'])
            print("Pengirim : ", data_pengiriman['pengirim'])
            print("Penerima : ", data_pengiriman['penerima'])
            print("Alamat Pengirim : ", data_pengiriman['alamat_pengirim'])
            print("Alamat Tujuan : ", data_pengiriman['alamat_tujuan'])
            print("Biaya Pengiriman : ", data_pengiriman['harga_pengiriman'])
            print("Kurir yang Bertugas : ", data_pengiriman['kurir'], "\n")

            cetak = input("Cetak sebagai PDF? (ya / tidak) : ")

            if cetak == "ya":
                data_pengiriman_pdf = {
                    "Barang yang Dikirim ": data_pengiriman['barang'],
                    "Tanggal Pengiriman": data_pengiriman['tanggal_pengiriman'],
                    "Pengirim": data_pengiriman['pengirim'],
                    "Penerima": data_pengiriman['penerima'],
                    "Alamat Pengirim ": data_pengiriman['alamat_pengirim'],
                    "Alamat Tujuan": data_pengiriman['alamat_tujuan'],
                    "Biaya Pengiriman": data_pengiriman['harga_pengiriman'],
                    "Kurir yang Bertugas": data_pengiriman['kurir']
                }
                generate_resi_pdf(data_pengiriman_pdf)
                print("Data pengiriman berhasil dicetak ke file 'data_pengiriman.pdf'", "\n")
            else:
                dashboard(user)
        else:
            main()
    elif user['role'] == 'Admin':
        print("Fitur role ini belum tersedia.")
    else:
        print("Masih belum")

def main():
    while True:
        print("=== Sistem Informasi Pengiriman Barang ===")
        print("1. Login")
        print("2. Register")
        print("0. Keluar", "\n")
        pilihan = input("Pilih menu: ")
        if pilihan == '1':
            user = login()
            if user:
                print(f"Selamat datang, {user['username']} ({user['role']})")
                dashboard(user)
        elif pilihan == '2':
            register()
        elif pilihan == '0':
            break

if __name__ == '__main__':
    main()





