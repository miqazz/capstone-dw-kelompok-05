# Sprint 1 — Capstone (124450019)

Folder kerja Sprint 1 (Kasus 05: Akses layanan dan tenaga kesehatan) berisi persiapan tahap 5, ringkasan temuan Sprint 1, dan keterkaitan tahap 6.

## Isi

- `silver_ddl.sql` — DDL tabel Silver (SQLite) dengan PK dan tipe/constraint jelas.
- `muat_silver_pertama.py` — skrip ekstraksi-minimal & pemuat Silver pertama; verifikasi `MANIFEST.csv`, tulis `data/silver/silver.csv`, muat `data/silver/silver.sqlite`, dan hasilkan `profil_ringkasan.txt`.
  - Jalankan dari root repo: `python3 sprint/sprint-1/capstone/muat_silver_pertama.py`
- `profil_ringkasan.txt` — ringkasan profil/celah panel hasil muat Silver pertama (dapat ditarik ulang).
- `alasan_basis_data.md` — draf alasan pilihan basis data (SQLite) dan perbandingan singkat dengan penyimpanan respons JSON mentah sebagai dokumen (tahap 5).
- `draf-masalah-data-tim.md` — draf bagian *Masalah data dan penanganannya* (tahap 1–3) dengan angka yang dapat ditarik ulang dari Silver/profil dan `log-keputusan.csv`; disalin ke `reports/tim.md`.

## Keluaran di repo (tahap 5)

- `data/silver/silver.csv`, `data/silver/silver.sqlite` (Silver pertama, 1.541 baris, 7 seri)
- DDL & skrip pemuat: berkas di folder ini (berjalan pada Silver pertama)

## Tahap 6 (persiapan, artefak repo)

- Tabel nasional periode×seri: `data/gold/nasional_periode_seri.csv`
- Daftar pasangan & catatan keterbandingan: `reports/rekonsiliasi-tahap6.md` (dirujuk di `README.md`)
- Metrik: `results/124450019/metrics.json` (`pasangan_rekonsiliasi=4`, `periode_beririsan=11`)
