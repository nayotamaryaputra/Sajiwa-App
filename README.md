# 🍃 Sajiwa - Sistem Manajemen Lingkungan Terpadu

Sajiwa adalah aplikasi berbasis Web (Django) yang dirancang untuk mengelola operasional kebersihan lingkungan, penjemputan sampah, dan sistem poin/reward bagi warga. Aplikasi ini menggunakan tema **Nature/Clean** yang modern dan responsif.

---

## 🚀 Cara Menjalankan Proyek (Local Setup)

Pastikan kamu sudah menginstal **Python (versi 3.10 atau terbaru)** dan **Git** di laptopmu.

### 1. Clone Repository
Buka terminal/CMD, lalu arahkan ke folder tempat kamu ingin menyimpan proyek:
```bash
git clone [https://github.com/nayotamaryaputra/Sajiwa-App.git](https://github.com/nayotamaryaputra/Sajiwa-App.git)
cd Sajiwa-App
```

### 2. Buat Virtual Environment (Opsional tapi Disarankan)
Supaya library tidak bentrok dengan proyek lain:
```bash
# Windows
python -m venv Env
Env\Scripts\activate

# macOS/Linux
python3 -m venv Env
source Env/bin/activate
```

### 3. Instal Dependencies
Instal framework Django dan library yang dibutuhkan:
```bash
pip install setuptools
pip install django
# Jika ada file requirements.txt, gunakan:
# pip install -r requirements.txt
```

### 4. Persiapan Database
Jalankan migrasi untuk membuat struktur database lokal:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Buat Akun Admin (Superuser)
Supaya kamu bisa masuk ke panel admin Django:
```bash
python manage.py createsuperuser
```
Ikuti instruksinya (isi username, email, dan password).

### 6. Jalankan Server
```bash
python manage.py runserver
```

🛠️ Fitur Utama
Sajiwa Pay: Sistem saldo untuk transaksi hasil sampah.

Penjemputan: Warga bisa request jemput sampah, kurir bisa update berat real.

Sistem Poin (XP): Leveling system (Bronze, Silver, Gold) berdasarkan kontribusi warga.

Responsive Design: Tampilan elegan menggunakan Tailwind CSS & Alpine.js.

Riwayat Aktivitas: Log transparan untuk keuangan dan operasional.

📁 Struktur Folder Utama
Sajiwa/ - Folder inti Django (settings, urls).

templates/ - Berkas HTML (base, login, pengguna, jemput, riwayat).

static/ - Berkas CSS, Gambar, dan JS.

db.sqlite3 - Database lokal (jangan di-push ke produksi).

📝 Catatan untuk Pengembang
Jika kamu melakukan perubahan pada model database:

Jalankan python manage.py makemigrations

Jalankan python manage.py migrate

🤝 Kontribusi
Jika ingin berkontribusi:

Fork repository ini.

Buat branch baru (git checkout -b fitur-baru).

Commit perubahanmu (git commit -m 'Menambah fitur X').

Push ke branch (git push origin fitur-baru).

Buat Pull Request.
