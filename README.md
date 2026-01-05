# Web OCR Image to Text

## Deskripsi
Web OCR Image to Text adalah aplikasi web sederhana berbasis **Python dan Flask** yang berfungsi untuk mengekstrak teks dari gambar menggunakan teknologi **Optical Character Recognition (OCR)**.  
Pengguna dapat mengunggah gambar yang berisi teks, kemudian sistem akan memproses dan menampilkan hasil teks yang dapat disalin.

Aplikasi ini dibuat sebagai **proyek tugas kuliah** untuk memahami penerapan OCR dalam web application.

---

## Fitur Aplikasi
- Upload gambar berisi teks (JPG / PNG)
- Proses OCR untuk membaca teks dari gambar
- Menampilkan hasil teks di halaman web
- Teks hasil OCR dapat disalin
- Validasi file sederhana
- Aplikasi satu halaman (single page)

---

## Teknologi yang Digunakan
- Python 3
- Flask
- pytesseract
- Pillow / OpenCV
- HTML & CSS

---

## Alur Kerja Sistem
1. Pengguna mengunggah gambar melalui halaman web.
2. Flask menerima file gambar dari pengguna.
3. Gambar diproses menggunakan library OCR (pytesseract).
4. Sistem mengekstrak teks dari gambar.
5. Hasil teks dikirim kembali ke frontend dan ditampilkan.

---

## Struktur Folder
project/
│
├── app.py
├── requirements.txt
├── static/
│ └── css/
│ └── style.css
├── templates/
│ └── index.html
└── uploads/


---

## Cara Menjalankan Aplikasi

### 1. Install Dependency
```bash
pip install -r requirements.txt

#JALANKAN APLIKASI
python app.py


#AKSES APLIKASI
http://127.0.0.1:5000

## Cara Penggunaan

1. Buka aplikasi melalui browser.

2. Unggah gambar yang berisi teks.

3. Klik tombol proses.

4. Teks hasil OCR akan ditampilkan.

5. Salin teks sesuai kebutuhan.

## Batasan Aplikasi

1. Akurasi OCR tergantung kualitas gambar.

2. Gambar buram atau teks kecil dapat menurunkan hasil.

3. Aplikasi tidak menggunakan database.

4. Fokus aplikasi adalah demonstrasi OCR, bukan sistem produksi.

## Pengembangan Selanjutnya

1. Preprocessing gambar untuk meningkatkan akurasi OCR

2. Dukungan multi-bahasa

3. Upload file PDF

4. Deployment ke server cloud