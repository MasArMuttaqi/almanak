"""
surya_kala_sunda.py
Mesin kalender Kala Surya Sunda berbasis epoch tetap dan interkalasi 128 tahun.

Model kerja:
- 1 Kasa tahun 1 = JDN 1_749_905 = 22-12-0078 Gregorian proleptik.
- Taun Panjang: tahun habis dibagi 4, kecuali habis dibagi 128 (366 hari).
- Taun Pondok: selain itu (365 hari).
- Hari tambahan ditempatkan pada bulan ke-12, Hapitkayu (31 hari pada
  Taun Panjang; 30 hari pada Taun Pondok).
- Solstis Desember adalah landasan astronomis/validasi, bukan pemicu
  perubahan tanggal kalender dari tahun ke tahun.

Epoch adalah epoch kerja berdasarkan data acuan proyek dan masih terbuka
untuk verifikasi historis. Kalender Gregorian yang dipakai adalah
Gregorian proleptik. JDN memakai bilangan bulat tanggal sipil.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

# -------------------- KONFIGURASI --------------------

NAMA_KALENDER = "Kala Surya Sunda"
EPOCH_JDN = 1_749_905
HARI_PER_DAUR = 46_751
PANJANG_DAUR = 128

# Nama dan panjang dasar bulan. Hari interkalasi masuk ke bulan ke-12.
BULAN = (
    ("Kasa", 30),
    ("Karo", 31),
    ("Katiga", 30),
    ("Kapat", 31),
    ("Kalima", 30),
    ("Kanem", 31),
    ("Kapitu", 30),
    ("Kawalu", 31),
    ("Kasanga", 30),
    ("Kadasa", 31),
    ("Hapit Lemah", 30),
    ("Hapitkayu", 30),
)
NAMA_BULAN = tuple(x[0] for x in BULAN)


@dataclass(frozen=True)
class TanggalSunda:
    tahun: int
    bulan: int
    nama_bulan: str
    tanggal: int
    jenis_tahun: str
    jumlah_hari_tahun: int
    jdn: int

    def sebagai_dict(self) -> Dict[str, object]:
        return asdict(self)

    def __str__(self) -> str:
        return f"{self.tanggal} {self.nama_bulan} {self.tahun} Saka Sunda"


# -------------------- VALIDASI DAN ATURAN TAHUN --------------------

def _validasi_tahun(tahun: int) -> None:
    if not isinstance(tahun, int) or isinstance(tahun, bool):
        raise TypeError("Tahun Saka Sunda harus berupa integer.")
    if tahun < 1:
        raise ValueError("Tahun Saka Sunda harus >= 1.")


def taun_panjang(tahun: int) -> bool:
    """True jika tahun habis dibagi 4, tetapi tidak habis dibagi 128."""
    _validasi_tahun(tahun)
    return tahun % 4 == 0 and tahun % 128 != 0


def jenis_tahun(tahun: int) -> str:
    return "Taun Panjang" if taun_panjang(tahun) else "Taun Pondok"


def jumlah_hari_tahun(tahun: int) -> int:
    return 366 if taun_panjang(tahun) else 365


def hari_sebelum_tahun(tahun: int) -> int:
    """Jumlah hari sebelum 1 Kasa tahun Y, relatif terhadap epoch tahun 1."""
    _validasi_tahun(tahun)
    n = tahun - 1
    return 365 * n + n // 4 - n // 128


def informasi_daur_128() -> Dict[str, int]:
    return {
        "jumlah_tahun": 128,
        "tahun_panjang": 31,
        "tahun_pondok": 97,
        "jumlah_hari": 31 * 366 + 97 * 365,
    }


# -------------------- BULAN --------------------

def panjang_bulan(tahun: int, bulan: int) -> int:
    _validasi_tahun(tahun)
    if not isinstance(bulan, int) or isinstance(bulan, bool):
        raise TypeError("Nomor bulan harus berupa integer.")
    if not 1 <= bulan <= 12:
        raise ValueError("Nomor bulan harus 1 sampai 12.")
    if bulan == 12 and taun_panjang(tahun):
        return 31
    return BULAN[bulan - 1][1]


def daftar_bulan(tahun: int) -> List[Dict[str, object]]:
    _validasi_tahun(tahun)
    return [
        {"nomor": i, "nama": nama, "jumlah_hari": panjang_bulan(tahun, i)}
        for i, (nama, _) in enumerate(BULAN, start=1)
    ]


def hari_sebelum_bulan(tahun: int, bulan: int) -> int:
    if not 1 <= bulan <= 12:
        raise ValueError("Nomor bulan harus 1 sampai 12.")
    return sum(panjang_bulan(tahun, i) for i in range(1, bulan))


# -------------------- KALENDER SUNDA -> JDN --------------------

def sunda_ke_jdn(tahun: int, bulan: int, tanggal: int) -> int:
    _validasi_tahun(tahun)
    if not isinstance(tanggal, int) or isinstance(tanggal, bool):
        raise TypeError("Tanggal harus berupa integer.")
    batas = panjang_bulan(tahun, bulan)
    if not 1 <= tanggal <= batas:
        raise ValueError(
            f"Tanggal tidak valid. {NAMA_BULAN[bulan - 1]} "
            f"tahun {tahun} maksimum {batas} hari."
        )
    return (
        EPOCH_JDN
        + hari_sebelum_tahun(tahun)
        + hari_sebelum_bulan(tahun, bulan)
        + tanggal - 1
    )


# -------------------- GREGORIAN <-> JDN --------------------

def _kabisat_gregorian(tahun: int) -> bool:
    return tahun % 4 == 0 and (tahun % 100 != 0 or tahun % 400 == 0)


def gregorian_ke_jdn(tahun: int, bulan: int, tanggal: int) -> int:
    """Konversi Gregorian proleptik ke JDN integer."""
    if not all(isinstance(v, int) and not isinstance(v, bool)
               for v in (tahun, bulan, tanggal)):
        raise TypeError("Komponen tanggal Gregorian harus integer.")
    if tahun < 1 or not 1 <= bulan <= 12:
        raise ValueError("Tahun atau bulan Gregorian tidak valid.")
    hari_bulan = [31, 29 if _kabisat_gregorian(tahun) else 28,
                  31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not 1 <= tanggal <= hari_bulan[bulan - 1]:
        raise ValueError("Tanggal Gregorian tidak valid.")

    a = (14 - bulan) // 12
    y = tahun + 4800 - a
    m = bulan + 12 * a - 3
    return (tanggal + (153 * m + 2) // 5 + 365 * y + y // 4
            - y // 100 + y // 400 - 32045)


def jdn_ke_gregorian(jdn: int) -> Tuple[int, int, int]:
    """Konversi JDN integer ke (tahun, bulan, tanggal) Gregorian."""
    if not isinstance(jdn, int) or isinstance(jdn, bool):
        raise TypeError("JDN harus berupa integer.")
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    tanggal = e - (153 * m + 2) // 5 + 1
    bulan = m + 3 - 12 * (m // 10)
    tahun = 100 * b + d - 4800 + m // 10
    return tahun, bulan, tanggal


# -------------------- JDN -> KALENDER SUNDA --------------------

def jdn_ke_sunda(jdn: int) -> TanggalSunda:
    if not isinstance(jdn, int) or isinstance(jdn, bool):
        raise TypeError("JDN harus berupa integer.")
    selisih = jdn - EPOCH_JDN
    if selisih < 0:
        raise ValueError("Tanggal berada sebelum epoch kalender.")

    daur, sisa = divmod(selisih, HARI_PER_DAUR)
    tahun_awal = daur * PANJANG_DAUR + 1

    indeks = 0
    while indeks < PANJANG_DAUR:
        tahun_calon = tahun_awal + indeks
        panjang = jumlah_hari_tahun(tahun_calon)
        if sisa < panjang:
            break
        sisa -= panjang
        indeks += 1
    if indeks == PANJANG_DAUR:
        raise RuntimeError("Tidak dapat menentukan tahun.")

    tahun = tahun_awal + indeks
    bulan = 1
    while bulan <= 12:
        panjang = panjang_bulan(tahun, bulan)
        if sisa < panjang:
            break
        sisa -= panjang
        bulan += 1
    if bulan > 12:
        raise RuntimeError("Tidak dapat menentukan bulan.")

    return TanggalSunda(
        tahun=tahun,
        bulan=bulan,
        nama_bulan=NAMA_BULAN[bulan - 1],
        tanggal=sisa + 1,
        jenis_tahun=jenis_tahun(tahun),
        jumlah_hari_tahun=jumlah_hari_tahun(tahun),
        jdn=jdn,
    )


# -------------------- FUNGSI KONVERSI PUBLIK --------------------

def konversi_sunda_ke_masehi(
    tahun: int, bulan: int, tanggal: int
) -> Dict[str, object]:
    jdn = sunda_ke_jdn(tahun, bulan, tanggal)
    y, m, d = jdn_ke_gregorian(jdn)
    return {
        "tanggal_sunda": str(jdn_ke_sunda(jdn)),
        "tahun_masehi": y,
        "bulan_masehi": m,
        "tanggal_masehi": d,
        "tanggal_iso": f"{y:04d}-{m:02d}-{d:02d}",
        "jdn": jdn,
    }


def konversi_masehi_ke_sunda(
    tahun: int, bulan: int, tanggal: int
) -> Dict[str, object]:
    jdn = gregorian_ke_jdn(tahun, bulan, tanggal)
    hasil = jdn_ke_sunda(jdn)
    return {
        "tanggal_sunda": str(hasil),
        "tahun_saka": hasil.tahun,
        "bulan_sunda": hasil.bulan,
        "nama_bulan": hasil.nama_bulan,
        "tanggal_sunda_angka": hasil.tanggal,
        "jenis_tahun": hasil.jenis_tahun,
        "jumlah_hari_tahun": hasil.jumlah_hari_tahun,
        "jdn": jdn,
    }


def informasi_tahun(tahun: int) -> Dict[str, object]:
    _validasi_tahun(tahun)
    awal_jdn = EPOCH_JDN + hari_sebelum_tahun(tahun)
    akhir_jdn = awal_jdn + jumlah_hari_tahun(tahun) - 1
    ay, am, ad = jdn_ke_gregorian(awal_jdn)
    ey, em, ed = jdn_ke_gregorian(akhir_jdn)
    return {
        "tahun_saka": tahun,
        "jenis_tahun": jenis_tahun(tahun),
        "jumlah_hari": jumlah_hari_tahun(tahun),
        "jdn_awal": awal_jdn,
        "jdn_akhir": akhir_jdn,
        "awal_masehi": f"{ad:02d}-{am:02d}-{ay:04d}",
        "akhir_masehi": f"{ed:02d}-{em:02d}-{ey:04d}",
        "bulan": daftar_bulan(tahun),
    }


def tabel_tahun_panjang(
    tahun_mulai: int, tahun_selesai: int
) -> List[Dict[str, object]]:
    _validasi_tahun(tahun_mulai)
    _validasi_tahun(tahun_selesai)
    if tahun_selesai < tahun_mulai:
        raise ValueError("Rentang tahun tidak valid.")

    hasil = []
    for tahun in range(tahun_mulai, tahun_selesai + 1):
        if taun_panjang(tahun):
            info = informasi_tahun(tahun)
            hasil.append({
                "tahun_saka": tahun,
                "awal_masehi": info["awal_masehi"],
                "durasi": info["jumlah_hari"],
                "jdn_awal": info["jdn_awal"],
            })
    return hasil


# -------------------- PENGUJIAN --------------------

def jalankan_pengujian() -> None:
    assert informasi_daur_128()["jumlah_hari"] == 46_751
    assert informasi_daur_128()["tahun_panjang"] == 31
    assert informasi_daur_128()["tahun_pondok"] == 97
    assert not taun_panjang(1920)
    assert taun_panjang(1948)
    assert gregorian_ke_jdn(2025, 12, 21) == 2_461_031
    assert sunda_ke_jdn(1948, 1, 1) == 2_461_031
    assert sunda_ke_jdn(1947, 12, 30) == 2_461_030
    assert jdn_ke_gregorian(EPOCH_JDN) == (78, 12, 22)

    for y, m, d in [
        (1, 1, 1), (1920, 12, 30), (1947, 12, 30),
        (1948, 1, 1), (1948, 12, 31),
    ]:
        hasil = jdn_ke_sunda(sunda_ke_jdn(y, m, d))
        assert (hasil.tahun, hasil.bulan, hasil.tanggal) == (y, m, d)

    for y, m, d in [
        (78, 12, 22), (1901, 12, 21), (1997, 12, 21),
        (2025, 12, 21), (2030, 6, 15),
    ]:
        assert jdn_ke_gregorian(gregorian_ke_jdn(y, m, d)) == (y, m, d)

    print("Semua pengujian Kala Surya Sunda berhasil.")


if __name__ == "__main__":
    jalankan_pengujian()
    print("\nDaur 128 tahun:", informasi_daur_128())
    print("1 Kasa 1948:", konversi_sunda_ke_masehi(1948, 1, 1))
    print("1 November 2026:", konversi_masehi_ke_sunda(2026, 11, 1))
    print("Informasi tahun 1948:", informasi_tahun(1948))
