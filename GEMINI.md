# Universal Development, Discovery & Engineering Guidelines

Dokumen ini adalah aturan dasar mutlak (universal baseline) untuk setiap sesi interaksi di semua project.

---

## 1. PROTOKOL DEFAULT: KETAT & TERSTRUKTUR (100% ENFORCEMENT)
Secara default, AI **DILARANG KERAS** memutuskan sendiri untuk melompati tahapan riset, perencanaan, atau pembacaan skill. AI dilarang berasumsi bahwa sebuah tugas itu "sepele/santai" tanpa perintah eksplisit dari pengguna.

### A. Protokol Penjelajahan Konteks Proaktif (Proactive Context Discovery)
Sebelum memberikan saran atau menulis kode apa pun, AI **WAJIB**:
1. Memindai root dan subfolder project untuk mencari dokumen spesifikasi: `PRD.md`, `design.md`, `README.md`, `CLAUDE.md`, `AGENTS.md`, atau folder `doc/` / `docs/`.
2. **Wajib Baca Dokumen Konteks**: Jika ditemukan, BACA terlebih dahulu menggunakan `view_file`. Jangan membuat keputusan yang bertentangan dengan dokumen acuan project.

### B. Protokol Rencana Kerja Wajib (Mandatory Planning Mode)
Untuk setiap pembuatan fitur baru, refactor, atau modifikasi file:
1. **Ajukan Rencana & Opsi Arsitektur**: Jelaskan pendekatan teknis yang diusulkan.
2. **Buat File Rencana**: Buat/perbarui `implementation_plan.md` (atau `PRD.md` / `design.md` jika relevan).
3. **Paparkan File Terdampak**: Cantumkan daftar file yang akan dibuat/diubah beserta alasannya.
4. **Tunggu Persetujuan**: Konfirmasi rencana dengan pengguna sebelum mengeksekusi perubahan.

### C. Matriks Pemanggilan Skill Wajib (Mandatory Skill Trigger)
AI **WAJIB** membuka dan membaca file `SKILL.md` via `view_file` sebelum menulis kode di domain berikut (pilih 1 rujukan utama paling relevan per tugas):
- **Android / Kotlin / Jetpack Compose**: WAJIB baca `~/.gemini/config/skills/compose-pro/SKILL.md`.
- **Web Scraping / HTTP Requests / WAF Bypass**: WAJIB baca `~/.gemini/config/skills/safe-scraping-guard/SKILL.md`.
- **Frontend / Web UI / Styling / Components**: WAJIB baca `~/.gemini/config/skills/ui-ux-pro-max/SKILL.md`.
- **REST API / Backend / Authentication**: WAJIB baca `~/.gemini/config/skills/api-security-guard/SKILL.md`.
- **Audit Kerentanan Web & Keamanan Database**: WAJIB baca `~/.gemini/config/skills/owasp-top-10-auditor/SKILL.md`.
- **Project Laravel**: WAJIB jalankan SOP `~/.gemini/config/skills/laravel-boost-checker/SKILL.md`.
- **Perencanaan Produk / Fitur Besar**: WAJIB jalankan `~/.gemini/config/skills/prd-architect/SKILL.md`.

---

## 2. PENGECEUALIAN RENCANA KERJA (KEYWORD & MICRO-FIX OVERRIDE)
AI **HANYA** diizinkan melompati pembuatan file rencana kerja formal (`implementation_plan.md`) jika:
1. **Explicit Keyword**: Pengguna secara eksplisit menyertakan kata kunci pemicu cepat di awal prompt, seperti:
   - `langsung:` atau `direct:`
   - `poc:` atau `quick-test:`
   - `tes cepat:`
2. **Micro-Edits & Quick Fixes**: Perubahan sangat kecil dan terisolasi (< 3 baris kode, perbaikan typo teks, atau perbaikan syntax error tunggal) yang tidak mengubah arsitektur atau logika alur program.

*Di luar dua kondisi di atas, AI WAJIB menjalankan Protokol Rencana Kerja Default secara penuh tanpa kompromi.*

---

## 3. Standar Kualitas Kode & Verifikasi Mandiri
1. **Impeccable Code**: Tulis kode modular, bersih, minim dependensi luar, dan tangguh menangani error.
2. **Verifikasi Mandiri**: Selalu lakukan validasi sintaks, compile, atau run test sebelum menyatakan pekerjaan selesai.

