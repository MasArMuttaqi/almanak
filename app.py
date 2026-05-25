# save this as app.py
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from functools import wraps
# from datetime import datetime
# from konversitanggal import *
# import json
from kalender import *
from kalender_jawa_sultan_agungan import *
from hisab_rukyah_nu import *
from hisab_wujud_hilal import *
from hijriah_kgth import get_hijriah

import os
import io
import qrcode
import pyotp


app = Flask(__name__)
app.secret_key = "22de06ad-aff4-4d2e-bb32-1347f7a697a9"  # ganti dengan key aman

FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH = "data/koreksirukyah.json"

@app.route("/")
def dashboard():
    now = datetime.now()
    data = kalender_vertikal()
    bulan = bulan_indonesia(now)
    return render_template("dashboard.html",bulan= bulan,data=data["grid"],periode_hijriah=data["periode_hijriah"],periode_jawa=data["periode_jawa"], wuku=data["mingguan"],candranipun=data["candranipun"])

@app.route('/detail-kalender')
def detail_kalender():
    try:
        tanggal_str = request.args.get('tanggal')

        if tanggal_str:
            try:
                # parsing string ke date
                tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()
            except ValueError:
                # fallback jika format salah
                tanggal = datetime.now().date()
        else:
            # default hari ini
            tanggal = datetime.now().date()

        jawa = kalender_jawa(tanggal)
        hijriah = hisab_nu(tanggal.year, tanggal.month, tanggal.day)

        return jsonify({
            "masehi": format_tanggal_indonesia(tanggal),
            "pasaran_jawa": f"{jawa.get('hari_jawa', '-')}",
            "pasaran_caka": f"{jawa.get('hari_caka', '-')}",
            "hijriah": f"{hijriah.get('tanggal_hijriah', {}).get('full', '-')}",
            "jawa": f"{jawa.get('tanggal_jawa', '-')}",
            "wuku": f"{jawa.get('wuku', '-')}",
            "sadwara": f"{jawa.get('sadwara', '-')}"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/detail-wuku')
def detail_wuku():

    try:
        wuku_index = request.args.get('wuku_index')

        if not wuku_index:
            return jsonify({"error": "Data kosong"}), 400

        with open("data/wuku.json", "r") as list_wuku:
            desc_wuku = json.load(list_wuku)

            hasil = next((item for item in desc_wuku if item["index"] == wuku_index), None)

        return jsonify({
            "Wuku": f"{hasil.get('Wuku', '-')}",
            "ilustrasi": f"{hasil.get('Ilustrasi', '-')}",
            "interpretasi": f"{hasil.get('Interpretasi', '-')}",
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/tentang")
def tentang():
    return render_template("tentang.html")

@app.route("/kalenderjawa")
def kalenderjawa():
    # ambil parameter dari URL (?tanggal=2026-04-14)
    tanggal_str = request.args.get("tanggal")

    if tanggal_str:
        try:
            # parsing string ke date
            tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()
        except ValueError:
            # fallback jika format salah
            tanggal = datetime.now().date()
    else:
        # default hari ini
        tanggal = datetime.now().date()

    # panggil fungsi kalender kamu
    hasil = kalender_jawa(tanggal)
    masehi = format_tanggal_indonesia(datetime.strptime(hasil["masehi"], '%d-%m-%Y').strftime('%Y-%m-%d'))
    candra = candranipun(hasil["pranatamangsa"])

    with open("data/glosarium_kalender_jawa.json", "r") as raw_glosarium:
        desc = json.load(raw_glosarium)

    return render_template("kalenderjawa.html", data=hasil, masehi=masehi, candranipun=candra, raw_glosarium=desc)


@app.route("/kalenderhijriah")
def kalenderhijriah():
    # ambil parameter dari URL (?tanggal=2026-04-14)
    tanggal_str = request.args.get("tanggal")

    if tanggal_str:
        try:
            # parsing string ke date
            tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()
        except ValueError:
            # fallback jika format salah
            tanggal = datetime.now().date()
    else:
        # default hari ini
        tanggal = datetime.now().date()

    # now = datetime.now()

    #data render
    hisab_rukyah = hisab_nu(tanggal.year, tanggal.month, tanggal.day)
    hisab_wujud_hilal = hisab(tanggal.year, tanggal.month, tanggal.day)
    hijriah_kgth = get_hijriah(tanggal)

    with open(FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH, "r") as k2:
        rukyah_hijriah_raw = json.load(k2)
        # Buat list baru hasil konversi
        rukyahhijriah = []
        for key, value in rukyah_hijriah_raw.items():
            nama_bulan = hijri_label(key)
            tanggal_masehi_str = format_tanggal_indonesia(value)
            rukyahhijriah.append({
                "nama_bulan": nama_bulan,
                "tanggal_masehi": tanggal_masehi_str
            })

    return render_template("hijriah.html", data1=hisab_rukyah, data2=hisab_wujud_hilal, data3=hijriah_kgth,datahilal=rukyahhijriah)


# PIN Hardcoded
ADMIN_PIN = "123456"

# Decorator untuk mengecek apakah user sudah login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Silahkan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# --- RUTE SETUP (Jalankan ini SEKALI untuk mendaftarkan aplikasi ke HP Anda) ---
@app.route('/setup-mfa-qr')
def setup_mfa_qr():
    # Membuat URI standar Google Authenticator
    totp = pyotp.TOTP(MFA_SECRET)
    auth_url = totp.provisioning_uri(name="kangriza85@gmail.com", issuer_name="Almanak")

    # Generate QR Code ke memory
    img = qrcode.make(auth_url)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)

    return send_file(buf, mimetype='image/png')


# --- RUTE LOGIN YANG SUDAH MODIFIKASI ---
@app.route('/hilal', methods=['GET', 'POST'])
def login():
    # Jika sudah login, langsung lempar ke dashboard
    if 'logged_in' in session:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        pin_input = request.form.get('pin')  # Ini adalah 6 digit dari aplikasi Google Auth

        # Inisialisasi TOTP menggunakan MFA_SECRET yang dinamis
        totp = pyotp.TOTP(MFA_SECRET)

        # Mengganti 'pin_input == ADMIN_PIN' menjadi verifikasi dinamis TOTP
        if totp.verify(pin_input):
            session['logged_in'] = True  # Menyimpan status di session
            flash('Login Berhasil!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('PIN Salah atau Kedaluwarsa! Silahkan coba lagi.', 'danger')

    return render_template('login.html')


@app.route('/admin')
@login_required  # Route ini sekarang terproteksi
def admin():
    with open(FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH, "r") as k2:
        rukyah_hijriah_raw = json.load(k2)
        # Buat list baru hasil konversi
        rukyahhijriah = []
        for key, value in rukyah_hijriah_raw.items():
            nama_bulan = hijri_label(key)
            tanggal_masehi_str = format_tanggal_indonesia(value)
            rukyahhijriah.append({
                "nama_bulan": nama_bulan,
                "tanggal_masehi": tanggal_masehi_str
            })
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html',datahilal=rukyahhijriah)

@app.route('/simpan_rukyah', methods=['POST'])
def simpan_hijriah():
    data = request.get_json()
    hijriah = data.get('hijriah')           # contoh: "1447-03"
    tanggal_masehi = data.get('tanggalmasehi')  # contoh: "2025-08-25"

    if not hijriah or not tanggal_masehi:
        return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400

    # Jika file belum ada, buat kosong dulu
    if not os.path.exists(FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH):
        with open(FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH, 'w') as f:
            json.dump({}, f, indent=2)

    # Baca file JSON lama
    with open(FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH, 'r') as f:
        existing_data = json.load(f)

    # Tambahkan / update data baru
    existing_data[hijriah] = tanggal_masehi

    # Simpan kembali ke file JSON
    with open(FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH, 'w') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

    return jsonify({
        "status": "success",
        "message": f"Data {hijriah} berhasil disimpan.",
        "data": {hijriah: tanggal_masehi}
    })

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Menghapus session login
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
