from functools import lru_cache
from skyfield.api import load, wgs84
from skyfield import almanac
from datetime import datetime, timedelta, date
from pathlib import Path
import numpy as np
import json

# =========================================================
# DIRECTORY
# =========================================================

BASE_DIR = Path("data/khgt_v2")
ILDL_DIR = BASE_DIR / "ildl"
BASE_DIR.mkdir(parents=True, exist_ok=True)
ILDL_DIR.mkdir(parents=True, exist_ok=True)

TIMELINE_BIN = BASE_DIR / "timeline.npy"

# =========================================================
# ANCHOR FIXED (KRUSIAL)
# =========================================================

ANCHOR_DATE = date(2025, 6, 25)  # 1 Muharram 1447 KHGT

# =========================================================
# BULAN HIJRIAH
# =========================================================

BULAN_HIJRIAH = [
    "Muharram", "Safar", "Rabiul Awal", "Rabiul Akhir",
    "Jumadil Awal", "Jumadil Akhir", "Rajab", "Syaban",
    "Ramadhan", "Syawal", "Dzulqaidah", "Dzulhijjah"
]

# =========================================================
# TIMELINE STRUCTURE
# =========================================================

DTYPE = np.dtype([
    ("tgl", "U10"),
    ("bulan", "i1"),
    ("tahun", "i2"),
    ("alt", "f4"),
    ("elong", "f4"),
    ("status", "i1")
])

# =========================================================
# UTIL
# =========================================================

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path, default=None):
    if not Path(path).exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================================================
# EPHEMERIS
# =========================================================

@lru_cache(maxsize=1)
def get_ephemeris():
    ts = load.timescale()
    eph = load("de440s.bsp")
    return ts, eph


# =========================================================
# IJTIMA
# =========================================================

@lru_cache(maxsize=1)
def dapatkan_daftar_ijtima(tahun_mulai, tahun_akhir):
    ts, eph = get_ephemeris()

    t0 = ts.utc(tahun_mulai, 1, 1)
    t1 = ts.utc(tahun_akhir, 12, 31)

    f = almanac.moon_phases(eph)
    times, phases = almanac.find_discrete(t0, t1, f)

    return tuple(t.utc_datetime() for t, p in zip(times, phases) if p == 0)


# =========================================================
# HILAL CALC
# =========================================================

@lru_cache(maxsize=200000)
def hitung_hilal_cached(year, month, day, lat, lon):

    ts, eph = get_ephemeris()

    earth = eph["earth"]
    moon = eph["moon"]
    sun = eph["sun"]

    lokasi = wgs84.latlon(lat, lon)

    dt0 = datetime(year, month, day)
    dt1 = dt0 + timedelta(days=1)

    t0 = ts.utc(dt0.year, dt0.month, dt0.day)
    t1 = ts.utc(dt1.year, dt1.month, dt1.day)

    f = almanac.sunrise_sunset(eph, lokasi)
    times, events = almanac.find_discrete(t0, t1, f)

    sunset = None
    for t, e in zip(times, events):
        if e == 1:
            sunset = t
            break

    if sunset is None:
        return None

    topo = earth + lokasi

    moon_topo = topo.at(sunset).observe(moon).apparent()
    alt, _, _ = moon_topo.altaz()

    geo = earth.at(sunset)

    moon_geo = geo.observe(moon).apparent()
    sun_geo = geo.observe(sun).apparent()

    elong = moon_geo.separation_from(sun_geo).degrees

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
        round(lat, 2),
        round(lon, 2)
    )


# =========================================================
# GRID
# =========================================================

def generate_grid(step=2):
    return [
        (lat, lon)
        for lat in range(-60, 61, step)
        for lon in range(-180, 181, step)
    ]


# =========================================================
# KGTH CORE FIXED
# =========================================================

def cek_imkan_global_v2(tanggal, resolusi=2):

    grid = generate_grid(resolusi)

    titik_valid = []
    ildl = []

    lat_min, lat_max = -60, 60

    for lat, lon in grid:

        data = hitung_hilal(tanggal, lat, lon)
        if not data:
            continue

        ok = (data["elong"] >= 8 and data["alt"] >= 5)

        if ok:
            titik_valid.append({
                "lat": lat,
                "lon": lon,
                "alt": round(data["alt"], 2),
                "elong": round(data["elong"], 2),
                "sunset_utc": data["sunset_utc"].strftime("%Y-%m-%d %H:%M:%S")
            })

    # ILDL boundary
    for lon in range(-180, 181, resolusi):

        prev_ok = False
        prev_lat = None

        for lat in range(lat_min, lat_max + 1, resolusi):

            data = hitung_hilal(tanggal, lat, lon)
            if not data:
                continue

            current_ok = (data["elong"] >= 8 and data["alt"] >= 5)

            if (not prev_ok) and current_ok and prev_lat is not None:
                ildl.append([(prev_lat + lat) / 2, lon])

            prev_ok = current_ok
            prev_lat = lat

    return {
        "status": "Imkan Rukyat" if titik_valid else "Belum Memenuhi",
        "titik_valid": titik_valid[:50],
        "ildl": ildl
    }


