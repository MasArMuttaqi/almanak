from math import sin, cos, tan, asin, acos, atan2, radians, degrees, floor
from datetime import datetime, timedelta
import json
from konversitanggal import format_tanggal_indonesia


# ============================================================
# KONFIGURASI LOKASI
# ============================================================

LAT = -7.7974565
LON = 110.370697
TZ = 7


# ============================================================
# BACA FILE KOREKSI RUKYAH
# ============================================================

with open("data/koreksirukyah.json", "r") as c:
    HIJRI_CORRECTION = json.load(c)


bulan_hijri = [
    "Muharram",
    "Safar",
    "Rabiul Awal",
    "Rabiul Akhir",
    "Jumadil Awal",
    "Jumadil Akhir",
    "Rajab",
    "Syaban",
    "Ramadhan",
    "Syawal",
    "Dzulqaidah",
    "Dzulhijjah"
]

# ============================================================
# POLA HISAB URFI
# ============================================================

PANJANG_BULAN_URFI = [
    30,  # 1  Muharam
    29,  # 2  Safar
    30,  # 3  Rabiulawal
    29,  # 4  Rabiulakhir
    30,  # 5  Jumadilawal
    29,  # 6  Jumadilakhir
    30,  # 7  Rajab
    29,  # 8  Syakban
    30,  # 9  Ramadan
    29,  # 10 Syawal
    30,  # 11 Zulkaidah
    29   # 12 Zulhijah
]


# ============================================================
# TAHUN HIJRIAH KABISAT
# ============================================================

def tahun_hijri_kabisat(tahun):
    """
    Siklus Hisab Urfi 30 tahun.

    Tahun kabisat:
    2, 5, 7, 10, 13, 15,
    18, 21, 24, 26, 29
    """

    siklus = tahun % 30

    if siklus == 0:
        siklus = 30

    return siklus in {
        2, 5, 7, 10, 13,
        15, 18, 21, 24,
        26, 29
    }


# ============================================================
# JUMLAH HARI BULAN HISAB URFI
# ============================================================

def jumlah_hari_bulan_urfi(tahun, bulan):

    # Zulhijah menjadi 30 hari pada tahun kabisat
    if bulan == 12:

        if tahun_hijri_kabisat(tahun):
            return 30

        return 29

    return PANJANG_BULAN_URFI[bulan - 1]


# ============================================================
# FORMAT DURASI
# ============================================================
def durasi_jam(jd_awal, jd_akhir):

    if jd_awal is None or jd_akhir is None:
        return None

    return (
        jd_akhir - jd_awal
    ) * 24

def format_durasi(jam):

    if jam is None:
        return None

    total_menit = round(jam * 60)

    hari = total_menit // (24 * 60)

    sisa = total_menit % (24 * 60)

    jam_baru = sisa // 60
    menit = sisa % 60

    if hari > 0:
        return f"{hari} hari {jam_baru} jam {menit} menit"

    return f"{jam_baru} jam {menit} menit"

def format_jam_desimal(jam):

    if jam is None:
        return None

    jam = jam % 24

    h = int(jam)

    menit = int(
        (jam - h) * 60
    )

    detik = round(
        (
            (jam - h) * 60
            - menit
        ) * 60
    )

    if detik >= 60:
        detik = 0
        menit += 1

    if menit >= 60:
        menit = 0
        h += 1

    h %= 24

    return f"{h:02d}:{menit:02d}:{detik:02d}"

def jam_desimal_ke_jd(y, m, d, jam_desimal):
    return julian_day(
        y,
        m,
        d,
        jam_desimal
    )
