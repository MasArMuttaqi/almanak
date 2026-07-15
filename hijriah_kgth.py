from skyfield.api import load, wgs84
from skyfield import almanac
from functools import lru_cache
from datetime import (
    datetime,
    timedelta,
    timezone,
    date,
    time
)
from pathlib import Path
from math import radians, degrees
from math import sin, cos, tan, asin, atan

import numpy as np
import json

from konversitanggal import format_tanggal_indonesia

# =========================================================
# DIRECTORY CACHE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

REF_DIR = BASE_DIR / "data" / "ref_kgth_2"

REF_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TIMELINE_FILE = (
    REF_DIR /
    "timeline_cache_2.json"
)



# =========================================================
# GLOBAL CACHE
# =========================================================

TIMELINE_CACHE = {}


# =========================================================
# BULAN HIJRIAH
# =========================================================

BULAN_HIJRIAH = [
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

# =========================================================
# UTIL
# =========================================================

def deg_to_dms(deg):

    d = int(deg)

    m_float = abs(
        deg - d
    ) * 60

    m = int(m_float)

    s = (
        m_float - m
    ) * 60

    return (
        f"{d}° "
        f"{m}′ "
        f"{s:.4f}″"
    )


# =========================================================
# SAVE TIMELINE CACHE
# =========================================================
def save_timeline_cache():

    data_save = {}

    for tahun, timeline in (
        TIMELINE_CACHE.items()
    ):

        rows = []

        for item in timeline:
            rows.append({

                "tgl_1":
                    item["tgl_1"].isoformat(),

                "ijt_utc":
                    item["ijt_utc"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "elongasi":
                    item["elongasi"],

                "nama":
                    item["nama"],

                "tahun_h":
                    item["tahun_h"],

                "pkg1":
                    item.get("pkg1"),

                "pkg2":
                    item.get("pkg2"),

                "status_pkg":
                    item.get("status_pkg"),

                "nz_fajr_utc":
                    (
                        item["nz_fajr_utc"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if item.get("nz_fajr_utc")
                        else None
                    ),

                "lat":
                    item.get("lat"),

                "lon":
                    item.get("lon"),

                "alt":
                    item.get("alt"),

                "elong_hilal":
                    item.get("elong_hilal"),

                "lokasi_awal":
                    item.get("lokasi_awal"),

                "sunset_utc":
                    (
                        item["sunset_utc"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if item.get("sunset_utc")
                        else None
                    )
            })

        data_save[
            str(tahun)
        ] = rows

    with open(
        TIMELINE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data_save,
            f,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# LOAD TIMELINE CACHE
# =========================================================

def load_timeline_cache():

    if not TIMELINE_FILE.exists():
        return

    try:

        with open(
            TIMELINE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            raw = json.load(f)

        for tahun, rows in raw.items():

            timeline = []

            for item in rows:
                timeline.append({

                    "tgl_1":
                        datetime.strptime(
                            item["tgl_1"],
                            "%Y-%m-%d"
                        ).date(),

                    "ijt_utc":
                        datetime.strptime(
                            item["ijt_utc"],
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "elongasi":
                        item["elongasi"],

                    "nama":
                        item["nama"],

                    "tahun_h":
                        item["tahun_h"],

                    "pkg1":
                        item.get("pkg1", False),

                    "pkg2":
                        item.get("pkg2", False),

                    "status_pkg":
                        item.get("status_pkg"),

                    "nz_fajr_utc":
                        (
                            datetime.strptime(
                                item["nz_fajr_utc"],
                                "%Y-%m-%d %H:%M:%S"
                            )
                            if item.get("nz_fajr_utc")
                            else None
                        ),

                    "lat":
                        item.get("lat"),

                    "lon":
                        item.get("lon"),

                    "alt":
                        item.get("alt"),

                    "elong_hilal":
                        item.get("elong_hilal"),

                    "lokasi_awal":
                        item.get("lokasi_awal"),

                    "sunset_utc":
                        (
                            datetime.strptime(
                                item["sunset_utc"],
                                "%Y-%m-%d %H:%M:%S"
                            )
                            if item.get("sunset_utc")
                            else None
                        )
                })

            TIMELINE_CACHE[
                int(tahun)
            ] = timeline

        print(
            "[CACHE] timeline loaded"
        )

    except Exception as e:

        print(
            "Gagal load cache:",
            e
        )
# =========================================================
# BUILD TIMELINE
# =========================================================

def build_timeline(
    tanggal_target
):



    tahun_key = (
        tanggal_target.year
    )

    print("BUILD TIMELINE", tahun_key)
    print("Cache:", tahun_key in TIMELINE_CACHE)

    print(
        "tahun_key =",
        tahun_key
    )

    print(
        "cache keys =",
        TIMELINE_CACHE.keys()
    )

    if tahun_key in (
        TIMELINE_CACHE
    ):

        return TIMELINE_CACHE[
            tahun_key
        ]

    semua_ijtima = (
        get_range_ijtima(
            tanggal_target
        )
    )

    ref_idx = None

    for i, (
        ijt_dt,
        _
    ) in enumerate(
        semua_ijtima
    ):

        # if ijt_dt.date() >= date(
        #    2025,
        #    6,
        #    25
        # ):
        if ijt_dt.date() >= date(
                2024,
                12,
                30
        ):

            ref_idx = i

            break

    if ref_idx is None:
        return []

    # curr_h_idx = 1
    # curr_h_year = 1447
    curr_h_idx = 6
    curr_h_year = 1446

    timeline = []

    for i in range(
        ref_idx,
        len(semua_ijtima)
    ):

        ijt_dt, elong = (
            semua_ijtima[i]
        )

        # for offset in range(3):
        hasil = cek_imkan_global(
                ijt_dt.date(),
                ijt_dt
        )

            # if hasil["status"] == "Imkan Rukyat":
            #     tgl_1 = ijt_dt.date() + timedelta(days=1)
            # else:
            #     tgl_1 = ijt_dt.date() + timedelta(days=2)

        if hasil["pkg1"] or hasil["pkg2"]:

            tgl_1 = ijt_dt.date() + timedelta(days=1)

        else:

            tgl_1 = ijt_dt.date() + timedelta(days=2)


        timeline.append({

                "tgl_1": tgl_1,

                "ijt_utc": ijt_dt,

                "elongasi": elong,

                "nama": BULAN_HIJRIAH[curr_h_idx],

                "tahun_h": curr_h_year,

                "pkg1": hasil["pkg1"],

                "pkg2": hasil["pkg2"],

                "status_pkg": hasil["pkg"],

                "lat": hasil.get("lat"),

                "lon": hasil.get("lon"),

                "alt": hasil.get("alt"),

                "elong_hilal": hasil.get("elong"),

                "lokasi_awal": hasil.get("lokasi_awal"),

                "sunset_utc": hasil.get("sunset_utc"),

                "nz_fajr_utc": hasil.get("nz_fajr_utc")
        })

        curr_h_idx = (
            curr_h_idx + 1
        ) % 12

        if curr_h_idx == 0:

            curr_h_year += 1

    TIMELINE_CACHE[tahun_key] = timeline

    print(tahun_key,
        len(timeline)
    )
    print("=== ISI TIMELINE ===")

    for item in timeline:
        if item["tgl_1"].year == 2026:
            print(
                item["nama"],
                item["tgl_1"],
                item["ijt_utc"]
            )
    print("Jumlah timeline =", len(timeline))

    for item in timeline:
        print(
            item["nama"],
            item["tgl_1"],
            item["ijt_utc"]
        )

    save_timeline_cache()


    print(
        f"[CACHE BUILD] "
        f"{tahun_key}"
    )


    return timeline

# =========================================================
# KGTH RULE
# =========================================================
def is_america(lat, lon):

    return (
            -170 <= lon <= -35
            and
            -56 <= lat <= 72
    )


def ijtimak_before_nz_fajr(
    ijt_utc
):

    nz_local = (
        ijt_utc +
        timedelta(hours=12)
    )

    return (
        nz_local.hour < 5
    )

NZ_LAT = -36.8485
NZ_LON = 174.7633


@lru_cache(maxsize=5000)
def get_nz_fajr_utc(tanggal):

    ts, eph = get_ephemeris()

    lokasi = wgs84.latlon(
        NZ_LAT,
        NZ_LON
    )

    t0 = ts.utc(
        tanggal.year,
        tanggal.month,
        tanggal.day
    )

    t1 = ts.utc(
        tanggal.year,
        tanggal.month,
        tanggal.day + 1
    )

    f = almanac.sunrise_sunset(
        eph,
        lokasi
    )

    times, events = almanac.find_discrete(
        t0,
        t1,
        f
    )

    for t, e in zip(times, events):

        # sunrise
        if e == 0:
            return t.utc_datetime()

    return None
# =========================================================
# CEK TITIK
# =========================================================
def cek_titik(
    tanggal,
    ijt_utc,
    lat,
    lon
):

    data = _cached_hitung_hilal(
        tanggal,
        lat,
        lon
    )

    if data is None:
        return None

    sunset_utc = data["sunset_utc"]

    akhir_hari = datetime.combine(
        tanggal + timedelta(days=1),
        datetime.min.time(),
        tzinfo=timezone.utc
    )

    normal_case = (
        ijt_utc < sunset_utc < akhir_hari
    )

    # special_case = (
    #
    #         is_america(lat, lon)
    #
    #         and
    #
    #         sunset_utc <= get_nz_fajr_utc(tanggal)
    #
    # )

    nz_fajr = get_nz_fajr_utc(tanggal)
    special_case = ( sunset_utc > akhir_hari and is_america(lat, lon) and nz_fajr is not None and sunset_utc <= nz_fajr )

    if (
        (normal_case or special_case)

        and

        data["alt"] >= 5

        and

        data["elong"] >= 8
    ):
        return {

            "pkg":
                (
                    "PKG 1 (sebelum 24:00 UTC)"
                    if normal_case
                    else
                    "PKG 2 (penyelarasan global)"
                ),

            "alt": data["alt"],

            "elong": data["elong"],

            "sunset_utc": data["sunset_utc"]
        }

    return None

# =========================================================
# IJTIMAK
# =========================================================

@lru_cache(maxsize=8)
def dapatkan_daftar_ijtima(
    tahun_mulai,
    tahun_akhir
):

    ts, eph = (
        get_ephemeris()
    )

    earth = eph["earth"]
    moon = eph["moon"]
    sun = eph["sun"]

    t0 = ts.utc(
        tahun_mulai,
        1,
        1
    )

    t1 = ts.utc(
        tahun_akhir,
        12,
        31
    )



    f = almanac.moon_phases(
        eph
    )

    times, phases = (
        almanac.find_discrete(
            t0,
            t1,
            f
        )
    )

    hasil = []

    for t, p in zip(
        times,
        phases
    ):

        if p == 0:

            e = earth.at(t)

            m = (
                e.observe(moon)
                # .apparent()
            )

            s = (
                e.observe(sun)
                # .apparent()
            )

            elong = (
                m.separation_from(s)
                .degrees
            )

            hasil.append((
                t.utc_datetime(),
                elong
            ))

    return tuple(hasil)


def get_range_ijtima(
    tanggal_target,
    buffer=2
):

    tahun = (
        tanggal_target.year
    )

    return dapatkan_daftar_ijtima(
        tahun - buffer,
        tahun + buffer
    )


# =========================================================
# HITUNG HILAL
# =========================================================
@lru_cache(maxsize=500000)
def get_sunset_utc(
    year,
    month,
    day,
    lat,
    lon
):

    ts, eph = (
        get_ephemeris()
    )

    lokasi = (
        wgs84.latlon(
            lat,
            lon
        )
    )



    t0 = ts.utc(
        year,
        month,
        day
    )

    try:
        t1 = ts.utc(
            year,
            month,
            day + 1
        )

    # except:
    #     return None
    except Exception as e:
        print("ERROR get_sunset_utc:", e)
        raise

    f = (
        almanac.sunrise_sunset(
            eph,
            lokasi
        )
    )

    try:

        times, events = (
            almanac.find_discrete(
                t0,
                t1,
                f
            )
        )


        for t, e in zip(times, events):
            print(t.utc_datetime(), e)

        for t, e in zip(
            times,
            events
        ):

            if e == 1:
                return t


    except Exception as e:

        print("ERROR t1:", e)

        raise

    return None

@lru_cache(maxsize=1)
def get_ephemeris():

    ts = load.timescale()

    eph = load(
        "de440s.bsp"
    )

    return ts, eph

def geocentric_altitude(
    lat_deg,
    gst_hours,
    moon_ra_hours,
    moon_dec_deg,
    lon_deg
):
    """
    Tinggi Bulan geosentrik sesuai metodologi KHGT.
    """

    # Local Sidereal Time
    # lst = gst_hours + lon_deg / 15.0
    lst = (gst_hours + lon_deg / 15.0) % 24

    # Hour Angle
    # H = (lst - moon_ra_hours) * 15.0
    H = (lst - moon_ra_hours) % 24

    if H > 12:
        H -= 24

    H *= 15

    H = radians(H)

    e2 = 0.00669437999014

    lat = radians(lat_deg)

    phi = atan((1 - e2) * tan(lat))

    dec = radians(moon_dec_deg)

    h = asin(
        sin(phi) * sin(dec)
        +
        cos(phi) * cos(dec) * cos(H)
    )

    return degrees(h)

@lru_cache(maxsize=100000)
def hitung_hilal_cached(
    year,
    month,
    day,
    lat,
    lon
):

    ts, eph = (
        get_ephemeris()
    )


    earth = eph["earth"]
    moon = eph["moon"]
    sun = eph["sun"]

    sunset = get_sunset_utc(
        year,
        month,
        day,
        lat,
        lon
    )

    if sunset is None:
        return None


    earth_at = earth.at(sunset)

    moon_geo = earth_at.observe(moon)
    sun_geo = earth_at.observe(sun)

    ra_m, dec_m, _ = moon_geo.radec()
    ra_s, dec_s, _ = sun_geo.radec()

    ra_m, dec_m, _ = moon_geo.radec(epoch='date')

    gast = sunset.gast


    alt_geo = geocentric_altitude(
        lat,
        gast,
        ra_m.hours,
        dec_m.degrees,
        lon
    )

    elong = moon_geo.separation_from(sun_geo).degrees

    print("GAST =", sunset.gast)
    print("RA Moon =", ra_m.hours)
    print("Dec Moon =", dec_m.degrees)

    lst = sunset.gast + lon / 15.0
    print("LST =", lst)

    H = (lst - ra_m.hours) * 15.0
    print("Hour Angle =", H)

    print(
        lat,
        lon,
        "Geo Alt:",
        alt_geo,
        "Elong:",
        elong
    )

    return {

        "alt":
    round(
        alt_geo,
        4
    ),

        "elong":
            round(
                elong,
                4
            ),

        "sunset_utc":
            sunset.utc_datetime()
    }


@lru_cache(maxsize=100000)
def _cached_hitung_hilal(
    tanggal,
    lat,
    lon
):

    return hitung_hilal_cached(
        tanggal.year,
        tanggal.month,
        tanggal.day,
        round(lat, 4),
        round(lon, 4)
    )
# =========================================================
# SCAN GLOBAL
# =========================================================
@lru_cache(maxsize=500)
def scan_global_first_visibility(tanggal, ijt_utc):

    kandidat = []

    for lon in range(-180, 181, 2):
        for lat in range(-80, 81, 2):

            hasil = cek_titik(
                tanggal,
                ijt_utc,
                lat,
                lon
            )

            if hasil:

                kandidat.append({

                    "lat": lat,

                    "lon": lon,

                    **hasil
                })

    if not kandidat:
        return None

    kandidat.sort(
        key=lambda x: x["sunset_utc"]
    )

    return kandidat[0]

# =========================================================
# EVALUATE PKG 1
# =========================================================
def evaluate_pkg1(first_visibility):

    if first_visibility is None:
        return False

    return (
        first_visibility["sunset_utc"]
        <
        datetime.combine(
            first_visibility["sunset_utc"].date()
            + timedelta(days=1),
            time(0),
            tzinfo=timezone.utc
        )
    )
# =========================================================
# EVALUATE PKG 2
# =========================================================
def evaluate_pkg2(
    tanggal,
    ijt_utc
):

    nz_fajr = get_nz_fajr_utc(tanggal)

    if nz_fajr is None:
        return None

    # -------------------------------------------------
    # Syarat PKG2:
    # Ijtimak harus terjadi sebelum fajar Selandia Baru
    # -------------------------------------------------

    if ijt_utc >= nz_fajr:
        return None

    kandidat = []

    for lon in range(-170, -29):

        for lat in range(-60, 76):

            data = _cached_hitung_hilal(
                tanggal,
                lat,
                lon
            )

            if data is None:
                continue

            sunset = data["sunset_utc"]

            # hanya mencari sunset setelah 00 UTC
            # untuk memperoleh titik referensi peta

            if sunset <= datetime.combine(
                tanggal + timedelta(days=1),
                time(0),
                tzinfo=timezone.utc
            ):
                continue

            kandidat.append({

                "lat": lat,

                "lon": lon,

                "alt": data["alt"],

                "elong": data["elong"],

                "sunset_utc": sunset,

                "lokasi_awal":
                    f"{lat:.2f}, {lon:.2f}"

            })

    if not kandidat:

        return {

            "lat": None,
            "lon": None,
            "alt": None,
            "elong": None,
            "sunset_utc": None,
            "lokasi_awal": None,
            "nz_fajr_utc": nz_fajr

        }

    kandidat.sort(
        key=lambda x: x["sunset_utc"]
    )

    hasil = kandidat[0]

    hasil["nz_fajr_utc"] = nz_fajr

    return hasil

# =========================================================
# CEK GLOBAL KHGT
# =========================================================

def cek_imkan_global(
    tanggal,
    ijt_utc
):

    # -------------------------------------------------
    # First visibility (untuk PKG1)
    # -------------------------------------------------

    first_visibility = scan_global_first_visibility(
        tanggal,
        ijt_utc
    )

    pkg1 = evaluate_pkg1(
        first_visibility
    )

    # -------------------------------------------------
    # PKG2
    # -------------------------------------------------

    pkg2_result = evaluate_pkg2(
        tanggal,
        ijt_utc
    )

    pkg2 = pkg2_result is not None

    # -------------------------------------------------
    # Tentukan status
    # -------------------------------------------------

    if pkg1:

        status = "PKG 1"

    elif pkg2:

        status = "PKG 2"

    else:

        status = "Belum Memenuhi"



    hasil = {

        "status":
            (
                "Imkan Rukyat"
                if (pkg1 or pkg2)
                else "Belum Memenuhi"
            ),
        "pkg": status,

        "pkg1": pkg1,

        "pkg2": pkg2,

        "nz_fajr_utc":
            get_nz_fajr_utc(
                tanggal
            )
    }

    # -------------------------------------------------
    # Jika PKG1 terpenuhi
    # gunakan first visibility
    # -------------------------------------------------
    if pkg1:

        hasil.update(first_visibility)

    elif pkg2:

        hasil.update(pkg2_result)


    # if pkg1 and first_visibility:
    #
    #     hasil.update({
    #
    #         "lat":
    #             first_visibility["lat"],
    #
    #         "lon":
    #             first_visibility["lon"],
    #
    #         "alt":
    #             first_visibility["alt"],
    #
    #         "elong":
    #             first_visibility["elong"],
    #
    #         "lokasi_awal":
    #             first_visibility["lokasi_awal"],
    #
    #         "sunset_utc":
    #             first_visibility["sunset_utc"]
    #     })

    # -------------------------------------------------
    # Jika PKG1 gagal tetapi PKG2 berhasil
    # gunakan lokasi PKG2
    # -------------------------------------------------

    # elif pkg2:
    #
    #     hasil.update(pkg2_result)


    return hasil

# =========================================================
# KONVERSI HIJRIAH
# =========================================================

def konversi_hijriah(
    tanggal_target
):

    if isinstance(
        tanggal_target,
        datetime
    ):

        tanggal_target = (
            tanggal_target.date()
        )

    timeline = (
        build_timeline(
            tanggal_target
        )
    )

    for i in range(
        len(timeline) - 1
    ):

        if (

            timeline[i]["tgl_1"]

            <=

            tanggal_target

            <

            timeline[i + 1]["tgl_1"]

        ):

            hari = (

                tanggal_target

                -

                timeline[i]["tgl_1"]

            ).days + 1

            return {

                "hari":
                    hari,

                "bulan":
                    timeline[i]["nama"],

                "tahun":
                    timeline[i]["tahun_h"],

                "ijt_utc":
                    timeline[i]["ijt_utc"],

                "elongasi":
                    deg_to_dms(
                        timeline[i]["elongasi"]
                    ),

                "imkan":
                    (
                        "Imkan Rukyat"
                        if (
                                timeline[i]["pkg1"]
                                or
                                timeline[i]["pkg2"]
                        )
                        else
                        "Belum Memenuhi"
                    ),

                "pkg1":
                    timeline[i]["pkg1"],

                "pkg2":
                    timeline[i]["pkg2"],

                "status_kgth":
                    timeline[i]["status_pkg"],

                "lokasi_awal":
                    timeline[i]["lokasi_awal"],

                "lat":
                    timeline[i]["lat"],

                "lon":
                    timeline[i]["lon"],

                "alt":
                    timeline[i]["alt"],

                "elong_hilal":
                    timeline[i]["elong_hilal"],

                "sunset_utc":
                    timeline[i]["sunset_utc"],

                "nz_fajr_utc":
                    timeline[i].get("nz_fajr_utc")
            }



    return None


# =========================================================
# NORMALIZE
# =========================================================

def normalize_data(data):

    def convert(value):

        if isinstance(
            value,
            np.generic
        ):

            return value.item()

        if hasattr(
            value,
            "strftime"
        ):

            return value.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        return value

    if isinstance(data, dict):

        return {

            k:
                normalize_data(v)

            for k, v in (
                data.items()
            )
        }

    elif isinstance(data, list):

        return [

            normalize_data(v)

            for v in data
        ]

    return convert(data)


# =========================================================
# API
# =========================================================

def get_hijriah(
    tanggal=None
):

    if isinstance(
        tanggal,
        str
    ):

        tanggal = (
            datetime.strptime(
                tanggal,
                "%Y-%m-%d"
            ).date()
        )

    elif isinstance(
        tanggal,
        datetime
    ):

        tanggal = tanggal.date()

    elif tanggal is None:

        tanggal = (
            datetime.now()
            .date()
        )

    hasil = (
        konversi_hijriah(
            tanggal
        )
    )





    return {

        "tanggal":
            format_tanggal_indonesia(
                tanggal.isoformat()
            ),

        "hijriah":
            normalize_data(
                hasil
            )
    }


# =========================================================
# AUTO LOAD CACHE
# =========================================================

load_timeline_cache()

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    data = get_hijriah(
        "2026-11-10"
    )

    print("=" * 60)

    print(
        "Tanggal :",
        data["tanggal"]
    )

    print("=" * 60)

    print(
        "Hijriah :"
    )

    print(
        data["hijriah"]
    )

    print("=" * 60)

    print("\n=== TEST HILAL ===")
    print(
        hitung_hilal_cached(
            2026,
            6,
            15,
            63.7492,
            120.6267
        )
    )
