# Laporan tim — Kelompok 05, kasus 05 Akses layanan dan tenaga kesehatan

Satu dokumen bersama, enam bagian. Angka pada bagian yang diperbarui dapat ditarik ulang dari `data/silver`, `data/gold`, `data/raw/MANIFEST.csv`, dan `log-keputusan.csv`.

## Ringkasan

Kasus ini mengolah indikator BPS dan WHO GHO untuk akses layanan serta tenaga kesehatan: `var1402` (unmet need), `var2279` (kepemilikan JKN), `var1477` (kepadatan tenaga kesehatan), `UHC_INDEX_REPORTED`, `FINPROTECTION_CATA_TOT_10_POP`, `HWF_0001`, dan `HWF_0006`. Temuan utama: Silver berisi 1.541 observasi tanpa duplikat kunci; Gold menghasilkan 1.448 baris panel provinsi, 96 baris nasional, dan 76 baris rekonsiliasi dengan 4 pasangan. Hanya pasangan tenaga kesehatan (P1/P2) yang memiliki satuan sebanding setelah konversi, sehingga hanya dua selisih numerik yang dihitung; mediannya 2,9. Pasangan var1402–UHC dan var2279–FINPROTECTION tetap dicatat sebagai kontekstual dengan definisi berbeda, bukan disetarakan.

## Data dan lineage

Sumber raw: 13 berkas pada snapshot `2026-10-20` menurut `data/raw/MANIFEST.csv` — 7 berkas BPS (3 CSV observasi, 3 JSON metadata, 1 `manifest_asal.json`) dan 6 berkas WHO GHO (4 CSV observasi, `ddiindicators_skip0000.json`, `Indicator.json`). Format mentah: CSV dan JSON. Tidak ada tarik ulang API pada Sprint 2; seluruh angka berasal dari snapshot yang terdaftar di manifest. `data_hash` di `results/<nim>/metrics.json` adalah sha256 dari pasangan `berkas:sha256` pada manifest tersebut, sehingga perubahan satu berkas mentah mengubah sidik hasil.

Jumlah observasi yang dibaca pipeline dari 7 CSV adalah 1.722 baris (`baris_masuk`): `var1402` 393, `var2279` 152, `var1477` 926, `HWF_0001` 13, `HWF_0006` 13, UHC 24, FINPROTECTION 201. JSON BPS memuat 1.471 entri `datacontent` yang selaras dengan baris BPS di Silver; `ddiindicators_skip0000.json` memuat 62 indikator; `Indicator.json` memuat 3.099 rekaman. Angka-angka ini dibaca dari snapshot lokal dan dapat dihitung ulang dengan `src.ekstraksi.jalankan()` serta parser JSON bawaan, tetapi `data/raw/` tetap dikecualikan dari Git.

Kolom `_berkas_raw` dan `_sha256_raw` diambil dari `src.common.manifest.sha256_raw`, bukan ditulis tangan. Silver menyimpan 7 berkas sumber unik; pemeriksaan `python -m src.common.skema data/silver/silver.parquet` lolos untuk 1.541 baris, 7 seri, 39 wilayah, dan 7 berkas sumber. Silver dipisahkan menjadi tabel `silver` di `data/silver/silver.sqlite`; Gold menjadi `gold_panel_provinsi`, `gold_nasional_periode_seri`, dan `rekonsiliasi_nasional` di `data/gold/gold.sqlite`. Samanya jumlah baris Parquet dan SQL dibuktikan oleh `reports/validasi_jumlah_baris.csv` (4/4 tabel `sesuai`) dan ringkasan di `reports/validasi.md`.

**Pilihan basis data:** SQLite dipilih untuk Silver dan Gold karena portabel (file tunggal), tanpa server, mendukung PK/CHECK/indeks untuk integritas skema, dan dapat direproduksi oleh `python pipeline.py` dengan `sqlite3` + pandas standar. JSON mentah tetap disimpan sebagai bronze/provenance karena mempertahankan struktur asli sumber; tabel relasional dipakai untuk Silver/Gold karena mudah divalidasi, dijoin, dan diquery. Perbandingan detail: `sprint/sprint-1/capstone/alasan_basis_data.md`.