# ============================================================
# KONVERSI MASEHI → HIJRIAH BERDASARKAN ANCHOR
# ============================================================
def masehi_to_hijri_json(target_date):

    target = datetime.strptime(
        target_date,
        "%Y-%m-%d"
    )

    # ========================================================
    # BACA SEMUA ANCHOR KOREKSI RUKYAH
    # ========================================================

    anchors = []

    for key, value in HIJRI_CORRECTION.items():

        try:

            hy, hm = map(
                int,
                key.split("-")
            )

            base_date = datetime.strptime(
                value,
                "%Y-%m-%d"
            )

            anchors.append(
                (
                    base_date,
                    hy,
                    hm
                )
            )

        except (ValueError, TypeError):

            continue

    # ========================================================
    # TIDAK ADA DATA KOREKSI
    # ========================================================

    if not anchors:
        return "-", "-", "-"

    # ========================================================
    # URUTKAN BERDASARKAN TANGGAL MASEHI
    # ========================================================

    anchors.sort(
        key=lambda x: x[0]
    )

    # ========================================================
    # CARI ANCHOR BULAN YANG BERLAKU
    # ========================================================

    current_index = None

    for i, anchor in enumerate(anchors):

        if target >= anchor[0]:

            current_index = i

        else:

            break

    # Belum mencapai anchor pertama
    if current_index is None:
        return "-", "-", "-"

    base_date, hy, hm = anchors[current_index]

    # ========================================================
    # CARI ANCHOR BERIKUTNYA
    # ========================================================

    next_anchor = None

    if current_index + 1 < len(anchors):

        next_anchor = anchors[current_index + 1]

    # ========================================================
    # JUMLAH HARI BULAN
    #
    # PRIORITAS:
    #
    # 1. Jika anchor bulan berikutnya tersedia:
    #    gunakan selisih tanggal koreksi rukyah.
    #
    # 2. Jika tidak tersedia:
    #    gunakan pola Hisab Urfi.
    # ========================================================

    if next_anchor is not None:

        next_date = next_anchor[0]

        jumlah_hari_bulan = ( next_date - base_date ).days

    else:

        jumlah_hari_bulan = (
            jumlah_hari_bulan_urfi(
                hy,
                hm
            )
        )

    # ========================================================
    # HITUNG HARI HIJRIAH
    # ========================================================

    day = ( target - base_date).days + 1

    # ========================================================
    # VALIDASI HARI
    # ========================================================

    if day < 1:

        return "-", "-", "-"

    # ========================================================
    # JIKA MELEBIHI PANJANG BULAN
    # ========================================================

    if day > jumlah_hari_bulan:

        # ----------------------------------------------------
        # Jika sudah masuk anchor berikutnya,
        # gunakan anchor tersebut.
        # ----------------------------------------------------

        if (
            next_anchor is not None
            and target >= next_anchor[0]
        ):

            return masehi_to_hijri_json(
                target_date
            )

        return "-", "-", "-"

    # ========================================================
    # NAMA BULAN
    # ========================================================

    nama_bulan = bulan_hijri[hm - 1]

    # ========================================================
    # HASIL
    # ========================================================

    return (
        day,
        nama_bulan,
        hy
    )
# ============================================================
# JULIAN DAY
# ============================================================

def julian_day(y, m, d, h=0):

    if m <= 2:

        y -= 1
        m += 12

    A = floor(y / 100)

    B = 2 - A + floor(A / 4)

    jd = (
        floor(365.25 * (y + 4716))
        + floor(30.6001 * (m + 1))
        + d
        + B
        - 1524.5
    )

    jd += h / 24

    return jd


# ============================================================
# SUN POSITION
# ============================================================

def sun_position(jd):

    T = (jd - 2451545.0) / 36525

    L0 = (
        280.46646
        + 36000.76983 * T
    ) % 360

    M = radians(
        (357.52911 + 35999.05029 * T) % 360
    )

    C = (
        (1.914602 - 0.004817 * T) * sin(M)
        + 0.019993 * sin(2 * M)
        + 0.000289 * sin(3 * M)
    )

    lam = radians(L0 + C)

    eps = radians(23.439291)

    RA = degrees(
        atan2(
            cos(eps) * sin(lam),
            cos(lam)
        )
    )

    Dec = degrees(
        asin(
            sin(eps) * sin(lam)
        )
    )

    return RA % 360, Dec


# ============================================================
# SUN ECLIPTIC LONGITUDE
# ============================================================

def sun_longitude(jd):

    T = (jd - 2451545.0) / 36525

    L0 = (
        280.46646
        + 36000.76983 * T
    ) % 360

    M = radians(
        (357.52911 + 35999.05029 * T) % 360
    )

    C = (
        (1.914602 - 0.004817 * T) * sin(M)
        + 0.019993 * sin(2 * M)
        + 0.000289 * sin(3 * M)
    )

    return (L0 + C) % 360


# ============================================================
# MOON POSITION
# ============================================================

