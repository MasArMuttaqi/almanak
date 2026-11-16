import json

FILE_JSON_PARIRIMBON = "data/poe_hade_goreng.json"

def pancawuku(saptawara, pancawara):
    # 1. Membaca file JSON
    with open(FILE_JSON_PARIRIMBON, "r", encoding="utf-8") as file:
        data_list = json.load(file)

    # 2. Mencari item yang cocok (case-insensitive / tidak peduli huruf besar-kecil)
    hasil = next(
        (
            item
            for item in data_list
            if item["Saptawara"].lower() == saptawara.lower()
            and item["Pancawara"].lower() == pancawara.lower()
        ),
        None,  # Mengembalikan None jika data tidak ditemukan
    )

    return hasil

def hitung_indeks_dawuh(neptu_weton, nomor_tanggal_sasih):
    """
    Menghitung indeks Dawuh aktif (1–5). Jika sisa pembagian adalah 0, harus menjadi Dawuh 5
    """
    indeks = ((neptu_weton + nomor_tanggal_sasih - 1) % 5) + 1
    return indeks

def hitung_paririmbon_sunda(saptawara, pancawara, nomor_tanggal_sasih):
    hasil_pencarian = pancawuku(saptawara, pancawara)
    dawuh = hitung_indeks_dawuh(hasil_pencarian['Nilai_Pancawuku'], nomor_tanggal_sasih)

    return{
        "poehade": hasil_pencarian['PoeHade'],
        "poegoreng" : hasil_pencarian['PoeGoreng'],
        "sifat": hasil_pencarian['Sifat_Utama'],
        "dawuh": dawuh
    }
    
if __name__ == "__main__":

    print("=" * 60)
    print("PENGUJIAN PANCAWUKU")
    print("=" * 60)

    hasil_pencarian = pancawuku("Respati", "Kaliwon")
    dawuh = hitung_indeks_dawuh(hasil_pencarian['Nilai_Pancawuku'], 2)

    if hasil_pencarian:
        print("Data ditemukan:")
        print(f"Nilai Pancawuku : {hasil_pencarian['Nilai_Pancawuku']}")
        print(f"Poe Hade        : {hasil_pencarian['PoeHade']}")
        print(f"Poe Goreng      : {hasil_pencarian['PoeGoreng']}")
        print(f"Sifat Utama     : {hasil_pencarian['Sifat_Utama']}")
    else:
        print("Kombinasi Saptawara dan Pancawara tidak ditemukan.")

    print(f"dawuh     : {dawuh}")


    print("=" * 60)