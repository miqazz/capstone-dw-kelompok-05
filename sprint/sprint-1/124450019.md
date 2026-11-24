# Catatan Sprint 1 — Allisha

**NIM:** 124450019  
**Peran:** Penjaga Data & Evaluasi — Ekstraksi dan lineage  
**Kasus:** 05 — Akses layanan dan tenaga kesehatan

## Pekerjaan (Sprint 1)

- **Persiapan tahap 5 (Silver & SQL):** merancang skema tabel Silver (SQLite) dengan PK dan tipe/constraint jelas (`sprint/sprint-1/capstone/silver_ddl.sql`), membuat skrip pemuat/ekstraksi-minimal Silver pertama (`sprint/sprint-1/capstone/muat_silver_pertama.py`) yang memverifikasi `data/raw/MANIFEST.csv` dan lineage `_berkas_raw`/`_sha256_raw`. Muat berhasil ke `data/silver/silver.csv` dan `data/silver/silver.sqlite` (1.541 baris, 7 seri, duplikat kunci 0). Ringkasan profil/celah: `sprint/sprint-1/capstone/profil_ringkasan.txt`.
- **Alasan pilihan basis data:** draf tertulis di `sprint/sprint-1/capstone/alasan_basis_data.md` (SQLite) beserta perbandingan singkat dengan penyimpanan respons JSON mentah sebagai dokumen.
- **Ringkasan temuan (Masalah data dan penanganannya):** dirangkum dari `log-keputusan.csv` dan hasil profil (celah panel, rincian nasional var1477 tidak lengkap, satuan/koreksi katalog var1477, celah/potensi patahan deret WHO, disagregasi & keterbandingan definisi, duplikat/format, rentang nilai) — draf di `sprint/sprint-1/capstone/draf-masalah-data-tim.md` dan disalin ke `reports/tim.md` (angka dapat ditarik ulang).
- **Persiapan tahap 6:** tabel nasional periode × seri `data/gold/nasional_periode_seri.csv`; daftar pasangan & catatan keterbandingan `reports/rekonsiliasi-tahap6.md` (satuan var1477 ditetapkan kepadatan/100.000; definisi profesi WHO diperiksa sebelum penjumlahan rincian; pasangan var1402/var2279–UHC/FINPROTECTION dilaporkan kontekstual, definisi berbeda); keputusan K-002 s.d. K-004 di `log-keputusan.csv`; metrik `results/124450019/metrics.json` (`pasangan_rekonsiliasi=4`, `periode_beririsan=11`).

## Keterlacakan

- Profil/muat Silver: `python3 sprint/sprint-1/capstone/muat_silver_pertama.py`
- Metrik tahap 6: `python3 -m src.common.hasil 124450019 pasangan_rekonsiliasi=4 periode_beririsan=11`

## Hambatan

- Eksekusi `python -m ...` dan commit/push GitHub terkendala di lingkungan WSL ini (ketersediaan dependensi/pip dan kredensial git); pemuatan Silver dilakukan dengan `sqlite3` standar Python, metrik dihasilkan, dan berkas disiapkan untuk di-commit.

## Pekerjaan (Sprint 2)

- **Tugas 1 (Silver & Gold di SQL):** Menambah DDL `sql/silver.sql` dan `sql/gold.sql` (PK, tipe, CHECK jelas). Memperbaiki `pipeline.py` (bug variabel `hasil`) dan mengimplementasikan `src/ekstraksi`, `src/silver`, `src/gold`, `src/validasi` agar `python pipeline.py` membentuk Silver/Gold dari `data/raw/`.
  - `data/silver/silver.sqlite` = 1541 baris; `data/gold/gold.sqlite` berisi `gold_panel_provinsi` (1448), `gold_nasional_periode_seri` (96), `rekonsiliasi_nasional` (76).
  - Jumlah baris SQL sama dengan Parquet/CSV. `python -m src.common.skema data/silver/silver.parquet` LOLOS.
  - Alasan basis data: SQLite dipilih untuk portabilitas, integritas PK/CHECK, reproducibility tanpa server; JSON mentah tetap sebagai bronze/raw. Ditulis di `reports/tim.md` bagian Data dan lineage/Validasi dan alasan di `sprint/sprint-1/capstone/alasan_basis_data.md`.

- **Tugas 2 (Rekonsiliasi):** Membuat `data/gold/rekonsiliasi_nasional.(csv|parquet|sqlite)` dari pipeline. 4 pasangan kasus 05: P1 var1477 Dokter Umum per10k vs HWF_0001 (cakupan berbeda, 1 beririsan 2018, selisih -2.11); P2 Perawat+Bidan per10k vs HWF_0006 (cakupan berbeda, 1 beririsan 2018, selisih +7.91); P3 var1402 vs UHC_INDEX_REPORTED (definisi berbeda, 9 beririsan 2015-2023, selisih tidak dihitung karena konstruk berbeda); P4 var2279 vs FINPROTECTION_CATA_TOT_10_POP (definisi berbeda, 0 beririsan, WHO TOTAL). Semua baris berkategori; `belum terjelaskan` diberi dugaan/bukti dicari. Periode tanpa pasangan tetap tampil.

- **Tugas 3 (Laporan):** Draf bagian Integrasi dan rekonsiliasi ditulis di `reports/tim.md`; angka ditarik ulang dari `data/gold/rekonsiliasi_nasional.csv` dan `log-keputusan.csv`.

## Metrik Sprint 2

`results/124450019/metrics.json` diperbarui via `src.common.hasil`: baris_masuk=1722, baris_silver=1541, baris_gold_panel=1448, baris_gold_nasional=96, pasangan_rekonsiliasi=4, periode_beririsan=11, selisih_median=2.9.