def moon_position(jd):

    D = jd - 2451545.0

    L0 = (
        218.316
        + 13.176396 * D
    ) % 360

    M = radians(
        (134.963 + 13.064993 * D) % 360
    )

    Ms = radians(
        (357.529 + 0.98560028 * D) % 360
    )

    F = radians(
        (93.272 + 13.229350 * D) % 360
    )

    lon = (
        L0
        + 6.289 * sin(M)
        + 1.274 * sin(
            2 * radians(L0) - M
        )
        + 0.658 * sin(
            2 * radians(L0)
        )
        + 0.214 * sin(2 * M)
        - 0.186 * sin(Ms)
    )

    lat = (
        5.128 * sin(F)
        + 0.280 * sin(M + F)
    )

    eps = radians(23.439291)

    lam = radians(lon)
    beta = radians(lat)

    RA = degrees(
        atan2(
            sin(lam) * cos(eps)
            - tan(beta) * sin(eps),
            cos(lam)
        )
    )

    Dec = degrees(
        asin(
            sin(beta) * cos(eps)
            + cos(beta)
            * sin(eps)
            * sin(lam)
        )
    )

    return RA % 360, Dec


# ============================================================
# MOON ECLIPTIC LONGITUDE
# ============================================================

def moon_longitude(jd):

    D = jd - 2451545.0

    L0 = (
        218.316
        + 13.176396 * D
    ) % 360

    M = radians(
        (134.963 + 13.064993 * D) % 360
    )

    Ms = radians(
        (357.529 + 0.98560028 * D) % 360
    )

    lon = (
        L0
        + 6.289 * sin(M)
        + 1.274 * sin(
            2 * radians(L0) - M
        )
        + 0.658 * sin(
            2 * radians(L0)
        )
        + 0.214 * sin(2 * M)
        - 0.186 * sin(Ms)
    )

    return lon % 360


# ============================================================
# SELISIH BUJUR EKLIPTIK BULAN - MATAHARI
# ============================================================

def moon_sun_difference(jd):

    diff = (
        moon_longitude(jd)
        - sun_longitude(jd)
    ) % 360

    if diff > 180:

        diff -= 360

    return diff


# ============================================================
# MENCARI IJTIMA / KONJUNGSI
# ============================================================
def find_conjunction(jd_target):

    # --------------------------------------------------------
    # Cari titik awal dengan selisih terkecil
    # --------------------------------------------------------

    start = jd_target - 20
    end = jd_target + 20

    step = 1 / 24

    best_jd = None
    best_abs = 999

    jd = start

    while jd <= end:

        diff = moon_sun_difference(jd)

        value = abs(diff)

        if value < best_abs:

            best_abs = value
            best_jd = jd

        jd += step

    if best_jd is None:
        return None


    # --------------------------------------------------------
    # Refinement
    # --------------------------------------------------------

    a = best_jd - step
    b = best_jd + step

    for _ in range(60):

        c = (a + b) / 2

        fa = moon_sun_difference(a)
        fc = moon_sun_difference(c)

        # Cari titik menuju 0
        if abs(fa) < abs(fc):

            b = c

        else:

            a = c

    return (
        a + b
    ) / 2

# ============================================================
# JULIAN DAY → DATETIME UTC
# ============================================================

def jd_to_datetime(jd):

    jd += 0.5

    Z = int(jd)

    F = jd - Z

    if Z < 2299161:

        A = Z

    else:

        alpha = int(
            (Z - 1867216.25)
            / 36524.25
        )

        A = (
            Z
            + 1
            + alpha
            - alpha // 4
        )

    B = A + 1524

    C = int(
        (B - 122.1) / 365.25
    )

    D = int(
        365.25 * C
    )

    E = int(
        (B - D) / 30.6001
    )

    day = (
        B
        - D
        - int(30.6001 * E)
        + F
    )

    if E < 14:

        month = E - 1

    else:

        month = E - 13

    if month > 2:

        year = C - 4716

    else:

        year = C - 4715

    day_int = int(day)

    fraction = day - day_int

    total_seconds = round(
        fraction * 86400
    )

    if total_seconds >= 86400:

        day_int += 1
        total_seconds -= 86400

    hour = total_seconds // 3600

    minute = (
        total_seconds % 3600
    ) // 60

    second = (
        total_seconds % 60
    )

    return datetime(
        year,
        month,
        day_int,
        hour,
        minute,
        second
    )