## Masalah data dan penanganannya (draf Sprint 1, 124450019)

Seluruh angka pada bagian ini dihitung dari `data/silver/silver.csv` dengan skrip `sprint/sprint-1/capstone/audit_profil.py`. Jalankan dari root repository menggunakan `python sprint/sprint-1/capstone/audit_profil.py`; hasil rinci ditulis ke `sprint/sprint-1/capstone/audit_profil.txt`. Silver yang diaudit berisi 1.541 baris, 7 seri, 39 kode wilayah unik, dan 0 duplikat pada kunci Silver.

Perlu dibedakan bahwa `profil_ringkasan.txt` adalah hasil profiling saat pemuatan Silver pertama, sedangkan `audit_profil.txt` adalah audit ulang terhadap berkas Silver yang sama. Perbedaan jumlah baris per seri disebabkan oleh cakupan penghitungan: ringkasan awal mencakup data nasional dan provinsi, sedangkan celah panel BPS pada audit hanya mencakup data provinsi dengan mengecualikan `9999` (INDONESIA). Ini bukan perbedaan sumber data.

| No | Masalah | Bukti/angka dan cara penarikan ulang | Penanganan/keputusan | Status/ID log |
|---:|---|---|---|---|
| 1 | Agregat nasional tercampur dengan unit provinsi | `wilayah_kode = 9999` untuk INDONESIA; 39 kode wilayah unik di Silver. | Pisahkan `9999` sebagai agregat nasional; 38 provinsi menjadi unit analisis. | K-001 |
| 2 | Celah panel provinsi×periode — var1402 | 38 provinsi × 11 tahun (2015–2025) × 1 rincian = 418 sel; observasi provinsi 382; celah **36**, yaitu 9200/9500/9600/9700 pada 2015–2023. | Tidak diimputasi; kekosongan dicatat sebagai celah panel. | K-019 |
| 3 | Celah panel — var2279 | 38 × 4 tahun (2022–2025) = 152 sel; observasi 148; celah **4**, yaitu 9200/9500/9600/9700 pada 2022. | Pertahankan observasi sumber; ketiadaan dicatat, bukan missing sebelum 2022. | K-013, K-021 |
| 4 | Celah panel dan rincian tidak penuh — var1477 | 34 provinsi × 3 tahun (2016–2018) × 10 rincian = 1.020 sel; observasi 918; celah **102**. Audit mencatat 68 kombinasi wilayah-tahun tidak lengkap: 34 dengan 9 rincian pada 2017 dan 34 dengan 8 rincian pada 2018. | Rincian tidak teramati tidak diisi nol atau diimputasi. | K-014, K-020 |
| 5 | Rincian nasional var1477 tidak lengkap | 8 baris nasional, seluruhnya 2018. Dari 10 rincian provinsi, yang tidak tersedia secara nasional adalah “Ahli Teknologi Laboratorium Medik” dan “Pekarya”. | Rekonsiliasi dibatasi pada rincian/periode yang tersedia. | K-009, K-010 |
| 6 | Satuan var1477 tidak eksplisit pada CSV mentah | Kolom `satuan` kosong; metadata BPS menyatakan kepadatan per 100.000 penduduk. Silver menyimpan `kepadatan per 100.000 penduduk`. | Konversi `/10` hanya untuk pasangan yang definisinya sebanding dengan WHO (per 10.000). | K-004, K-009 |
| 7 | Celah dan perubahan pada seri pembanding WHO | FINPROTECTION 20 observasi (1999–2021), hilang 2000/2003/2008; HWF_0001 13 observasi (1993–2023), 18 tahun hilang; HWF_0006 13 observasi (1992–2023), 19 tahun hilang; UHC 24 observasi (2000–2023), tanpa tahun hilang dalam rentang. HWF_0006 berubah 30,89 (2018) → 37,81 (2019), +6,92 (22,40%). | Observasi dipertahankan. Perubahan ditandai untuk verifikasi metadata, bukan otomatis galat/patahan definisi. | K-005, K-007, K-008 |
| 8 | Disagregasi pembanding dan keterbandingan definisi | FINPROTECTION memiliki 201 baris mentah; setelah `DIM_DEG_URB = TOTAL` menjadi 20 observasi nasional. var1402–UHC dan var2279–FINPROTECTION berkaitan dengan SDG 3.8 tetapi konstruknya berbeda. | Filter TOTAL dipertahankan. Pasangan kontekstual tidak disetarakan; `selisih` numerik dikosongkan. | K-002, K-003, K-011 |
| 9 | Duplikat dan format periode | 0 duplikat dari 1.541 baris pada kunci (`sumber`, `seri_kode`, `wilayah_kode`, `periode`, `rincian`, `_berkas_raw`); seluruh seri memakai `jenis_periode = tahun`. | Pemeriksaan kunci dan representasi tahun dipertahankan. | K-001 |
| 10 | Rentang nilai perlu ditinjau | var1477 0–377 per 100.000; var1402 1,39–10,21%; var2279 53,49–98,18%. | Nilai dipertahankan; outlier diverifikasi ke sumber pada K-016/K-018. | K-016, K-018 |

