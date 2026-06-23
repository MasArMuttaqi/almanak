# generate_version.py
import subprocess
import json
import os
from datetime import datetime

def get_git_data():
    # Ambil data dari env variable (jika dijalankan via GitHub Actions) atau via Git CLI lokal
    commit_count = os.environ.get("GITHUB_RUN_NUMBER") # GitHub Actions otomatis menyediakan ini sebagai nomor build/deployment
    commit_hash = os.environ.get("GITHUB_SHA")
    
    # Jika tidak ada env dari GitHub (berarti dijalankan lokal), gunakan Git CLI
    if not commit_count:
        try:
            commit_count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
            commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except Exception:
            commit_count = "0"
            commit_hash = "local-dev"
            
    if commit_hash and len(commit_hash) > 7:
        commit_hash = commit_hash[:7]

    return commit_count, commit_hash

def write_version_file():
    commit_count, commit_hash = get_git_data()
    
    commit_count_1 = int(commit_count) + 4 
    # Format versi dasar aplikasi Anda
    major_minor = "2.8"
    
    version_data = {
        "version": f"v{major_minor}.{commit_count_1}",
        "build_number": commit_count_1,        # Mewakili urutan jumlah commit / run deployment
        "commit_hash": commit_hash,          # Hash untuk melacak kode spesifik di GitHub
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Simpan di root directory
    file_path = os.path.join(os.path.dirname(__file__), "version.json")
    with open(file_path, "w") as f:
        json.dump(version_data, f, indent=4)

if __name__ == "__main__":
    write_version_file()