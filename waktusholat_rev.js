let jadwal = {};
const today_date = new Date().toISOString().split("T")[0];

    //AMBIL JADWAL SHOLAT
fetch("https://raw.githubusercontent.com/MasArMuttaqi/masjid-info/refs/heads/main/src/json/JadwalSholat.json")
    .then(response => response.json())
    .then(data => {
        jadwal = data.find(item => item.TANGGAL === today_date);

        //console.log(jadwal);

        // LOGIK PENGECEKAN JADWAL
        if (!jadwal) {
            showPopup("Jadwal sholat hari ini tidak tersedia.<br>Silakan periksa koneksi internet atau perbaharui data jadwal.");
            return;
        }

        $("#time-imsak").html(jadwal.IMSAK);
        $("#time-subuh").html(jadwal.SUBUH);
        $("#time-terbit").html(jadwal.TERBIT);
        $("#time-dhuha").html(jadwal.DUHA);
        $("#time-zuhur").html(jadwal.ZUHUR);
        $("#time-asar").html(jadwal.ASAR);
        $("#time-magrib").html(jadwal.MAGRIB);
        $("#time-isya").html(jadwal.ISYA);

        // Jalankan countdown setelah jadwal tersedia
        updateCountdown();
    })
    .catch(err => console.error(err));
    // END OF AMBUL JADWAL SHOLAT

    // FUNGSI UNTUK MENAMPILKAN OVERLAY & CARD
    function showPopup(message) {
        // Masukkan pesan ke dalam card
        $("#pesanJadwal").html(message);
        
        // Hapus class 'd-none' untuk menampilkan overlay
        $("#overlayJadwal").removeClass("d-none");
    }

// === CACHE GLOBAL
    const CACHE_KEY = "MASJID_COUNTDOWN_CACHE";

function saveCountdownCache(mode, prayerName, endTime) {

    const data = {
        mode,                   // iqomah | jamaah | jumatan
        prayer: prayerName,
        endTime: endTime.getTime(),
        updated: Date.now()
    };

    localStorage.setItem(CACHE_KEY, JSON.stringify(data));
}

function loadCountdownCache() {

    const cache = localStorage.getItem(CACHE_KEY);

    if (!cache) return null;

    try {

        const data = JSON.parse(cache);

        // otomatis hapus jika sudah selesai
        if (Date.now() >= data.endTime) {
            localStorage.removeItem(CACHE_KEY);
            return null;
        }

        return data;

    } catch(e){

        console.warn(e);
        localStorage.removeItem(CACHE_KEY);
        return null;

    }

}

function clearCountdownCache(){

    localStorage.removeItem(CACHE_KEY);

}
// === CACHE GOLBAL
// === Ambil waktu sholat dengan urutan tetap ===
function getPrayerTimes() {
    const now = new Date();

    const order = [
        ["IMSAK", "Imsak"],
        ["SUBUH", "Subuh"],
        ["TERBIT", "Terbit"],
        ["DUHA", "Duha"],
        ["ZUHUR", "Zuhur"],
        ["ASAR", "Asar"],
        ["MAGRIB", "Magrib"],
        ["ISYA", "Isya"]
    ];

    if (!jadwal || Object.keys(jadwal).length === 0)
        return [];

    return order
        .map(([key, label]) => {

            const waktu = jadwal[key];

            if (!waktu) return null;

            const [h, m] = waktu.split(":");

            const d = new Date(now);
            d.setHours(Number(h), Number(m), 0, 0);

            return {
                name: label,
                time: d
            };

        })
        .filter(Boolean);
}

function getCurrentPrayerTime() {
  const now = new Date();
  const prayers = getPrayerTimes();
  for (let i = prayers.length - 1; i >= 0; i--) {
    if (now >= prayers[i].time) return prayers[i];
  }
  return null;
}

function getNextPrayerTime() {
  const now = new Date();
  const prayers = getPrayerTimes();
  return prayers.find(p => now < p.time) || null;
}

// === Data jeda iqomah & jamaah ===
function jedaIqomah(target) {
  const hasil = jeda.find(item => item.jeda_iqomah === target);
  return hasil ? hasil.menit : null;
}

function jamaah(target) {
  const hasil = jeda.find(item => item.jeda_iqomah === target);
  return hasil ? hasil.jamaah : null;
}

// === Status global ===
let iqomahActive = false;
let jamaahActive = false;
let jamaahEnd = null;
let jeda = [];
let lastJedaJSON = "";

// === CALLBACK EVENT ===

