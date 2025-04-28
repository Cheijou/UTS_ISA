
import mysql.connector
import os
from cryptography.fernet import Fernet
from utils.encryption import encrypt,verify_password, decrypt
from utils.pdf_generator import generate_resi_pdf
from utils.password_sensor import input_password
from utils.buat_resi import generate_random_resi
from utils.buat_qr import create_resi_qr, AESCipher
import tkinter as tk
from tkinter.filedialog import askopenfilename

from datetime import date

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
    password = input_password()
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
    nama_lengkap = encrypt(input("Nama Lengkap : "))
    username = input("Username: ")
    password = encrypt(input_password())
    no_telp = encrypt(input("Nomor Telpon : "))
    role = input("Anda adalah? (kurir/pengirim): ")
    print()
    cursor.execute("INSERT INTO tUsers (username, password,nama,nomor_telepon, role) VALUES (%s, %s, %s, %s, %s)", (username, password,nama_lengkap,no_telp,role))
    db.commit()
    print("Registrasi berhasil.", "\n")

def dashboard(user):
    if user['role'] == 'Pengirim':
        print("1. Kirim Barang")
        print("2. Lacak Resi")
        print("0. Keluar")
        pilihan = input("Pilih menu: ")
        print()
        if pilihan == '1':
            print("=== Buat Pengiriman ===", "\n")
            print("Silahkan masukkan data-data terkait pengiriman.")
            nama_penerima = input("Nama Penerima : ")
            barang = input("Barang yang Dikirim : ")
            alamat_pengirim = input("Alamat Pengirim : ")
            alamat_tujuan = input("Alamat Tujuan : ")
            jenis = input("Pilih Jenis Pengiriman (express/economy)) : ")
            if (jenis == "express"):
                harga_pengiriman = 20000
            else:
                harga_pengiriman = 8000
            tanggal_pengiriman = date.today()
            tanggal_pengiriman_sql = tanggal_pengiriman.isoformat()
            
            cek_resi = True
            while (cek_resi == True):
                resi = generate_random_resi()
                cursor.execute("SELECT no_resi FROM tPengiriman WHERE no_resi = %s", (resi,))
                result = cursor.fetchone()
                create_resi_qr(resi)
                if result is None:
                    cek_resi = False
            cursor.execute("INSERT INTO tPengiriman (no_resi, pengirim, penerima, barang, harga_pengiriman, alamat_pengirim, alamat_tujuan, tanggal_pengiriman) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (resi, user['username'], nama_penerima, barang, harga_pengiriman, alamat_pengirim, alamat_tujuan, tanggal_pengiriman_sql))
            print()
            print("Pengiriman Anda Tercatat, resi anda -->",resi)
            db.commit()
            
        elif pilihan == '2':
            print("=== LACAK RESI ===", "\n")
            file_path = askopenfilename()
            print()
            print("1. Manual \n2. Input QR")

            pilih_metode = input("Pilih metode pelacakan : ")
            
            if(pilih_metode == "1"):
                resi = input("Masukkan resi yang ingin anda lacak: ")
                cursor.execute("SELECT * FROM tPengiriman WHERE no_resi = %s", (resi,))
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
            elif(pilih_metode == "2"):
                print("=== Input QR Code ===\n")
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.update()
                file_path = filedialog.askopenfilename()
                print("tes")
                cipher = AESCipher.decrypt(file_path)
                cursor.execute("SELECT * FROM tPengiriman WHERE no_resi = %s", (cipher,))
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
        print("1. Lihat Pengiriman Terbaru")
        print("0. Keluar")
        pilihan = input("Pilih menu: ")
        print()

        if pilihan == "1":
            print("=== Semua Daftar Pengiriman  ===", "\n")
            cursor.execute("SELECT * FROM tPengiriman")
            all_pengiriman = cursor.fetchall()

            for i in range(0, len(all_pengiriman)):
                print((i+1), ". Pengiriman ", all_pengiriman[i]['barang'], " kepada ", all_pengiriman[i]['penerima'])
            print()
            
            pilihan = int(input("Data pengiriman mana yang ingin anda periksa? : "))
            id_pengiriman = pilihan

            cursor.execute("SELECT * FROM tPengiriman WHERE no_resi = %s", (all_pengiriman[id_pengiriman-1]["no_resi"],))
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
                generate_resi_pdf(data_pengiriman_pdf, "data_pengiriman.pdf")
                print("Data pengiriman berhasil dicetak ke file 'data_pengiriman.pdf'", "\n")
            else:
                dashboard(user)
        else:
            main()

    else:
        kurir_lanjut = True
        while kurir_lanjut == True:
            print("1. Ambil Pesanan Pengiriman")
            print("2. Cek Daftar Pesanan Pengiriman")
            print("3. Update Status Pengiriman")
            print("0. Keluar")
            pilihan = input("Pilih menu: ")
            print()
            if pilihan == '1':
                cursor.execute("SELECT * FROM tPengiriman WHERE kurir = %s", (user['username'],), " and tanggal_sampai is NULL")
                jumlah_belum_selesai= cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM tPengiriman")
                temp = cursor.fetchone()
                total_pengiriman = temp['COUNT(*)']
                cursor.execute("SELECT COUNT(*) FROM tPengiriman WHERE kurir = %s ",(user['username'],))
                temp2 = cursor.fetchone()
                pengiriman_saya = temp2['COUNT(*)']


                if jumlah_belum_selesai is None:
                    print("=== Pesanan yang dapat Diambil ===", "\n")
                    cursor.execute("SELECT * FROM tPengiriman WHERE kurir is NULL")
                    pesanan_yang_ada = cursor.fetchall()

                    for i in range(0, len(pesanan_yang_ada)):
                        print((i+1), ". Pengiriman", pesanan_yang_ada[i]['barang'], "ke", pesanan_yang_ada[i]['alamat_tujuan'])
                    print()

                    pilihan = int(input("Pesanan mana yang ingin anda ambil? : "))
                    print()
                    urutan_pengiriman = pilihan

                    resi_pengiriman = pesanan_yang_ada[urutan_pengiriman-1]['no_resi']

                    cursor.execute(
                                    "UPDATE tPengiriman SET kurir = %s WHERE no_resi = %s",
                                    (user['username'], resi_pengiriman))
                    db.commit()
                elif pengiriman_saya == total_pengiriman:
                    print('Belum ada Pesanan Pengiriman.','\n')
                else:
                    print("Harap selesaikan pesanan pengiriman yang telah anda ambil sebelumnya.", "\n")
            elif pilihan == '2':
                print("=== Daftar Pesanan Pengiriman Barang ===", "\n")
                cursor.execute("SELECT * FROM tPengiriman WHERE kurir = %s", (user['username'],))
                all_pengiriman = cursor.fetchall()

                for i in range(0, len(all_pengiriman)):
                    print((i+1), ". Pengiriman", all_pengiriman[i]['barang'], "kepada", all_pengiriman[i]['penerima'])
                    if (all_pengiriman[i]['tanggal_sampai'] is None):
                        print("Status Pengiriman: Belum Dikirim")
                    else:
                        print("Status Pengiriman: Selesai Dikirim")
                    print()
            elif pilihan == '3':
                print("=== Daftar Pesanan Pengiriman Barang ===", "\n")
                cursor.execute("SELECT * FROM tPengiriman WHERE kurir = %s", (user['username'],))
                all_pengiriman = cursor.fetchall()

                for i in range(0, len(all_pengiriman)):
                    print((i+1), ". Pengiriman", all_pengiriman[i]['barang'], "kepada", all_pengiriman[i]['penerima'])
                print()

                lanjut = True

                while lanjut == True:
                    pilihan = int(input("Data pengiriman mana yang ingin anda perbarui? : "))
                    urutan_pengiriman = pilihan

                    resi_pengiriman = all_pengiriman[urutan_pengiriman-1]['no_resi']

                    print("\n", "=== Berikut merupakan data-data yang dapat anda perbarui ===", "\n")

                    status_pengiriman = input("Status Pengiriman (Dikirim / Diterima) : ")

                    if "kirim" in status_pengiriman:
                        lokasi_barang = input("Lokasi Barang saat ini : ")
                        lanjut = False
                    elif "terima" in status_pengiriman:
                        lokasi_barang = ""
                        tgl_selesai = date.today()
                        tgl_selesai_sql = tgl_selesai.isoformat()
                        cursor.execute("UPDATE tPengiriman SET tanggal_sampai = %s WHERE no_resi = %s ",(tgl_selesai_sql, resi_pengiriman))
                        lanjut = False
                    else:
                        print("Masukkan status pengiriman dengan benar!")

                    cursor.execute("SELECT * FROM tAktivitasPengiriman ORDER BY id DESC LIMIT 1")
                    id_terakhir = cursor.fetchone()
                    
                    if lanjut == False:
                        if (id_terakhir is not None):
                            cursor.execute("INSERT INTO tAktivitasPengiriman (id, status_pengiriman, lokasi, tPengiriman_no_resi) VALUES (%s, %s, %s, %s)", (id_terakhir['id'] + 1, status_pengiriman, lokasi_barang, resi_pengiriman))
                        else:
                             cursor.execute("INSERT INTO tAktivitasPengiriman (id, status_pengiriman, lokasi, tPengiriman_no_resi) VALUES (%s, %s, %s, %s)", (1, status_pengiriman, lokasi_barang, resi_pengiriman))
                        db.commit()
                        print("\n", "Data terkait pengiriman ", all_pengiriman[urutan_pengiriman-1]['barang'], " kepada ", all_pengiriman[urutan_pengiriman-1]['penerima'], " telah selesai diperbarui", "\n")
            elif pilihan == "0":
                kurir_lanjut = False
                main()

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





