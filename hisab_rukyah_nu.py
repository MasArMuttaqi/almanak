from math import sin, cos, tan, asin, acos, atan2, radians, degrees, floor
from datetime import datetime
import json
from konversitanggal import format_tanggal_indonesia

# =========================
# KONFIGURASI LOKASI
# =========================
LAT = -7.7974565
LON = 110.370697
TZ  = 7

# baca file JSON
with open("data/koreksirukyah.json", "r") as c:
    HIJRI_CORRECTION = json.load(c)

bulan_hijri = [
    "Muharram","Safar","Rabiul Awal","Rabiul Akhir",
    "Jumadil Awal","Jumadil Akhir","Rajab","Syaban",
    "Ramadhan","Syawal","Dzulqaidah","Dzulhijjah"
]

# =====================
# KONVERSI HIJRIAH JSON
# =====================
def masehi_to_hijri_json(target_date):
    target = datetime.strptime(target_date,"%Y-%m-%d")

    anchors = []

    for k,v in HIJRI_CORRECTION.items():
        y,m = k.split("-")
        anchors.append((datetime.strptime(v,"%Y-%m-%d"),int(y),int(m)))

    anchors.sort()

    for i in range(len(anchors)-1,-1,-1):
        base_date, hy, hm = anchors[i]

        if target >= base_date:
            delta = (target-base_date).days
            hm += delta // 30
            day = (delta % 30)+1

            while hm > 12:
                hm -= 12
                hy += 1

            return day, bulan_hijri[hm-1], hy

    return "-", "-", "-"

# =====================
# JULIAN DAY
# =====================
def julian_day(y,m,d,h=0):
    if m <= 2:
        y -= 1
        m += 12

    A = floor(y/100)
    B = 2 - A + floor(A/4)

    jd = floor(365.25*(y+4716)) + floor(30.6001*(m+1)) + d + B - 1524.5
    jd += h/24

    return jd

# =====================
# SUN POSITION
# =====================
def sun_position(jd):
    T = (jd-2451545.0)/36525

    L0 = (280.46646 + 36000.76983*T)%360
    M = radians((357.52911 + 35999.05029*T)%360)

    C = (1.914602-0.004817*T)*sin(M)+0.019993*sin(2*M)+0.000289*sin(3*M)

    lam = radians(L0+C)

    eps = radians(23.439291)

    RA = degrees(atan2(cos(eps)*sin(lam),cos(lam)))
    Dec = degrees(asin(sin(eps)*sin(lam)))

    return RA%360, Dec

# =====================
# MOON POSITION PRESISI
# =====================
def moon_position(jd):
    D = jd-2451545.0

    L0 = (218.316 + 13.176396*D)%360
    M = radians((134.963 + 13.064993*D)%360)
    Ms = radians((357.529 + 0.98560028*D)%360)
    F = radians((93.272 + 13.229350*D)%360)

    lon = L0 \
        + 6.289*sin(M) \
        + 1.274*sin(2*radians(L0)-M) \
        + 0.658*sin(2*radians(L0)) \
        + 0.214*sin(2*M) \
        - 0.186*sin(Ms)

    lat = 5.128*sin(F) + 0.280*sin(M+F)

    eps = radians(23.439291)

    lam = radians(lon)
    beta = radians(lat)

    RA = degrees(atan2(
        sin(lam)*cos(eps)-tan(beta)*sin(eps),
        cos(lam)
    ))

    Dec = degrees(asin(
        sin(beta)*cos(eps)+cos(beta)*sin(eps)*sin(lam)
    ))

    return RA%360, Dec

# =====================
# SIDEREAL TIME
# =====================
def sidereal_time(jd):
    T = (jd-2451545.0)/36525
    return (280.46061837 + 360.98564736629*(jd-2451545))%360

# =====================
# ALT AZ
# =====================
def altitude_azimuth(RA,Dec,jd):
    LST = (sidereal_time(jd)+LON)%360
    HA = radians((LST-RA)%360)

    lat = radians(LAT)
    dec = radians(Dec)

    alt = asin(
        sin(lat)*sin(dec)+cos(lat)*cos(dec)*cos(HA)
    )

    az = atan2(
        sin(HA),
        cos(HA)*sin(lat)-tan(dec)*cos(lat)
    )

    return degrees(alt),(degrees(az)+360)%360

# =====================
# REFRAKSI
# =====================
def refraksi(alt):
    if alt > -1:
        return 1.02/tan(radians(alt+10.3/(alt+5.11)))/60
    return 0

# =====================
# PARALLAX
# =====================
def parallax(alt):
    return 0.95*cos(radians(alt))

