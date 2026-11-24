# Sprint 2 — 124450019

Folder ini berisi salinan artefak Sprint 2 untuk NIM 124450019 (Kasus 05: Akses layanan dan tenaga kesehatan). File asli yang dipakai pipeline tetap ada di lokasi repo masing-masing.

## Isi
- `catatan-sprint.md` — catatan Sprint 1 & 2
- `silver.sql`, `gold.sql` — DDL Silver/Gold
- `rekonsiliasi_nasional.csv`, `nasional_periode_seri.csv`, `panel_provinsi.csv` — keluaran Gold
- `rekonsiliasi-tahap6.md` — daftar pasangan & catatan keterbandingan
- `metrics.json` — metrik hasil (`src.common.hasil`), memuat metrik Sprint 1 & 2
- `data-dictionary.md` — kamus data
- `validasi.md` — ringkasan validasi (termasuk cek SQL vs Parquet dan kelengkapan `belum terjelaskan`)

## Lokasi asli
- Pipeline: `pipeline.py`, `src/ekstraksi`, `src/silver`, `src/gold`, `src/validasi`
- SQL: `sql/`
- Data: `data/silver/`, `data/gold/`
- Laporan tim: `reports/tim.md`