# ============================================================
# SIDEREAL TIME
# ============================================================

def sidereal_time(jd):

    return (
        280.46061837
        + 360.98564736629
        * (jd - 2451545)
    ) % 360


# ============================================================
# ALTITUDE / AZIMUTH
# ============================================================

def altitude_azimuth(RA, Dec, jd):

    LST = (
        sidereal_time(jd)
        + LON
    ) % 360

    HA = radians(
        (LST - RA) % 360
    )

    lat = radians(LAT)

    dec = radians(Dec)

    alt = asin(
        sin(lat) * sin(dec)
        + cos(lat)
        * cos(dec)
        * cos(HA)
    )

    az = atan2(
        sin(HA),
        cos(HA) * sin(lat)
        - tan(dec) * cos(lat)
    )

    return (
        degrees(alt),
        (degrees(az) + 360) % 360
    )


# ============================================================
# ALTITUDE BULAN
# ============================================================

def moon_altitude(jd):

    RA, Dec = moon_position(jd)

    alt, az = altitude_azimuth(
        RA,
        Dec,
        jd
    )

    return alt


# ============================================================
# REFRAKSI
# ============================================================

def refraksi(alt):

    if alt > -1:

        return (
            1.02
            / tan(
                radians(
                    alt
                    + 10.3
                    / (alt + 5.11)
                )
            )
            / 60
        )

    return 0


# ============================================================
# PARALLAX
# ============================================================

def parallax(alt):

    return (
        0.95
        * cos(radians(alt))
    )


# ============================================================
# SUNSET / GHURUB
# ============================================================

def sunset(y, m, d):

    jd0 = julian_day(
        y,
        m,
        d,
        12
    )

    RA, Dec = sun_position(jd0)

    latr = radians(LAT)

    decr = radians(Dec)

    H = degrees(
        acos(
            (
                -sin(radians(-0.833))
                - sin(latr)
                * sin(decr)
            )
            /
            (
                cos(latr)
                * cos(decr)
            )
        )
    )

    return (
        12
        + (H - LON) / 15
    )


# ============================================================
# CARI MOONSET
# ============================================================
def find_moon_events_local(y, m, d):

    """
    Mencari moonrise dan moonset
    untuk tanggal lokal WIB.
    """

    # Awal hari WIB dikonversi ke UTC
    jd_start = julian_day(
        y,
        m,
        d,
        -TZ
    )

    # Akhir hari lokal
    jd_end = jd_start + 1

    step = 5 / 1440

    events = []

    previous_jd = jd_start

    previous_alt = moon_altitude(
        previous_jd
    )

    jd = jd_start + step

    while jd <= jd_end:

        current_alt = moon_altitude(jd)

        # ----------------------------------------------------
        # MOONRISE
        # ----------------------------------------------------

        if (
            previous_alt <= 0
            and current_alt > 0
        ):

            a = previous_jd
            b = jd

            for _ in range(40):

                c = (a + b) / 2

                alt = moon_altitude(c)

                if alt > 0:
                    b = c
                else:
                    a = c

            events.append(
                (
                    "moonrise",
                    (a + b) / 2
                )
            )


        # ----------------------------------------------------
        # MOONSET
        # ----------------------------------------------------

        elif (
            previous_alt >= 0
            and current_alt < 0
        ):

            a = previous_jd
            b = jd

            for _ in range(40):

                c = (a + b) / 2

                alt = moon_altitude(c)

                if alt >= 0:
                    a = c
                else:
                    b = c

            events.append(
                (
                    "moonset",
                    (a + b) / 2
                )
            )


        previous_jd = jd
        previous_alt = current_alt

        jd += step


    moonrise_jd = None
    moonset_jd = None

    for event, jd_event in events:

        if event == "moonrise":
            moonrise_jd = jd_event

        elif event == "moonset":
            moonset_jd = jd_event


    return moonrise_jd, moonset_jd

# ============================================================
# HISAB FINAL
# ============================================================

