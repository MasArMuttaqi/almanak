from math import sin, cos, tan, asin, acos, atan2, radians, degrees, floor
from datetime import datetime, timedelta, timezone
from konversitanggal import format_tanggal_indonesia

# ==========================================
# LOKASI
# ==========================================
LAT = -7.7974565
LON = 110.370697
TZ = 7

# ==========================================
# AWAL BULAN WUJUDUL HILAL
# ==========================================
ANCHOR_DATE = datetime(2025, 6, 26)
ANCHOR_MONTH = 1
ANCHOR_YEAR = 1447


# ==========================================
# JULIAN DAY
# ==========================================
def julian_day(y, m, d, hour=0):
    if m <= 2:
        y -= 1
        m += 12

    A = y // 100
    B = 2 - A + (A // 4)

    jd = floor(365.25 * (y + 4716)) + floor(30.6001 * (m + 1)) + d + B - 1524.5
    return jd + hour / 24


# ==========================================
# SUN POSITION
# ==========================================
def sun_pos(jd):
    T = (jd - 2451545.0) / 36525

    L0 = (280.46646 + 36000.76983 * T) % 360
    M = radians((357.52911 + 35999.05029 * T) % 360)

    C = (1.914602 - 0.004817 * T) * sin(M) + 0.019993 * sin(2 * M)
    true_long = (L0 + C) % 360

    eps = radians(23.439291)

    ra = degrees(atan2(
        cos(eps) * sin(radians(true_long)),
        cos(radians(true_long))
    )) % 360

    dec = degrees(asin(
        sin(eps) * sin(radians(true_long))
    ))

    return ra / 15, dec, true_long


# ==========================================
# MOON POSITION
# ==========================================
def moon_pos(jd):
    T = (jd - 2451545.0) / 36525

    L = (218.316 + 481267.881 * T) % 360
    M = radians((134.963 + 477198.867 * T) % 360)
    F = radians((93.272 + 483202.017 * T) % 360)

    lon = (L + 6.289 * sin(M)) % 360
    lat_m = 5.128 * sin(F)

    eps = radians(23.439291)

    ra = degrees(atan2(
        sin(radians(lon)) * cos(eps) - tan(radians(lat_m)) * sin(eps),
        cos(radians(lon))
    )) % 360

    dec = degrees(asin(
        sin(radians(lat_m)) * cos(eps) +
        cos(radians(lat_m)) * sin(eps) * sin(radians(lon))
    ))

    return ra / 15, dec, lon


# ==========================================
# SIDEREAL TIME
# ==========================================
def lst(jd):
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0)
    return (gmst + LON) % 360


# ==========================================
# SUNSET
# ==========================================
def sunset(year, month, day):
    jd = julian_day(year, month, day, 0)
    _, dec_s, _ = sun_pos(jd)

    lat = radians(LAT)
    dec = radians(dec_s)
    h0 = radians(-0.833)

    cosH = (sin(h0) - sin(lat) * sin(dec)) / (cos(lat) * cos(dec))
    cosH = max(min(cosH, 1), -1)

    H = degrees(acos(cosH))

    return 12 + H / 15 - (LON / 15 - TZ)


# ==========================================
# ⚡ NEWTON IJTIMAK SOLVER (TAMBAHAN BARU)
# ==========================================
def synodic_diff(jd):
    _, _, sun_lon = sun_pos(jd)
    _, _, moon_lon = moon_pos(jd)
    return (moon_lon - sun_lon + 180) % 360 - 180


def derivative(jd, h=0.0001):
    return (synodic_diff(jd + h) - synodic_diff(jd - h)) / (2 * h)


def newton_step(jd):
    f = synodic_diff(jd)
    df = derivative(jd)

    if abs(df) < 1e-8:
        return jd

    return jd - f / df


def ijtimak_newton(year, month, day):
    jd = julian_day(year, month, day, 12)

    # initial scan ringan
    best = jd
    best_f = abs(synodic_diff(jd))

    for h in range(-24, 25):
        jd_test = julian_day(year, month, day, 12 + h)
        f = abs(synodic_diff(jd_test))
        if f < best_f:
            best_f = f
            best = jd_test

    jd = best

    # Newton iteration
    for _ in range(6):
        jd_next = newton_step(jd)
        if abs(jd_next - jd) < 1 / (24 * 60):  # < 1 menit
            break
        jd = jd_next

    return jd

# ==========================================
# JD -> DATETIME WIB
# ==========================================
def jd_to_datetime(jd):
    unix = (jd - 2440587.5) * 86400
    dt = datetime.fromtimestamp(unix, tz=timezone.utc)
    dt = dt + timedelta(hours=TZ)
    return dt.strftime("%Y-%m-%d %H:%M:%S WIB")



