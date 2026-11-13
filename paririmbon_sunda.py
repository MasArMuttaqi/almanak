"""
Modul Paririmbon Sunda
======================

Membaca data Poé-poé Hadé jeung Goréng dari JSON berdasarkan hasil
fungsi kala_candra_sunda().

Letakkan file JSON `poe_hade_goreng_kartika_1959.json` satu folder
dengan modul ini, atau berikan argumen `file_json` secara eksplisit.

Kontrak input utama:
    hasil = kala_candra_sunda(...)
    paririmbon = hitung_paririmbon_sunda(hasil)

Kunci yang dibaca:
    tanggal / kaping       : tanggal Caka (1..30), atau tanggal paksa (1..15)
    bulan                  : nama bulan Caka Sunda
    tahun                  : tahun Caka Sunda
    paksa                  : opsional, "Suklapaksa"/"Kresnapaksa" atau "s"/"k"

Jika `tanggal` bernilai 16..30, fungsi menganggapnya sebagai tanggal
berjalan dalam bulan dan mengubahnya menjadi kaping 1..15 Kresnapaksa.
Jika tanggal bernilai 1..15 dan paksa tidak disediakan, diasumsikan
Suklapaksa. Untuk tanggal paksa 1..15 Kresnapaksa, paksa wajib diberikan.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


# FILE_JSON_DEFAULT = Path(__file__).with_name(
#     "poe_hade_goreng_kartika_1959.json"
# )

FILE_PARIRIMBON = "data/poe_hade_goreng_kartika_1959.json"


class ParirimbonError(Exception):
    """Kesalahan umum saat membaca atau mencari data paririmbon."""


class TanggalParirimbonError(ParirimbonError):
    """Struktur tanggal Caka Sunda tidak lengkap atau tidak valid."""


class DataParirimbonTidakDitemukan(ParirimbonError):
    """Data untuk tanggal yang diminta belum tersedia di JSON."""


@lru_cache(maxsize=8)
def baca_data_paririmbon(file_json: str | Path = FILE_PARIRIMBON) -> dict:
    """Membaca JSON paririmbon. Hasil dib缓存 berdasarkan lokasi file."""
    path = Path(file_json).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(
            f"File JSON paririmbon tidak ditemukan: {path}"
        )

    with path.open("r", encoding="utf-8") as berkas:
        data = json.load(berkas)

    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        raise ParirimbonError(
            "Format JSON tidak sesuai: harus berupa objek dengan daftar 'data'."
        )

    return data


def _ambil(hasil: Mapping[str, Any], *nama_kunci: str) -> Any:
    """Mengambil nilai pertama yang tersedia dari beberapa nama kunci."""
    for nama in nama_kunci:
        if nama in hasil and hasil[nama] is not None:
            return hasil[nama]
    return None


def _normalisasi_paksa(nilai: Any) -> str | None:
    if nilai is None:
        return None

    teks = str(nilai).strip().lower()
    if teks in {"s", "sukla", "suklapaksa", "sukla paksa"}:
        return "Suklapaksa"
    if teks in {"k", "kresna", "kresnapaksa", "kresna paksa"}:
        return "Kresnapaksa"

    raise TanggalParirimbonError(
        f"Nilai paksa tidak dikenali: {nilai!r}. "
        "Gunakan 's'/'Suklapaksa' atau 'k'/'Kresnapaksa'."
    )


def _normalisasi_tanggal(hasil_kala_candra: Mapping[str, Any]) -> dict:
    """
    Mengubah hasil kala_candra_sunda menjadi kunci pencarian JSON.

    Mendukung:
      - kode_kaping: '1s' sampai '15s', atau '1k' sampai '15k'
      - tanggal/kaping 1..30 (tanggal berjalan dalam bulan)
      - tanggal/tanggal_paksa 1..15 + paksa eksplisit
    """
    if not isinstance(hasil_kala_candra, Mapping):
        raise TanggalParirimbonError(
            "Hasil kala_candra_sunda harus berupa dictionary/mapping."
        )

    tahun = _ambil(hasil_kala_candra, "tahun", "tahun_caka")
    bulan = _ambil(hasil_kala_candra, "bulan", "nama_bulan")
    kode = _ambil(hasil_kala_candra, "kode_kaping")

    if tahun is None or bulan is None:
        raise TanggalParirimbonError(
            "Hasil kala_candra_sunda harus memiliki kunci 'tahun' dan 'bulan'."
        )

    if kode is not None:
        kode = str(kode).strip().lower()
        if len(kode) < 2 or kode[-1] not in {"s", "k"}:
            raise TanggalParirimbonError(
                f"Format kode_kaping tidak valid: {kode!r}."
            )
        try:
            kaping = int(kode[:-1])
        except ValueError as exc:
            raise TanggalParirimbonError(
                f"Format kode_kaping tidak valid: {kode!r}."
            ) from exc
        paksa = "Suklapaksa" if kode.endswith("s") else "Kresnapaksa"
    else:
        nilai_tanggal = _ambil(
            hasil_kala_candra, "tanggal_paksa", "kaping", "tanggal"
        )
        if nilai_tanggal is None:
            raise TanggalParirimbonError(
                "Tanggal tidak ditemukan. Diperlukan 'tanggal', 'kaping', "
                "atau 'kode_kaping'."
            )

        try:
            nilai_tanggal = int(nilai_tanggal)
        except (TypeError, ValueError) as exc:
            raise TanggalParirimbonError(
                f"Nilai tanggal bukan bilangan bulat: {nilai_tanggal!r}."
            ) from exc

        paksa = _normalisasi_paksa(
            _ambil(hasil_kala_candra, "paksa", "fase", "paksa_bulan")
        )

        if 16 <= nilai_tanggal <= 30:
            # Tanggal berjalan 16..30 berarti Kresnapaksa kaping 1..15.
            if paksa == "Suklapaksa":
                raise TanggalParirimbonError(
                    "Tanggal 16..30 bertentangan dengan paksa Suklapaksa."
                )
            paksa = "Kresnapaksa"
            kaping = nilai_tanggal - 15
        elif 1 <= nilai_tanggal <= 15:
            # Jika tidak ada paksa, tanggal 1..15 diasumsikan Suklapaksa.
            paksa = paksa or "Suklapaksa"
            kaping = nilai_tanggal
        else:
            raise TanggalParirimbonError(
                f"Tanggal harus berada pada rentang 1..30, bukan {nilai_tanggal}."
            )

    if not 1 <= kaping <= 15:
        raise TanggalParirimbonError(
            f"Kaping paksa harus 1..15, bukan {kaping}."
        )

    try:
        tahun = int(tahun)
    except (TypeError, ValueError) as exc:
        raise TanggalParirimbonError(
            f"Tahun Caka tidak valid: {tahun!r}."
        ) from exc

    bulan = str(bulan).strip()
    kode_kaping = f"{kaping}{'s' if paksa == 'Suklapaksa' else 'k'}"

    return {
        "tahun": tahun,
        "bulan": bulan,
        "paksa": paksa,
        "kaping": kaping,
        "kode_kaping": kode_kaping,
    }


def cari_data_paririmbon(
    hasil_kala_candra: Mapping[str, Any],
    file_json: str | Path = FILE_PARIRIMBON,
) -> dict:
    """
    Mencari satu rekaman paririmbon berdasarkan hasil kala_candra_sunda().

    Mengembalikan rekaman JSON apa adanya. Tidak menghitung atau mengubah
    waktu Salamet/Rejeki.
    """
    kunci = _normalisasi_tanggal(hasil_kala_candra)
    data = baca_data_paririmbon(file_json)

    tahun_json = data.get("tahun")
    bulan_json = data.get("bulan")

    if tahun_json is not None and int(tahun_json) != kunci["tahun"]:
        raise DataParirimbonTidakDitemukan(
            f"Data tersedia untuk tahun {tahun_json}, "
            f"sedangkan tanggal yang diminta tahun {kunci['tahun']}."
        )

    if bulan_json is not None and str(bulan_json).casefold() != kunci["bulan"].casefold():
        raise DataParirimbonTidakDitemukan(
            f"Data tersedia untuk bulan {bulan_json}, "
            f"sedangkan tanggal yang diminta bulan {kunci['bulan']}."
        )

    for rekaman in data["data"]:
        if (
            int(rekaman.get("tahun", data.get("tahun", 0))) == kunci["tahun"]
            and str(rekaman.get("bulan", data.get("bulan", ""))).casefold()
                == kunci["bulan"].casefold()
            and str(rekaman.get("paksa", "")).casefold()
                == kunci["paksa"].casefold()
            and int(rekaman.get("kaping", 0)) == kunci["kaping"]
        ):
            return dict(rekaman)

    raise DataParirimbonTidakDitemukan(
        "Rekaman paririmbon belum tersedia untuk "
        f"{kunci['kaping']} {kunci['paksa']} {kunci['bulan']} {kunci['tahun']}."
    )


def hitung_paririmbon_sunda(
    hasil_kala_candra: Mapping[str, Any],
    file_json: str | Path = FILE_PARIRIMBON,
) -> dict:
    """
    Antarmuka utama untuk dipanggil setelah kala_candra_sunda().

    Nama 'hitung' dipertahankan untuk kemudahan integrasi, tetapi fungsi ini
    mengambil hasil tabel JSON; bukan menghitung ulang rumus paririmbon.
    """
    kunci = _normalisasi_tanggal(hasil_kala_candra)
    rekaman = cari_data_paririmbon(hasil_kala_candra, file_json)

    return {
        "tersedia": True,
        "tahun": kunci["tahun"],
        "bulan": kunci["bulan"],
        "paksa": kunci["paksa"],
        "kaping": kunci["kaping"],
        "kode_kaping": kunci["kode_kaping"],
        "poe": rekaman.get("poe"),
        "pasar": rekaman.get("pasar"),
        "poe_hade": rekaman.get("klasifikasi", {}).get("poe_hade"),
        "poe_goreng": rekaman.get("klasifikasi", {}).get("poe_goreng"),
        "dawuh": rekaman.get("dawuh", []),
        "status_verifikasi": rekaman.get("status_verifikasi"),
        "sumber_data": "poe_hade_goreng_kartika_1959.json",
    }


def format_waktu_paririmbon(hasil_paririmbon: Mapping[str, Any]) -> str:
    """Membuat ringkasan teks sederhana; berguna untuk log atau pengujian."""
    baris = [
        (
            f"{hasil_paririmbon.get('kaping')} "
            f"{hasil_paririmbon.get('bulan')} "
            f"{hasil_paririmbon.get('tahun')}"
        ),
        (
            f"{hasil_paririmbon.get('poe')} "
            f"{hasil_paririmbon.get('pasar')}"
        ),
        (
            f"Poé Hadé: {hasil_paririmbon.get('poe_hade')} | "
            f"Poé Goréng: {hasil_paririmbon.get('poe_goreng')}"
        ),
    ]

    for item in hasil_paririmbon.get("dawuh", []):
        baris.append(
            f"Dawuh {item.get('nomor')}: "
            f"Salamet {item.get('salamet')} - "
            f"Rejeki {item.get('rejeki')}"
        )

    return "\n".join(baris)


if __name__ == "__main__":
    # Contoh uji mandiri. Ganti dictionary ini dengan hasil fungsi
    # kala_candra_sunda() dari proyek Anda.
    contoh_hasil_kala_candra = {
        "tanggal": 1,
        "bulan": "Kartika",
        "tahun": 1959,
        "paksa": "Suklapaksa",
    }

    try:
        hasil = hitung_paririmbon_sunda(contoh_hasil_kala_candra)
        print(format_waktu_paririmbon(hasil))
        print(hasil)
    except ParirimbonError as error:
        print(f"Paririmbon: {error}")
    except FileNotFoundError as error:
        print(error)