def hisab_nu(y, m, d):

    # --------------------------------------------------------
    # GHURUB
    # --------------------------------------------------------

    ghurub = sunset(
        y,
        m,
        d
    )

    jd_ghurub = jam_desimal_ke_jd(
        y,
        m,
        d,
        ghurub
    )


    # --------------------------------------------------------
    # HIJRIAH
    # --------------------------------------------------------

    hijri_d, hijri_m, hijri_y = (
        masehi_to_hijri_json(
            f"{y:04d}-{m:02d}-{d:02d}"
        )
    )


    # --------------------------------------------------------
    # IJTIMA
    # --------------------------------------------------------

    jd_ijtima = find_conjunction(
        jd_ghurub
    )

    if jd_ijtima is not None:

        ijtima_utc = jd_to_datetime(
            jd_ijtima
        )

        ijtima_wib = (
            ijtima_utc
            + timedelta(hours=TZ)
        )

        # Umur Bulan saat ghurub
        umur_bulan_jam = (
            jd_ghurub
            - jd_ijtima
        ) * 24

    else:

        ijtima_utc = None
        ijtima_wib = None
        umur_bulan_jam = None


    # --------------------------------------------------------
    # POSISI MATAHARI
    # --------------------------------------------------------

    sunRA, sunDec = sun_position(
        jd_ghurub
    )


    # --------------------------------------------------------
    # POSISI BULAN
    # --------------------------------------------------------

    moonRA, moonDec = moon_position(
        jd_ghurub
    )


    # --------------------------------------------------------
    # ALT AZ
    # --------------------------------------------------------

    sunAlt, sunAz = altitude_azimuth(
        sunRA,
        sunDec,
        jd_ghurub
    )

    moonAlt, moonAz = altitude_azimuth(
        moonRA,
        moonDec,
        jd_ghurub
    )


    # --------------------------------------------------------
    # TINGGI HILAL MAR'I
    # --------------------------------------------------------

    moon_mar_i = (
        moonAlt
        + refraksi(moonAlt)
        - parallax(moonAlt)
    )


    # --------------------------------------------------------
    # ELONGASI
    # --------------------------------------------------------

    delta_ra = abs(
        sunRA - moonRA
    )

    if delta_ra > 180:

        delta_ra = 360 - delta_ra

    elong = acos(
        sin(radians(sunDec))
        * sin(radians(moonDec))
        +
        cos(radians(sunDec))
        * cos(radians(moonDec))
        * cos(radians(delta_ra))
    )

    elong = degrees(elong)


    # ========================================================
    # MOONRISE / MOONSET
    # ========================================================

  

    jd_moonrise, jd_moonset = find_moon_events_local(
        y,
        m,
        d
    )


    # --------------------------------------------------------
    # KONVERSI WAKTU
    # --------------------------------------------------------

    moonrise_wib = None
    moonset_wib = None

    if jd_moonrise is not None:
        moonrise_utc = jd_to_datetime(
            jd_moonrise
        )

        moonrise_wib = (
                moonrise_utc
                + timedelta(hours=TZ)
        )

    if jd_moonset is not None:
        moonset_utc = jd_to_datetime(
            jd_moonset
        )

        moonset_wib = (
                moonset_utc
                + timedelta(hours=TZ)
        )


    # ========================================================
    # LAMA BULAN DI ATAS UFUK
    # ========================================================

    if (
            jd_moonrise is not None
            and jd_moonset is not None
    ):

        lama_ufuk_jam = durasi_jam(
            jd_moonrise,
            jd_moonset
        )

    else:

        lama_ufuk_jam = None

        if jd_moonrise is not None and jd_moonset is not None:
            lama_ufuk_jam = (
                                    jd_moonset - jd_moonrise
                            ) * 24


    # ========================================================
    # LAMA BULAN DI ATAS UFUK SETELAH GHURUB
    # ========================================================

    if jd_moonset is not None:

        lama_setelah_ghurub_jam = durasi_jam(
            jd_ghurub,
            jd_moonset
        )

        if lama_setelah_ghurub_jam < 0:
            lama_setelah_ghurub_jam = 0

    else:

        lama_setelah_ghurub_jam = None

        if jd_moonset is not None:

            lama_setelah_ghurub_jam = (
                                              jd_moonset - jd_ghurub
                                      ) * 24

            if lama_setelah_ghurub_jam < 0:
                lama_setelah_ghurub_jam = 0

    # ========================================================
    # UMUR BULAN SAAT MOONSET
    # ========================================================

    if (
        jd_ijtima is not None
        and jd_moonset is not None
    ):

        umur_bulan_moonset_jam = (
            jd_moonset
            - jd_ijtima
        ) * 24

    else:

        umur_bulan_moonset_jam = None


    # ========================================================
    # KRITERIA NU
    # ========================================================

    # Imkanur Rukyah:
    #
    # Tinggi Hilal Mar'i >= 3°
    # Elongasi >= 6.4°
    # Umur Bulan >= 8 jam
    #
    # Umur 8 jam merupakan kriteria tambahan,
    # bukan bagian dari angka resmi MABIMS 3-6.4.

    irnu = (
        moon_mar_i >= 3
        and elong >= 6.4
        and (
            umur_bulan_jam is not None
            and umur_bulan_jam >= 8
        )
    )


    # Qath'iy Rukyah NU
    qrnu = elong >= 9.9


    # ========================================================
    # KESIMPULAN
    # ========================================================

    kesimpulan = None


    if hijri_d in [29, 30]:

        if qrnu:

            kesimpulan = {
                "status":"Qath'iy Rukyah NU",
                "kriteria":"QRNU elongasi ≥ 9.9°",
                "informasi":"Hilal sangat kuat. Istikmal dinafikan (Nafyul Ikmal), besok tanggal 1."
            }

        elif irnu:

            kesimpulan = {
                "status": "Memenuhi dilakukan pengamatan hilal",
                "kriteria":"tinggi hilal minimal 3° dan jarak lengkung (elongasi) minimal 6.4°",
                "informasi":"Hilal memenuhi batas imkanur rukyah. Menunggu hasil rukyah/isbat/ikhbar PBNU."
            }

        else:

            kesimpulan = {
                "status":"Istikmal 30 Hari",
                "kriteria":"Tidak memenuhi kriteria Imkanur Rukyah",
                "informasi": "Salah satu atau lebih parameter astronomis tidak memenuhi kriteria."
            }


    elif hijri_d == 1:

        if qrnu:

            kesimpulan = {
                "status": "Awal Bulan Baru (Qath'iy Rukyah NU)",
                "kriteria": "Elongasi ≥ 9.9°",
                "informasi":"Masuk bulan baru melalui Nafyul Ikmal."
            }

        elif irnu:

            kesimpulan = {
                "status": "Awal Bulan Baru (Imkanur Rukyah NU)",
                "kriteria": "Tinggi hilal ≥ 3°, elongasi ≥ 6.4°",
                "informasi":"Masuk bulan baru setelah hilal memenuhi imkanur rukyah."
            }

        else:

            kesimpulan = {
                "status":"Awal Bulan Baru (Istikmal)",
                "kriteria": "Di bawah Imkanur Rukyah",
                "informasi": "Masuk bulan baru setelah penggenapan 30 hari."
            }


    # ========================================================
    # HASIL
    # ========================================================

    result = {

        "tanggal_masehi":
            format_tanggal_indonesia(
                f"{y}-{m:02d}-{d:02d}"
            ),


        "tanggal_hijriah": {

            "hari": hijri_d,

            "bulan": hijri_m,

            "tahun": hijri_y,

            "full":
                f"{hijri_d} "
                f"{hijri_m} "
                f"{hijri_y}"

        },


        "data_ijtima": {

            "tanggal_ijtima_utc":
                (
                    ijtima_utc.strftime(
                        "%d-%m-%Y"
                    )
                    if ijtima_utc
                    else None
                ),

            "waktu_ijtima_utc":
                (
                    ijtima_utc.strftime(
                        "%H:%M:%S"
                    )
                    if ijtima_utc
                    else None
                ),

            "tanggal_ijtima_wib":
                (
                    ijtima_wib.strftime(
                        "%d-%m-%Y"
                    )
                    if ijtima_wib
                    else None
                ),

            "waktu_ijtima_wib":
                (
                    ijtima_wib.strftime(
                        "%H:%M:%S"
                    )
                    if ijtima_wib
                    else None
                ),

            "umur_bulan_saat_ghurub_jam":
                (
                    round(
                        umur_bulan_jam,
                        2
                    )
                    if umur_bulan_jam
                    is not None
                    else None
                ),

            "umur_bulan_saat_moonset_jam":
                (
                    round(
                        umur_bulan_moonset_jam,
                        2
                    )
                    if umur_bulan_moonset_jam
                    is not None
                    else None
                )

        },


        "data_ufuk": {

            "ghurub_wib":
                round(
                    ghurub + TZ,
                    2
                ),

            "moonrise_wib":
                (
                    moonrise_wib.strftime(
                        "%H:%M:%S"
                    )
                    if moonrise_wib
                    else None
                ),

            "moonset_wib":
                (
                    moonset_wib.strftime(
                        "%H:%M:%S"
                    )
                    if moonset_wib
                    else None
                ),

            "lama_bulan_di_atas_ufuk_jam":
                (
                    round(
                        lama_ufuk_jam,
                        2
                    )
                    if lama_ufuk_jam
                    is not None
                    else None
                ),

            "lama_bulan_di_atas_ufuk":
                format_durasi(
                    lama_ufuk_jam
                ),

            "lama_bulan_setelah_ghurub_jam":
                (
                    round(
                        lama_setelah_ghurub_jam,
                        2
                    )
                    if lama_setelah_ghurub_jam
                    is not None
                    else None
                ),

            "lama_bulan_setelah_ghurub":
                format_durasi(
                    lama_setelah_ghurub_jam
                )

        },


        "data_astronomi": {

            "ghurub_wib":
                format_jam_desimal(
                    ghurub + TZ
                ),

            "tinggi_hilal_hakiki":
                round(
                    moonAlt,
                    2
                ),

            "tinggi_hilal_mari":
                round(
                    moon_mar_i,
                    2
                ),

            "elongasi":
                round(
                    elong,
                    2
                ),

            "azimut_matahari":
                round(
                    sunAz,
                    2
                ),

            "azimut_bulan":
                round(
                    moonAz,
                    2
                )

        },


        "kesimpulan":
            kesimpulan

    }

    return result


