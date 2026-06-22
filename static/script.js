// KONFIGURASI JAVASCRIPT/JQUERY BARU LETAKKAN DI BAWAH INI
// navbar title
$(document).ready(function() {
  let items = $('.brand-item');
  let currentIndex = 0;

  function rotateDates() {
    // 1. Sembunyikan item yang sedang tampil (FadeOut)
    $(items[currentIndex]).fadeOut(1000, function() {

      // 2. Hitung index berikutnya
      currentIndex = (currentIndex + 1) % items.length;

      // 3. Tampilkan item berikutnya (FadeIn)
      $(items[currentIndex]).fadeIn(1000);
    });
  }

  // Atur interval penggantian (misal: setiap 4 detik)
  setInterval(rotateDates, 4000);
});

// Tambahkan event scroll
window.addEventListener("scroll", function () {
  const navbar = document.getElementById("navbar-atas");
  if (window.scrollY > 50) {   // jika scroll > 50px
    navbar.classList.add("scrolled");
  } else {
    navbar.classList.remove("scrolled");
  }
});

// back to top
$(document).ready(function () {
  const $backToTop = $("#btnBackToTop");

  // Logika memunculkan/menyembunyikan tombol saat scroll
  $(window).on("scroll", function () {
    if ($(this).scrollTop() > 300) {
      $backToTop.fadeIn(400); // Muncul perlahan selama 400ms
    } else {
      $backToTop.fadeOut(400); // Menghilang perlahan
    }
  });

  // Logika klik tombol untuk kembali ke atas
  $backToTop.on("click", function (e) {
    e.preventDefault();
    $("html, body").animate(
      {
        scrollTop: 0
      },
      600 // Durasi scroll dalam milidetik (600ms)
    );
  });
});

// datepicker
$(document).ready(function() {
  // Tanggal minimum tetap
  let minDate = '2025-01-01';

  // Tahun maksimum = tahun sekarang + 3
  let currentYear = new Date().getFullYear();
  let maxYear = currentYear + 3;

  // Tanggal maksimum 31 Desember tahun maksimum
  let maxDate = maxYear + '-12-31';

  $('#myDateInput').attr({
    'min': minDate,
    'max': maxDate                                        
  });
});