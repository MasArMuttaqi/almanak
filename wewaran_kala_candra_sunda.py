
from datetime import date, datetime


# ============================================================
# 1. DAFTAR SIKLUS
# ============================================================

# Urutan Saptawara
SAPTAWARA = [
    "Dite",
    "Soma",
    "Anggara",
    "Buda",
    "Respati",
    "Sukra",
    "Tumpek",
]

# Urutan Pancawara
PANCAWARA = [
    "Manis",
    "Pahing",
    "Pon",
    "Wage",
    "Kaliwon",
]

# Urutan Sadwara
# Berdasarkan nama yang diberikan pengguna.
SADWARA = [
    "Tungleh",
    "Ariang",
    "Urukung",
    "Paniron",
    "Was",
    "Maulu",
]

# Alias ejaan Sadwara
SADWARA_ALIAS = {
    "Tungle": "Tungleh",
    "Hariyang": "Ariang",
    "Wurukung": "Urukung",
    "Paningron": "Paniron",
    "Paningran": "Paniron",
    "Uwas": "Was",
    "Mawulu": "Maulu",
}

# Urutan 30 Wuku Caka Sunda
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
# 2. JANGKAR PERHITUNGAN
# ============================================================

# 26 April 2025
# 21 (6k) Badra 1961
#
# Saptawara : Tumpek
# Pancawara : Kaliwon
# Sadwara   : Paniron
# Wuku      : Maktal

TANGGAL_JANGKAR = date(2025, 4, 26)

JANGKAR = {
    "saptawara": "Tumpek",
    "pancawara": "Kaliwon",
    "sadwara": "Paniron",
    "wuku": "Maktal",
}


# ============================================================
# 3. FUNGSI DASAR
# ============================================================

def hitung_siklus(tanggal, daftar, nama_jangkar):
    """
    Menghitung posisi suatu siklus berdasarkan tanggal jangkar.

    tanggal       : datetime.date
    daftar        : daftar nama siklus
    nama_jangkar  : nama yang diketahui pada tanggal jangkar
    """

    if not isinstance(tanggal, date):
        raise TypeError("tanggal harus berupa datetime.date")

    try:
        indeks_jangkar = daftar.index(nama_jangkar)
    except ValueError:
        raise ValueError(
            f"Nama jangkar '{nama_jangkar}' tidak ditemukan"
        )

    selisih_hari = (tanggal - TANGGAL_JANGKAR).days

    indeks = (indeks_jangkar + selisih_hari) % len(daftar)

    return daftar[indeks]


# ============================================================
# 4. FUNGSI SAPTAWARA
# ============================================================

def hitung_saptawara(tanggal):
    return hitung_siklus(
        tanggal,
        SAPTAWARA,
        JANGKAR["saptawara"]
    )


# ============================================================
# 5. FUNGSI PANCAWARA
# ============================================================

def hitung_pancawara(tanggal):
    return hitung_siklus(
        tanggal,
        PANCAWARA,
        JANGKAR["pancawara"]
    )


# ============================================================
# 6. FUNGSI SADWARA
# ============================================================

def hitung_sadwara(tanggal):
    return hitung_siklus(
        tanggal,
        SADWARA,
        JANGKAR["sadwara"]
    )


# ============================================================
# 7. FUNGSI WUKU
# ============================================================


def hitung_wuku(tanggal):
    """
    Menghitung Wuku Caka Sunda.

    Jangkar:
    26 April 2025 = Maktal
    Posisi hari dalam Wuku = 5 (indeks dimulai dari 0)
    """

    selisih_hari = (tanggal - TANGGAL_JANGKAR).days

    posisi_hari_wuku = 5

    indeks_jangkar = WUKU.index(JANGKAR["wuku"])

    indeks = (
        indeks_jangkar
        + (selisih_hari + posisi_hari_wuku) // 7
    ) % 30

    return WUKU[indeks]



# ============================================================
# 8. FUNGSI GABUNGAN
# ============================================================

def hitung_wara_sunda(tanggal):
    """
    Menghitung seluruh wara dan wuku berdasarkan tanggal Masehi.
    """

    if isinstance(tanggal, str):
        tanggal = date.fromisoformat(tanggal)

    if isinstance(tanggal, datetime):
        tanggal = tanggal.date()

    if not isinstance(tanggal, date):
        raise TypeError(
            "Gunakan datetime.date atau string YYYY-MM-DD"
        )

    return {
        "tanggal_masehi": tanggal.isoformat(),
        "saptawara": hitung_saptawara(tanggal),
        "pancawara": hitung_pancawara(tanggal),
        "sadwara": hitung_sadwara(tanggal),
        "wuku": hitung_wuku(tanggal),
    }


# ============================================================
# 9. PENGUJIAN
# ============================================================

if __name__ == "__main__":

    daftar_uji = [
        "2025-04-26",
        "2025-05-31",
        "2025-07-05",
        "2025-08-09",
        "2025-09-13",
        "2025-10-18",
        "2025-11-22",
        "2025-12-27",
        "2022-07-16",
        "2026-11-09",
        "2026-11-06",
    ]

    for tanggal_str in daftar_uji:

        hasil = hitung_wara_sunda(tanggal_str)

        print(
            hasil["tanggal_masehi"],
            "|", hasil["saptawara"],
            "|", hasil["pancawara"],
            "|", hasil["wuku"],
            "|", hasil["sadwara"],
        )
