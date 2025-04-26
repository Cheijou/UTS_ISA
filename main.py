
import mysql.connector
import os
from cryptography.fernet import Fernet
from utils.encryption import encrypt_password,verify_password
from utils.pdf_generator import generate_resi_pdf
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
        print("1. Buat Pengiriman")
        pilihan = input("Pilih menu: ")
        print()

        if pilihan == "1":
            print("=== Buat Pengiriman ===", "\n")
            print("Silahkan masukkan data-data terkait pengiriman.")
            user_pengirim = input("Username Pengirim : ")
            nama_penerima = input("Nama Penerima : ")
            barang = input("Barang yang Dikirim : ")
            harga_pengiriman = input("Biaya Pengiriman : ")
            alamat_pengirim = input("Alamat Pengirim : ")
            alamat_tujuan = input("Alamat Tujuan : ")
            tanggal_pengiriman = date.today()
            tanggal_pengiriman_sql = tanggal_pengiriman.isoformat()

            cursor.execute("SELECT * FROM tPengiriman ORDER BY ID DESC LIMIT 1")
            id_terakhir = cursor.fetchone()

            cursor.execute("INSERT INTO tPengiriman (id, pengirim, penerima, barang, harga_pengiriman, alamat_pengirim, alamat_tujuan, tanggal_pengiriman) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id_terakhir['id']+1, user_pengirim, nama_penerima, barang, harga_pengiriman, alamat_pengirim, alamat_tujuan, tanggal_pengiriman_sql))
            db.commit()

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
                jumlah_pesanan = cursor.fetchone()

                if jumlah_pesanan is None:
                    print("=== Pesanan yang dapat Diambil ===", "\n")
                    cursor.execute("SELECT * FROM tPengiriman WHERE kurir is NULL")
                    pesanan_yang_ada = cursor.fetchall()

                    for i in range(0, len(pesanan_yang_ada)):
                        print((i+1), ". Pengiriman", pesanan_yang_ada[i]['barang'], "ke", pesanan_yang_ada[i]['alamat_tujuan'])
                    print()

                    pilihan = int(input("Pesanan mana yang ingin anda ambil? : "), "\n")
                    urutan_pengiriman = pilihan

                    id_pengiriman = pesanan_yang_ada[urutan_pengiriman-1]['id']

                    cursor.execute(
                                    "UPDATE tPengiriman SET kurir = %s WHERE id = %s",
                                    (user['username'], id_pengiriman))
                    db.commit()
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

                    id_pengiriman = all_pengiriman[urutan_pengiriman-1]['id']

                    print("\n", "=== Berikut merupakan data-data yang dapat anda perbarui ===", "\n")

                    status_pengiriman = input("Status Pengiriman (Dikirim / Diterima) : ")

                    if "kirim" in status_pengiriman:
                        lokasi_barang = input("Lokasi Barang saat ini : ")
                        lanjut = False
                    elif "terima" in status_pengiriman:
                        lokasi_barang = ""
                        lanjut = False
                    else:
                        print("Masukkan status pengiriman dengan benar!")

                    cursor.execute("SELECT * FROM tAktivitasPengiriman ORDER BY ID DESC LIMIT 1")
                    id_terakhir = cursor.fetchone()

                    if lanjut == False:
                        cursor.execute("INSERT INTO tAktivitasPengiriman (id, status_pengiriman, lokasi, tPengiriman_id) VALUES (%s, %s, %s, %s)", (id_terakhir['id'] + 1, status_pengiriman, lokasi_barang, id_pengiriman))
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





