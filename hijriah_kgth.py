from functools import lru_cache
from skyfield.api import load, wgs84
from skyfield import almanac
from datetime import datetime, timedelta, date
import numpy as np
from konversitanggal import format_tanggal_indonesia

@lru_cache(maxsize=500000)
def _cached_hitung_hilal(tanggal, lat, lon):
    return hitung_hilal(tanggal, lat, lon)


def deg_to_dms(deg):
    d = int(deg)
    m_float = abs(deg - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}′ {s:.2f}″"
def smooth_ildl(ildl):
    return np.array(ildl).tolist()
# =========================================
# 1. EPHEMERIS CACHE
# =========================================
@lru_cache(maxsize=1)
def get_ephemeris():
    ts = load.timescale()
    eph = load('de440s.bsp')
    return ts, eph


# =========================================
# 2. IJTIMAK CACHE (DINAMIS)
# =========================================
@lru_cache(maxsize=8)
def dapatkan_daftar_ijtima(tahun_mulai, tahun_akhir):
    ts, eph = get_ephemeris()

    earth = eph['earth']
    moon = eph['moon']
    sun = eph['sun']

    t0 = ts.utc(tahun_mulai, 1, 1)
    t1 = ts.utc(tahun_akhir, 12, 31)

    f = almanac.moon_phases(eph)
    times, phases = almanac.find_discrete(t0, t1, f)

    hasil = []
    for t, p in zip(times, phases):
        if p == 0:
            e = earth.at(t)
            m = e.observe(moon).apparent()
            s = e.observe(sun).apparent()
            elong = m.separation_from(s).degrees

            hasil.append((t.utc_datetime(), elong))

    return tuple(hasil)


def get_range_ijtima(tanggal_target, buffer=2):
    tahun = tanggal_target.year
    return dapatkan_daftar_ijtima(tahun - buffer, tahun + buffer)


# =========================================
# 3. HITUNG HILAL
# =========================================
@lru_cache(maxsize=10000)
def hitung_hilal_cached(year, month, day, lat, lon):
    ts, eph = get_ephemeris()

    earth = eph['earth']
    moon = eph['moon']
    sun = eph['sun']

    lokasi = wgs84.latlon(lat, lon)

    t0 = ts.utc(year, month, day)
    t1 = ts.utc(year, month, day + 1)

    f = almanac.sunrise_sunset(eph, lokasi)
    times, events = almanac.find_discrete(t0, t1, f)

    sunset = None
    for t, e in zip(times, events):
        if e == 0:
            sunset = t
            break

    if sunset is None:
        return None

    e_topo = earth + lokasi

    m = e_topo.at(sunset).observe(moon).apparent()
    alt, _, _ = m.altaz()

    geo = earth.at(sunset)
    elong = geo.observe(moon).apparent().separation_from(
        geo.observe(sun).apparent()
    ).degrees

    return {
        "alt": alt.degrees,
        "elong": elong,
        "sunset_utc": sunset.utc_datetime()
    }


def hitung_hilal(tanggal, lat, lon):
    return hitung_hilal_cached(
        tanggal.year,
        tanggal.month,
        tanggal.day,
        round(lat, 3),
        round(lon, 3)
    )


# =========================================
# 4. GRID GLOBAL
# =========================================
def generate_grid(step=5):
    return [(lat, lon)
            for lat in range(-60, 61, step)
            for lon in range(-180, 181, step)]


# =========================================
# 5. IMKAN RUKYAT GLOBAL
# =========================================
# def cek_imkan_global(tanggal, ijt_utc, resolusi=5):
#
#     grid = generate_grid(resolusi)
#     titik_valid = []
#
#     for lat, lon in grid:
#         data = hitung_hilal(tanggal, lat, lon)
#         if not data:
#             continue
#
#         if data["elong"] >= 8 and data["alt"] >= 5:
#             titik_valid.append({
#                 "lat": lat,
#                 "lon": lon,
#                 "alt": data["alt"],
#                 "elong": data["elong"],
#                 "sunset_utc": data["sunset_utc"]
#             })
#
#     return {
#         "status": "Imkan Rukyat" if titik_valid else "Belum Memenuhi",
#         "titik_valid": titik_valid[:50]
#     }

