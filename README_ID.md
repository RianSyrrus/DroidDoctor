# DroidDoctor Desktop Suite (v1.0.0 Pro)

> Suite Diagnostik Perangkat Keras Android, Pencerminan Layar Berlatensi Rendah, Debloater Aman, dan Pemeliharaan Sistem untuk Windows.

[Read Documentation in English (README.md)](README.md)

---

## Ringkasan

DroidDoctor adalah perangkat lunak manajemen desktop sumber terbuka tingkat produksi yang dirancang khusus untuk teknisi servis ponsel, pengguna mahir, dan pengembang Android. Dibangun di atas pustaka CustomTkinter, Python 3.10+, dan Android Debug Bridge (ADB), aplikasi ini menyediakan telemetri perangkat keras secara langsung, pencerminan layar berlatensi rendah melalui Scrcpy 4.0, penghapus bloatware aman tanpa risiko *brick*, pembersih penyimpanan pintar, dan sertifikat inspeksi kendali mutu (QC).

---

## Fitur dan Kemampuan Utama

### 1. Telemetri Perangkat Keras & Dashboard Real-Time
* Metrik baterai komprehensif: Tingkat Kesehatan (SoH), Kapasitas Pabrik (mAh), Kapasitas Riil yang Dapat Dicapai, Tegangan, Suhu Operasional, dan Daya Pengisian (Watt).
* Pemantauan penggunaan memori RAM dan Swap ZRAM secara langsung.
* Inspeksi partisi penyimpanan (teknologi UFS / eMMC dan status enkripsi FBE).
* Diagnostik panel layar: Kecepatan refresh (Hz), Resolusi Layar, Kerapatan Piksel (DPI), dan Level DRM Widevine (L1/L3).
* Spesifikasi sensor kamera dan prosesor (SoC, arsitektur CPU, dan konfigurasi multi-kamera).

### 2. Pencerminan Layar & Kendali Perangkat
* Ditenagai oleh mesin Scrcpy 4.0 (SDL 3.4.8 dan libavcodec 62).
* Aliran video berlatensi rendah hingga 60 FPS dengan opsi resolusi (1080p / 720p).
* Dukungan emulasi Keyboard USB HID (mengetik langsung dari keyboard laptop ke ponsel).
* Tombol navigasi perangkat keras: Home, Back, App Switcher (Recents), Power, Volume +, Volume -, dan sakelar Layar Tetap Menyala (Stay Awake).
* Fitur tangkapan layar (Screenshot) dan perekaman video layar yang tersimpan otomatis di komputer.

### 3. Debloater & Manajemen Aplikasi Aman
* Bekerja pada ruang profil pengguna tanpa akses root (`pm uninstall -k --user 0`). Aplikasi dapat dipulihkan kembali hanya dengan 1-klik tombol Restore.
* Kunci Pengaman Paket Kritis: Komponen vital sistem (seperti `com.android.systemui`, `com.android.settings`, dan launcher utama) dikunci mati agar sistem tidak mengalami *bootloop*.
* Mode Teknisi Eksklusif: Tab Debloater disembunyikan secara bawaan dan hanya dapat diaktifkan melalui menu Pengaturan Aplikasi.
* Fitur verifikasi tantangan ketik (*Type-to-Confirm*) sebelum mengeksekusi penghapusan aplikasi sistem.

### 4. Pembersih Penyimpanan Terproteksi
* Membersihkan berkas sampah, cache thumbnail, dan log error secara aman.
* Garansi Proteksi Data Pribadi: Folder media pengguna (`DCIM/Camera`, `Pictures`, `Downloads`, `Documents`, dan `WhatsApp Media`) terkunci permanen dan dikecualikan dari proses pembersihan.
* Inspektor berkas untuk memeriksa rincian file sebelum proses pembersihan dieksekusi.

### 5. Peralatan Teknisi & Laporan Kendali Mutu (QC)
* Ekspor laporan diagnostik perangkat keras teknis (.TXT) dan Sertifikat Inspeksi Kendali Mutu (QC Certificate).
* Pemasangan file APK langsung dari PC dengan toleransi downgrade otomatis (`-r -d -t`).
* Reset kalibrasi baterai melalui perintah *dumpsys batterystats*.
* Perintah muat ulang (Reboot) 1-klik: Normal Reboot, Mode Recovery, dan Mode Bootloader / Fastboot.

---

## Persyaratan Sistem

* Sistem Operasi: Windows 10 (1703+) atau Windows 11 (64-bit x64 atau ARM64 Prism).
* Perangkat Android: Android 5.0 (Lollipop) hingga Android 14+ dengan USB Debugging aktif.
* Konektivitas: Kabel data USB standar atau Wireless ADB melalui jaringan Wi-Fi lokal.

---

## Panduan Penggunaan Aman & Penafian Tanggung Jawab

### Arsitektur Keselamatan
1. **Operasi Tanpa Root (Non-Root):** DroidDoctor beroperasi sepenuhnya melalui protokol resmi Android Debug Bridge. Aplikasi ini tidak memodifikasi partisi bootloader atau melakukan *flashing* tanpa izin.
2. **Isolasi User 0:** Penghapusan aplikasi debloater tidak menghapus file master dari partisi sistem `/system`. Reset pabrik atau tombol pulihkan akan mengembalikan seluruh aplikasi bawaan.
3. **Perlindungan Data:** Seluruh folder berkas pribadi dijamin aman dari penghapusan otomatis.

### Penafian Hukum (Disclaimer)
Perangkat lunak ini disediakan "sebagaimana adanya" (as-is), tanpa jaminan apa pun, baik tersurat maupun tersirat. Pengembang tidak bertanggung jawab atas segala kerusakan atau dampak yang timbul akibat kesalahan penggunaan oleh pengguna. Modifikasi paket sistem dan pengoperasian fungsi ADB harus dilakukan dengan kehati-hatian teknis yang memadai.

---

## Atribusi Komponen Pihak Ketiga

DroidDoctor mengintegrasikan dan menyampaikan apresiasi kepada proyek sumber terbuka berikut:

* **Scrcpy:** Dikembangkan oleh [Genymobile](https://github.com/Genymobile/scrcpy). Digunakan untuk pencerminan layar berkecepatan tinggi dan injeksi input HID.
* **Android SDK Platform-Tools:** Dikembangkan oleh [Google LLC](https://developer.android.com/tools/releases/platform-tools). Digunakan untuk komunikasi perangkat melalui Android Debug Bridge (ADB).
* **CustomTkinter:** Dikembangkan oleh [Tom Schimansky](https://github.com/TomSchimansky/CustomTkinter). Digunakan untuk komponen antarmuka grafis desktop modern.

---

## Pengembang & Lisensi

* **Pengembang:** RianSyrrus
* **Lisensi:** Sumber Terbuka di bawah [MIT License](LICENSE).