let onJedaChange = (data) => {
  console.log("📢 [Event] Data jeda berubah:", data);
  updateCountdown();
};



// === ⏱️ Sinkronisasi data JEDA IQOMAH ===
function syncJeda() {

  // $.getJSON("jeda_iqomah.json", function (data) {
  //   const newJedaJSON = JSON.stringify(data);
  //   if (newJedaJSON !== lastJedaJSON) {
  //     lastJedaJSON = newJedaJSON;
  //     jeda = data;
  //     console.log("✅ Data jeda diperbarui.");
  //     // $(".verified-badge").hide().fadeIn(300);
  //     onJedaChange(jeda);
  //   }
  // }).fail(function (xhr, status, error) {
  //   console.warn("❌ Gagal sync jeda:", error);
  // });

  fetch("https://raw.githubusercontent.com/MasArMuttaqi/masjid-info/refs/heads/main/src/json/jeda_iqomah.json")
    .then(response => response.json())
    .then(data => {
      const newJedaJSON = JSON.stringify(data);
      if (newJedaJSON !== lastJedaJSON) {
            lastJedaJSON = newJedaJSON;
            jeda = data;
          console.log("✅ Data jeda diperbarui.");
          // $(".verified-badge").hide().fadeIn(300);
          onJedaChange(jeda);
      }

    })
    .catch(err => console.error(err));

}

// === Jadwalkan interval sinkronisasi ===
setInterval(syncJeda, 30000);

// === Event perubahan ikon  jeda ===
onJedaChange = function(newData) {
  console.log("🕒 Jeda terbaru diterapkan:", newData);
  // $(".verified-badge").hide().fadeIn(300);
  updateCountdown();
};

// Hilangkan badge otomatis setelah 5 detik
// setTimeout(() => {
//   $(".verified-badge").fadeOut(500, function() {
//     $(this).remove();
//   });
// }, 5000);

// === 🔊 AUDIO IQOMAH SELESAI ===
let audioEndIqomah;
let audioUnlocked = false;

function initAudio() {
  if (!audioEndIqomah) {
    audioEndIqomah = new Audio("https://raw.githubusercontent.com/MasArMuttaqi/masjid-info/refs/heads/main/src/audio/videoplayback.m4a");
    audioEndIqomah.preload = "auto";
  }
}

function unlockAudio() {
  if (audioEndIqomah && !audioUnlocked) {
    audioEndIqomah.play().then(() => {
      audioEndIqomah.pause();
      audioEndIqomah.currentTime = 0;
      audioUnlocked = true;
      console.log("🔓 Audio diizinkan autoplay.");
    }).catch(err => console.warn("Gagal unlock audio:", err));
  }
}

document.addEventListener("click", unlockAudio, { once: true });
document.addEventListener("touchstart", unlockAudio, { once: true });
window.addEventListener("load", initAudio);

// === 🔒 SIMPAN & PULIHKAN STATUS COUNTDOWN ===
const LOCK_KEY = "COUNTDOWN_STATE";

function saveCountdownState() {
  const state = {
    iqomahActive,
    jamaahActive,
    iqomahEnd: iqomahActive
      ? new Date(getCurrentPrayerTime()?.time.getTime() + (jedaIqomah(getCurrentPrayerTime()?.name) || 0) * 60000).getTime()
      : null,
    jamaahEnd: jamaahEnd ? jamaahEnd.getTime() : null,
    currentPrayerName: getCurrentPrayerTime()?.name || null,
    timestamp: Date.now(),
  };
  localStorage.setItem(LOCK_KEY, JSON.stringify(state));
}

function restoreCountdownState() {
  const saved = localStorage.getItem(LOCK_KEY);
  if (!saved) return;
  try {
    const state = JSON.parse(saved);
    const now = Date.now();

    // Hapus data lama (>2 jam)
    if (now - state.timestamp > 2 * 60 * 60 * 1000) {
      localStorage.removeItem(LOCK_KEY);
      return;
    }

    const currentPrayer = getCurrentPrayerTime();
    const prayerMatch = currentPrayer && state.currentPrayerName === currentPrayer.name;

    if (prayerMatch) {
      if (state.iqomahActive && state.iqomahEnd && now < state.iqomahEnd) {
        iqomahActive = true;
        jamaahActive = false;
        console.log("⏱️ Lanjutkan IQOMAH dari penyimpanan...");
      } else if (state.jamaahActive && state.jamaahEnd && now < state.jamaahEnd) {
        iqomahActive = false;
        jamaahActive = true;
        jamaahEnd = new Date(state.jamaahEnd);
        console.log("🕌 Lanjutkan JAMAAH dari penyimpanan...");
      }
    }
  } catch (e) {
    console.warn("⚠️ Gagal memulihkan countdown:", e);
  }
}