# def cek_imkan_global(tanggal, ijt_utc, resolusi=2):
#
#     ildl = []
#
#     lat_min, lat_max = -60, 60
#
#     for lon in range(-180, 181, resolusi):
#
#         boundary_points = []
#
#         prev = None
#         prev_data = None
#
#         prev_lat = None
#         prev_data = None
#
#         for lat in range(lat_min, lat_max + 1, resolusi):
#
#             data = _cached_hitung_hilal(tanggal, lat, lon)
#
#             if not data:
#                 prev_lat = lat
#                 prev_data = {"ok": False}
#                 continue
#
#             current_ok = (data["elong"] >= 8 and data["alt"] >= 5)
#
#             # 🔥 DETEKSI EDGE FALSE → TRUE
#             if prev_data is not None:
#
#                 if (not prev_data["ok"]) and current_ok:
#                     # ======================================
#                     # 🔥 INI TEMPAT INTERPOLASI
#                     # ======================================
#                     t = 0.5
#                     lat_boundary = prev_lat + t * (lat - prev_lat)
#
#                     ildl.append([lat_boundary, lon])
#
#             # update state
#             prev_lat = lat
#             prev_data = {"ok": current_ok}
#
#         if boundary_points:
#             ildl.extend(boundary_points)
#
#     # 🔥 optional smoothing ringan (menghindari zigzag noise)
#     ildl = ildl[::2]
#
#     return {
#         "status": "Imkan Rukyat" if ildl else "Belum Memenuhi",
#         "ildl": ildl
#     }


# =========================================
# 6. KONVERSI HIJRIAH
# =========================================
def konversi_hijriah(tanggal_target):

    if isinstance(tanggal_target, datetime):
        tanggal_target = tanggal_target.date()

    semua_ijtima = get_range_ijtima(tanggal_target)

    # anchor Rajab 1446
    ref_idx = None
    for i, (ijt_dt, _) in enumerate(semua_ijtima):
        if ijt_dt.date() >= date(2024, 12, 30):
            ref_idx = i
            break

    if ref_idx is None:
        return None

    bulan = [
        "Muharram","Safar","Rabiul Awal","Rabiul Akhir",
        "Jumadil Awal","Jumadil Akhir","Rajab","Syaban",
        "Ramadhan","Syawal","Dzulqaidah","Dzulhijjah"
    ]

    curr_h_idx = 6
    curr_h_year = 1446

    timeline = []

    for i in range(ref_idx, len(semua_ijtima)):
        ijt_dt, elong = semua_ijtima[i]
        tgl_1 = ijt_dt.date() + timedelta(days=1)

        timeline.append({
            "tgl_1": tgl_1,
            "ijt_utc": ijt_dt,
            "elongasi": elong,
            "nama": bulan[curr_h_idx],
            "tahun_h": curr_h_year
        })

        curr_h_idx = (curr_h_idx + 1) % 12
        if curr_h_idx == 0:
            curr_h_year += 1

    for i in range(len(timeline) - 1):
        if timeline[i]["tgl_1"] <= tanggal_target < timeline[i + 1]["tgl_1"]:

            selisih = (tanggal_target - timeline[i]["tgl_1"]).days + 1

            # imkan = cek_imkan_global(
            #     timeline[i]["tgl_1"],
            #     timeline[i]["ijt_utc"]
            # )

            return {
                "hari": selisih,
                "bulan": timeline[i]["nama"],
                "tahun": timeline[i]["tahun_h"],
                "ijt_utc": timeline[i]["ijt_utc"],
                "elongasi": deg_to_dms(timeline[i]["elongasi"]),
                # "imkan": imkan["status"],
                # "titik_valid": imkan["titik_valid"],
                # "ildl": smooth_ildl(imkan["ildl"])
            }

    return None


# =========================================
# 7. NORMALIZE
# =========================================
def normalize_data(data):

    def convert(value):
        if isinstance(value, np.generic):
            return value.item()

        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d %H:%M:%S")

        return value

    if isinstance(data, dict):
        return {k: normalize_data(v) for k, v in data.items()}

    elif isinstance(data, list):
        return [normalize_data(v) for v in data]

    else:
        return convert(data)


# =========================================
# 8. API FUNCTION (FLASK READY)
# =========================================
def get_hijriah(tanggal=None):

    if isinstance(tanggal, str):
        tanggal = datetime.strptime(tanggal, "%Y-%m-%d").date()

    elif isinstance(tanggal, datetime):
        tanggal = tanggal.date()

    elif tanggal is None:
        tanggal = datetime.now().date()

    hasil = konversi_hijriah(tanggal)
    hasil_bersih = normalize_data(hasil)

    return {
        "tanggal": format_tanggal_indonesia(tanggal.isoformat()),
        "hijriah": hasil_bersih
    }


# =========================================
# 9. TEST
# =========================================
if __name__ == "__main__":
    data = get_hijriah("2026-04-15")
    print("Tanggal:", data["tanggal"])
    print("Hijriah:", data["hijriah"])