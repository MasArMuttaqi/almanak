"""
Kalkulator jadwal salat — implementasi astronomi modern yang mengikuti
urutan kerja pada PDF (Darojatus Syams, Mail Awal, Bu'dul Quthri,
Asal Mutlaq/Nisful Fudlah, lalu waktu salat).

PENTING:
- Ini bukan transkripsi numerik 1:1 metode tabel log-sin pada buku.
- PDF menggunakan tabel log-sin dan jadwal Ardul Balad yang tidak ikut
  terbaca/tersedia lengkap. Script ini memakai rumus astronomi trigonometri
  modern sebagai pengganti yang dapat diuji.
- Parameter sudut Subuh (-19°), Isya (-17°), Dhuha (+4°30'), koreksi
  terbit/terbenam (-0.833°), tamkin Magrib 3m30s, dan Imsak dapat diubah.
- Hasil adalah estimasi; validasi dengan otoritas/jadwal setempat diperlukan.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from math import sin, cos, tan, asin, acos, atan, radians, degrees, floor
from zoneinfo import ZoneInfo


@dataclass
class Lokasi:
    nama: str
    lintang: float       # derajat; utara positif, selatan negatif
    bujur: float         # derajat; timur positif, barat negatif
    zona: str = "Asia/Jakarta"


@dataclass
class ParameterSalat:
    sudut_subuh: float = 19.0       # Matahari 19° di bawah ufuk
    sudut_isya: float = 17.0        # Matahari 17° di bawah ufuk
    sudut_dhuha: float = 4.5        # Matahari 4°30' di atas ufuk
    tinggi_matahari_terbit: float = -0.833  # refraksi + semidiameter (aproksimasi)
    tamkin_magrib_menit: float = 3.5
    imsak_menit_sebelum_subuh: float = 10.0
    ihtiyat_menit: float = 0.0
    faktor_asar: float = 1.0        # 1 = bayangan sama panjang + bayangan saat zawal


class d:
    """Pembungkus jadwal salat yang dapat di-serialisasi dan diformat."""

    def __init__(self, tanggal, lokasi, parameter=None):
        if isinstance(tanggal, str):
            tanggal = date.fromisoformat(tanggal)
        self.tanggal = tanggal
        self.lokasi = lokasi
        self.parameter = parameter or ParameterSalat()

    def jadwal(self):
        """Kembalikan hasil jadwal sebagai dictionary yang siap dipakai."""
        return hitung_jadwal(self.tanggal, self.lokasi, self.parameter)

    def as_dict(self):
        """Versi data jadwal yang aman untuk JSON atau penyimpanan."""
        return self.jadwal()

    @classmethod
    def from_dict(cls, payload, lokasi=None, parameter=None):
        """Bangun objek d dari data jadwal hasil hitung_jadwal()."""
        tanggal = payload.get("tanggal")
        lokasi_obj = lokasi or Lokasi(
            nama=payload.get("lokasi", "Lokasi tidak dikenal"),
            lintang=float(payload.get("lintang", 0.0)),
            bujur=float(payload.get("bujur", 0.0)),
            zona=payload.get("zona", "Asia/Jakarta"),
        )
        return cls(tanggal=tanggal, lokasi=lokasi_obj, parameter=parameter)

    def __str__(self):
        jadwal = self.jadwal()
        baris = [
            f"Jadwal shalat {jadwal['tanggal']}",
            f"lokasi: {jadwal['lokasi']}",
            f"koordinat: {jadwal['lintang']}, {jadwal['bujur']}",
        ]
        for nama in ("Imsak", "Subuh", "Terbit", "Dhuha", "Zuhur", "Asar", "Magrib", "Isya"):
            value = jadwal["waktu"][nama]
            baris.append(f"{nama:8s}: {value or 'Tidak terdefinisi pada tanggal/lokasi ini'}")
        return "\n".join(baris)


def _normalisasi_menit(menit):
    """Normalisasi menit ke rentang [0, 1440)."""
    return menit % 1440


def _format_waktu(menit, zona, tanggal):
    """Format waktu lokal HH:MM:SS; tanggal dapat bergeser lintas tengah malam."""
    menit = _normalisasi_menit(menit)
    detik_total = round(menit * 60)
    jam, sisa = divmod(detik_total, 3600)
    menit_bulat, detik = divmod(sisa, 60)
    return f"{jam:02d}:{menit_bulat:02d}:{detik:02d}"


def _parameter_matahari(tgl: date):
    """
    Aproksimasi NOAA untuk deklinasi Matahari dan equation of time.
    Return: deklinasi (derajat), equation of time (menit).
    """
    n = tgl.timetuple().tm_yday
    gamma = 2.0 * 3.141592653589793 / 365.0 * (n - 1)
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * cos(gamma)
        - 0.032077 * sin(gamma)
        - 0.014615 * cos(2 * gamma)
        - 0.040849 * sin(2 * gamma)
    )
    decl = (
        0.006918
        - 0.399912 * cos(gamma)
        + 0.070257 * sin(gamma)
        - 0.006758 * cos(2 * gamma)
        + 0.000907 * sin(2 * gamma)
        - 0.002697 * cos(3 * gamma)
        + 0.00148 * sin(3 * gamma)
    )
    return degrees(decl), eqtime


def _sudut_jam(tinggi_derajat, lintang, deklinasi):
    """
    Sudut jam untuk tinggi Matahari tertentu.
    cos(H) = sin(h) - sin(phi) sin(delta)
             --------------------------------
                    cos(phi) cos(delta)
    Return derajat; None jika Matahari tidak mencapai tinggi tersebut.
    """
    phi, dec, h = radians(lintang), radians(deklinasi), radians(tinggi_derajat)
    penyebut = cos(phi) * cos(dec)
    if abs(penyebut) < 1e-12:
        return None
    x = (sin(h) - sin(phi) * sin(dec)) / penyebut
    if x < -1.0 or x > 1.0:
        return None
    return degrees(acos(x))


def _waktu_zawal_menit(tgl, lokasi, eqtime):
    """Waktu kulminasi atas dalam menit dari tengah malam waktu lokal."""
    offset = datetime(tgl.year, tgl.month, tgl.day, tzinfo=ZoneInfo(lokasi.zona)).utcoffset()
    zona_jam = offset.total_seconds() / 3600
    return 720 - 4 * lokasi.bujur - eqtime + 60 * zona_jam


def hitung_jadwal(tgl: date, lokasi: Lokasi,
                  parameter: ParameterSalat = ParameterSalat()):
    """
    Menghitung Imsak, Subuh, Terbit, Dhuha, Zuhur, Asar, Magrib, Isya.
    tgl harus datetime.date; koordinat dalam derajat desimal.
    """
    if not -90 <= lokasi.lintang <= 90:
        raise ValueError("Lintang harus berada pada -90 sampai 90 derajat.")
    if not -180 <= lokasi.bujur <= 180:
        raise ValueError("Bujur harus berada pada -180 sampai 180 derajat.")

    dec, eqtime = _parameter_matahari(tgl)
    zawal = _waktu_zawal_menit(tgl, lokasi, eqtime)
    hasil = {"Zuhur": zawal}

    # Sudut jam untuk tiap tinggi Matahari.
    h_subuh = _sudut_jam(-parameter.sudut_subuh, lokasi.lintang, dec)
    h_isya = _sudut_jam(-parameter.sudut_isya, lokasi.lintang, dec)
    h_terbit = _sudut_jam(parameter.tinggi_matahari_terbit, lokasi.lintang, dec)
    h_dhuha = _sudut_jam(parameter.sudut_dhuha, lokasi.lintang, dec)

    hasil["Subuh"] = None if h_subuh is None else zawal - 4 * h_subuh
    hasil["Terbit"] = None if h_terbit is None else zawal - 4 * h_terbit
    hasil["Dhuha"] = None if h_dhuha is None else zawal - 4 * h_dhuha
    hasil["Magrib"] = None if h_terbit is None else zawal + 4 * h_terbit + parameter.tamkin_magrib_menit
    hasil["Isya"] = None if h_isya is None else zawal + 4 * h_isya

    # Asar: cot(tinggi Asar) = faktor + tan(|lintang - deklinasi|)
    phi, d = radians(lokasi.lintang), radians(dec)
    tinggi_asar = degrees(atan(1.0 / (parameter.faktor_asar + tan(abs(phi - d)))))
    h_asar = _sudut_jam(tinggi_asar, lokasi.lintang, dec)
    hasil["Asar"] = None if h_asar is None else zawal + 4 * h_asar

    # Imsak adalah interval sebelum Subuh; interval perlu dipilih sesuai pakem lokal.
    hasil["Imsak"] = (
        None if hasil["Subuh"] is None
        else hasil["Subuh"] - parameter.imsak_menit_sebelum_subuh
    )

    # Ihtiyat ditambahkan ke waktu-waktu salat utama; Terbit tidak ditambah.
    for nama in ("Imsak", "Subuh", "Dhuha", "Zuhur", "Asar", "Magrib", "Isya"):
        if hasil[nama] is not None:
            hasil[nama] += parameter.ihtiyat_menit

    return {
        "tanggal": tgl.isoformat(),
        "lokasi": lokasi.nama,
        "lintang": lokasi.lintang,
        "bujur": lokasi.bujur,
        "zona": lokasi.zona,
        "deklinasi_matahari_derajat": round(dec, 6),
        "equation_of_time_menit": round(eqtime, 4),
        "waktu_menit": hasil,
        "waktu": {
            nama: None if menit is None else _format_waktu(menit, lokasi.zona, tgl)
            for nama, menit in hasil.items()
        },
    }


if __name__ == "__main__":
    # Contoh: Surabaya (koordinat dapat diganti sesuai markaz yang dipakai).
    lokasi = Lokasi(
        nama="Surabaya",
        lintang=-7.2575,
        bujur=112.7521,
        zona="Asia/Jakarta",
    )
    tanggal_hitung = date(2026, 10, 27)
    parameter = ParameterSalat(
        sudut_subuh=19.0,
        sudut_isya=17.0,
        sudut_dhuha=4.5,
        tamkin_magrib_menit=3.5,
        imsak_menit_sebelum_subuh=10.0,
        ihtiyat_menit=0.0,
    )
    jadwal = hitung_jadwal(tanggal_hitung, lokasi, parameter)

    print(f"Jadwal shalat {jadwal['tanggal']}")
    print(f"lokasi: {jadwal['lokasi']}")
    print(f"koordinat: {jadwal['lintang']}, {jadwal['bujur']}")
    print(f"Deklinasi Matahari: {jadwal['deklinasi_matahari_derajat']}°")
    print(f"Equation of time: {jadwal['equation_of_time_menit']} menit")
    for nama in ("Imsak", "Subuh", "Terbit", "Dhuha", "Zuhur", "Asar", "Magrib", "Isya"):
        print(f"{nama:8s}: {jadwal['waktu'][nama] or 'Tidak terdefinisi pada tanggal/lokasi ini'}")