# ============================================================
# CONTOH
# ============================================================

if __name__ == "__main__":

    data = hisab_nu(
        2026,
        8,
        13
    )

    print("=" * 70)

    print(
        "Tanggal Masehi :",
        data["tanggal_masehi"]
    )

    print(
        "Tanggal Hijriah :",
        data["tanggal_hijriah"]["full"]
    )

    print("=" * 70)

    print("DATA IJTIMA")
    print(
        "Tanggal ijtima UTC :",
        data["data_ijtima"]["tanggal_ijtima_utc"]
    )

    print(
        "Waktu ijtima UTC   :",
        data["data_ijtima"]["waktu_ijtima_utc"]
    )

    print(
        "Tanggal ijtima WIB :",
        data["data_ijtima"]["tanggal_ijtima_wib"]
    )

    print(
        "Waktu ijtima WIB   :",
        data["data_ijtima"]["waktu_ijtima_wib"]
    )

    print(
        "Umur bulan ghurub  :",
        data["data_ijtima"]["umur_bulan_saat_ghurub_jam"],
        "jam"
    )

    print(
        "Umur bulan moonset :",
        data["data_ijtima"]["umur_bulan_saat_moonset_jam"],
        "jam"
    )

    print("=" * 70)

    print("DATA UFUK")

    print(
        "Ghurub WIB         :",
        data["data_ufuk"]["ghurub_wib"]
    )

    print(
        "Moonrise WIB       :",
        data["data_ufuk"]["moonrise_wib"]
    )

    print(
        "Moonset WIB        :",
        data["data_ufuk"]["moonset_wib"]
    )

    print(
        "Lama di atas ufuk  :",
        data["data_ufuk"]["lama_bulan_di_atas_ufuk"]
    )

    print(
        "Lama setelah ghurub:",
        data["data_ufuk"]["lama_bulan_setelah_ghurub"]
    )

    print("=" * 70)

    print("DATA ASTRONOMI")

    print(
        "Tinggi hilal hakiki:",
        data["data_astronomi"]["tinggi_hilal_hakiki"]
    )

    print(
        "Tinggi hilal mar'i :",
        data["data_astronomi"]["tinggi_hilal_mari"]
    )

    print(
        "Elongasi           :",
        data["data_astronomi"]["elongasi"]
    )

    print(
        "Azimut matahari    :",
        data["data_astronomi"]["azimut_matahari"]
    )

    print(
        "Azimut bulan       :",
        data["data_astronomi"]["azimut_bulan"]
    )

    print("=" * 70)

    print(
        "Hipotesis :",
        data["kesimpulan"]
    )