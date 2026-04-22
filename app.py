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
        tanggal = request.args.get('tanggal')

        if not tanggal:
            return jsonify({"error": "tanggal kosong"}), 400

        y, m, d = map(int, tanggal.split('-'))

        date_obj = datetime(y, m, d)

        # ✅ kirim sesuai kebutuhan fungsi
        jawa = kalender_jawa(date_obj)
        hijriah = hisab_nu(y, m, d)

        return jsonify({
            "masehi": format_tanggal_indonesia(tanggal),
            "pasaran": f"{jawa.get('hari_jawa', '-')} / {jawa.get('hari_caka', '-')}",
            "hijriah": f"{hijriah.get('tanggal_hijriah', {}).get('full', '-')}",
            "jawa": jawa.get('tanggal_jawa', '-')
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Jika sudah login, langsung lempar ke dashboard
    if 'logged_in' in session:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        pin_input = request.form.get('pin')

        if pin_input == ADMIN_PIN:
            session['logged_in'] = True  # Menyimpan status di session
            return redirect(url_for('admin'))
        else:
            flash('PIN Salah! Silahkan coba lagi.', 'danger')

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

    return render_template('admin.html',datahilal=rukyahhijriah)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Menghapus session login
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="127.0.0.1", port=5000, debug=True)