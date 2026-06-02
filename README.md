```markdown
# Almanak (المنك / ꦄꦭ꧀ꦩꦤꦏ꧀)

A comprehensive multi-system calendar application designed to bridge traditional Javanese timekeeping with major global Islamic Hijri calendar methods. This project integrates complex historical, astronomical, and mathematical algorithms into a modern, single unified application.

---

## 📌 Latar Belakang
Aplikasi ini dibuat untuk merangkum **Kalender Jawa Sultan Agungan** dan *petung jawa* (populer dengan sebutan **Primbon**), yang kemudian dipadukan secara harmonis dengan **Kalender Hijriah**. Untuk kalender Islam, sistem menyediakan simulasi dan konversi berdasarkan 3 metode kontemporer utama:
1. **Hisab Rukyah** (Kriteria MABIMS yang digunakan oleh Nahdlatul Ulama / NU)
2. **Hisab Wujudul Hilal** (Digunakan oleh Persyarikatan Muhammadiyah)
3. **Kalender Hijriah Global Tunggal (KHGT)** (Keputusan terbaru Persyarikatan Muhammadiyah untuk kalender global)

---

## ⚙️ Skema & Metode Penghitungan

### 1. Kalender Jawa Sultan Agungan
Sistem ini menggunakan algoritma berbasis jangkar sejarah penetapan kalender oleh Sultan Agung yang dimulai pada **Jumat Legi, 1 Sura tahun Alip 1555 J** (setara dengan **1 Muharram 1043 H** atau **8 Juli 1633 M**). Peristiwa inisiasi historis ini tercatat dalam *Windu Kuntara Lambang Kulawu*.

Komponen perhitungan penanggalan meliputi:
* **Pananggalan:** Kronologis murni perputaran bulan.
* **Periode Musim:** Penanda penanggalan agraris alami (**Pranata Mangsa**).
* **Pawukon:** Matriks siklus spiritual 210 hari (Wuku).
* **Siklus Wara:** Matematika sisa pembagi untuk penentuan pasaran (Pancawara, Sadwara, Saptawara, dll).
* **Karakteristik Hari:** Mesin logika yang menghasilkan output ramalan/watak berdasarkan kombinasi hari.

### 2. Kalender Hijriah Rukyatul Hilal (MABIMS)
Mengombinasikan metode perhitungan matematis (hisab) sebagai panduan ilmiah awal, dan pengamatan fisik hilal (*rukyatul hilal*) di lapangan sebagai dasar keputusan resmi (*ikhbar*).
* **Kriteria Imkanur Rukyat:** Hilal dinyatakan mungkin terlihat (masuk bulan baru) apabila saat matahari terbenam memenuhi parameter:
    * **Tinggi Hilal Minimal:** 3° di atas ufuk.
    * **Elongasi Minimal:** 6.4° (jarak sudut antara Bulan dan Matahari).

### 3. Kalender Hijriah Hisab Hakiki Wujudul Hilal
Metode penentuan awal bulan Kamariah berdasarkan posisi geometris-astronomis murni tanpa mensyaratkan keterlihatan mata telanjang. Bulan baru dinyatakan masuk jika 3 kriteria astronomis ini terpenuhi secara berurutan:
1.  **Sudah Terjadi Ijtimak (Konjungsi):** Bumi, Bulan, dan Matahari berada dalam satu garis bujur astronomis yang sama.
2.  **Ijtimak Terjadi Sebelum Matahari Terbenam:** Proses konjungsi selesai sebelum waktu magrib di hari ke-29 bulan berjalan.
3.  **Bulan Berada di Atas Ufuk:** Pada saat matahari terbenam, piringan atas Bulan sudah berada di atas garis cakrawala (tinggi hilal > 0°). Walaupun posisinya hanya 0.1°, bulan baru dianggap sudah berganti.

### 4. Kalender Hijriah Global Tunggal (KHGT)
Mengadopsi prinsip kesatuan *mathla‘*, menganggap seluruh dunia sebagai satu kesatuan wilayah hukum terpadu.
* **Parameter Kalender Global (PKG 1):** Bulan baru dimulai serentak di seluruh dunia jika parameter terpenuhi di mana pun di permukaan bumi sebelum pukul 24.00 UT, dengan syarat:
    * **Tinggi Bulan:** ≥ 5°
    * **Elongasi:** ≥ 8°
* **Mekanisme Penyelarasan (PKG 2):** Jika syarat PKG 1 belum terpenuhi, pelacakan dilanjutkan setelah pukul 24.00 UT di wilayah daratan Benua Amerika, atau sebelum waktu fajar di Selandia Baru untuk memastikan sinkronisasi kalender global tunggal.

---

## 💻 Lingkungan Pengembangan (Environment) & Struktur Kode

Aplikasi ini dikembangkan menggunakan bahasa pemrograman **Python** dengan arsitektur modular terpisah untuk tiap logika sistem penanggalan:

```text
├── app.py                  # Aplikasi utama / Entry point (Flask web controller)
├── kalenderjawa.py         # Logika & algoritma Kalender Jawa, Wuku, Pranatamangsa
├── rukyahhilal.py          # Modul perhitungan Imkanur Rukyat (Kriteria MABIMS)
├── wujudulhilal.py         # Modul perhitungan Hisab Wujudul Hilal
└── KHGT.py                 # Modul parameter Kalender Hijriah Global Tunggal
