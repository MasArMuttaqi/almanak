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

def hari_penting(tanggal_hijriah, tanggal_masehi):
    with open("data/hari_besar.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    hasil = []

    # Hari besar Islam
    for item in data.get("hari_peringatan_keagamaan_islam", []):
        if item.get("tanggal_hijriah") == tanggal_hijriah:
            hasil.append({
                "kategori": "hijr-day",
                "tanggal_masehi": tanggal_masehi,
                **item
            })

    # Hari nasional
    for item in data.get("hari_peringatan_nasional_indonesia", []):
        if item.get("tanggal_masehi") == tanggal_masehi:
            hasil.append({
                "kategori": "national-day",
                "tanggal_hijriah": tanggal_hijriah,
                **item
            })

    return hasil

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

    hari_penting_hasil = {}

    while tgl.month == tanggal.month:
        # ubah ke format Minggu=0
        hari_index = (tgl.weekday() + 1) % 7
        minggu_ke = (tgl.day + offset - 1) // 7

        # =========================
        # TANGGAL MASEHI
        # =========================
        tgl_masehi = f"{tgl.day} {bulan_indonesia_pendek(tgl.month)}"

        # =========================
        # HISAB HIJRIAH
        # =========================
        h = hisab_nu(tgl.year, tgl.month, tgl.day)
        bulan_h = h['tanggal_hijriah']['bulan']
        tahun_h = h['tanggal_hijriah']['tahun']
        tanggal_h = h['tanggal_hijriah']['hari']
        tgl_bulan_h = f"{h['tanggal_hijriah']['hari']} {h['tanggal_hijriah']['bulan']}"

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
        wuku_index = j['wuku_index']
        sadwara = j['sadwara']

        # =========================
        # HARI PENTING
        # =========================
        hp = hari_penting(tgl_bulan_h, tgl_masehi)
        for item in hp:
            key = f"{tgl:%Y-%m-%d}-{item.get('nama_peringatan','')}"
            hari_penting_hasil[key] = {
                # "tanggal": tgl.strftime("%Y-%m-%d"),
                **item
            }

        # =========================
        # SIMPAN KE GRID KALENDER
        # =========================
        hasil[hari_index][minggu_ke] = {
            "tanggal_id": f"{today.year}-{today.month:02d}-{tgl.day:02d}",
            "tgl": tgl.day,
            "tgl_jawa":tgl_jawa,
            "pasaran": pasaran_j,
            "pasaran_caka": pasaran_c,
            "hari": hari_index,
            "wuku": wuku,
            "wuku_index": wuku_index,
            "sadwara": sadwara,
            "tgl_hijriah":konversi_ke_hijaiyah(tanggal_h),
            "is_today": tgl.date() == today
        }

        current_week = mingguan[minggu_ke]

        if not current_week:
            # entry pertama di minggu ini
            current_week.append({
                "wuku": wuku,
                "wuku_index": wuku_index,
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
                    "wuku_index": wuku_index,
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
       "grid": hasil,
       "periode_hijriah": periode_hijriah, 
       "periode_jawa": periode_jawa,
       "mingguan": mingguan,
       "candranipun": candranipun(pranatamangsa),
       "hari_penting": list(hari_penting_hasil.values())
       # "data_harian": data_harian  # opsional
    }

if __name__ == "__main__":

    # data = kalender_vertikal(
    #     datetime.now
    # )

    print(kalender_vertikal())