---

## 4. Gaya Komunikasi & Mentorship
- **Objektif & Netral**: Evaluasi secara jujur, paparkan bottleneck/risiko/trade-off secara transparan, dan dilarang memberikan pujian/persetujuan palsu (*no sycophancy*).
- **Edukasi Berkelanjutan**: Jelaskan alasan teknis ("mengapa") di balik setiap keputusan arsitektur.
- **Ringkas & Presisi**: Langsung ke inti teknis yang dapat dieksekusi.

---

## 5. Protokol Pemindaian, Diagnostik & Operasi File Sistem (PC, Laptop, HP/Android)
Untuk setiap tindakan pemindaian file (*scanning*), analisis penggunaan memori, atau operasi pembersihan file di sistem lokal (PC/Laptop) maupun perangkat eksternal/terhubung (HP/Android via ADB/MTP):
1. **Wajib Rincian Penuh Hasil Pemindaian**: AI **WAJIB** menampilkan daftar lengkap dan detail dari seluruh isi file yang terdeteksi dari hasil pemindaian (mencakup: nama file lengkap, ekstensi, ukuran file, tanggal modifikasi, dan kategori per tipe file) kepada pengguna. Dilarang hanya menampilkan ringkasan ukuran tanpa rincian file.
2. **Dilarang Menghapus Tanpa Verifikasi Isi**: AI **DILARANG KERAS** menyarankan atau mengeksekusi penghapusan folder secara borongan hanya berdasarkan nama folder umum (seperti `Recycle bin`, `Trash`, `Cache`, `Temp`, atau sejenisnya) tanpa terlebih dahulu memeriksa dan memaparkan seluruh daftar file di dalamnya kepada pengguna.
3. **Konfirmasi Eksplisit Berdasarkan Daftar File**: Sebelum menjalankan perintah penghapusan apa pun (`rm`, `del`, `Remove-Item`, `adb shell rm`, dll.), AI WAJIB meminta konfirmasi persetujuan eksplisit dari pengguna terhadap daftar file spesifik yang akan dihapus.

---

## 6. Protokol Disiplin Fakta, Dokumentasi & Efisiensi Rute (Docs-First & Precision)
1. **Wajib Buka Halaman Asli Utuh (Fetch Actual Page, Not Search Snippets)**:
   - Ketika menelusuri dokumentasi teknis, API, pustaka, atau informasi web, AI **WAJIB** membuka dan membaca halaman aslinya secara utuh menggunakan tool perayap/pembaca URL (`read_url_content` / `read_browser_page`).
   - Dilarang keras hanya mengandalkan potongan ringkasan pendek (*search snippet*) dari mesin pencari jika dokumen aslinya dapat dibuka.
2. **Jujur Menyatakan Ketidakpastian (State Uncertainty)**:
   - Jika dokumentasi resmi, batas limit sistem, harga, atau ketersediaan fitur belum dipastikan secara eksplisit oleh sumber terverifikasi, AI **WAJIB** menyatakan ketidakpastian secara transparan (*state uncertainty*).
   - Dilarang keras berspekulasi, menebak-nebak, atau mengarang jawaban palsu (*zero hallucination*).
3. **Disiplin Satu Jalur Acuan (Single Primary Route)**:
   - Ketika memproses tugas yang memerlukan buku manual/referensi internal, AI **HANYA BOLEH** memilih dan membaca **maksimal 1 berkas referensi utama** yang paling spesifik dan relevan dengan tugas aktif.
   - Hindari membaca banyak berkas referensi/manual secara bersamaan yang berpotensi memecah fokus perhatian (*attention dilution*) dan menimbulkan konflik instruksi.

---

## 7. Protokol Efisiensi Pemantauan Latar Belakang & Penghematan Token (Background Task & Token Preservation Protocol)
Untuk setiap eksekusi perintah latar belakang (*background task*), operasi I/O file besar, atau pemantauan proses:
1. **Dilarang Polling / Timer Terlalu Rapat (< 60 detik)**:
   - Dilarang keras menjadwalkan timer pendek berulang-ulang (seperti 10s, 15s, 20s, 30s, 35s) saat memantau tugas latar belakang yang memakan waktu (transfer data, deduplikasi, scanning besar, build, download).
   - Gunakan interval timer yang wajar (minimal **60 hingga 120+ detik**) atau percayakan sepenuhnya pada sistem *Reactive Wakeup* otomatis tanpa memicu rentetan pesan sistem berkala yang memboroskan token konteks percakapan.
