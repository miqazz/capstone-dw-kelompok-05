# Sprint 1 — Capstone (124450019)

Folder kerja Sprint 1 (Kasus 05: Akses layanan dan tenaga kesehatan) berisi persiapan tahap 5, ringkasan temuan Sprint 1, audit keterlacakan angka, dan keterkaitan tahap 6.

## Isi

- `silver_ddl.sql` — DDL tabel Silver (SQLite) dengan PK dan tipe/constraint jelas.
- `muat_silver_pertama.py` — skrip ekstraksi-minimal dan pemuat Silver pertama; verifikasi `MANIFEST.csv`, menulis `data/silver/silver.csv`, memuat `data/silver/silver.sqlite`, dan menghasilkan `profil_ringkasan.txt`.
  - Jalankan dari root repo: `python3 sprint/sprint-1/capstone/muat_silver_pertama.py`
- `profil_ringkasan.txt` — ringkasan profil dan celah panel hasil pemuatan Silver pertama.
- `audit_profil.py` — skrip audit mandiri yang menghitung ulang angka laporan dari `data/silver/silver.csv` tanpa membaca `data/raw/`.
- `audit_profil.txt` — hasil audit rinci, termasuk daftar wilayah-tahun/tahun WHO yang hilang dan perhitungan panel.
- `alasan_basis_data.md` — draf alasan pilihan basis data (SQLite) dan perbandingan singkat dengan penyimpanan respons JSON mentah sebagai dokumen (tahap 5).
- `draf-masalah-data-tim.md` — draf bagian *Masalah data dan penanganannya* (tahap 1–3), disinkronkan dengan `reports/tim.md` dan didukung hasil profiling serta log keputusan.

Jalankan audit dari root repo dengan:

`python sprint/sprint-1/capstone/audit_profil.py`

Hasil audit digunakan untuk memeriksa keterlacakan angka dan rujukan pada `reports/tim.md`.

## Keluaran di repo (tahap 5)

- `data/silver/silver.csv` dan `data/silver/silver.sqlite` (Silver pertama, 1.541 baris, 7 seri).
- DDL dan skrip pemuat tersedia di folder ini dan berjalan pada Silver pertama.

## Tahap 6 (persiapan, artefak repo)

- Tabel nasional periode × seri: `data/gold/nasional_periode_seri.csv`.
- Daftar pasangan dan catatan keterbandingan: `reports/rekonsiliasi-tahap6.md`.
- Metrik: `results/124450019/metrics.json` (`pasangan_rekonsiliasi=4`, `periode_beririsan=11`).