# =====================
# SUNSET
# =====================
def sunset(y,m,d):
    jd0 = julian_day(y,m,d,12)

    RA,Dec = sun_position(jd0)

    latr = radians(LAT)
    decr = radians(Dec)

    H = degrees(acos(
        (-sin(radians(-0.833))-sin(latr)*sin(decr)) /
        (cos(latr)*cos(decr))
    ))

    return 12+(H-LON)/15

# =====================
# HISAB FINAL
# =====================
def hisab_nu(y,m,d):
    ghurub = sunset(y,m,d)

    jd = julian_day(y,m,d,ghurub)

    hijri_d,hijri_m,hijri_y = masehi_to_hijri_json(f"{y:04d}-{m:02d}-{d:02d}")

    sunRA,sunDec = sun_position(jd)
    moonRA,moonDec = moon_position(jd)

    sunAlt,sunAz = altitude_azimuth(sunRA,sunDec,jd)
    moonAlt,moonAz = altitude_azimuth(moonRA,moonDec,jd)

    moon_mar_i = moonAlt + refraksi(moonAlt) - parallax(moonAlt)

    delta_ra = abs(sunRA-moonRA)
    if delta_ra > 180:
        delta_ra = 360-delta_ra

    elong = acos(
        sin(radians(sunDec))*sin(radians(moonDec)) +
        cos(radians(sunDec))*cos(radians(moonDec))*cos(radians(delta_ra))
    )

    elong = degrees(elong)

    # print("=== HISAB NU PRESISI ===")
    # print(f"Tanggal Masehi      : {y}-{m:02d}-{d:02d}")
    # print(f"Tanggal Hijriah     : {hijri_d} {hijri_m} {hijri_y} H")
    # print(f"Ghurub WIB          : {ghurub+TZ:.2f}")
    # print(f"Tinggi Hilal Hakiki : {moonAlt:.2f}°")
    # print(f"Tinggi Hilal Mar'i  : {moon_mar_i:.2f}°")
    # print(f"Elongasi            : {elong:.2f}°")
    # print(f"Azimut Matahari     : {sunAz:.2f}°")
    # print(f"Azimut Bulan        : {moonAz:.2f}°")
    #
    # if moon_mar_i >= 3 and elong >= 6.4:
    #     print("Status              : Memenuhi Imkan Rukyat")
    # else:
    #     print("Status              : Istikmal 30 Hari")
    # 1. Logika untuk Akhir Bulan (Penentuan apakah besok tanggal 1 atau Istikmal)
    if hijri_d in [29, 30]:
        if moon_mar_i >= 3 and elong >= 6.4:
            kesimpulan = {
                "status": "Memenuhi Imkan Rukyat",
                "kriteria": "MABIMS 3-6.4",
                "keterangan": "Besok adalah tanggal 1 bulan baru."
            }
        else:
            kesimpulan = {
                "status": "Istikmal 30 Hari",
                "kriteria": "MABIMS 3-6.4",
                "keterangan": "Bulan digenapkan menjadi 30 hari."
            }

    # 2. Logika Khusus saat masuk Tanggal 1 Bulan Baru
    elif hijri_d == 1:
        if moon_mar_i >= 3 and elong >= 6.4:
            kesimpulan = {
                "status": "Awal Bulan Baru",
                "kriteria": "MABIMS 3-6.4",
                "informasi": "Hilal terlihat/memenuhi syarat pada petang sebelumnya."
            }
        else:
            # Kasus jika tanggal 1 dicapai melalui jalur Istikmal
            kesimpulan = {
                "status": "Awal Bulan Baru (Istikmal)",
                "kriteria": "MABIMS 3-6.4",
                "informasi": "Bulan baru dimulai setelah penggenapan 30 hari."
            }
    else:
        kesimpulan = None  # Tidak tampil di pertengahan bulan


    result = {
        "tanggal_masehi": format_tanggal_indonesia(f"{y}-{m:02d}-{d:02d}"),
        "tanggal_hijriah": {
            "hari": hijri_d,
            "bulan": hijri_m,
            "tahun": hijri_y,
            "full": f"{hijri_d} {hijri_m} {hijri_y} H"
        },
        "data_astronomi": {
            "ghurub_wib": round(ghurub + TZ, 2),
            "tinggi_hilal_hakiki": round(moonAlt, 2),
            "tinggi_hilal_mari": round(moon_mar_i, 2),
            "elongasi": round(elong, 2),
            "azimut_matahari": round(sunAz, 2),
            "azimut_bulan": round(moonAz, 2)
        },
        "kesimpulan": kesimpulan,
        # "kesimpulan": {
        #     "status": "Memenuhi Imkan Rukyat" if (moon_mar_i >= 3 and elong >= 6.4) else "Istikmal 30 Hari",
        #     "kriteria": "MABIMS 3-6.4"
        # }
    }
    return result
# =====================
# CONTOH
# =====================
# hisab_nu(2026,4,2)
# today = datetime.now().date()
# print(hisab_nu(today.year, today.month, today.day))