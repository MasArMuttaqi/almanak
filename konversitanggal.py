from datetime import datetime

def konversi_ke_hijaiyah(angka_input):
    # Mapping angka Arab ke Hijaiyah
    map_angka = {
        '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
        '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
    }

    # Konversi setiap karakter dalam string
    hasil = "".join(map_angka.get(char, char) for char in str(angka_input))
    return hasil

def hijri_label(hijri_code: str) -> str:
    # Mapping bulan Hijriyah
    hijri_months = {
        "01": "Muharram",
        "02": "Safar",
        "03": "Rabiul Awal",
        "04": "Rabiul Akhir",
        "05": "Jumadil Ula",
        "06": "Jumadil Akhir",
        "07": "Rajab",
        "08": "Syaban",
        "09": "Ramadhan",
        "10": "Syawal",
        "11": "Zulqaidah",
        "12": "Zulhijjah"
    }

    # Pisahkan tahun-bulan → contoh "1447-03"
    tahun, bulan = hijri_code.split("-")
    bulan_nama = hijri_months.get(bulan, "Unknown")

    return f"{bulan_nama} {tahun}"

def format_tanggal_indonesia(tanggal_str):
    # Ubah string ke objek datetime
    tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d")

    # Nama bulan dalam bahasa Indonesia
    bulan_indonesia = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    # Ambil bagian hari, bulan, tahun
    hari = tanggal.day
    bulan = bulan_indonesia[tanggal.month - 1]
    tahun = tanggal.year

    # Format jadi string
    return f"{hari} {bulan} {tahun}"

def bulan_indonesia(tanggal):
    nama_bulan = [
        "Januari","Februari","Maret","April","Mei","Juni",
        "Juli","Agustus","September","Oktober","November","Desember"
    ]
    return f"{nama_bulan[tanggal.month-1]} {tanggal.year}"