**Batas keterlacakan:** `data/raw/` dikecualikan Git. Angka yang memakai CSV mentah (mis. 201 baris FINPROTECTION) diverifikasi dari snapshot lokal `2026-10-20` dan dapat dihitung ulang saat snapshot tersedia, tetapi tidak dapat ditarik dari berkas yang di-commit. Metrik Sprint 1 `aturan_validasi = 3`, `aturan_lolos = 3`, dan `baris_mentah = 6028` dipertahankan apa adanya karena repository tidak menyimpan definisi perhitungannya; statusnya **belum terverifikasi** untuk dihitung ulang, bukan diubah atau dihapus.

**Keterlacakan:** `python sprint/sprint-1/capstone/audit_profil.py` menghasilkan `audit_profil.txt` dari `data/silver/silver.csv` tanpa bergantung pada `data/raw/`.

## Integrasi dan rekonsiliasi

Sumber: `data/gold/rekonsiliasi_nasional.csv`, `.parquet`, dan tabel `rekonsiliasi_nasional` di SQLite (76 baris). Rekonsiliasi dibuat oleh `src.gold._buat_rekonsiliasi()` dari Gold nasional, CSV mentah, metadata BPS/WHO, dan `log-keputusan.csv`. Setiap baris memiliki `status_pasangan`, `kategori_konsep`, `kategori_selisih`, `penjelasan`, `bukti_dicari`, `rentang_utama`, dan `rentang_pembanding`.

### Pasangan, cakupan, dan periode

| Pasangan | Seri utama (BPS) | Pembanding (WHO) | Baris | Berpasangan | Hanya utama | Hanya pembanding | Kategori konsep |
|---|---|---|---:|---:|---:|---:|---|
| P1_dokter_hwf0001 | `var1477_dokter_umum_per10k` (Dokter Umum) | `HWF_0001` medical doctors (per 10.000) | 13 | 1 | 0 | 12 | cakupan berbeda |
| P2_perawat_bidan_hwf0006 | `var1477_perawat_bidan_per10k` (Perawat+Bidan) | `HWF_0006` nursing/midwifery (per 10.000) | 13 | 1 | 0 | 12 | cakupan berbeda |
| P3_var1402_uhc | `var1402` unmet need (%) | `UHC_INDEX_REPORTED` (indeks 0–100) | 26 | 9 | 2 | 15 | definisi berbeda |
| P4_var2279_finprot | `var2279` kepemilikan JKN (%) | `FINPROTECTION_CATA_TOT_10_POP` (% populasi, TOTAL) | 24 | 0 | 4 | 20 | definisi berbeda |

