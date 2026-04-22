from datetime import datetime, timedelta
from konversitanggal import *
from hisab_rukyah_nu import *
from kalender_jawa_sultan_agungan import *

today = datetime.now().date()

def candranipun(pranatamangsa):

    with open("data/prantamangsa.json", "r") as raw_pr:
        candra = json.load(raw_pr)
        # Mencari data dengan List Comprehension
    candranipun = [item for item in candra if item['Mangsa'] == pranatamangsa]

    return candranipun

def kalender_vertikal(tanggal=None):
    if tanggal is None:
        tanggal = datetime.now()

    awal = tanggal.replace(day=1)

    # offset hari pertama (Minggu=0)
    offset = (awal.weekday() + 1) % 7

    # struktur: 7 hari x 6 minggu (fix kolom)
    hasil = [[None for _ in range(6)] for _ in range(7)]

    mingguan = [[] for _ in range(6)]

    tgl = awal
    periode_hijriah = []
    periode_jawa = []

    current_periode_h = None
    current_periode_j = None

    while tgl.month == tanggal.month:
        # ubah ke format Minggu=0
        hari_index = (tgl.weekday() + 1) % 7
        minggu_ke = (tgl.day + offset - 1) // 7

        # =========================
        # HISAB HIJRIAH
        # =========================
        h = hisab_nu(tgl.year, tgl.month, tgl.day)
        bulan_h = h['tanggal_hijriah']['bulan']
        tahun_h = h['tanggal_hijriah']['tahun']
        tanggal_h = h['tanggal_hijriah']['hari']

        # =========================
        # KALENDER JAWA
        # =========================
        j = kalender_jawa(tgl)
        tanggal_j = j['tanggal_jawa'].split()
        tgl_jawa = tanggal_j[0]
        bulan_tahun_j = f"{tanggal_j[1]} {tanggal_j[2]} {tanggal_j[3]}"
        pasaran_j = j['hari_jawa']
        pasaran_c = j['hari_caka']
        wuku = j['wuku']
        sadwara = j['sadwara']

        # =========================
        # SIMPAN KE GRID KALENDER
        # =========================
        hasil[hari_index][minggu_ke] = {
            "tanggal_id": f"{today.year}-{today.month}-{tgl.day}",
            "tgl": tgl.day,
            "tgl_jawa":tgl_jawa,
            "pasaran": pasaran_j,
            "pasaran_caka": pasaran_c,
            "hari": hari_index,
            "wuku": wuku,
            "sadwara": sadwara,
            "tgl_hijriah":konversi_ke_hijaiyah(tanggal_h),
            "tgl_bulan_tahun_h": h['tanggal_hijriah'],
            "is_today": tgl.date() == today
        }

        current_week = mingguan[minggu_ke]

        if not current_week:
            # entry pertama di minggu ini
            current_week.append({
                "wuku": wuku,
                "awal": tgl,
                "akhir": tgl
            })
        else:
            last = current_week[-1]

            # jika masih wuku yang sama → lanjut
            if last["wuku"] == wuku:
                last["akhir"] = tgl
            else:
                # 🔥 wuku berubah → buat segmen baru
                current_week.append({
                    "wuku": wuku,
                    "awal": tgl,
                    "akhir": tgl
                })

        # =========================
        # GROUPING PERIODE HIJRIAH
        # =========================
        if current_periode_h is None:
            current_periode_h = {
                "bulan_hijriah": bulan_h,
                "tahun_hijriah": tahun_h,
                "awal_masehi": tgl,
                "akhir_masehi": tgl
            }

        elif (bulan_h, tahun_h) == (current_periode_h['bulan_hijriah'], current_periode_h['tahun_hijriah']):
            current_periode_h['akhir_masehi'] = tgl
        else:
            periode_hijriah.append(current_periode_h)
            current_periode_h = {
                "bulan_hijriah": bulan_h,
                "tahun_hijriah": tahun_h,
                "awal_masehi": tgl,
                "akhir_masehi": tgl
            }

        if current_periode_j is None:
            current_periode_j = {
                "bulan_tahun_jawa": bulan_tahun_j,
                "awal": tgl,
                "akhir": tgl
            }

        elif bulan_tahun_j == current_periode_j['bulan_tahun_jawa']:
            current_periode_j['akhir'] = tgl
        else:
            periode_jawa.append(current_periode_j)
            current_periode_j = {
                "bulan_tahun_jawa": bulan_tahun_j,
                "awal": tgl,
                "akhir": tgl
            }

        tgl += timedelta(days=1)

    if current_periode_h:
        periode_hijriah.append(current_periode_h)

    if current_periode_j:
        periode_jawa.append(current_periode_j)

    # return hasil
    for minggu in mingguan:
        for seg in minggu:
            if seg.get("awal") and hasattr(seg["awal"], "strftime"):
                seg["awal"] = seg["awal"].strftime("%d")

            if seg.get("akhir") and hasattr(seg["akhir"], "strftime"):
                seg["akhir"] = seg["akhir"].strftime("%d")
        # =========================
        # RETURN TETAP KOMPATIBEL
        # =========================
    pranatamangsa = hitung_mangsa(today)
    return {
       "grid": hasil,  # 🔥 tetap dipakai Jinja kamu
       "periode_hijriah": periode_hijriah,  # 🔥 tambahan baru
       "periode_jawa": periode_jawa,
       "mingguan": mingguan,
       "candranipun": candranipun(pranatamangsa)
       # "data_harian": data_harian  # opsional
    }

