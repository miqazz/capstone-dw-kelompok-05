# Validasi

- Silver lolos skema minimal: 1541 baris
- Gold panel_provinsi: 1448 baris
- Gold nasional_periode_seri: 96 baris
- Rekonsiliasi_nasional: 76 baris
- Semua baris rekonsiliasi memiliki kategori.
- Baris 'belum terjelaskan' memiliki penjelasan dan bukti_dicari: 65 baris
- Validasi jumlah baris: SESUAI (4/4 tabel sesuai).
- Detail CSV: `reports/validasi_jumlah_baris.csv`

## SQL vs Parquet

| nama_tabel | jumlah_baris_parquet | jumlah_baris_sql | selisih | status |
|---|---:|---:|---:|---|
| silver | 1541 | 1541 | 0 | sesuai |
| gold_panel_provinsi | 1448 | 1448 | 0 | sesuai |
| gold_nasional_periode_seri | 96 | 96 | 0 | sesuai |
| rekonsiliasi_nasional | 76 | 76 | 0 | sesuai |
