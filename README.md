
![MahesaVault](https://readme-typing-svg.demolab.com?font=Fira+Code&size=26&duration=3000&pause=1000&color=00CDFF&width=850&lines=%F0%9F%94%92+MahesaVault+-+The+Dual-Protocol+Secure+Vault.;Cryptography+And+Steganography+Tools+.)

## 📌 Deskripsi Proyek
[README.md](https://github.com/user-attachments/files/28848621/README.md)
**MahesaVault** adalah platform keamanan data terpadu berbasis web yang menggabungkan dua protokol keamanan:

| Modul | Teknik | Fungsi |
|-------|--------|--------|
| 🕵️ **Steganografi** | Dual-Variant LSB (Sequential + Random) + XOR | Menyembunyikan pesan rahasia di dalam gambar PNG |
| 🔒 **Kriptografi** | Classical Cipher + Modern Cipher (AES-256 / RSA) | Mengenkripsi pesan agar tidak terbaca |

### 💡 Ide Inti: "Double-Lock Architecture"

```
[Pesan Asli]
     ↓ LAYER 1: Kriptografi
[Ciphertext (terenkripsi AES-256)]
     ↓ LAYER 2: Steganografi LSB
[Gambar PNG biasa — tidak mencurigakan]
     ↓ Kirim via WhatsApp / Google Drive
[Penerima: Ekstrak LSB → Dekripsi AES]
[Pesan Asli diterima] ✅
```

Bahkan jika gambar bocor → penyerang tetap perlu **dua kunci** berbeda.
Bahkan jika kunci kriptografi diketahui → penyerang harus tahu ada steganografi dulu.

---

## 🎯 Fitur Utama

### Modul Steganografi
- ✅ **Sequential LSB**: Penyisipan bit secara urut dari pixel (0,0)
- ✅ **Random LSB**: Posisi pixel diacak menggunakan PRNG + seed dari password
- ✅ **XOR Pre-Encryption**: Pesan dienkripsi XOR sebelum disisipkan (kombinasi)
- ✅ **Quality Metrics**: Kalkulasi PSNR, MSE, dan SSIM otomatis
- ✅ **Steganalisis Histogram**: Visualisasi perbandingan RGB sebelum/sesudah
- ✅ **Capacity Calculator**: Hitung kapasitas maksimal karakter per gambar
- ✅ **Bit-Plane Slicer**: Visualisasi 8 layer bit gambar untuk analisis forensik
- ✅ **Error Map Generator**: Peta pixel yang berubah (visualisasi MSE)

### Modul Kriptografi
- ✅ **Classical Cipher** (pilih 1): Caesar / Vigenere / Playfair / Hill / Affine
- ✅ **Modern Cipher** (pilih 1): AES-256 / RSA / DES / 3DES / Blowfish / ChaCha20
- ✅ **Key Generator**: Generate pasangan kunci RSA atau AES key secara otomatis
- ✅ **Analisis Matematis**: Tampilkan step-by-step perhitungan cipher klasik vs modern
- ✅ **Perbandingan Keamanan**: Tabel komparatif classical vs modern + penjelasan matematis
- ✅ **Digital Signature (Bonus)**: Tanda tangan digital menggunakan RSA

### Mode Kombinasi (Eksklusif MahesaVault)
- ✅ **Encrypt-then-Hide**: AES/RSA → LSB Steganografi dalam satu workflow
- ✅ **Extract-then-Decrypt**: LSB Extraction → Dekripsi otomatis
- ✅ **Security Report**: Laporan lengkap keamanan berlapis untuk dokumentasi akademis

---

## 🗂️ Struktur Folder

```
mahesavault/
├── app.py                    # Entry point Streamlit
├── requirements.txt          # Dependencies
├── README.md                 # File ini
│
├── modules/
│   ├── steganography/
│   │   ├── lsb_sequential.py     # LSB Sequential embed/extract
│   │   ├── lsb_random.py         # LSB Random (PRNG) embed/extract
│   │   ├── xor_cipher.py         # XOR pre-encryption
│   │   ├── quality_metrics.py    # PSNR, MSE, SSIM
│   │   ├── steganalysis.py       # Histogram + Bit-plane analysis
│   │   └── capacity.py           # Capacity calculator
│   │
│   ├── cryptography/
│   │   ├── classical/
│   │   │   ├── caesar.py
│   │   │   ├── vigenere.py
│   │   │   ├── playfair.py
│   │   │   ├── hill.py
│   │   │   └── affine.py
│   │   ├── modern/
│   │   │   ├── aes_cipher.py     # AES-256 CBC mode
│   │   │   ├── rsa_cipher.py     # RSA 2048-bit
│   │   │   ├── des_cipher.py
│   │   │   └── chacha20.py
│   │   ├── key_generator.py
│   │   ├── digital_signature.py  # RSA digital signature
│   │   └── math_visualizer.py    # Tampilkan perhitungan step-by-step
│   │
│   └── combined/
│       ├── dual_lock.py          # Encrypt-then-Hide workflow
│       └── security_report.py    # Generate laporan PDF/text
│
├── ui/
│   ├── home.py                   # Landing page dengan animasi
│   ├── stego_ui.py               # UI modul steganografi
│   ├── crypto_ui.py              # UI modul kriptografi
│   ├── combined_ui.py            # UI mode dual-lock
│   └── components/
│       ├── metric_card.py        # Komponen kartu metrik
│       └── histogram_plot.py     # Komponen histogram
│
├── assets/
│   ├── sample_images/            # Contoh gambar cover
│   └── styles/
│       └── custom.css            # CSS tambahan untuk Streamlit

```

---

## 🛠️ Instalasi & Menjalankan

```bash
# 1. Clone / download project
git clone https://github.com/yourusername/mahesavault.git
cd mahesavault

# 2. Buat virtual environment (opsional tapi recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan aplikasi
streamlit run app.py
```

### requirements.txt
```
streamlit>=1.32.0
opencv-python>=4.9.0
numpy>=1.26.0
matplotlib>=3.8.0
scikit-image>=0.22.0
cryptography>=42.0.0
Pillow>=10.2.0
pandas>=2.2.0
reportlab>=4.1.0
```

---

## 📊 Perbandingan Teknis (untuk Laporan)

### Steganografi: Sequential vs Random LSB

| Parameter | Sequential LSB | Random LSB |
|-----------|---------------|------------|
| Visibilitas | Tidak terlihat | Tidak terlihat |
| PSNR | ~50 dB | ~52 dB |
| Keamanan | Rendah (tanpa kunci) | Tinggi (butuh seed/key) |
| Distribusi perubahan | Menumpuk di awal gambar | Tersebar merata |
| Resistensi steganalisis | Lemah | Kuat |

### Kriptografi: Classical vs Modern

| Parameter | Classical (e.g. Vigenere) | Modern (e.g. AES-256) |
|-----------|--------------------------|----------------------|
| Key space | Kecil (26^n) | Sangat besar (2^256) |
| Brute force | Mungkin (feasible) | Tidak feasible |
| Known-plaintext attack | Rentan | Tahan |
| Perhitungan | Sederhana / manual | Kompleks / komputer |
| Standar industri | Tidak | Ya (NIST standard) |

---

## 👥 Tim / Pembuat

Rafi Mahesa Adyaksa
---

## 📚 Referensi

**Literatur & Jurnal Akademis:**
* Cheddad, A., et al. (2010). *Digital Image Steganography: Survey and Analysis of Current Methods*. Signal Processing.
* Cox, I. J., Miller, M. L., Bloom, J. A., Fridrich, J., & Kalker, T. (2007). *Digital Watermarking and Steganography* (2nd ed.). Morgan Kaufmann.
* Schneier, B. (2015). *Applied Cryptography: Protocols, Algorithms, and Source Code in C* (20th Anniversary Edition). John Wiley & Sons.
* Stallings, W. (2020). *Cryptography and Network Security: Principles and Practice* (8th ed.). Pearson.

**Dokumentasi Teknologi:**
* [Python 3.11 Documentation](https://docs.python.org/3/)
* [Streamlit Documentation](https://docs.streamlit.io/)
* [OpenCV Documentation](https://docs.opencv.org/)
* [Python Cryptography Package](https://cryptography.io/en/latest/)

---

## 📝 Lisensi

Proyek ini dibuat untuk keperluan akademis UAS semester genap 2026/2027.
