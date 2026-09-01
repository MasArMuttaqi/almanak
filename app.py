# save this as app.py
import os
import io
import json
import secrets
from functools import wraps
import pyotp
import qrcode

from flask import (Flask,render_template,request,redirect,url_for,session,flash,send_file)

import requests
from bs4 import BeautifulSoup

from kalender import *
from kalender_jawa_sultan_agungan import *
from hisab_rukyah_nu import *
from hisab_wujud_hilal import *
from hijriah_kgth import get_hijriah
from generate_version import write_version_file



app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-secret") # ganti dengan key aman

ACCOUNTS_FILE = "accounts.json"
FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH = "data/koreksirukyah.json"

@app.route("/")
def dashboard():
    # now = datetime.now()
    periode = request.args.get("periode")
    data = kalender_vertikal(periode)
    bulan = periode_bulan_indonesia(data["periode"])
    return render_template("dashboard.html",bulan=bulan,data=data["grid"],periode_hijriah=data["periode_hijriah"],periode_jawa=data["periode_jawa"], wuku=data["mingguan"],pranatamangsa=data["pranatamangsa"],candranipun=data["candranipun"],hari_penting=data["hari_penting"],prev_bulan=data["prev_bulan"],next_bulan=data["next_bulan"])

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
            # "pasaran_jawa": f"{jawa.get('hari_jawa', '-')}",
            "pasaran_caka": f"{jawa.get('hari_caka', '-')}",
            "hari_pasaran": f"{jawa.get('hari_pasaran', '-')}",
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

    #data dari khgt.muhammadiyah.or.id
    url = "https://khgt.muhammadiyah.or.id"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
        # Ambil elemen <p class="fs-18 m-0 text-center">
    tanggal = soup.find("p",class_="fs-18 m-0 text-center"
    )
    tanggal_text = tanggal.get_text(" ", strip=True)

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

    with open("data/glosarium_hijriah.json", "r") as raw_glosarium:
            desc = json.load(raw_glosarium)

    return render_template("hijriah.html", data1=hisab_rukyah, data2=hisab_wujud_hilal, data3=hijriah_kgth,datahilal=rukyahhijriah,tanggal_khgt=tanggal_text,raw_glosarium=desc)




# ============================================================
# ACCOUNT STORAGE
# ============================================================

def default_accounts():
    return {
        "administrator": [],
        "admin": []
    }

def load_accounts():

    # ========================================================
    # Jika accounts.json tersedia
    # ========================================================

    if os.path.exists(ACCOUNTS_FILE):

        try:

            with open(
                ACCOUNTS_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                accounts = json.load(f)

        except (
            json.JSONDecodeError,
            OSError
        ) as e:

            raise RuntimeError(
                f"Gagal membaca "
                f"{ACCOUNTS_FILE}: {e}"
            )

        accounts.setdefault(
            "administrator",
            []
        )

        accounts.setdefault(
            "admin",
            []
        )

        return accounts

    # ========================================================
    # Bootstrap dari Codespaces Secret
    # ========================================================

    raw = os.environ.get(
        "AUTH_ACCOUNTS"
    )

    if raw:

        try:

            accounts = json.loads(raw)

        except json.JSONDecodeError as e:

            raise RuntimeError(
                "AUTH_ACCOUNTS bukan JSON valid."
            ) from e

        if not isinstance(
            accounts,
            dict
        ):

            raise RuntimeError(
                "AUTH_ACCOUNTS harus berupa "
                "object JSON."
            )

        accounts.setdefault(
            "administrator",
            []
        )

        accounts.setdefault(
            "admin",
            []
        )

        save_accounts(
            accounts
        )

        return accounts

    # ========================================================
    # Tidak ada data
    # ========================================================

    return {
        "administrator": [],
        "admin": []
    }


def save_accounts(accounts):
    """
    Menyimpan accounts.json dengan format rapi.
    """

    temp_file = ACCOUNTS_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            accounts,
            f,
            indent=2,
            ensure_ascii=False
        )

    os.replace(
        temp_file,
        ACCOUNTS_FILE
    )


