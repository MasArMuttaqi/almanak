
# ============================================================
# KONFIGURASI MARKAZ
# ============================================================

# Lokasi default
MARKAZ_DEFAULT = {
    "nama_kota": "Kota Yogyakarta",
    "lat": -7.7974565,
    "lon": 110.370697,
    "tz": 7
}


# ============================================================
# FUNGSI MENGAMBIL MARKAZ
# ============================================================

def get_markaz(
    nama_kota=None,
    lat=None,
    lon=None,
    tz=None
):

    return {
        "nama_kota": nama_kota or MARKAZ_DEFAULT["nama_kota"],
        "lat": MARKAZ_DEFAULT["lat"] if lat is None else float(lat),
        "lon": MARKAZ_DEFAULT["lon"] if lon is None else float(lon),
        "tz": MARKAZ_DEFAULT["tz"] if tz is None else float(tz)
    }
