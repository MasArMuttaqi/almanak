
from datetime import date, datetime,timedelta

# ============================================================
# 1. KONFIGURASI EPOCH
# ============================================================

# Epoch model rekonstruksi Kala Candra Sunda
# 1 Kartika 1921 Caka Sunda = 11 Desember 1999 Masehi

# TANGGAL_EPOCH_MASEHI = date(1999, 12, 11)
"""
CATATAN REKONSTRUKSI EPOCH

Epoch kerja:
1 Kartika 1921 Caka Sunda = 24 Agustus 1985 Masehi.

Penetapan ini diperoleh melalui kalibrasi aritmetis
terhadap data pembanding tahun 1959.

Kecocokan tambahan:
- 1 Kartika 1948 = 4 November 2011.
- 1 Maret 2012 = 1 Palguna 1948.
- 1 November 2026 = 13s Setra 1963.

Status:
Epoch kerja model, belum merupakan pembuktian
historis final.
"""
TANGGAL_EPOCH_MASEHI = date(1985, 8, 24)

TAHUN_EPOCH = 1921
BULAN_EPOCH = 1
TANGGAL_EPOCH = 1


# ============================================================
# 2. NAMA DAN PANJANG BULAN
# ============================================================

BULAN_CAKA = [
    "Kartika",
    "Margasira",
    "Posya",
    "Maga",
    "Palguna",
    "Setra",
    "Wesaka",
    "Yesta",
    "Asada",
    "Srawana",
    "Badra",
    "Asuji",
]

# Tahun Wastu = 354 hari
PANJANG_BULAN_WASTU = [
    30, 29, 30, 29, 30, 29,
    30, 29, 30, 29, 30, 29
]

# Tahun Wuntu = 355 hari
PANJANG_BULAN_WUNTU = [
    30, 29, 30, 29, 30, 29,
    30, 29, 30, 29, 30, 30
]



# ============================================================
# 3. SIKLUS DEWATAUN (8 TAHUN)
# ============================================================

DEWATAUN = [
    ("Kebo", "Wastu", 354),
    ("Monyet", "Wuntu", 355),
    ("Hurang Tembey", "Wastu", 354),
    ("Kalabang", "Wastu", 354),
    ("Embe", "Wuntu", 355),
    ("Keuyeup", "Wastu", 354),
    ("Cacing", "Wastu", 354),
    ("Hurang Tutug", "Wuntu", 355),
]

PANJANG_WINDU = sum(item[2] for item in DEWATAUN)

assert PANJANG_WINDU == 2835


def dewataun(tahun):
    """Menentukan Dewataun berdasarkan tahun Caka."""

    indeks = (tahun - TAHUN_EPOCH) % 8

    nama, jenis, jumlah_hari = DEWATAUN[indeks]

    return {
        "nama": nama,
        "jenis": jenis,
        "panjang_normal": jumlah_hari,
        "indeks": indeks + 1,
    }


# ============================================================
# 9. SIKLUS WINDU KALA CANDRA SUNDA
# ============================================================

NAMA_WINDU = [
    "Adi",
    "Kuntara",
    "Sangara",
    "Sancaya",
]

PANJANG_WINDU_NORMAL = 8
JUMLAH_WINDU_TUNGGUL = 15

assert len(NAMA_WINDU) == 4


