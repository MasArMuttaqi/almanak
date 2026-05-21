from functools import lru_cache
from skyfield.api import load, wgs84
from skyfield import almanac
from datetime import datetime, timedelta, date
from pathlib import Path

import numpy as np
import json

from konversitanggal import format_tanggal_indonesia

# =========================================================
# DIRECTORY CACHE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

REF_DIR = BASE_DIR / "data" / "ref_kgth"

REF_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TIMELINE_FILE = (
    REF_DIR /
    "timeline_cache.json"
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
        f"{s:.2f}″"
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
                    item["tgl_1"]
                    .isoformat(),

                "ijt_utc":
                    item["ijt_utc"]
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "elongasi":
                    item["elongasi"],

                "nama":
                    item["nama"],

                "tahun_h":
                    item["tahun_h"],

                "status_pkg":
                    item["status_pkg"]
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

                    "status_pkg":
                        item["status_pkg"]
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
# EPHEMERIS
# =========================================================

@lru_cache(maxsize=1)
def get_ephemeris():

    ts = load.timescale()

    eph = load(
        "de440s.bsp"
    )

    return ts, eph


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
                .apparent()
            )

            s = (
                e.observe(sun)
                .apparent()
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
# SUNSET CACHE
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
            datetime(
                year,
                month,
                day
            ) + timedelta(days=1)
        )

    except:
        return None

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

        for t, e in zip(
            times,
            events
        ):

            if e == 0:
                return t

    except:
        return None

    return None


# =========================================================
# HITUNG HILAL
# =========================================================

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

    lokasi = (
        wgs84.latlon(
            lat,
            lon
        )
    )

    observer = (
        earth + lokasi
    )

    observer_at = (
        observer.at(sunset)
    )

    moon_app = (
        observer_at
        .observe(moon)
        .apparent()
    )

    sun_app = (
        observer_at
        .observe(sun)
        .apparent()
    )

    alt, az, dist = (
        moon_app.altaz()
    )

    elong = (
        moon_app
        .separation_from(
            sun_app
        )
        .degrees
    )

    return {

        "alt":
            round(
                alt.degrees,
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
        round(lat, 2),
        round(lon, 2)
    )


# =========================================================
# KGTH RULE
# =========================================================

def is_america(lon):

    return (
        -170 <= lon <= -30
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


# =========================================================
# CEK TITIK
# =========================================================

def cek_titik(
    tanggal,
    ijt_utc,
    lat,
    lon
):

    data = (
        _cached_hitung_hilal(
            tanggal,
            lat,
            lon
        )
    )

    if not data:
        return None

    sunset_utc = (
        data["sunset_utc"]
    )

    normal_case = (

        sunset_utc > ijt_utc

        and

        sunset_utc.date()
        == tanggal
    )

    special_case = False

    if sunset_utc > ijt_utc:

        if (
            sunset_utc.date()
            > tanggal
        ):

            if (

                is_america(lon)

                and

                ijtimak_before_nz_fajr(
                    ijt_utc
                )

            ):

                special_case = True

    sunset_ok = (
        normal_case or
        special_case
    )

    current_ok = (

        sunset_ok

        and

        data["alt"] >= 5

        and

        data["elong"] >= 8
    )

    if not current_ok:
        return None

    return {

        "pkg":
            (
                "PKG 1 "
                "(sebelum 24:00 UTC)"
            )
            if normal_case
            else
            (
                "PKG 2 "
                "(penyelarasan global)"
            )
    }


# =========================================================
# CEK GLOBAL OPTIMIZED
# =========================================================

@lru_cache(maxsize=500)
def cek_imkan_global(
    tanggal,
    ijt_utc,
    resolusi_awal=10,
    resolusi_final=5
):

    # =====================================================
    # PASS 1
    # GRID KASAR
    # =====================================================

    kandidat_area = []

    for lon in range(
        -180,
        181,
        resolusi_awal
    ):

        for lat in range(
            -60,
            61,
            resolusi_awal
        ):

            hasil = cek_titik(
                tanggal,
                ijt_utc,
                lat,
                lon
            )

            if hasil:

                kandidat_area.append(
                    (
                        lat,
                        lon
                    )
                )

    # =====================================================
    # TIDAK ADA KANDIDAT
    # =====================================================

    if not kandidat_area:

        return {

            "status":
                "Belum Memenuhi",

            "pkg":
                "Belum Memenuhi"
        }

    # =====================================================
    # PASS 2
    # REFINE 5°
    # =====================================================

    for base_lat, base_lon in (
        kandidat_area
    ):

        for lon in range(
            base_lon - 10,
            base_lon + 11,
            resolusi_final
        ):

            for lat in range(
                base_lat - 10,
                base_lat + 11,
                resolusi_final
            ):

                hasil = cek_titik(
                    tanggal,
                    ijt_utc,
                    lat,
                    lon
                )

                if hasil:

                    return {

                        "status":
                            "Imkan Rukyat",

                        "pkg":
                            hasil["pkg"]
                    }

    return {

        "status":
            "Belum Memenuhi",

        "pkg":
            "Belum Memenuhi"
    }


# =========================================================
# BUILD TIMELINE
# =========================================================

def build_timeline(
    tanggal_target
):

    tahun_key = (
        tanggal_target.year
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

        if ijt_dt.date() >= date(
            2024,
            12,
            30
        ):

            ref_idx = i

            break

    if ref_idx is None:
        return []

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

        start_offset = 1

        if ijt_dt.hour >= 18:

            start_offset = 2

        tgl_1 = None

        status_pkg = (
            "PKG 2 "
            "(penyelarasan global)"
        )

        for offset in range(
            start_offset,
            4
        ):

            kandidat = (

                ijt_dt.date()

                +

                timedelta(days=offset)
            )

            imkan = (
                cek_imkan_global(
                    kandidat,
                    ijt_dt
                )
            )

            if (
                imkan["status"]
                ==
                "Imkan Rukyat"
            ):

                tgl_1 = kandidat

                status_pkg = (
                    imkan["pkg"]
                )

                break

        if tgl_1 is None:

            tgl_1 = (

                ijt_dt.date()

                +

                timedelta(days=2)
            )

        timeline.append({

            "tgl_1":
                tgl_1,

            "ijt_utc":
                ijt_dt,

            "elongasi":
                elong,

            "nama":
                BULAN_HIJRIAH[
                    curr_h_idx
                ],

            "tahun_h":
                curr_h_year,

            "status_pkg":
                status_pkg
        })

        curr_h_idx = (
            curr_h_idx + 1
        ) % 12

        if curr_h_idx == 0:

            curr_h_year += 1

    TIMELINE_CACHE[
        tahun_key
    ] = timeline

    save_timeline_cache()

    print(
        f"[CACHE BUILD] "
        f"{tahun_key}"
    )

    return timeline


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
                        timeline[i][
                            "elongasi"
                        ]
                    ),

                "imkan":
                    "Imkan Rukyat",

                "status_kgth":
                    timeline[i][
                        "status_pkg"
                    ]
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
        "2026-05-24"
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