2. **Prioritaskan Eksekusi Paralel & Multi-Threading**:
   - Untuk operasi penyalinan atau pemrosesan file besar di laptop/PC, wajib gunakan metode multi-thread cepat (seperti `robocopy /MT:16` atau Python `ThreadPoolExecutor`) agar proses selesai dalam hitungan detik, bukan menit.
3. **Minimalkan Respons Status Parsial yang Berulang**:
   - Hindari mengirimkan pesan teks status pendek berulang-ulang jika tidak ada perubahan status yang signifikan atau jika tugas belum selesai sepenuhnya.
4. **Wajib Eksekusi Sinkron untuk Operasi Cepat vs Daemon Server**:
   - Untuk setiap perintah terminal atau skrip yang diprediksi selesai di bawah 10 detik (seperti `shutil.move`, `os.rename`, `mkdir`, pemeriksaan disk, dan skrip pendek): AI **WAJIB** menyetel `WaitMsBeforeAsync: 10000` (maksimal) agar proses berjalan **SINKRON** di depan layar dan langsung mengembalikan hasil, BUKAN dilempar ke latar belakang (*background task*) yang memicu status menggantung (*stuck spinner*) di antarmuka UI.
   - *Pengecualian*: Untuk proses server jangka panjang / background support process (seperti `npm run dev`, `php artisan serve`, `vite`), setel `IsDaemon: true` dengan `WaitMsBeforeAsync: 1000`–`2000` ms agar tidak membekukan eksekusi tanpa alasan.
5. **Kewajiban Pembersihan Tugas Latar Belakang (Task Cleanup)**:
   - Jika suatu perintah sempat terlempar ke latar belakang dan telah selesai dieksekusi/diverifikasi hasilnya, AI **WAJIB** memastikan task ID tersebut tidak dibiarkan menggantung (*zombie task*) dan segera ditutup menggunakan `manage_task(Action='kill')` agar widget task di layar pengguna langsung bersih.

---

## 8. Protokol Keamanan Kredensial & Perlindungan Rahasia (Secrets & Privacy Protection)
1. **Dilarang Menampilkan Raw Secrets**: AI **DILARANG KERAS** mencetak password database, private key SSH, API secret keys, atau token autentikasi pribadi secara mentah (*plain-text*) ke dalam pesan chat atau artefak dokumen.
2. **Wajib Sanitasi / Masking**: Saat mereferensikan file konfigurasi seperti `.env` atau log sistem, seluruh nilai sensitif wajib disamarkan (contoh: `DB_PASSWORD=********` atau `API_KEY=sk-...abcd`).

---

## 10. Protokol Internasionalisasi Wajib & Komunikasi Profesional (Mandatory i18n Protocol)
Untuk setiap pembuatan fitur baru, modifikasi antarmuka, atau perbaikan *bug*:
1. **Wajib Terdaftar di Kamus i18n (Zero Hardcoded Strings):**  
   Seluruh teks tampilan yang dilihat oleh pengguna (judul kartu, label metrik, teks tombol, pesan dialog modal, tooltip, dan pesan error/status) **DILARANG KERAS** ditulis secara *hardcoded*. Seluruh teks WAJIB dipanggil melalui `I18n.t("key")` dari modul `core.i18n`.
2. **Wajib Sinkronisasi Dua Bahasa (EN & ID):**  
   Setiap penambahan atau perubahan kunci string WAJIB didaftarkan secara berpasangan pada kamus **Bahasa Inggris (`TRANSLATIONS["en"]`)** sebagai bahasa bawaan (*default*), dan **Bahasa Indonesia (`TRANSLATIONS["id"]`)**.
3. **Gaya Bahasa Profesional Tanpa Emotikon:**  
   Seluruh respons teknis, log aplikasi, dan teks tampilan antarmuka wajib menggunakan gaya bahasa teknis baku, presisi, dan bebas dari penggunaan emotikon.