// === 🔒 LOCK PER STATUS SHOLAT (Iqomah & Jamaah) ===
const PRAYER_LOCK_KEY = "PRAYER_STATUS_LOCK";

function setPrayerLock(status, prayerName, durationMinutes) {
  const lockUntil = Date.now() + durationMinutes * 60000;

  const state = {
    status: status,              // iqomah | jamaah
    prayer: prayerName,          // ex: Subuh
    lockUntil: lockUntil,
    timestamp: Date.now()
  };

  localStorage.setItem(PRAYER_LOCK_KEY, JSON.stringify(state));
}

// saveCountdownCache(
//     "iqomah",
//     prayerName,
//     iqomahEnd
// );

function clearPrayerLock() {
  localStorage.removeItem(PRAYER_LOCK_KEY);
}

function restorePrayerLock() {
  const saved = localStorage.getItem(PRAYER_LOCK_KEY);
  if (!saved) return null;

  const data = JSON.parse(saved);
  const now = Date.now();

  if (now >= data.lockUntil) {
    localStorage.removeItem(PRAYER_LOCK_KEY);
    return null;
  }

  return data; // status masih aktif
}

window.addEventListener("load", ()=>{

    syncJeda();

    const cache = loadCountdownCache();

    if(cache){

        console.log("🔒 Restore Cache :", cache);

        if(cache.mode==="iqomah"){

            iqomahActive = true;
            jamaahActive = false;

        }

        if(cache.mode==="jamaah"){

            iqomahActive = false;
            jamaahActive = true;
            jamaahEnd = new Date(cache.endTime);

        }

    }

    updateCountdown();

});

// helper: ambil sisa lock dalam ms (atau 0)
function getPrayerLockRemainingMs() {
  const lock = restorePrayerLock();
  if (!lock) return 0;
  return lock.lockUntil - Date.now();
}