`pasangan_rekonsiliasi = 4`, `periode_beririsan = 11` (11 baris dengan nilai di kedua sisi), dan `selisih_median = 2.9` (median dari dua selisih numerik: −2,11 dan 7,91). P1 dan P2 memakai konversi var1477 dari per 100.000 ke per 10.000 (K-004, K-009). Dokter Gigi tidak digabung ke `HWF_0001`; Perawat+Bidan digabung untuk `HWF_0006` setelah verifikasi definisi WHO (K-007, K-008, K-010). P3/P4 adalah pasangan kontekstual SDG 3.8 dengan konstruk berbeda, sehingga `selisih` sengaja kosong (K-002, K-003, K-005, K-006, K-011).

### Nilai masing-masing sumber dan selisih pada periode beririsan

| Pasangan | Periode | Nilai utama | Nilai pembanding | Selisih | Kategori | Penjelasan |
|---|---:|---:|---:|---:|---|---|
| P1 | 2018 | 2,10 per 10.000 | 4,21 per 10.000 | −2,11 | cakupan berbeda | Dokter Umum BPS vs *density of doctors* WHO; satuan disetarakan, cakupan profesi/beda sumber tidak dipaksa sama. |
| P2 | 2018 | 38,80 per 10.000 | 30,89 per 10.000 | +7,91 | cakupan berbeda | Perawat+Bidan BPS vs *nursing and midwifery personnel* WHO; satuan disetarakan. |
| P3 | 2015 | 4,66% | 59 | kosong | definisi berbeda | Unmet need BPS bukan indeks cakupan layanan WHO; keduanya terkait SDG 3.8.1. |
| P3 | 2016 | 4,33% | 60 | kosong | definisi berbeda | Sama seperti 2015. |
| P3 | 2017 | 5,26% | 63 | kosong | definisi berbeda | Sama seperti 2015. |
| P3 | 2018 | 4,91% | 63 | kosong | definisi berbeda | Sama seperti 2015. |
| P3 | 2019 | 5,18% | 65 | kosong | definisi berbeda | Sama seperti 2015. |
| P3 | 2020 | 5,44% | 66 | kosong | definisi berbeda | Sama seperti 2015. |
| P3 | 2021 | 5,03% | 66 | kosong | definisi berbeda | Sama seperti 2015. |
| P3 | 2022 | 6,09% | 68 | kosong | definisi berbeda | Sama seperti 2015. |
| P3 | 2023 | 5,22% | 67 | kosong | definisi berbeda | Sama seperti 2015. |

### Periode tanpa pasangan yang tetap tercatat

| Pasangan | Sisi kosong | Periode | Dugaan dan bukti yang diperiksa | Status baris |
|---|---|---|---|---|
| P1 | Utama (BPS) | WHO 1993, 2003, 2009, 2010, 2012, 2015, 2017, 2019, 2020, 2021, 2022, 2023 | Agregat nasional var1477 hanya 2018 pada snapshot; metadata BPS mencatat 2016–2018 (`last_update = 2021-11-08 09:53:25`) dan WHO `DataUpdateLast = 2023-01-12T20:00:00Z`. Ketersediaan di rilis lain belum terverifikasi. | `belum terjelaskan` |
| P2 | Utama (BPS) | WHO 1992, 2003, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023 | Sama seperti P1; `HWF_0006` juga 13 observasi pada snapshot WHO yang sama. | `belum terjelaskan` |
| P3 | Pembanding (WHO) | BPS 2000–2014 (15 tahun) | Di luar awal seri var1402 (2015, K-019), bukan missing dalam grid BPS. | `belum terjelaskan` |
| P3 | Utama (BPS) | WHO 2024, 2025 | UHC berhenti di 2023 pada snapshot meski metadata mencatat `DataUpdateLast = 2024-01-08T20:00:00Z`; perlu cek rilis WHO terbaru. | `belum terjelaskan` |
| P4 | Utama (BPS) | WHO 1999, 2001, 2002, 2004, 2005, 2006, 2007, 2009–2021 (20 tahun) | Di luar awal seri var2279 (2022, K-013/K-021), bukan missing dalam grid BPS. | `belum terjelaskan` |
| P4 | Pembanding (WHO) | BPS 2022–2025 | FINPROTECTION berhenti di 2021 pada snapshot; metadata mencatat `DataUpdateLast = 2023-06-20T19:00:00Z`. | `belum terjelaskan` |