# ==========================================
# BUILD TIMELINE
# ==========================================
def build_timeline(sampai_tahun=2035):

    timeline = []

    bulan = ANCHOR_MONTH
    tahun = ANCHOR_YEAR

    current = ANCHOR_DATE

    timeline.append(
        (current, bulan, tahun)
    )

    while current.year <= sampai_tahun:

        found = None

        for offset in range(28, 32):

            test = current + timedelta(days=offset)

            ss = sunset(
                test.year,
                test.month,
                test.day
            )

            jd_ss = julian_day(
                test.year,
                test.month,
                test.day,
                ss - TZ
            )

            jd_ij = ijtimak_newton(
                test.year,
                test.month,
                test.day
            )

            ra_m, dec_m, lon_m = moon_pos(jd_ss)

            LST = lst(jd_ss)

            ha = (LST - ra_m * 15) % 360

            if ha > 180:
                ha -= 360

            alt = degrees(
                asin(
                    sin(radians(LAT))*sin(radians(dec_m))
                    +
                    cos(radians(LAT))*cos(radians(dec_m))*cos(radians(ha))
                )
            )

            if jd_ij < jd_ss and alt > 0:

                found = test + timedelta(days=1)
                break

        if found is None:
            break

        bulan += 1

        if bulan > 12:
            bulan = 1
            tahun += 1

        timeline.append(
            (found, bulan, tahun)
        )

        current = found

    return timeline


# ==========================================
# HIJRIAH MUHAMMADIYAH
# ==========================================
def hijriah_muhammadiyah(y,m,d):

    target = datetime(y,m,d)

    start = TIMELINE[0]

    for item in TIMELINE:

        if item[0] <= target:
            start = item
        else:
            break

    awal, bulan, tahun = start

    hari = (target - awal).days + 1

    return hari, bulan, tahun


# ==========================================
# ENGINE UTAMA (SUDAH DIGANTI NEWTON)
# ==========================================
def hisab(year, month, day):

    ss = sunset(year, month, day)
    jd_ss = julian_day(year, month, day, ss - TZ)

    # 🔥 GANTI DI SINI
    jd_ij = ijtimak_newton(year, month, day)
    ijtima_time = jd_to_datetime(jd_ij)

    ra_m, dec_m, lon_m = moon_pos(jd_ss)
    ra_s, dec_s, lon_s = sun_pos(jd_ss)

    LST = lst(jd_ss)

    ha = (LST - ra_m * 15) % 360
    if ha > 180:
        ha -= 360

    x = (
        sin(radians(LAT)) * sin(radians(dec_m)) +
        cos(radians(LAT)) * cos(radians(dec_m)) * cos(radians(ha))
    )

    alt = degrees(asin(max(-1, min(1, x))))

    elong = abs(lon_m - lon_s)
    if elong > 180:
        elong = 360 - elong

    h_d, h_m, h_y = hijriah_muhammadiyah(
        year,
        month,
        day
    )

    bulan_nama = [
        "Muharram",
        "Safar",
        "Rabiul Awal",
        "Rabiul Akhir",
        "Jumadil Ula",
        "Jumadil Akhir",
        "Rajab",
        "Sya'ban",
        "Ramadhan",
        "Syawal",
        "Dzulqa'dah",
        "Dzulhijjah"
    ]

    return {
        "tanggal_masehi": format_tanggal_indonesia( f"{year}-{month:02d}-{day:02d}"),
        "sunset_wib": round(ss, 2),
        "ijtima": ijtima_time,
        "tinggi_hilal": round(alt, 3),
        "elongasi": round(elong, 3),
        "hijriah": f"{h_d} {bulan_nama[h_m-1]} {h_y}",
        "keputusan": keputusan(jd_ss, jd_ij, alt)
    }


# ==========================================
# KEPUTUSAN
# ==========================================
def keputusan(jd_ss, jd_ij, alt):
    if jd_ij is None:
        # return "ISTIKMAL (Ijtimak tidak terjadi)"
        return {
            "status": "Istikmal",
            "keterangan": "Ijtimak tidak terjadi"
        }

    if jd_ij > jd_ss:
        # return "ISTIKMAL (Ijtimak setelah maghrib)"
        return {
            "status": "Istikmal",
            "keterangan": "Ijtimak terjadi setelah magrib"
        }

    if alt > 0:
        # return "Masuk Bulan Baru (Wujudul Hilal)"
        return {
            "status": "Masuk bulan baru",
            "keterangan": "Wujudul hilal"
        }

    # return "ISTIKMAL (Hilal belum wujud)"
    return {
        "status": "Istikmal",
        "keterangan": "Hilal belum wujud"
    }




TIMELINE = build_timeline(2035)
# ==========================================
# TEST
# ==========================================
if __name__ == "__main__":
    data = hisab(2026, 6, 15)
    print("=" * 60)
    print("Tanggal Masehi :", data["tanggal_masehi"])
    print("Tanggal Hijriah :", data["hijriah"])
    print("=" * 60)
    print("Sunset WIB :", data["sunset_wib"])
    print("Ijtima :", data["ijtima"])
    print("Tinggi Hilal :", data["tinggi_hilal"])
    print("Elongasi :", data["elongasi"])
    print("=" * 60)
    print("keputusan :", data["keputusan"])