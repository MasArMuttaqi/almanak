
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

NAMA_BULAN = [
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

# Panjang bulan 1 sampai 11
# Bulan ke-12 (Asuji) mengikuti panjang tahun.
PANJANG_BULAN_NORMAL = [
    30,  # Kartika
    29,  # Margasira
    30,  # Posya
    29,  # Maga
    30,  # Palguna
    29,  # Setra
    30,  # Wesaka
    29,  # Yesta
    30,  # Asada
    29,  # Srawana
    30,  # Badra
]


# ============================================================
# 3. SIKLUS DEWATAUN (8 TAHUN)
# ============================================================

# Urutan siklus dimulai dari tahun 1921 = Kebo.
#
# Format:
# (nama_dewataun, jenis_tahun, jumlah_hari)

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

PANJANG_WINDU = 5 * 354 + 3 * 355

assert PANJANG_WINDU == 2835


def dewataun(tahun):
    """
    Menghasilkan informasi Dewataun berdasarkan siklus 8 tahun.

    Tahun 1921 merupakan tahun pertama Dewataun, yaitu Kebo.
    """

    indeks = (tahun - TAHUN_EPOCH) % 8

    nama, jenis, jumlah_hari = DEWATAUN[indeks]

    return {
        "nama": nama,
        "jenis": jenis,
        "panjang_normal": jumlah_hari,
        "indeks": indeks + 1,
    }


# ============================================================
# 4. SIKLUS TUNGGUL TAUN (120 TAHUN)
# ============================================================

PANJANG_TUNGGUL_TAUN = 120

# 15 windu dikurangi 1 hari
PANJANG_TUNGGUL = 15 * PANJANG_WINDU - 1

assert PANJANG_TUNGGUL == 42524


def tunggul_taun(tahun):
    """
    Menentukan posisi tahun dalam siklus Tunggul Taun.

    Tahun ke-120 dalam setiap siklus merupakan tahun
    pengecualian yang menggunakan panjang 354 hari.
    """

    if tahun < 1:
        raise ValueError("Tahun Caka harus lebih besar atau sama dengan 1.")

    nomor = ((tahun - 1) // PANJANG_TUNGGUL_TAUN) + 1

    tahun_awal = (
        (nomor - 1) * PANJANG_TUNGGUL_TAUN
    ) + 1

    tahun_akhir = nomor * PANJANG_TUNGGUL_TAUN

    posisi = tahun - tahun_awal + 1

    return {
        "nomor": nomor,
        "tahun_awal": tahun_awal,
        "tahun_akhir": tahun_akhir,
        "posisi": posisi,
    }


# ============================================================
# 5. MENENTUKAN PANJANG TAHUN
# ============================================================

def panjang_tahun(tahun):
    """
    Menghasilkan jumlah hari dalam satu tahun Caka Sunda.

    Wastu = 354 hari
    Wuntu = 355 hari

    Pengecualian:
    Tahun ke-120 dalam siklus Tunggul Taun = 354 hari.
    """

    info_tunggul = tunggul_taun(tahun)

    # Tahun terakhir dalam siklus 120 tahun
    if info_tunggul["posisi"] == 120:
        return 354

    info_dewataun = dewataun(tahun)

    return info_dewataun["panjang_normal"]


# ============================================================
# 6. MENENTUKAN PANJANG BULAN
# ============================================================

def panjang_bulan(tahun, bulan):
    """
    Menentukan panjang bulan berdasarkan tahun Caka.

    Bulan 1 sampai 11 mengikuti panjang tetap.
    Bulan 12 (Asuji) menyesuaikan panjang tahun.
    """

    if not isinstance(bulan, int) or not 1 <= bulan <= 12:
        raise ValueError("Nomor bulan harus berupa bilangan 1 sampai 12.")

    if bulan <= 11:
        return PANJANG_BULAN_NORMAL[bulan - 1]

    # Asuji
    if panjang_tahun(tahun) == 354:
        return 29

    return 30


# ============================================================
# 7. AKUMULASI HARI SEBELUM TAHUN
# ============================================================

def jumlah_hari_sebelum_tahun(tahun):
    """
    Menghitung jumlah hari dari epoch sampai awal tahun tertentu.

    Nilai positif berarti tahun berada setelah epoch.
    Nilai negatif berarti tahun berada sebelum epoch.
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
    """
    Menghitung jumlah hari dari awal tahun sampai awal bulan.
    """

    if not isinstance(bulan, int) or not 1 <= bulan <= 12:
        raise ValueError("Nomor bulan harus berupa bilangan 1 sampai 12.")

    total = 0

    for bln in range(1, bulan):
        total += panjang_bulan(tahun, bln)

    return total


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

    # print({
    #     "tanggal_masehi": tanggal_masehi,
    #     "tahun_hasil": tahun,
    #     "tahun_epoch": TAHUN_EPOCH,
    #     "selisih_epoch": (
    #             tanggal_masehi - TANGGAL_EPOCH_MASEHI
    #     ).days,
    #     "awal_tahun": tanggal_awal_tahun_masehi(tahun),
    #     "hari_ke_tahun": hari_ke_tahun,
    #     "panjang_tahun": jumlah_hari_tahun,
    #     "dewataun": info_dewataun["nama"],
    #     "tunggul": info_tunggul,
    # })


    # --------------------------------------------------------
    # F. HASIL KONVERSI
    # --------------------------------------------------------

    return {
        "tahun": tahun,
        "bulan": bulan,
        "nama_bulan": NAMA_BULAN[bulan - 1],
        "umur_bulan": panjang_bulan(tahun, bulan),
        "tanggal": tanggal,
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

    from datetime import timedelta

    selisih = jumlah_hari_sebelum_tahun(tahun)

    return TANGGAL_EPOCH_MASEHI + timedelta(days=selisih)


def tanggal_awal_bulan_masehi(tahun, bulan):
    """
    Menghitung tanggal Masehi untuk tanggal 1
    pada bulan Caka tertentu.
    """

    from datetime import timedelta

    awal_tahun = tanggal_awal_tahun_masehi(tahun)
    selisih = jumlah_hari_sebelum_bulan(tahun, bulan)

    return awal_tahun + timedelta(days=selisih)


def uji_batas_bulan(tahun, bulan):
    """
    Menguji hari terakhir suatu bulan dan hari pertama
    bulan berikutnya.
    """

    from datetime import timedelta

    awal_bulan = tanggal_awal_bulan_masehi(tahun, bulan)

    akhir_bulan = (
        awal_bulan
        + timedelta(days=panjang_bulan(tahun, bulan) - 1)
    )

    bulan_berikutnya = bulan + 1
    tahun_berikutnya = tahun

    if bulan_berikutnya > 12:
        bulan_berikutnya = 1
        tahun_berikutnya += 1

    awal_berikutnya = tanggal_awal_bulan_masehi(
        tahun_berikutnya,
        bulan_berikutnya
    )

    hasil_akhir = masehi_to_caka(akhir_bulan)
    hasil_awal = masehi_to_caka(awal_berikutnya)

    assert hasil_akhir["tahun"] == tahun
    assert hasil_akhir["bulan"] == bulan
    assert hasil_akhir["tanggal"] == panjang_bulan(tahun, bulan)

    assert hasil_awal["tahun"] == tahun_berikutnya
    assert hasil_awal["bulan"] == bulan_berikutnya
    assert hasil_awal["tanggal"] == 1

    assert awal_berikutnya == akhir_bulan + timedelta(days=1)

    return {
        "akhir_bulan_masehi": akhir_bulan,
        "awal_bulan_berikutnya": awal_berikutnya,
        "hasil_akhir": hasil_akhir,
        "hasil_awal": hasil_awal,
    }


def uji_batas_tahun(tahun):
    """
    Menguji akhir Asuji dan awal Kartika tahun berikutnya.
    """

    from datetime import timedelta

    awal_tahun = tanggal_awal_tahun_masehi(tahun)

    akhir_tahun = (
        awal_tahun
        + timedelta(days=panjang_tahun(tahun) - 1)
    )

    awal_tahun_berikutnya = tanggal_awal_tahun_masehi(
        tahun + 1
    )

    hasil_akhir = masehi_to_caka(akhir_tahun)
    hasil_awal = masehi_to_caka(awal_tahun_berikutnya)

    assert hasil_akhir["bulan"] == 12
    assert hasil_akhir["tanggal"] == panjang_bulan(tahun, 12)

    assert hasil_awal["tahun"] == tahun + 1
    assert hasil_awal["bulan"] == 1
    assert hasil_awal["tanggal"] == 1

    assert awal_tahun_berikutnya == akhir_tahun + timedelta(days=1)

    return {
        "tahun": tahun,
        "jenis_tahun": (
            "Wastu" if panjang_tahun(tahun) == 354 else "Wuntu"
        ),
        "akhir_asuji": akhir_tahun,
        "awal_kartika": awal_tahun_berikutnya,
        "tanggal_akhir": hasil_akhir["tanggal"],
    }


def uji_transisi_dewataun():
    """
    Menguji tiga peralihan Wastu ke Wuntu
    dalam satu siklus Dewataun.
    """

    tahun_wastu = [1921, 1924, 1927]

    for tahun in tahun_wastu:

        tahun_wuntu = tahun + 1

        assert panjang_tahun(tahun) == 354
        assert panjang_tahun(tahun_wuntu) == 355

        akhir_wastu = uji_batas_tahun(tahun)
        awal_wuntu = tanggal_awal_tahun_masehi(tahun_wuntu)

        assert akhir_wastu["tanggal_akhir"] == 29
        assert (
            akhir_wastu["awal_kartika"] == awal_wuntu
        )

    return True


def uji_tunggul_taun():
    """
    Menguji tahun ke-120 pada blok Tunggul Taun.
    """

    tahun = 2040

    info = tunggul_taun(tahun)

    assert info["nomor"] == 17
    assert info["posisi"] == 120

    # Tahun ke-120 dipaksa menjadi Wastu
    assert panjang_tahun(tahun) == 354
    assert panjang_bulan(tahun, 12) == 29

    hasil = uji_batas_tahun(tahun)

    assert hasil["tanggal_akhir"] == 29

    return hasil


def jalankan_pengujian_batas():

    print("\n" + "=" * 60)
    print("PENGUJIAN BATAS KALA CANDRA SUNDA")
    print("=" * 60)

    # 1. Kartika ke Margasira
    print("\n1. Batas Kartika ke Margasira")

    hasil = uji_batas_bulan(1921, 1)

    print("30 Kartika :", hasil["akhir_bulan_masehi"])
    print("1 Margasira:", hasil["awal_bulan_berikutnya"])

    # 2. Pergantian tahun Wastu ke Wuntu
    print("\n2. Pergantian Wastu ke Wuntu")

    for tahun in [1921, 1924, 1927]:

        hasil = uji_batas_tahun(tahun)

        print(
            f"{tahun} Wastu -> {tahun + 1} Wuntu:",
            hasil["akhir_asuji"],
            "->",
            hasil["awal_kartika"]
        )

    # 3. Pergantian tahun Wuntu ke Wastu
    print("\n3. Pergantian Wuntu ke Wastu")

    for tahun in [1922, 1925, 1928]:

        hasil = uji_batas_tahun(tahun)

        print(
            f"{tahun} Wuntu -> {tahun + 1} Wastu:",
            hasil["akhir_asuji"],
            "->",
            hasil["awal_kartika"]
        )

    # 4. Tunggul Taun tahun 2040
    print("\n4. Pengujian Tunggul Taun 2040")

    hasil = uji_tunggul_taun()

    print("Tahun Caka :", hasil["tahun"])
    print("Jenis      :", hasil["jenis_tahun"])
    print("29 Asuji   :", hasil["akhir_asuji"])
    print("1 Kartika  :", hasil["awal_kartika"])

    # 5. Pengujian transisi Dewataun
    print("\n5. Pengujian transisi Dewataun")

    assert uji_transisi_dewataun()

    print("Transisi Wastu ke Wuntu: LULUS")

    print("\n" + "=" * 60)
    print("SELURUH PENGUJIAN BATAS BERHASIL")
    print("=" * 60)

def uji_caka_to_masehi():

    print("\n" + "=" * 60)
    print("PENGUJIAN CAKA SUNDA KE MASEHI")
    print("=" * 60)

    daftar_uji = [
        (1921, 1, 1),    # Epoch
        (1921, 1, 30),   # Akhir Kartika
        (1921, 2, 1),    # Awal Margasira
        (1921, 12, 29),  # Akhir Asuji Wastu
        (1922, 12, 30),  # Akhir Asuji Wuntu
        (1948, 9, 19),   # 19 Asada
        (2040, 12, 29),  # Akhir Tunggul Taun
        (2041, 1, 1),    # Awal tahun berikutnya
    ]

    for tahun, bulan, tanggal in daftar_uji:

        hasil = caka_to_masehi(
            tahun,
            bulan,
            tanggal
        )

        print(
            f"{tanggal} {NAMA_BULAN[bulan - 1]} {tahun}"
            f" -> {hasil}"
        )

    print("\nPENGUJIAN SELESAI")


def uji_round_trip():

    print("\n" + "=" * 60)
    print("PENGUJIAN ROUND-TRIP")
    print("=" * 60)

    daftar_uji = [
        (1921, 1, 1),
        (1921, 1, 30),
        (1921, 2, 1),
        (1921, 12, 29),
        (1922, 12, 30),
        (1948, 9, 19),
        (2040, 12, 29),
        (2041, 1, 1),
    ]

    for tahun, bulan, tanggal in daftar_uji:

        # Caka -> Masehi
        masehi = caka_to_masehi(
            tahun,
            bulan,
            tanggal
        )

        # Masehi -> Caka
        hasil = masehi_to_caka(masehi)

        # Periksa kesamaan
        assert hasil["tahun"] == tahun
        assert hasil["bulan"] == bulan
        assert hasil["tanggal"] == tanggal

        print(
            f"{tanggal} {NAMA_BULAN[bulan - 1]} {tahun}"
            f" <-> {masehi} : LULUS"
        )

    print("\nSELURUH ROUND-TRIP LULUS")

def audit_batas_tunggul(tahun):
    """
    Memeriksa tahun terakhir suatu Tunggul dan
    tahun pertama Tunggul berikutnya.
    """

    awal = tanggal_awal_tahun_masehi(tahun)
    panjang = panjang_tahun(tahun)

    akhir = awal + timedelta(days=panjang - 1)
    awal_berikutnya = tanggal_awal_tahun_masehi(tahun + 1)

    hasil = {
        "tahun": tahun,
        "awal_tahun": awal,
        "panjang_tahun": panjang,
        "akhir_tahun": akhir,
        "awal_tahun_berikutnya": awal_berikutnya,
        "selisih": (
            awal_berikutnya - (akhir + timedelta(days=1))
        ).days,
        "tunggul": tunggul_taun(tahun),
        "dewataun": dewataun(tahun),
    }

    print("=" * 60)
    print(f"AUDIT TAHUN {tahun}")
    print("=" * 60)
    print("Awal tahun          :", hasil["awal_tahun"])
    print("Panjang tahun       :", hasil["panjang_tahun"])
    print("Akhir tahun         :", hasil["akhir_tahun"])
    print("Awal tahun berikut  :", hasil["awal_tahun_berikutnya"])
    print("Selisih             :", hasil["selisih"], "hari")
    print("Tunggul             :", hasil["tunggul"])
    print("Dewataun            :", hasil["dewataun"])

    return hasil

def kalacandra_sunda(tanggal_masehi):

    hasil = masehi_to_caka(tanggal_masehi)
    tanggal_paksa = format_tanggal_caka(hasil)
    
    return {
        "tanggal_masehi": tanggal_masehi,
        "tanggal_caka": f"{tanggal_paksa['tanggal_paksa']} {hasil['nama_bulan']} {hasil['tahun']}",
        "bulan": hasil["nama_bulan"],
        "tahun": hasil["tahun"],
        "tanggal": hasil["tanggal"],
        "hari_ke_tahun": hasil["hari_ke_tahun"],
        "panjang_tahun": hasil["panjang_tahun"],
        "jenis_tahun": hasil["jenis_tahun"],
        "dewataun": hasil["dewataun"],
        "tunggul_taun": hasil["tunggul_taun"],
        "posisi_tunggul": hasil["posisi_tunggul"],
        "umur_bulan": hasil["umur_bulan"],
        "tanggal_paksa": tanggal_paksa,
        "paksa": tanggal_paksa["paksa"],
        "istilah": tanggal_paksa["istilah"]
    }


if __name__ == "__main__":

    print("=" * 60)
    print("PENGUJIAN KALA CANDRA SUNDA")
    print("=" * 60)

    daftar_uji = [
        "1999-12-11", "2000-11-29", "2001-11-18", "2002-11-07", "2003-10-27", "2004-10-16", "2005-10-05", "2006-09-24",
    "2007-09-15", "2006-09-03","2114-06-16", "2115-05-27", "2116-05-16"
    ]

    for tanggal_masehi in daftar_uji:

        hasil = masehi_to_caka(tanggal_masehi)

        print()
        print("Tanggal Masehi :", tanggal_masehi)
        print("Tanggal Caka   :", f"{format_tanggal_caka(hasil)}")
        print("Tahun          :", hasil["tahun"])
        print("Bulan          :", hasil["nama_bulan"])
        print("Umur Bulan     :", hasil["umur_bulan"])
        print("Tanggal        :", hasil["tanggal"])
        print("Hari ke tahun  :", hasil["hari_ke_tahun"])
        print("Panjang tahun  :", hasil["panjang_tahun"])
        print("Jenis tahun    :", hasil["jenis_tahun"])
        print("Dewataun       :", hasil["dewataun"])
        print("Tunggul Taun   :", hasil["tunggul_taun"])
        print("Posisi Tunggul :", hasil["posisi_tunggul"])

    print()
    print("=" * 60)
    print("PENGUJIAN SELESAI")
    print("=" * 60)

    # jalankan_pengujian_batas()
    # uji_caka_to_masehi()
    # uji_round_trip()

    # print("=" * 60)
    # print("PENGUJIAN BATAS TUNGGUL KALA CANDRA SUNDA")
    # print("=" * 60)
    # audit_batas_tunggul(2040)
    # audit_batas_tunggul(2160)

    # for tgl in [
    #     date(2054, 5, 27),
    #     date(2055, 5, 16),
    # ]:
    #     hasil = masehi_to_caka(tgl)

    #     awal = tanggal_awal_tahun_masehi(
    #         hasil["tahun"]
    #     )

    #     hari_absolut = (tgl - awal).days + 1

    #     print("-" * 50)
    #     print("Tanggal Masehi :", tgl)
    #     print("Tahun Caka     :", hasil["tahun"])
    #     print("Awal tahun     :", awal)
    #     print("Hari ke tahun  :", hasil["hari_ke_tahun"])
    #     print("Hari absolut   :", hari_absolut)
    #     print("Panjang tahun  :", hasil["panjang_tahun"])