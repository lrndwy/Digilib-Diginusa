# 🚀 Instalasi Digilib Lokal Komputer

Selamat datang di Digilib! Panduan ini akan membantu Anda menginstal dan menjalankan Digilib dengan mudah.

## 📋 Prasyarat

Sebelum memulai, pastikan Anda telah menginstal:

- Python (versi 3.8 atau lebih baru)
- pip (manajer paket Python)
- virtualenv (opsional, tapi sangat disarankan)
- Node.js (versi 12 atau lebih tinggi) dan npm

## 🛠️ Langkah-langkah Instalasi

### 1. Clone Repositori

```bash
git clone https://github.com/Tamvan15/Digilib.git
cd Nama_Folder_Digilib
```

### 2. Buat dan Aktifkan Lingkungan Virtual

```bash
python -m venv venv
source venv/bin/activate  # Untuk Unix atau MacOS
venv\Scripts\activate  # Untuk Windows
```

### 3. Instal Dependensi

```bash
pip install -r requirements.txt
```

### 4. Atur Database

```bash
python manage.py migrate
```

### 5. Buat Superuser (Opsional)

```bash
python manage.py createsuperuser
```

### 6. Jalankan Server Pengembangan

```bash
python manage.py runserver
```

Kunjungi `http://127.0.0.1:8000/` di browser Anda untuk melihat aplikasi.

### Untuk Mengatur ke IP Komputer
```bash
python manage.py runserver 0.0.0.0:8000
```

---

Dibuat dengan ❤️ oleh Hafiz & Alif