// === Update countdown utama ===
function updateCountdown() {
  const now = new Date();
  const cache = loadCountdownCache();
  const currentPrayer = getCurrentPrayerTime();
  const iqomahMinutes = jedaIqomah(currentPrayer?.name) || 0;
  $("#statusSholat").html("Menunggu waktu sholat");
  if(cache){

    if(cache.mode==="iqomah"){

        const diff = cache.endTime - Date.now();

        if(diff>0){

            iqomahActive=true;

            const m=Math.floor(diff/60000);
            const s=Math.floor((diff%60000)/1000);

            $("#statusSholat").html("Menuju Iqomah "+cache.prayer);
            $("#countdown").html("- "+m+" : "+s);

            return;
        }

    }

    if(cache.mode==="jamaah"){

        jamaahActive=true;
        jamaahEnd=new Date(cache.endTime);

    }

}

  // ==== Kasus khusus Jumatan (90 menit) ====
  const KHUTBAH_MULAI_SEBELUM = 10; // menit sebelum Zuhur
  const KHUTBAH_TOTAL = 90;         // total durasi menit

  // Ambil atau inisialisasi awal instance carousel Anda
  const carouselEl = document.getElementById('carouselExampleAutoplaying');
  let infoCarousel = bootstrap.Carousel.getInstance(carouselEl) || new bootstrap.Carousel(carouselEl);

  if (now.getDay() === 5) {
      const zuhur = getPrayerTimes().find(p => p.name === "Zuhur");

      if (zuhur) {
          const mulaiKhutbah = new Date(
              zuhur.time.getTime() - KHUTBAH_MULAI_SEBELUM * 60000
          );

          const selesaiKhutbah = new Date(
              mulaiKhutbah.getTime() + KHUTBAH_TOTAL * 60000
          );

          saveCountdownCache(
              "jumatan",
              "Zuhur",
              selesaiKhutbah
          );

          if (now >= mulaiKhutbah && now < selesaiKhutbah) {

              const sisa = selesaiKhutbah - now;
              const jam = Math.floor(sisa / 3600000);
              const menit = Math.floor((sisa % 3600000) / 60000);
              const detik = Math.floor((sisa % 60000) / 1000);

              $("#statusSholat").html("Khutbah Jum'at sedang berlangsung");
              $("#Nextprayer").html("Sholat Jum'at");
              $("#countdown").html(
                  `Sisa ${jam} jam ${menit} menit ${detik} detik`
              );
              $("#countdown").css("display", "none");
              $("#icon-keterangan")
                  .show()
                  .attr("src", "https://lh3.googleusercontent.com/d/1ACEs1pqksBtOHRCzKcNdrwlLjRIiihfw=w800?authuser=1");
              // $(".weather-container").addClass("bg-Zuhur");
              // $(".waktu-Zuhur").addClass('active');

              saveCountdownState();
              return;
          }
      }
  }

  if (currentPrayer) {
    // hitung akhir menuju iqomah dari schedule (bukan lock)
    const iqomahEnd = new Date(currentPrayer.time.getTime() + iqomahMinutes * 60000);

    // === Menuju iqomah ===
    if (now < iqomahEnd && !jamaahActive) {
      // Jika ada lock yang sudah disimpan untuk iqomah/jamaah, gunakan sisa lock (agar tidak reset)
      const existingLock = restorePrayerLock();
      if (existingLock && existingLock.prayer === currentPrayer.name && existingLock.status === "iqomah") {
        // gunakan sisa waktu lock untuk menampilkan countdown menuju iqomah
        const remainingMs = existingLock.lockUntil - Date.now();
        if (remainingMs > 0) {
          iqomahActive = true;
          jamaahActive = false;
          const minutes = Math.floor(remainingMs / (1000 * 60));
          const seconds = Math.floor((remainingMs % (1000 * 60)) / 1000);
          $('#Nextprayer').html(currentPrayer.name);
          $('#NextPrayerTime').html(currentPrayer.time.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }).replace('.', ':')+" WIB");
          $("#statusSholat").html("IQOMAH");
          $("#countdown").html("- " + minutes + " : " + seconds);
          $("#icon-keterangan").show().attr("src", "https://lh3.googleusercontent.com/d/1bYPNHAK5BbdxUaq-rwRY0CQOKfXimn9h=w800?authuser=1");
          // $(".weather-container").addClass("bg-"+currentPrayer.name);
          // $(".waktu-"+currentPrayer.name).addClass('active');
          saveCountdownState();
          return;
        } else {
          // lock habis, clear
          // clearPrayerLock();
          clearCountdownCache();
        }
      }

      // jika tidak ada lock, set lock baru sesuai jeda dan tampilkan
      iqomahActive = true;
      jamaahActive = false;

      // jangan set lock jika iqomahMinutes === 0
      if (iqomahMinutes > 0) {
        setPrayerLock("iqomah", currentPrayer.name, iqomahMinutes);
      }

      const diff = iqomahEnd - now;
      const minutes = Math.floor(diff / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      $('#Nextprayer').html(currentPrayer.name);
      $('#NextPrayerTime').html(currentPrayer.time.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }).replace('.', ':')+" WIB");
      $("#statusSholat").html("IQOMAH");
      $("#countdown").html("- " + minutes + " : " + seconds);
      $("#icon-keterangan").show().attr("src", "https://lh3.googleusercontent.com/d/1bYPNHAK5BbdxUaq-rwRY0CQOKfXimn9h=w800?authuser=1");
      // $(".weather-container").addClass("bg-"+currentPrayer.name);
      // $(".waktu-"+currentPrayer.name).addClass('active');
      saveCountdownState();
      return;
    }

    // === Iqomah selesai → sholat berjamaah ===
    if (iqomahActive && !jamaahActive) {
      // play audio ketika iqomah selesai (jika sudah unlock)
      if (audioUnlocked && audioEndIqomah) {
        audioEndIqomah.play().catch(err => console.warn("Autoplay diblokir:", err));
      }

      iqomahActive = false;
      jamaahActive = true;

      let durasiJamaah = jamaah(currentPrayer.name) || 0;
      // set jamaahEnd menggunakan durasiJamaah
      // jika ada existing lock jamaah untuk sholat ini, gunakan sisa lock
      const existingLock = restorePrayerLock();
      if (existingLock && existingLock.prayer === currentPrayer.name && existingLock.status === "jamaah") {
        const remainingMs = existingLock.lockUntil - Date.now();
        if (remainingMs > 0) {
          jamaahEnd = new Date(Date.now() + remainingMs);
        } else {
          // clearPrayerLock();
          clearCountdownCache();
          jamaahEnd = new Date(Date.now() + durasiJamaah * 60000);
          saveCountdownCache(
              "jamaah",
              currentPrayer.name,
              jamaahEnd
          );
          if (durasiJamaah > 0) setPrayerLock("jamaah", currentPrayer.name, durasiJamaah);
        }
      } else {
        jamaahEnd = new Date(Date.now() + durasiJamaah * 60000);
        saveCountdownCache(
            "jamaah",
            currentPrayer.name,
            jamaahEnd
        );
        if (durasiJamaah > 0) setPrayerLock("jamaah", currentPrayer.name, durasiJamaah);
      }
    }

    // === Sedang sholat berjamaah ===
    if (jamaahActive && jamaahEnd && now < jamaahEnd) {
      const diff = jamaahEnd - now;
      const m = Math.floor(diff / (1000 * 60));
      const s = Math.floor((diff % (1000 * 60)) / 1000);
      $('#Nextprayer').html(currentPrayer.name);
      $('#NextPrayerTime').html(currentPrayer.time.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }).replace('.', ':')+" WIB");
      $("#statusSholat").html("Sholat " + currentPrayer.name + " berjamaah");
      $("#countdown").html(+ m + " : " + s);
      $("#icon-keterangan").show().attr("src", "https://lh3.googleusercontent.com/d/1ImnQSsRrKFRjo4VN708lwEaZJKueRazl=w800?authuser=1");
      // $(".weather-container").addClass("bg-"+currentPrayer.name);
      // $(".waktu-"+currentPrayer.name).addClass('active');
      saveCountdownState();
      return;
    }

    // === Sholat berjamaah selesai ===
    if (jamaahActive && jamaahEnd && now >= jamaahEnd) {
      jamaahActive = false;
      jamaahEnd = null;
      // clearPrayerLock(); // clear lock saat jamaah selesai
      clearCountdownCache();
      $("#statusSholat").html("Menunggu waktu sholat");
      $("#icon-keterangan").show().attr("src", "https://lh3.googleusercontent.com/d/1pBWlBAhdX2lOSwgT6ivJazJTw_kD-ciC=w800?authuser=1");
      saveCountdownState();
      return;
    }
  }

  // === Menuju sholat berikutnya ===
  const nextPrayer = getNextPrayerTime();
  if (!nextPrayer) {
    $("#Nextprayer").html("-");
    $("#countdown").html("00:00:00");
    $("#statusSholat").html("Semua sholat selesai hari ini");
    $("#icon-keterangan").show().attr("src", "https://lh3.googleusercontent.com/d/1pBWlBAhdX2lOSwgT6ivJazJTw_kD-ciC=w800?authuser=1");
    saveCountdownState();
    return;
  }

  const diff = nextPrayer.time - now;
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);

  $("#statusSholat").html("Dalam Waktu");
  $('#Nextprayer').html(nextPrayer.name);
  $('#NextPrayerTime').html(nextPrayer.time.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }).replace('.', ':')+" WIB");
  $('#countdown').html("- " + hours + " : " + minutes + " : " + seconds);
  $("#icon-keterangan").show().attr("src", "https://lh3.googleusercontent.com/d/1pBWlBAhdX2lOSwgT6ivJazJTw_kD-ciC=w800?authuser=1");
  // $(".weather-container").addClass("bg-"+nextPrayer.name);
  // $(".waktu-"+nextPrayer.name).addClass('active');
  saveCountdownState();
}

// Jalankan terus setiap detik
setInterval(updateCountdown, 1000);

// === Restore on load: gabungkan restoreCountdownState + restorePrayerLock ===
window.addEventListener("load", () => {
  // pulihkan countdown (existing)
  restoreCountdownState();

  // sinkronisasi data
  syncJeda();

  // restore lock per sholat (jika ada) -> set flags agar updateCountdown menampilkan sesuai lock
  const lock = restorePrayerLock();
  const currentPrayer = getCurrentPrayerTime();
  if (lock && currentPrayer && lock.prayer === currentPrayer.name) {
    console.log("🔒 Restore prayer lock:", lock);
    if (lock.status === "iqomah") {
      iqomahActive = true;
      jamaahActive = false;
      // tidak set jamaahEnd di sini
    } else if (lock.status === "jamaah") {
      iqomahActive = false;
      jamaahActive = true;
      // jamaahEnd ambil dari lock.lockUntil
      jamaahEnd = new Date(lock.lockUntil);
    }
  }

  // inisialisasi audio sudah dilakukan di atas (initAudio)
  // jalankan update segera agar UI cepat terisi
  updateCountdown();

  
});


updateCountdown();