Tidak ada bukti di repository yang memastikan ketersediaan nilai pada rilis lain; oleh karena itu penyebab akhirnya dinyatakan **belum terverifikasi** dan tidak disimpulkan sebagai “data tidak tersedia” secara global. Kolom `bukti_dicari` menyimpan jalur berkas, tahun, dan metadata yang benar-benar diperiksa. Detail penuh ada di `reports/rekonsiliasi-tahap6.md`.

## Validasi dan reproduksibilitas

- `python pipeline.py` dieksekusi dari root repository dan menghasilkan Silver, Gold, tabel SQLite, `reports/validasi.md`, serta `reports/validasi_jumlah_baris.csv`.
- `python -m src.common.skema data/silver/silver.parquet` lolos: 1.541 baris, 7 seri, 39 wilayah, 7 berkas sumber; hash source diverifikasi terhadap MANIFEST.
- Validasi jumlah baris Parquet vs SQL: `silver` 1541/1541, `gold_panel_provinsi` 1448/1448, `gold_nasional_periode_seri` 96/96, `rekonsiliasi_nasional` 76/76 → `sesuai` 4/4. Tabel tampil di stdout pipeline pada saat validasi berjalan. Jika ada selisih, CSV/MD tetap ditulis dengan status `tidak sesuai` sebelum pipeline menggagal.
- Validasi rekonsiliasi: `kategori_selisih` dan `kategori_konsep` termasuk enum DDL; seluruh 65 baris `belum terjelaskan` memiliki `penjelasan` dan `bukti_dicari`; `selisih` hanya numerik pada P1/P2.
- `python -m src.common.hasil` menulis ulang seluruh `results/<nim>/metrics.json` dari data yang tersedia dan menggabungkannya dengan metrik lama. Metrik yang dapat dihitung ulang: `baris_masuk`, `baris_silver`, `baris_gold_panel`, `baris_gold_nasional`, `berkas_dibaca`, `format`, `seri_silver`, `rincian_dienkode`, `sel_kosong_grid`, `outlier_ditandai`, `pasangan_rekonsiliasi`, `periode_beririsan`, `selisih_median`. Tiga metrik Sprint 1 (`aturan_validasi`, `aturan_lolos`, `baris_mentah`) dipertahankan dan ditandai belum terverifikasi untuk dihitung ulang.
- Validasi skema penuh dengan pandera/Great Expectations masih menjadi pekerjaan Tahap 8; yang ada saat ini adalah pemeriksaan skema starter dan validasi tim di atas.

## Pembagian kerja

| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
| M. Rizky Pratama Putra | 124450011 | Validasi awal | Peninjau kualitas data | Masalah data dan penanganannya |
| M. Ilham Maulana | 124450019 | Ekstraksi, Silver, integrasi & rekonsiliasi | Pipeline, validasi jumlah baris, SQLite | Ringkasan, Data dan lineage, Integrasi dan rekonsiliasi |
| Nurul Huda | 124450052 | Ekstraksi multi-format | Pemeriksaan manifest | Daftar sumber dan format |
| Salsabila Putri | 124450085 | Profiling & metadata | Verifikasi definisi indikator | Kamus data dan metadata |
| Aditya Pratama | 124450092 | Grid, missing, anomali | Deduplikasi | Kualitas data dan anomali |
| M. Naufal Al Ghifari | 124450099 | Visualisasi | Uji keterbacaan laporan | Visualisasi dan tata letak |