# =========================================================
# SAVE / LOAD
# =========================================================

def save_timeline_binary(data):
    arr = np.array(data, dtype=DTYPE)
    np.save(TIMELINE_BIN, arr)


def load_timeline_binary():
    if not TIMELINE_BIN.exists():
        return None
    return np.load(TIMELINE_BIN, allow_pickle=False)


# =========================================================
# SAVE ILDL NPZ
# =========================================================

def save_ildl_npz(path, ildl):
    if not ildl:
        np.savez_compressed(path, lat=[], lon=[])
        return

    lat = np.array([x[0] for x in ildl], dtype=np.float32)
    lon = np.array([x[1] for x in ildl], dtype=np.float32)

    np.savez_compressed(path, lat=lat, lon=lon)


def load_ildl_npz(path):
    data = np.load(path)
    return np.column_stack((data["lat"], data["lon"]))


# =========================================================
# BUILD CACHE FIXED (ANCHOR SAFE)
# =========================================================

def build_kgth_cache_v2():

    print("BUILD KGTH CACHE v2 FIXED")

    semua_ijtima = dapatkan_daftar_ijtima(2025, 2030)

    # =====================================================
    # ALIGN ANCHOR (FIX KRUSIAL)
    # =====================================================

    start_index = None
    for i, ijt_dt in enumerate(semua_ijtima):
        if ijt_dt.date() >= ANCHOR_DATE:
            start_index = i
            break

    if start_index is None:
        raise Exception("ANCHOR KHGT tidak ditemukan")

    semua_ijtima = semua_ijtima[start_index:]

    timeline = []

    curr_h_idx = 0
    curr_h_year = 1447

    for ijt_dt in semua_ijtima:

        print("COMPUTE:", ijt_dt.date())

        imkan = cek_imkan_global_v2(ijt_dt.date(), resolusi=2)

        base_date = (ijt_dt + timedelta(hours=12)).date()

        tgl_1 = base_date if imkan["status"] == "Imkan Rukyat" else base_date + timedelta(days=1)

        titik = imkan["titik_valid"][0] if imkan["titik_valid"] else None

        # SAVE ILDL
        save_ildl_npz(ILDL_DIR / f"{tgl_1}.npz", imkan["ildl"])

        timeline.append((
            tgl_1.isoformat(),
            curr_h_idx + 1,   # FIX: 1-12
            curr_h_year,
            float(titik["alt"]) if titik else 0,
            float(titik["elong"]) if titik else 0,
            1 if imkan["status"] == "Imkan Rukyat" else 0
        ))

        curr_h_idx += 1

        if curr_h_idx >= 12:
            curr_h_idx = 0
            curr_h_year += 1

    save_timeline_binary(timeline)

    print("CACHE COMPLETE v2 FIXED")


# =========================================================
# FAST API
# =========================================================

def get_hijriah_v2(tanggal):

    if isinstance(tanggal, str):
        tanggal = datetime.strptime(tanggal, "%Y-%m-%d").date()

    timeline = load_timeline_binary()

    if timeline is None:
        return None

    dates = timeline["tgl"]

    idx = np.searchsorted(dates, tanggal.isoformat(), side="right") - 1

    if idx < 0:
        return None

    row = timeline[idx]

    ildl_file = ILDL_DIR / f"{row['tgl']}.npz"

    return {
        "tanggal": tanggal.isoformat(),
        "bulan": int(row["bulan"]),
        "bulan_nama": BULAN_HIJRIAH[int(row["bulan"]) - 1],
        "tahun": int(row["tahun"]),
        "status": bool(row["status"]),
        "alt": float(row["alt"]),
        "elong": float(row["elong"]),
        "ildl": load_ildl_npz(ildl_file) if ildl_file.exists() else []
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    if not TIMELINE_BIN.exists():
        build_kgth_cache_v2()

    print(get_hijriah_v2("2026-05-19"))
