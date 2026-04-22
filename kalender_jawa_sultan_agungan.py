from datetime import datetime
# import math

# =========================
# JDN
# =========================
def gregorian_to_jdn(y, m, d):
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + (a // 4)
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524


# =========================
# SIKLUS
# =========================
BULAN_JAWA = [
    "Sura", "Sapar", "Mulud", "Bakdamulud",
    "Jumadilawal", "Jumadilakhir", "Rejeb",
    "Ruwah", "Pasa", "Sawal", "Dulkangidah", "Besar"
]

SIKLUS_WARSA = ["Alip", "Ehe", "Jimawal", "Je", "Dal", "Be", "Wawu", "Jimakir"]
SIKLUS_WINDU = ["Adi", "Kuntara", "Sengara", "Sancaya"]
SIKLUS_LAMBANG = ["Kulawu", "Langkir"]

SADWARA = ["Tungle","Aryang","Wurukung","Paningron","Uwas","Mawulu"]
HASTAWARA = ["Sri","Indra","Guru","Yama","Ludra","Brahma","Kala","Uma"]
SANGAWARA = ["Dangu","Jangur","Gigis","Nohan","Ogan","Erangan","Urungan","Tulus","Dadi"]

POLA_TAHUN = [354, 355, 354, 354, 355, 354, 354, 355]


# =========================
# ANCHOR TANGGAL JAWA
# =========================
ANCHOR = {
    "date": datetime(2026, 4, 11),
    "jdn": gregorian_to_jdn(2026, 4, 11),
    "tanggal": 23,
    "bulan": 9,
    "tahun": 1959,
    "warsa_index": 4,
    "windu_index": 0
}


# =========================
# AUTO KALIBRASI WARA
# =========================
def kalibrasi_wara(tanggal_ref, ref):
    jdn = gregorian_to_jdn(tanggal_ref.year, tanggal_ref.month, tanggal_ref.day)

    return {
        "sad": (SADWARA.index(ref["sadwara"]) - jdn % 6) % 6,
        "hasta": (HASTAWARA.index(ref["hastawara"]) - jdn % 8) % 8,
        "sanga": (SANGAWARA.index(ref["sangawara"]) - jdn % 9) % 9
    }


# 🔥 REFERENSI NYATA (INI KUNCI)
OFFSET = kalibrasi_wara(
    datetime(2026, 4, 14),
    {
        "sadwara": "Paningron",
        "hastawara": "Uma",
        "sangawara": "Dangu"
    }
)


# =========================
# HITUNG WARA
# =========================
def hitung_wara(jdn):
    return {
        "sadwara": SADWARA[(jdn + OFFSET["sad"]) % 6],
        "hastawara": HASTAWARA[(jdn + OFFSET["hasta"]) % 8],
        "sangawara": SANGAWARA[(jdn + OFFSET["sanga"]) % 9],
    }


# =========================
# KONVERSI JAWA
# =========================
def jdn_to_jawa(jdn):
    delta = jdn - ANCHOR["jdn"]

    siklus_8 = sum(POLA_TAHUN)
    siklus_count = delta // siklus_8
    sisa_hari = delta % siklus_8

    tahun = ANCHOR["tahun"] + siklus_count * 8

    i = 0
    while sisa_hari >= POLA_TAHUN[i]:
        sisa_hari -= POLA_TAHUN[i]
        tahun += 1
        i += 1

    panjang_bulan = [30,29,30,29,30,29,30,29,30,29,30,29]

    if POLA_TAHUN[(tahun - ANCHOR["tahun"]) % 8] == 355:
        panjang_bulan[-1] = 30

    bulan = ANCHOR["bulan"]
    tanggal = ANCHOR["tanggal"] + sisa_hari

    while tanggal > panjang_bulan[bulan]:
        tanggal -= panjang_bulan[bulan]
        bulan += 1
        if bulan > 11:
            bulan = 0
            tahun += 1

    selisih_tahun = tahun - ANCHOR["tahun"]

    return {
        "tanggal": tanggal,
        "bulan": BULAN_JAWA[bulan],
        "tahun": tahun,
        "warsa": SIKLUS_WARSA[(ANCHOR["warsa_index"] + selisih_tahun) % 8],
        "windu": SIKLUS_WINDU[(ANCHOR["windu_index"] + selisih_tahun // 8) % 4],
        "lambang": SIKLUS_LAMBANG[(selisih_tahun // 8) % 2]
    }

# =========================
# PRANATAMANGSA
# =========================
def hitung_mangsa(tanggal):
    m = tanggal.month
    d = tanggal.day

    data = [
        ((6,22),(8,1),"Kasa-Kartika"),
        ((8,2),(8,24),"Karo-Pusa"),
        ((8,25),(9,17),"Katiga-Agrahayana"),
        ((9,18),(10,12),"Kapat-Sitamasa"),
        ((10,13),(11,8),"Kalima-Sita"),
        ((11,9),(12,21),"Kanem-Naya"),
        ((12,22),(2,2),"Kapitu-Palguna"),
        ((2,3),(2,28),"Kawalu-Wisaka"),
        ((3,1),(3,25),"Kasanga-Jita"),
        ((3,26),(4,18),"Kasapuluh-Srawana"),
        ((4,19),(5,11),"Dhesta-Pratrawana"),
        ((5,12),(6,21),"Sada-Asuji")
    ]

    for mulai, akhir, nama in data:
        sm, sd = mulai
        em, ed = akhir

        if sm <= em:
            if (m == sm and d >= sd) or (m == em and d <= ed) or (m > sm and m < em):
                pranatamangsa = f"{nama}"
        else:
            if (m == sm and d >= sd) or (m == em and d <= ed) or (m > sm or m < em):
                pranatamangsa = f"{nama}"

    return pranatamangsa

# =====================
# Parerasan & Pancasuda
# =====================
data_parerasan = {
        "PasaranPancasuda": ["Ahad Pon", "Senen Kliwon", "Selasa Pahing", "Rebo Legi", "Kemis Wage"],
        "Aras Kembang": ["Senen Pon", "Selasa Kliwon", "Rebo Wage", "Jumuwah Legi"],
        "Aras Tuding": ["Ahad Pon", "Senen Pahing", "Rebo Pon", "Kemis Kliwon", "Setu Legi"],
        "Bumi Kapetak": ["Setu Pon", "Rebo Pahing", "Kemis Kliwon"],
        "Laku Yeh": ["Senen Wage", "Selasa Legi", "Setu Pahing"],
        "Laku Api": ["Ahad Wage", "Senen Legi"],
        "Laku Angin": ["Ahad Kliwon", "Senen Pahing", "Kemis Legi", "Jemuwah Pon"],
        "Laku Bintang": ["Ahad Pahing", "Rebo Pon", "Jemuwah Kliwon", "Setu Legi"],
        "Laku Bulan": ["Selasa Wage", "Setu Kliwon", "Kemis Pahing"],
        "Laku Bumi": ["Rebo Kliwon", "Kemis Pon", "Setu Pahing"],
        "Laku Surya": ["Ahad Legi", "Selasa Pon", "Setu Wage"],
        "Laku Pandita Sakti": ["Ahad Kliwon", "Selasa Wage", "Kemis Pahing", "Setu Pon"],
        "Lebu Katiup Angin": ["Senen Wage", "Selasa Pon", "Rebo Wage", "Kemis Legi", "Setu Pahing"],
        "Satria Wibawa": ["Senen Kliwon", "Selasa Pahing", "Kemis Pon", "Jemuwah Legi", "Setu Wage"],
        "Satria Wirang": ["Ahad Legi", "Senen Pon", "Selasa Kliwon", "Rebo Legi", "Jemuwah Wage"],
        "Sumur Sinaba": ["Senen Legi", "Jemuwah Pahing", "Kemis Wage", "Setu Kliwon"],
        "Tunggak Semi": ["Ahad Pahing", "Senen Wage", "Selasa Legi", "Jemuwah Kliwon", "Setu Pon"]
    }

def cari_parerasan(dina_nama, pasaran_nama):
    # 1. Concat menjadi satu variabel
    hari_input = f"{dina_nama} {pasaran_nama}"

    hasil = []
    # 2. Mencari hari di dalam setiap kategori
    for kategori, daftar_hari in data_parerasan.items():
        if hari_input in daftar_hari:
            hasil.append(kategori)

    # 3. Kembalikan seluruh array hasil
    if hasil:
        return hasil  # Mengembalikan array berisi semua kategori yang ditemukan
    else:
        return ["Data tidak ditemukan"]

# =====================
# PANCASUDA BIASA
# =====================
def pancasuda_biasa(dina_nama, pasaran_nama):
    hari_pancasuda_biasa = {
        "Ahad": 5, "Senen": 4, "Selasa": 3, "Rebo": 7, "Kemis": 8, "Jemuwah": 6, "Setu": 9
    }
    pasaran_pancasuda_biasa = {
        "Pon": 7, "Wage": 4, "Kliwon": 8, "Legi": 5, "Pahing": 9
    }

    data_sisa_pancasuda_biasa = [
        {"sisa": 1, "nama": "Sri"},  # Index 0
        {"sisa": 2, "nama": "Lungguh"},  # Index 1
        {"sisa": 3, "nama": "Gedhong"},  # Index 2
        {"sisa": 4, "nama": "Lara"},  # Index 3
        {"sisa": 5, "nama": "Pati"}  # Index 4
    ]

    jumlah_neptu = hari_pancasuda_biasa[dina_nama] + pasaran_pancasuda_biasa[pasaran_nama]

    sisa = jumlah_neptu % 5

    if sisa == 0:
        index = 4  # The 5th item in the list
    else:
        index = sisa - 1  # Subtract 1 to convert math result to Python index

    return data_sisa_pancasuda_biasa[index]['nama']

    # =====================
    # PANCASUDA PAKUWON
    # =====================
def pancasuda_pakuwon(dina_nama, pasaran_nama, wuku_neptu):
   hari_val = {
        "Ahad": 6, "Senen": 4, "Selasa": 3, "Rebo": 6, "Kemis": 5, "Jemuwah": 7, "Setu": 8
   }
   pasaran_val = {
        "Pon": 7, "Wage": 4, "Kliwon": 8, "Legi": 5, "Pahing": 9
   }

   data_sisa_pancasuda_pakuwon = [
       {"sisa": 1, "nama": "Satriya Wibawa"},
       {"sisa": 2, "nama": "Tayung Angin"},
       {"sisa": 3, "nama": "Satriya Wirang"},
       {"sisa": 4, "nama": "Lumbu Kentheng"},
       {"sisa": 5, "nama": "Gajah Menur"},
       {"sisa": 6, "nama": "Bumi Kapetak"},
       {"sisa": 0, "nama": "Lebu Katiup Angin"}  # Sisa 0 atau 7
    ]

   total_neptu = hari_val[dina_nama] + pasaran_val[pasaran_nama] + int(wuku_neptu)
   sisa = total_neptu % 7

   if sisa == 0:
       index = 6
   else:
       index = sisa - 1

   return data_sisa_pancasuda_pakuwon[index]['nama']

# =====================
# RAKAM
# =====================

def hitung_rakam(dina_nama, pasaran_nama):

     hari_rakam = {
            "Ahad": 3, "Senen": 4, "Selasa": 5, "Rebo": 6,"Kemis": 7, "Jemuwah": 1, "Setu": 2
     }
     pasaran_rakam = {
            "Pon": 4, "Wage": 5, "Kliwon": 1, "Legi": 2, "Pahing": 3
     }

        # Data Rakam (Index 0-5 untuk sisa 1-6)
     data_rakam = [
            {"sisa": 1, "nama": "Nuju Pati"},
            {"sisa": 2, "nama": "Sanggar Waringin"},
            {"sisa": 3, "nama": "Mantri Sinaroja"},
            {"sisa": 4, "nama": "Macan Ketawang"},
            {"sisa": 5, "nama": "Demang Kadhuruwun"},
            {"sisa": 6, "nama": "Gigis Bumi"}
     ]

        # 1. Jumlahkan Neptu Rakam
     jumlah_neptu = hari_rakam[dina_nama] + pasaran_rakam[pasaran_nama]

        # 2. Hitung sisa bagi 6
     sisa = jumlah_neptu % 6

        # 3. Tentukan Index
        # Jika sisa 0, maka itu adalah Gigis Bumi (Sisa 6 / Index 5)
     if sisa == 0:
        index = 5
     else:
        index = sisa - 1

     return data_rakam[index]['nama']

# =========================
# MAIN
# =========================
def kalender_jawa(tanggal):
    jdn = gregorian_to_jdn(tanggal.year, tanggal.month, tanggal.day)

    # WUKU
    jdn_anchor_landep = 2461143
    idx_wuku = (1 + (jdn - jdn_anchor_landep) // 7) % 30

    WUKU = [
        {"nama": "Sinta", "neptu": 7},
        {"nama": "Landep", "neptu": 1},
        {"nama": "Wukir", "neptu": 4},  # Ukir
        {"nama": "Kurantil", "neptu": 6},  # Kulantir
        {"nama": "Tolu", "neptu": 5},  # Taulu
        {"nama": "Gumbreg", "neptu": 8},
        {"nama": "Warigalit", "neptu": 9},  # Wariga
        {"nama": "Warigagung", "neptu": 3},  # Warigadean
        {"nama": "Julungwangi", "neptu": 7},
        {"nama": "Sungsang", "neptu": 1},
        {"nama": "Galungan", "neptu": 4},  # Dungulan
        {"nama": "Kuningan", "neptu": 6},
        {"nama": "Langkir", "neptu": 5},
        {"nama": "Mandasiya", "neptu": 8},  # Medangsia
        {"nama": "Julungpujut", "neptu": 9},  # Pujut
        {"nama": "Pahang", "neptu": 3},
        {"nama": "Kuruwelut", "neptu": 7},  # Krulut
        {"nama": "Marakeh", "neptu": 1},  # Merakih
        {"nama": "Tambir", "neptu": 4},
        {"nama": "Medangkungan", "neptu": 6},
        {"nama": "Maktal", "neptu": 5},  # Matal
        {"nama": "Wuye", "neptu": 8},  # Uye
        {"nama": "Manahil", "neptu": 9},  # Menail
        {"nama": "Prangbakat", "neptu": 3},
        {"nama": "Bala", "neptu": 7},
        {"nama": "Wugu", "neptu": 1},  # Ugu
        {"nama": "Wayang", "neptu": 4},
        {"nama": "Kulawu", "neptu": 6},  # Klau
        {"nama": "Dukut", "neptu": 5},
        {"nama": "Watugunung", "neptu": 8}
    ]

    # WARA
    wara = hitung_wara(jdn)

    # HARI
    # DINA = ["Senen","Selasa","Rebo","Kemis","Jemuwah","Setu","Ahad"]
    DINA = [
        ["Senen", "Soma"],
        ["Selasa", "Anggara"],
        ["Rebo", "Budha"],
        ["Kemis", "Respati"],
        ["Jemuwah", "Sukra"],
        ["Setu", "Tumpak"],
        ["Ahad", "Radite"]
    ]

    # PASARAN = ["Legi","Pahing","Pon","Wage","Kliwon"]
    PASARAN = [
        ["Legi", "Umanis (Manis) / Kasih"],
        ["Pahing", "Paing (Jenar)"],
        ["Pon", "Palguna"],
        ["Wage", "Cemengan"],
        ["Kliwon", "Kasih"]
    ]

    jawa = jdn_to_jawa(jdn)

    dina = DINA[jdn%7]
    pasaran = PASARAN[jdn%5]
    wuku_hasil = WUKU[idx_wuku]
    return {
        "masehi": tanggal.strftime("%d-%m-%Y"),
        "hari_jawa": f"{dina[0]} {pasaran[0]}",
        "hari_caka": f"{dina[1]} {pasaran[1]}",
        "tanggal_jawa": f"{jawa['tanggal']} {jawa['bulan']} {jawa['warsa']} {jawa['tahun']}",
        "windu": f"{jawa['windu']} ({jawa['lambang']})",
        "wuku": wuku_hasil['nama'],
        **wara,
        "parerasan": cari_parerasan(dina[0], pasaran[0]),
        "pancasuda_biasa": pancasuda_biasa(dina[0], pasaran[0]),
        "pawukon": pancasuda_pakuwon(dina[0], pasaran[0],wuku_hasil['neptu']),
        "rakam": hitung_rakam(dina[0], pasaran[0]),
        "pranatamangsa": hitung_mangsa(tanggal)
    }

# TEST
# today = datetime.now().date()
# print(kalender_jawa(today))