# ============================================================
# ACCOUNT HELPER
# ============================================================

def normalize_email(email):
    return email.strip().lower()


def find_account(email):
    """
    Mencari akun berdasarkan email.
    """

    email = normalize_email(email)

    accounts = load_accounts()

    for role in ("administrator", "admin"):

        for account in accounts.get(role, []):

            if normalize_email(
                account.get("email", "")
            ) == email:

                return {
                    "email": normalize_email(
                        account["email"]
                    ),
                    "role": role,
                    "totp_secret": account.get(
                        "totp_secret"
                    )
                }

    return None


def email_exists(email):
    return find_account(email) is not None


# ============================================================
# SECURITY DECORATOR
# ============================================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("logged_in"):

            flash(
                "Silahkan login terlebih dahulu.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function


def administrator_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("logged_in"):

            flash(
                "Silahkan login terlebih dahulu.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        if session.get("role") != "administrator":

            flash(
                "Anda tidak memiliki akses.",
                "danger"
            )

            return redirect(
                url_for("admin")
            )

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# CSRF
# ============================================================

def get_csrf_token():

    if "csrf_token" not in session:

        session["csrf_token"] = secrets.token_urlsafe(32)

    return session["csrf_token"]


@app.context_processor
def inject_csrf():

    return {
        "csrf_token": get_csrf_token()
    }


def check_csrf():

    token = request.form.get("csrf_token")

    if not token:

        return False

    return secrets.compare_digest(
        token,
        session.get("csrf_token", "")
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/hilal",
    methods=["GET", "POST"]
)
def login():

    # --------------------------------------------------------
    # Sudah login
    # --------------------------------------------------------

    if session.get("logged_in"):

        return redirect(
            url_for("admin")
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        step = request.form.get("step")

        # ====================================================
        # STEP 1 : EMAIL
        # ====================================================

        if step == "email":

            email = normalize_email(
                request.form.get("email", "")
            )

            if not email:

                flash(
                    "Email wajib diisi.",
                    "danger"
                )

                return redirect(
                    url_for("login")
                )

            account = find_account(email)

            # ------------------------------------------------
            # EMAIL TIDAK TERDAFTAR
            # ------------------------------------------------

            if not account:

                flash(
                    "Email tidak terdaftar.",
                    "danger"
                )

                return render_template(
                    "login.html",
                    show_totp=False,
                    email=email
                )

            # ------------------------------------------------
            # Email ditemukan
            # ------------------------------------------------

            if not account.get("totp_secret"):

                flash(
                    "Akun belum memiliki konfigurasi MFA.",
                    "danger"
                )

                return redirect(
                    url_for("login")
                )

            # ------------------------------------------------
            # Simpan email sementara
            # ------------------------------------------------

            session["mfa_email"] = email

            return render_template(
                "login.html",
                show_totp=True,
                email=email
            )

        # ====================================================
        # STEP 2 : TOTP
        # ====================================================

        if step == "totp":

            email = normalize_email(
                session.get("mfa_email", "")
            )

            if not email:

                flash(
                    "Sesi login telah berakhir.",
                    "warning"
                )

                return redirect(
                    url_for("login")
                )

            otp_code = request.form.get(
                "otp",
                ""
            ).strip()

            # ------------------------------------------------
            # Pastikan 6 digit
            # ------------------------------------------------

            if (
                len(otp_code) != 6
                or not otp_code.isdigit()
            ):

                flash(
                    "Kode TOTP harus 6 digit.",
                    "danger"
                )

                return render_template(
                    "login.html",
                    show_totp=True,
                    email=email
                )

            # ------------------------------------------------
            # Cari akun
            # ------------------------------------------------

            account = find_account(email)

            if not account:

                session.pop(
                    "mfa_email",
                    None
                )

                flash(
                    "Email tidak terdaftar.",
                    "danger"
                )

                return redirect(
                    url_for("login")
                )

            secret = account.get(
                "totp_secret"
            )

            if not secret:

                flash(
                    "Konfigurasi MFA akun tidak ditemukan.",
                    "danger"
                )

                return redirect(
                    url_for("login")
                )

            # ------------------------------------------------
            # Verifikasi TOTP
            # ------------------------------------------------

            totp = pyotp.TOTP(secret)

            # valid_window=1 memberi toleransi ±30 detik
            valid = totp.verify(
                otp_code,
                valid_window=1
            )

            if not valid:

                flash(
                    "Kode TOTP salah atau sudah kedaluwarsa.",
                    "danger"
                )

                return render_template(
                    "login.html",
                    show_totp=True,
                    email=email
                )

            # ------------------------------------------------
            # LOGIN BERHASIL
            # ------------------------------------------------

            session.clear()

            session["logged_in"] = True
            session["email"] = account["email"]
            session["role"] = account["role"]

            # Buat CSRF baru
            session["csrf_token"] = secrets.token_urlsafe(32)

            flash(
                "Login berhasil!",
                "success"
            )

            return redirect(
                url_for("admin")
            )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render_template(
        "login.html",
        show_totp=False,
        email=""
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Anda telah logout.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
@login_required
def admin():

    rukyahhijriah = []

    try:

        with open(
            FILE_JSON_KOREKSI_AWAL_BULAN_HIJRIAH,
            "r",
            encoding="utf-8"
        ) as k2:

            rukyah_hijriah_raw = json.load(k2)

            for key, value in rukyah_hijriah_raw.items():

                # =================================================
                # Gunakan fungsi Anda yang sudah ada
                # =================================================

                nama_bulan = hijri_label(key)

                tanggal_masehi_str = (
                    format_tanggal_indonesia(value)
                )

                rukyahhijriah.append({
                    "nama_bulan": nama_bulan,
                    "tanggal_masehi":
                        tanggal_masehi_str
                })

    except FileNotFoundError:

        flash(
            "File data koreksi rukyah tidak ditemukan.",
            "warning"
        )

    return render_template(
        "rukyatulhilal.html",
        datahilal=rukyahhijriah
    )

# ============================================================
# BOOTSTRAP QR ADMINISTRATOR
# ============================================================

@app.route("/setup-mfa-qr")
def setup_mfa_qr():

    # --------------------------------------------------------
    # Ambil token setup dari URL
    # --------------------------------------------------------

    token = request.args.get(
        "token",
        ""
    ).strip()

    setup_token = os.environ.get(
        "MFA_SETUP_TOKEN",
        ""
    ).strip()

    # --------------------------------------------------------
    # Token wajib tersedia
    # --------------------------------------------------------

    if not setup_token:

        return (
            "MFA_SETUP_TOKEN belum dikonfigurasi.",
            500
        )

    # --------------------------------------------------------
    # Validasi token
    # --------------------------------------------------------

    if not token:

        return (
            "Setup token diperlukan.",
            401
        )

    if not secrets.compare_digest(
        token,
        setup_token
    ):

        return (
            "Setup token tidak valid.",
            403
        )

    # --------------------------------------------------------
    # Ambil akun administrator
    # --------------------------------------------------------

    accounts = load_accounts()

    administrators = accounts.get(
        "administrator",
        []
    )

    if not administrators:

        return (
            "Akun administrator belum tersedia.",
            404
        )

    administrator = administrators[0]

    email = normalize_email(
        administrator.get(
            "email",
            ""
        )
    )

    totp_secret = administrator.get(
        "totp_secret"
    )

    # --------------------------------------------------------
    # Pastikan email
    # --------------------------------------------------------

    if not email:

        return (
            "Email administrator belum dikonfigurasi.",
            500
        )

    # --------------------------------------------------------
    # Pastikan TOTP secret
    # --------------------------------------------------------

    if not totp_secret:

        return (
            "TOTP secret administrator belum dikonfigurasi.",
            500
        )

    # --------------------------------------------------------
    # Generate provisioning URI
    # --------------------------------------------------------

    totp = pyotp.TOTP(
        totp_secret
    )

    auth_url = totp.provisioning_uri(
        name=email,
        issuer_name="Almanak"
    )

    # --------------------------------------------------------
    # Generate QR
    # --------------------------------------------------------

    img = qrcode.make(
        auth_url
    )

    buf = io.BytesIO()

    img.save(
        buf,
        format="PNG"
    )

    buf.seek(0)

    response = send_file(
        buf,
        mimetype="image/png"
    )

    # --------------------------------------------------------
    # Jangan cache QR
    # --------------------------------------------------------

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, "
        "max-age=0"
    )

    response.headers["Pragma"] = "no-cache"

    return response

# ============================================================
# TAMBAH / EDIT ADMIN
# ============================================================

@app.route(
    "/admin/users/save",
    methods=["POST"]
)
@administrator_required
def user_save():

    # --------------------------------------------------------
    # CSRF
    # --------------------------------------------------------

    if not check_csrf():

        flash(
            "CSRF token tidak valid.",
            "danger"
        )

        return redirect(
            url_for("users")
        )

    # --------------------------------------------------------
    # Ambil data form
    # --------------------------------------------------------

    mode = request.form.get(
        "mode",
        "add"
    ).strip().lower()

    email = normalize_email(
        request.form.get(
            "email",
            ""
        )
    )

    original_email = normalize_email(
        request.form.get(
            "original_email",
            ""
        )
    )

    # --------------------------------------------------------
    # Validasi email
    # --------------------------------------------------------

    if not email:

        flash(
            "Email wajib diisi.",
            "danger"
        )

        return redirect(
            url_for("users")
        )

    # --------------------------------------------------------
    # Load accounts
    # --------------------------------------------------------

    accounts = load_accounts()

    # ========================================================
    # MODE TAMBAH
    # ========================================================

    if mode == "add":

        # -----------------------------------------------
        # Cek email sudah terdaftar
        # -----------------------------------------------

        if email_exists(email):

            flash(
                "Email tersebut sudah terdaftar.",
                "warning"
            )

            return redirect(
                url_for("users")
            )

        # -----------------------------------------------
        # Generate TOTP Secret
        # -----------------------------------------------

        totp_secret = pyotp.random_base32()

        # -----------------------------------------------
        # Tambahkan admin
        # -----------------------------------------------

        accounts["admin"].append({
            "email": email,
            "totp_secret": totp_secret
        })

        save_accounts(accounts)

        flash(
            "Admin berhasil ditambahkan. "
            "Silahkan scan QR MFA.",
            "success"
        )

        # -----------------------------------------------
        # Setelah tambah, tampilkan QR
        # -----------------------------------------------

        return redirect(
            url_for(
                "user_qr",
                email=email
            )
        )

    # ========================================================
    # MODE EDIT
    # ========================================================

    if mode == "edit":

        if not original_email:

            flash(
                "Identitas akun lama tidak ditemukan.",
                "danger"
            )

            return redirect(
                url_for("users")
            )

        account = None

        # -----------------------------------------------
        # Cari akun admin berdasarkan email lama
        # -----------------------------------------------

        for item in accounts["admin"]:

            if normalize_email(
                item.get("email", "")
            ) == original_email:

                account = item
                break

        # -----------------------------------------------
        # Tidak ditemukan
        # -----------------------------------------------

        if not account:

            flash(
                "Admin tidak ditemukan.",
                "danger"
            )

            return redirect(
                url_for("users")
            )

        # -----------------------------------------------
        # Jika email berubah
        # -----------------------------------------------

        if email != original_email:

            existing = find_account(email)

            if existing:

                flash(
                    "Email baru sudah digunakan "
                    "oleh akun lain.",
                    "danger"
                )

                return redirect(
                    url_for("users")
                )

        # -----------------------------------------------
        # Ubah email
        #
        # TOTP SECRET TIDAK DIUBAH
        # -----------------------------------------------

        account["email"] = email

        save_accounts(accounts)

        flash(
            "Data admin berhasil diperbarui.",
            "success"
        )

        return redirect(
            url_for("users")
        )

    # ========================================================
    # MODE TIDAK DIKENAL
    # ========================================================

    flash(
        "Mode operasi tidak valid.",
        "danger"
    )

    return redirect(
        url_for("users")
    )

# ============================================================
# DAFTAR USER
# ============================================================

@app.route("/admin/users")
@administrator_required
def users():

    accounts = load_accounts()

    return render_template(
        "users.html",
        accounts=accounts
    )


# ============================================================
# QR MFA USER
# ============================================================

@app.route(
    "/admin/users/<path:email>/qr"
)
@administrator_required
def user_qr(email):

    email = normalize_email(email)

    account = find_account(email)

    if not account:

        flash(
            "Akun tidak ditemukan.",
            "danger"
        )

        return redirect(
            url_for("users")
        )

    secret = account.get(
        "totp_secret"
    )

    if not secret:

        flash(
            "TOTP secret tidak ditemukan.",
            "danger"
        )

        return redirect(
            url_for("users")
        )

    # --------------------------------------------------------
    # Generate provisioning URI
    # --------------------------------------------------------

    totp = pyotp.TOTP(secret)

    auth_url = totp.provisioning_uri(
        name=email,
        issuer_name="Almanak"
    )

    # --------------------------------------------------------
    # Generate QR
    # --------------------------------------------------------

    img = qrcode.make(auth_url)

    buf = io.BytesIO()

    img.save(
        buf,
        format="PNG"
    )

    buf.seek(0)

    return send_file(
        buf,
        mimetype="image/png"
    )


# ============================================================
# RESET MFA
# ============================================================

@app.route(
    "/admin/users/reset-mfa/<path:email>",
    methods=["POST"]
)
@administrator_required
def reset_mfa(email):

    if not check_csrf():

        flash(
            "CSRF token tidak valid.",
            "danger"
        )

        return redirect(
            url_for("users")
        )

    email = normalize_email(email)

    accounts = load_accounts()

    account = None

    for item in accounts["admin"]:

        if normalize_email(
            item.get("email", "")
        ) == email:

            account = item
            break

    if not account:

        flash(
            "Admin tidak ditemukan.",
            "danger"
        )

        return redirect(
            url_for("users")
        )

    # --------------------------------------------------------
    # Generate secret baru
    # --------------------------------------------------------

    account["totp_secret"] = (
        pyotp.random_base32()
    )

    save_accounts(accounts)

    flash(
        "MFA berhasil di-reset. QR baru harus dipindai.",
        "success"
    )

    return redirect(
        url_for(
            "user_qr",
            email=email
        )
    )


# ============================================================
# DELETE ADMIN
# ============================================================

@app.route(
    "/admin/users/delete/<path:email>",
    methods=["POST"]
)
@administrator_required
def user_delete(email):

    if not check_csrf():

        flash(
            "CSRF token tidak valid.",
            "danger"
        )

        return redirect(
            url_for("users")
        )

    email = normalize_email(email)

    accounts = load_accounts()

    before = len(
        accounts["admin"]
    )

    accounts["admin"] = [
        account
        for account in accounts["admin"]
        if normalize_email(
            account.get("email", "")
        ) != email
    ]

    after = len(
        accounts["admin"]
    )

    if before == after:

        flash(
            "Admin tidak ditemukan.",
            "warning"
        )

        return redirect(
            url_for("users")
        )

    save_accounts(accounts)

    flash(
        "Admin berhasil dihapus.",
        "success"
    )

    return redirect(
        url_for("users")
    )

def get_cached_version():
    json_path = os.path.join(os.path.dirname(__file__), "version.json")
    
    # Jika file json belum terbentuk, buat otomatis
    if not os.path.exists(json_path):
        write_version_file()
        
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception:
        return {"version": "v1.0.0", "build_number": "0", "commit_hash": "dev", "updated_at": "-"}

# Inject data versi secara global ke seluruh template di folder /templates
@app.context_processor
def inject_app_metadata():
    return dict(app_version=get_cached_version())

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5001, debug=True)