def windu(tahun):
    """
    Menentukan informasi Windu Kala Candra Sunda.

    Ketentuan:
    - Satu windu terdiri dari 8 tahun.
    - Nama windu: Adi, Kuntara, Sangara, Sancaya.
    - Nama windu berulang setiap 4 windu.
    - Satu Tunggul Taun terdiri dari 15 windu.
    - Tahun ke-120 merupakan tahun pendek pengecualian.

    Acuan:
    - Tahun Caka 1 = Windu Adi.
    - Tahun Caka 1921 = Windu Adi.
    """

    if not isinstance(tahun, int) or isinstance(tahun, bool):
        raise TypeError("Tahun harus berupa bilangan bulat.")

    if tahun < 1:
        raise ValueError("Tahun Caka harus minimal 1.")

    # --------------------------------------------------------
    # A. NOMOR WINDU GLOBAL
    # --------------------------------------------------------

    nomor_windu = ((tahun - 1) // 8) + 1

    tahun_ke_windu = ((tahun - 1) % 8) + 1

    indeks_windu = (nomor_windu - 1) % 4

    nama_windu = NAMA_WINDU[indeks_windu]

    # --------------------------------------------------------
    # B. POSISI DALAM TUNGGUL TAUN
    # --------------------------------------------------------

    info_tunggul = tunggul_taun(tahun)

    posisi_tunggul = info_tunggul["posisi"]

    nomor_windu_tunggul = (
        (posisi_tunggul - 1) // 8
    ) + 1

    tahun_ke_windu_tunggul = (
        (posisi_tunggul - 1) % 8
    ) + 1

    # --------------------------------------------------------
    # C. RENTANG TAHUN DALAM WINDU
    # --------------------------------------------------------

    tahun_awal_windu = (
        tahun - tahun_ke_windu + 1
    )

    tahun_akhir_windu = (
        tahun_awal_windu + 7
    )

    # --------------------------------------------------------
    # D. AKUMULASI HARI WINDU
    # --------------------------------------------------------

    jumlah_hari = sum(
        panjang_tahun(th)
        for th in range(
            tahun_awal_windu,
            tahun_akhir_windu + 1
        )
    )

    # --------------------------------------------------------
    # E. INFORMASI TAHUN DALAM WINDU
    # --------------------------------------------------------

    info_dewataun = dewataun(tahun)

    panjang_tahun_ini = panjang_tahun(tahun)

    # --------------------------------------------------------
    # F. STATUS PENGECUALIAN
    # --------------------------------------------------------

    tahun_pengecualian = (
        info_tunggul["posisi"] == 120
    )

    # --------------------------------------------------------
    # G. HASIL
    # --------------------------------------------------------

    return {
        "nomor": nomor_windu,
        "nama": nama_windu,
        "indeks": indeks_windu + 1,

        "tahun_awal": tahun_awal_windu,
        "tahun_akhir": tahun_akhir_windu,

        "tahun_ke": tahun_ke_windu,

        "nomor_tunggul": info_tunggul["nomor"],
        "windu_ke_tunggul": nomor_windu_tunggul,
        "tahun_ke_tunggul_windu": tahun_ke_windu_tunggul,

        "jumlah_tahun": 8,
        "panjang_normal": PANJANG_WINDU_NORMAL,
        "jumlah_hari": jumlah_hari,

        "tahun_caka": tahun,
        "dewataun": info_dewataun["nama"],
        "panjang_tahun": panjang_tahun_ini,

        "pengecualian_tunggul": tahun_pengecualian,
    }
# ============================================================
# 4. SIKLUS TUNGGUL TAUN (120 TAHUN)
# ============================================================

PANJANG_TUNGGUL_TAUN = 120

PANJANG_TUNGGUL = (
    15 * PANJANG_WINDU - 1
)

assert PANJANG_TUNGGUL == 42524


def tunggul_taun(tahun):
    """
    Menentukan posisi tahun dalam siklus Tunggul Taun.

    Tunggul Taun ke-17:
        1921–2040 Caka
        Indung Poe: Sabtu Keliwon
        Tahun 2040: tahun pendek pengecualian.
    """

    if not isinstance(tahun, int) or tahun < 1:
        raise ValueError(
            "Tahun Caka harus bilangan bulat >= 1."
        )

    nomor = ((tahun - 1) // 120) + 1

    tahun_awal = ((nomor - 1) * 120) + 1
    tahun_akhir = nomor * 120

    posisi = tahun - tahun_awal + 1

    windu_ke = ((posisi - 1) // 8) + 1
    tahun_ke_windu = ((posisi - 1) % 8) + 1

    pengecualian = posisi == 120

    return {
        "nomor": nomor,
        "tahun_awal": tahun_awal,
        "tahun_akhir": tahun_akhir,
        "posisi": posisi,
        "windu_ke": windu_ke,
        "tahun_ke_windu": tahun_ke_windu,
        "pengecualian": pengecualian,
        "panjang_tunggul": PANJANG_TUNGGUL,
    }


# ============================================================
# 5. MENENTUKAN PANJANG TAHUN
# ============================================================

def panjang_tahun(tahun):
    """Menentukan panjang tahun Caka Sunda."""

    info = tunggul_taun(tahun)

    # Tahun ke-120 dalam satu Tunggul Taun
    if info["pengecualian"]:
        return 354

    return dewataun(tahun)["panjang_normal"]


import unicodedata


# ============================================================
# DAFTAR BULAN KALA CANDRA SUNDA
# ============================================================

BULAN_CANDRA = [
    "Kartika",
    "Margasira",
    "Posya",
    "Maga",
    "Palguna",
    "Sétra",
    "Wesaka",
    "Yesta",
    "Asada",
    "Srawana",
    "Badra",
    "Asuji",
]

# Panjang 11 bulan pertama.
# Bulan Asuji dihitung berdasarkan panjang aktual tahun.
PANJANG_BULAN_CANDRA = [
    30, 29, 30, 29, 30, 29,
    30, 29, 30, 29, 30,
]


# ============================================================
# NORMALISASI NAMA BULAN
# ============================================================

def normalisasi_bulan(bulan):
    """
    Normalisasi nama atau nomor bulan Kala Candra Sunda.

    Hasil nomor bulan:
    Kartika   = 1
    Margasira = 2
    ...
    Asuji     = 12
    """

    if isinstance(bulan, int):
        if 1 <= bulan <= 12:
            return bulan

        raise ValueError(
            f"Nomor bulan tidak valid: {bulan}"
        )

    nama_bulan = [
        "kartika",
        "margasira",
        "posya",
        "maga",
        "palguna",
        "setra",
        "wesaka",
        "yesta",
        "asada",
        "srawana",
        "badra",
        "asuji",
    ]

    nama = str(bulan).strip().lower()

    if nama not in nama_bulan:
        raise ValueError(
            f"Nama bulan tidak dikenal: {bulan}"
        )

    return nama_bulan.index(nama) + 1


# ============================================================
# PANJANG BULAN KALA CANDRA
# ============================================================

def panjang_bulan_candra(tahun, bulan):
    """
    Menghasilkan panjang bulan berdasarkan tahun Caka Sunda.

    Asuji dihitung dari panjang aktual tahun sehingga
    pengecualian Tunggul Taun ikut diperhitungkan.
    """

    indeks_bulan = normalisasi_bulan(bulan)

    if indeks_bulan < 11:
        return PANJANG_BULAN_CANDRA[indeks_bulan]

    # Asuji = panjang tahun aktual - jumlah 11 bulan pertama.
    return (
        panjang_tahun(tahun)
        - sum(PANJANG_BULAN_CANDRA)
    )


# ============================================================
# HITUNG HARI KE DALAM TAHUN
# ============================================================
def hitung_hari_ke_tahun(tahun, bulan, tanggal):
    """
    Menghitung jumlah hari sejak 1 Kartika.
    1 Kartika = 0.
    """

    nomor_bulan = normalisasi_bulan(bulan)

    maksimum = panjang_bulan(tahun, nomor_bulan)

    if not 1 <= tanggal <= maksimum:
        raise ValueError(
            f"Tanggal {tanggal} tidak valid "
            f"untuk bulan {bulan} tahun {tahun}"
        )

    jumlah_hari = sum(
        panjang_bulan(tahun, nomor)
        for nomor in range(1, nomor_bulan)
    )

    return jumlah_hari + tanggal - 1

# ============================================================
# 6. MENENTUKAN PANJANG BULAN
# ============================================================

def panjang_bulan(tahun, bulan):
    """
    Mengembalikan jumlah hari dalam bulan Kala Candra Sunda.

    Wastu = 354 hari
    Wuntu = 355 hari

    Mengikuti panjang tahun aktual, termasuk
    pengecualian Tunggul Taun.
    """

    if not 1 <= bulan <= 12:
        raise ValueError(f"Nomor bulan tidak valid: {bulan}")

    if panjang_tahun(tahun) == 355:
        daftar_bulan = PANJANG_BULAN_WUNTU
    else:
        daftar_bulan = PANJANG_BULAN_WASTU

    return daftar_bulan[bulan - 1]


# ============================================================
# 7. AKUMULASI HARI SEBELUM TAHUN
# ============================================================

def jumlah_hari_sebelum_tahun(tahun):
    """
    Menghitung selisih hari dari awal tahun epoch.
    """

    total = 0

    if tahun > TAHUN_EPOCH:
        for th in range(TAHUN_EPOCH, tahun):
            total += panjang_tahun(th)

    elif tahun < TAHUN_EPOCH:
        for th in range(tahun, TAHUN_EPOCH):
            total -= panjang_tahun(th)

    return total


# ============================================================
# 8. AKUMULASI HARI SEBELUM BULAN
# ============================================================

def jumlah_hari_sebelum_bulan(tahun, bulan):
    """Menghitung jumlah hari dari awal tahun sampai awal bulan."""

    if not isinstance(bulan, int) or not 1 <= bulan <= 12:
        raise ValueError("Nomor bulan harus bilangan 1 sampai 12.")

    return sum(
        panjang_bulan(tahun, bln)
        for bln in range(1, bulan)
    )

# ============================================================
# 8A. INDUNG POE
# ============================================================
HARI_SUNDA = [
    "Senin",
    "Selasa",
    "Rabu",
    "Kamis",
    "Jumat",
    "Sabtu",
    "Minggu",
]

PASARAN_SUNDA = [
    "Manis",
    "Pahing",
    "Pon",
    "Wage",
    "Keliwon",
]

# ============================================================
# PEMETAAN INDUNG POE KE SAPTAWARA
# ============================================================

INDUNG_POE_KE_SAPTAWARA = {
    "Minggu": "Dite",
    "Senin": "Soma",
    "Selasa": "Anggara",
    "Rabu": "Buda",
    "Kamis": "Respati",
    "Jumat": "Sukra",
    "Sabtu": "Tumpek",
}

# Alias nama Saptawara
SAPTAWARA_ALIAS = {
    "Radite": "Dite",
}

SAPTAWARA = [
    "Dite",
    "Soma",
    "Anggara",
    "Buda",
    "Respati",
    "Sukra",
    "Tumpek",
]

HARI_MASEHI_KE_SUNDA = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu",
}

# Urutan Pancawara
PANCAWARA = [
    "Manis",
    "Pahing",
    "Pon",
    "Wage",
    "Kaliwon",
]
# Jangkar Indung Poe
TAHUN_JANGKAR_INDUNG_POE = 1921

INDEKS_HARI_JANGKAR = HARI_SUNDA.index("Sabtu")
INDEKS_PASARAN_JANGKAR = PASARAN_SUNDA.index("Keliwon")


def hitung_indung_poe(tahun):
    """
    Menghitung Indung Poe pada awal tahun Caka Sunda.

    Jangkar:
        1 Kartika 1921 = Sabtu Keliwon

    Perhitungan:
        Hari    = jumlah hari modulo 7
        Pasaran = jumlah hari modulo 5

    Panjang tahun menggunakan fungsi panjang_tahun()
    yang sudah memperhitungkan pengecualian Tunggul Taun.
    """

    if not isinstance(tahun, int):
        raise TypeError("Tahun harus berupa bilangan integer.")

    if tahun < 1:
        raise ValueError("Tahun Caka Sunda harus lebih besar dari 0.")

    tahun_jangkar = TAHUN_JANGKAR_INDUNG_POE

    # Menghitung jumlah hari dari tahun jangkar
    # menuju awal tahun yang dicari.
    if tahun > tahun_jangkar:
        jumlah_hari = sum(
            panjang_tahun(t)
            for t in range(tahun_jangkar, tahun)
        )

    elif tahun < tahun_jangkar:
        jumlah_hari = -sum(
            panjang_tahun(t)
            for t in range(tahun, tahun_jangkar)
        )

    else:
        jumlah_hari = 0

    # Menghitung indeks hari dan pasaran.
    indeks_hari = (
        INDEKS_HARI_JANGKAR + jumlah_hari
    ) % 7

    indeks_pasaran = (
        INDEKS_PASARAN_JANGKAR + jumlah_hari
    ) % 5

    return {
        "tahun": tahun,
        "hari": HARI_SUNDA[indeks_hari],
        "pasaran": PASARAN_SUNDA[indeks_pasaran],
        "indung_poe": (
            f"{HARI_SUNDA[indeks_hari]} "
            f"{PASARAN_SUNDA[indeks_pasaran]}"
        ),
        "jumlah_hari_dari_jangkar": jumlah_hari,
    }

def konversi_indung_poe_ke_saptawara(hari):
    """
    Mengonversi nama hari Indung Poe
    menjadi nama Saptawara Sunda.
    """

    if not isinstance(hari, str):
        raise TypeError("Hari harus berupa string.")

    hari = hari.strip().capitalize()

    try:
        return INDUNG_POE_KE_SAPTAWARA[hari]

    except KeyError:
        raise ValueError(
            f"Nama hari Indung Poe tidak dikenal: {hari}"
        )

def hitung_saptawara_caka(tahun, bulan, tanggal):
    indung_poe = hitung_indung_poe(tahun)

    hari_awal = indung_poe["hari"]

    hari_ke_tahun = hitung_hari_ke_tahun(
        tahun,
        bulan,
        tanggal
    )

    indeks_awal = HARI_SUNDA.index(hari_awal)

    indeks_hari = (
        indeks_awal + hari_ke_tahun
    ) % 7

    hari_sunda = HARI_SUNDA[indeks_hari]

    return {
        "hari": INDUNG_POE_KE_SAPTAWARA[hari_sunda],
        "index": indeks_hari
    }


def hitung_pancawara_caka(tahun, bulan, tanggal):
    """
    Menghitung Pancawara berdasarkan Indung Poe
    pada 1 Kartika tahun yang bersangkutan.
    """

    indung_poe = hitung_indung_poe(tahun)

    pasaran_awal = indung_poe["pasaran"]
    selisih_hari = hitung_hari_ke_tahun(
        tahun, bulan, tanggal
    )

    if pasaran_awal not in PASARAN_SUNDA:
        raise ValueError(
            f"Nama pasaran Indung Poe tidak dikenal: {pasaran_awal}"
        )

    indeks_awal = PASARAN_SUNDA.index(pasaran_awal)

    indeks_pasaran = (
        indeks_awal + selisih_hari
    ) % 5

    return {
        "nama": PANCAWARA[indeks_pasaran],
        "index": indeks_pasaran
    }




# ============================================================
# SADWARA
# ============================================================

SADWARA = [
    "Tungleh",
    "Ariang",
    "Urukung",
    "Paniron",
    "Was",
    "Maulu",
]


# Variasi penulisan dari sumber
SADWARA_ALIAS = {
    "tungle": "Tungleh",
    "tungleh": "Tungleh",

    "aryang": "Ariang",
    "ariang": "Ariang",
    "hariyang": "Ariang",

    "wurukung": "Urukung",
    "urukung": "Urukung",

    "paniron": "Paniron",

    "uwas": "Was",
    "was": "Was",

    "mawulu": "Maulu",
    "maulu": "Maulu",
}


# ============================================================
# JANGKAR SADWARA
# ============================================================

TANGGAL_JANGKAR_SADWARA = date(2025, 4, 26)

SADWARA_JANGKAR = "Paniron"


# ============================================================
# NORMALISASI NAMA SADWARA
# ============================================================

def normalisasi_sadwara(nama):
    nama_normal = nama.strip().lower()

    try:
        return SADWARA_ALIAS[nama_normal]
    except KeyError:
        raise ValueError(
            f"Nama Sadwara tidak dikenal: {nama}"
        )


# ============================================================
# HITUNG SADWARA
# ============================================================

def hitung_sadwara(tanggal):
    """
    Menghitung Sadwara berdasarkan jangkar tanggal.

    Jangkar:
        26 April 2025 = Paniron
    """

    if not isinstance(tanggal, date):
        raise TypeError(
            "Tanggal harus berupa datetime.date."
        )

    indeks_awal = SADWARA.index(
        normalisasi_sadwara(SADWARA_JANGKAR)
    )

    selisih_hari = (
        tanggal - TANGGAL_JANGKAR_SADWARA
    ).days

    indeks = (
        indeks_awal + selisih_hari
    ) % len(SADWARA)

    # return SADWARA[indeks]
    return {
        "sadwara": SADWARA[indeks],
        "sadwara_indeks": indeks
    }

# ============================================================
# DAFTAR WUKU SUNDA
# ============================================================

WUKU = [
    "Sinta",
    "Landep",
    "Wukir",
    "Kurantil",
    "Telu",
    "Gumbreg",
    "Warigalit",
    "Warigagung",
    "Jungjungwang",
    "Sungsang",
    "Galungan",
    "Kuningan",
    "Langkir",
    "Madasiya",
    "Julungpujud",
    "Pahang",
    "Kuruwelit",
    "Marakeh",
    "Tambir",
    "Madangkungan",
    "Maktal",
    "Wuye",
    "Manahil",
    "Prangbakat",
    "Bala",
    "Wugu",
    "Wayang",
    "Kulawu",
    "Dukut",
    "Watugunung",
]


# ============================================================
# JANGKAR WUKU
# ============================================================

TANGGAL_JANGKAR_WUKU = date(2025, 4, 26)

WUKU_JANGKAR = "Maktal"

# Sabtu adalah posisi ke-7, atau indeks 6
POSISI_HARI_JANGKAR = 6


# ============================================================
# HITUNG WUKU
# ============================================================

def hitung_wuku(tanggal):
    """
    Menghitung Wuku berdasarkan jangkar proyek.

    Jangkar:
        26 April 2025 = Sabtu, Wuku Maktal.

    Pergantian Wuku berlangsung setiap Ahad.
    """

    if not isinstance(tanggal, date):
        raise TypeError(
            "Tanggal harus berupa datetime.date."
        )

    indeks_jangkar = WUKU.index(WUKU_JANGKAR)

    selisih_hari = (
        tanggal - TANGGAL_JANGKAR_WUKU
    ).days

    jumlah_pergantian_wuku = (
        selisih_hari + POSISI_HARI_JANGKAR
    ) // 7

    indeks_wuku = (
        indeks_jangkar + jumlah_pergantian_wuku
    ) % len(WUKU)

    posisi_hari = (
        POSISI_HARI_JANGKAR + selisih_hari
    ) % 7

    return {
        "wuku": WUKU[indeks_wuku],
        "nomor_wuku": indeks_wuku + 1,
        "hari_ke_wuku": posisi_hari + 1,
    }


# ============================================================
# 9. VALIDASI INPUT TANGGAL MASEHI
# ============================================================

def validasi_tanggal_masehi(tanggal_masehi):
    """
    Menerima:
    - datetime.date
    - string ISO: YYYY-MM-DD

    datetime.datetime tidak diterima agar tidak terjadi
    pencampuran tanggal dan waktu.
    """

    if isinstance(tanggal_masehi, str):
        try:
            tanggal_masehi = date.fromisoformat(tanggal_masehi)
        except ValueError:
            raise ValueError(
                "Format tanggal harus YYYY-MM-DD."
            )

    if isinstance(tanggal_masehi, datetime):
        raise TypeError(
            "Gunakan datetime.date, bukan datetime.datetime."
        )

    if not isinstance(tanggal_masehi, date):
        raise TypeError(
            "Tanggal harus berupa datetime.date atau string YYYY-MM-DD."
        )

    return tanggal_masehi



# ============================================================
# 10. KONVERSI MASEHI KE CAKA SUNDA
# ============================================================

def masehi_to_caka(tanggal_masehi):
    """
    Mengonversi tanggal Masehi menjadi tanggal Kala Candra Sunda.

    Dasar perhitungan:
    1. Menghitung selisih hari dari epoch Masehi.
    2. Menentukan tahun Caka.
    3. Menentukan bulan Caka.
    4. Menentukan tanggal dalam bulan.

    Tidak menggunakan koreksi tanggal eksternal.
    """

    tanggal_masehi = validasi_tanggal_masehi(
        tanggal_masehi
    )

    # --------------------------------------------------------
    # A. SELISIH HARI DARI EPOCH
    # --------------------------------------------------------

    selisih = (
        tanggal_masehi - TANGGAL_EPOCH_MASEHI
    ).days

    tahun = TAHUN_EPOCH

    # --------------------------------------------------------
    # B. MENENTUKAN TAHUN CAKA
    # --------------------------------------------------------

    if selisih >= 0:

        # Bergerak maju dari epoch
        while True:

            jumlah_hari = panjang_tahun(tahun)

            if selisih < jumlah_hari:
                break

            selisih -= jumlah_hari
            tahun += 1

    else:

        # Bergerak mundur dari epoch
        while selisih < 0:

            tahun -= 1

            if tahun < 1:
                raise ValueError(
                    "Tanggal berada sebelum awal tahun Caka 1."
                )

            selisih += panjang_tahun(tahun)

    # --------------------------------------------------------
    # C. MENENTUKAN BULAN CAKA
    # --------------------------------------------------------

    bulan = 1

    while bulan <= 12:

        jumlah_hari_bulan = panjang_bulan(
            tahun,
            bulan
        )

        if selisih < jumlah_hari_bulan:
            break

        selisih -= jumlah_hari_bulan
        bulan += 1

    if bulan > 12:
        raise ArithmeticError(
            "Perhitungan bulan melewati batas 12 bulan."
        )

    # --------------------------------------------------------
    # D. MENENTUKAN TANGGAL DALAM BULAN
    # --------------------------------------------------------

    tanggal = selisih + 1

    # --------------------------------------------------------
    # E. INFORMASI TAHUN
    # --------------------------------------------------------

    info_dewataun = dewataun(tahun)
    info_tunggul = tunggul_taun(tahun)

    jumlah_hari_tahun = panjang_tahun(tahun)

    hari_ke_tahun = (
        jumlah_hari_sebelum_bulan(tahun, bulan)
        + tanggal
    )



    # Validasi independen berdasarkan tanggal awal tahun
    awal_tahun = tanggal_awal_tahun_masehi(tahun)

    hari_ke_tahun_masehi = (tanggal_masehi - awal_tahun).days + 1

    if hari_ke_tahun != hari_ke_tahun_masehi:
        raise ArithmeticError(
            f"Ketidaksesuaian hari ke tahun {tahun}: "
            f"hasil bulan={hari_ke_tahun}, "
            f"hasil Masehi={hari_ke_tahun_masehi}, "
            f"tanggal={tanggal_masehi}, "
            f"awal tahun={awal_tahun}"
        )
    if not 1 <= hari_ke_tahun <= jumlah_hari_tahun:
        raise ArithmeticError(
            f"Hari ke tahun berada di luar batas: "
            f"{hari_ke_tahun}/{jumlah_hari_tahun}"
        )


    # --------------------------------------------------------
    # F. HASIL KONVERSI
    # --------------------------------------------------------

    return {
        "tahun": tahun,
        "bulan": bulan,
        "nama_bulan": BULAN_CAKA[bulan - 1],
        "tanggal": tanggal,
        "umur_bulan": panjang_bulan(tahun, bulan),
        "hari_ke_tahun": hari_ke_tahun,
        "panjang_tahun": jumlah_hari_tahun,

        "jenis_tahun": (
            "Wastu"
            if jumlah_hari_tahun == 354
            else "Wuntu"
        ),

        "dewataun": info_dewataun["nama"],

        "tunggul_taun": info_tunggul["nomor"],
        "posisi_tunggul": info_tunggul["posisi"],
    }

def caka_to_masehi(tahun, bulan, tanggal):
    """
    Mengonversi tanggal Kala Candra Sunda menjadi tanggal Masehi.

    Parameter:
        tahun   : tahun Caka Sunda
        bulan   : nomor bulan (1-12)
        tanggal : tanggal dalam bulan

    Hasil:
        datetime.date

    Ketentuan:
        - Epoch: 1 Kartika 1921 = 11 Desember 1999
        - Wastu: 354 hari
        - Wuntu: 355 hari
        - Asuji: 29 atau 30 hari
        - Tunggul Taun: tahun ke-120 = 354 hari

    Konversi dibatasi mulai epoch Caka 1921 karena
    aturan historis sebelum epoch belum ditetapkan.
    """

    # --------------------------------------------------------
    # A. VALIDASI INPUT
    # --------------------------------------------------------

    if type(tahun) is not int:
        raise TypeError("Tahun harus berupa bilangan bulat.")

    if type(bulan) is not int:
        raise TypeError("Bulan harus berupa bilangan bulat.")

    if type(tanggal) is not int:
        raise TypeError("Tanggal harus berupa bilangan bulat.")

    if tahun < TAHUN_EPOCH:
        raise NotImplementedError(
            "Konversi sebelum epoch Kala Candra Sunda "
            "belum memiliki dasar aturan yang terverifikasi."
        )

    if not 1 <= bulan <= 12:
        raise ValueError(
            "Nomor bulan harus antara 1 sampai 12."
        )

    # --------------------------------------------------------
    # B. VALIDASI TANGGAL DALAM BULAN
    # --------------------------------------------------------

    jumlah_hari_bulan = panjang_bulan(tahun, bulan)

    if not 1 <= tanggal <= jumlah_hari_bulan:
        raise ValueError(
            f"Tanggal {tanggal} tidak valid untuk "
            f"{NAMA_BULAN[bulan - 1]} tahun {tahun}. "
            f"Bulan tersebut memiliki {jumlah_hari_bulan} hari."
        )

    # --------------------------------------------------------
    # C. AKUMULASI HARI SEBELUM TAHUN
    # --------------------------------------------------------

    hari_sebelum_tahun = jumlah_hari_sebelum_tahun(tahun)

    # --------------------------------------------------------
    # D. AKUMULASI HARI SEBELUM BULAN
    # --------------------------------------------------------

    hari_sebelum_bulan = jumlah_hari_sebelum_bulan(
        tahun,
        bulan
    )

    # --------------------------------------------------------
    # E. POSISI TANGGAL DALAM TAHUN
    # --------------------------------------------------------

    hari_sebelum_tanggal = tanggal - 1

    # --------------------------------------------------------
    # F. TOTAL SELISIH DARI EPOCH
    # --------------------------------------------------------

    total_hari = (
        hari_sebelum_tahun
        + hari_sebelum_bulan
        + hari_sebelum_tanggal
    )

    # --------------------------------------------------------
    # G. KONVERSI KE TANGGAL MASEHI
    # --------------------------------------------------------

    tanggal_masehi = (
        TANGGAL_EPOCH_MASEHI
        + timedelta(days=total_hari)
    )

    return tanggal_masehi

# ============================================================
# 11. FORMAT TANGGAL CAKA
# ============================================================

def format_tanggal_caka(hasil):
    """
    Menghasilkan tampilan tanggal Caka dengan pembagian paksa.

    Tanggal 1-15  = Suklapaksa (s)
    Tanggal 16-30 = Kresnapaksa (k)

    Contoh:
    Tanggal 19 Asada menjadi 4k Asada.
    """

    tanggal = hasil["tanggal"]
    umur_bulan = hasil["umur_bulan"]

    if umur_bulan not in (29, 30):
        raise ValueError("Umur bulan harus 29 atau 30")

    if not 1 <= tanggal <= umur_bulan:
        raise ValueError("Tanggal di luar umur bulan")

    if tanggal <= 15:
        tanggal_paksa = tanggal
        paksa = "Suklapaksa",
        singkatan = "s",
        istilah = "Parocaang"
    else:
        tanggal_paksa = tanggal - 15
        paksa = "Kresnapaksa"
        singkatan = "k"
        istilah = "Paropoek"

    return {
        "tanggal_paksa": f"{tanggal_paksa}{singkatan}",
        "paksa": paksa,
        "istilah": istilah
    }


# ============================================================
# 13. PENGUJIAN BATAS TANGGAL
# ============================================================

def tanggal_awal_tahun_masehi(tahun):
    """
    Menghitung tanggal Masehi untuk 1 Kartika
    pada tahun Caka tertentu berdasarkan epoch.
    """

    selisih = jumlah_hari_sebelum_tahun(tahun)

    return TANGGAL_EPOCH_MASEHI + timedelta(days=selisih)


def tanggal_awal_bulan_masehi(tahun, bulan):
    """
    Menghitung tanggal Masehi untuk tanggal 1
    pada bulan Caka tertentu.
    """
    awal_tahun = tanggal_awal_tahun_masehi(tahun)
    selisih = jumlah_hari_sebelum_bulan(tahun, bulan)

    return awal_tahun + timedelta(days=selisih)

def kalacandra_sunda(tanggal_masehi):
    """
    Mengonversi tanggal Masehi menjadi Kala Candra Sunda.

    Parameter:
        tanggal_masehi : datetime.date atau string YYYY-MM-DD

    Hasil:
        dict dengan informasi tanggal Caka Sunda.
    """

    hasil = masehi_to_caka(tanggal_masehi)

    tanggal_uji = validasi_tanggal_masehi(tanggal_masehi)
    tanggal_paksa = format_tanggal_caka(hasil)
    saptawara = hitung_saptawara_caka(
        hasil["tahun"],
        hasil["bulan"],
        hasil["tanggal"]
    )
    pancawara = hitung_pancawara_caka(
        hasil["tahun"],
        hasil["bulan"],
        hasil["tanggal"]
    )
    sadwara = hitung_sadwara(tanggal_uji)
    wuku = hitung_wuku(tanggal_uji)
    info_windu = windu(hasil["tahun"])
    indung_poe = hitung_indung_poe(hasil["tahun"])
    hari_ke_tahun = hitung_hari_ke_tahun(
        hasil["tahun"],
        hasil["bulan"],
        hasil["tanggal"]
    )

    return {
        "tanggal_masehi": tanggal_uji,
        "tanggal_caka": f"{tanggal_paksa['tanggal_paksa']} {hasil['nama_bulan']} {hasil['tahun']} Caka Sunda",
        "tahun": hasil["tahun"],
        "bulan": hasil["nama_bulan"],
        "tanggal": hasil["tanggal"],
        "tanggal_paksa": tanggal_paksa,
        "saptawara": saptawara,
        "pancawara": pancawara,
        "sadwara": sadwara,
        "wuku": wuku,
        "hari_ke_tahun": hari_ke_tahun,
        "panjang_tahun": hasil["panjang_tahun"],
        "jenis_tahun": hasil["jenis_tahun"],
        "dewataun": hasil["dewataun"],
        "tunggul_taun": hasil["tunggul_taun"],
        "posisi_tunggul": hasil["posisi_tunggul"],
        "windu": info_windu,
        "indung_poe": indung_poe
    }

if __name__ == "__main__":

    print("=" * 60)
    print("PENGUJIAN KALA CANDRA SUNDA")
    print("=" * 60)

    daftar_uji = [
        "1999-12-11", "2000-11-29", "2001-11-18", "2002-11-07", "2003-10-27", "2004-10-16", "2005-10-05", "2006-09-24",
    "2007-09-15", "2006-09-03","2114-06-16", "2115-05-27", "2116-05-16","2026-11-11"
    ]

    for tanggal_masehi in daftar_uji:

        hasil = masehi_to_caka(tanggal_masehi)

        tanggal_uji = datetime.strptime(tanggal_masehi, "%Y-%m-%d").date()
        tanggal_paksa = format_tanggal_caka(hasil)
        saptawara = saptawara_caka = hitung_saptawara_caka(hasil["tahun"],hasil["bulan"],hasil["tanggal"])
        pancawara = hitung_pancawara_caka(tanggal_uji.year, tanggal_uji.month, tanggal_uji.day)
        sadwara = hitung_sadwara(tanggal_uji)
        wuku = hitung_wuku(tanggal_uji)
        info_windu = windu(hasil["tahun"])
        indung_poe = hitung_indung_poe(hasil["tahun"])
        tahun = hasil["tahun"]
        bulan = hasil["bulan"]
        tanggal = hasil["tanggal"]

        hari_ke_tahun = hitung_hari_ke_tahun(
            tahun,
            bulan,
            tanggal)

        print("Tanggal Masehi :", tanggal_masehi)
        print("Tanggal Caka   :", f"{tanggal_paksa['tanggal_paksa']} {hasil['nama_bulan']} {hasil['tahun']} Caka Sunda")
        print("Tahun          :", hasil["tahun"])
        print("Bulan          :", hasil["nama_bulan"])
        print("Tanggal        :", hasil["tanggal"])
        print("tanggal_paksa  :", tanggal_paksa)
        # print("Saptawara_masehi      :", saptawara_masehi)
        print("Saptawara_caka          :", saptawara)
        print("Pancawara      :", pancawara)
        print("Sadwara        :", sadwara)
        print("Wuku           :", wuku)
        print("Hari ke tahun  :", hari_ke_tahun)
        print("Panjang tahun  :", hasil["panjang_tahun"])
        print("Jenis tahun    :", hasil["jenis_tahun"])
        print("Dewataun       :", hasil["dewataun"])
        print("Tunggul Taun   :", hasil["tunggul_taun"])
        print("Posisi Tunggul :", hasil["posisi_tunggul"])
        print("windu          :", info_windu)
        print("indung_poe      :", indung_poe)


    print()
    print("=" * 60)
    print("PENGUJIAN SELESAI")
    print("=" * 60)