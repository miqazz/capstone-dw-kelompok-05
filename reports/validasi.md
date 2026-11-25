# Validasi Pipeline (Sprint 2)

- **Total aturan validasi:** 8
- **Aturan lolos:** 8
- Silver lolos skema minimal: 1541 baris
- Gold panel_provinsi: 1710 baris
- Gold nasional_periode_seri: 96 baris
- Rekonsiliasi_nasional: 76 baris
- Baris 'belum terjelaskan' lengkap (penjelasan & bukti_dicari): 65 baris

## Ringkasan Aturan Validasi

| Aturan | Status | Detail |
| :--- | :--- | :--- |
| Silver: Skema minimal | **LOLOS** | Lolos |
| Silver: Rentang persen (0-100) | **LOLOS** | 0 pelanggaran |
| Silver: Satuan var1477 baku | **LOLOS** | 0 pelanggaran |
| Gold: Kunci panel_provinsi unik | **LOLOS** | 0 baris duplikat |
| Gold: Satuan satu per indikator | **LOLOS** | 0 indikator bersatuan ganda |
| Gold: Sel Gold punya pasangan di Silver | **LOLOS** | 0 kunci tidak ada di Silver |
| Rekonsiliasi: Kategori baku (V4) | **LOLOS** | Semua kategori valid |
| Penyimpanan: Baris SQL sama dengan Parquet | **LOLOS** | Semua tabel sama |

## SQL vs Parquet

| Tabel | SQL | Parquet | Status |
|---|---:|---:|---|
| silver | 1541 | 1541 | sama |
| gold_panel_provinsi | 1710 | 1710 | sama |
| gold_nasional_periode_seri | 96 | 96 | sama |
| rekonsiliasi_nasional | 76 | 76 | sama |
