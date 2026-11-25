# Validasi

- Silver lolos skema minimal: 1541 baris
- Gold panel_provinsi: 1448 baris
- Gold nasional_periode_seri: 96 baris
- Rekonsiliasi_nasional: 76 baris
- Semua baris rekonsiliasi memiliki kategori.
- Baris 'belum terjelaskan' memiliki penjelasan dan bukti_dicari: 65 baris

## SQL vs Parquet

| Tabel | SQL | Parquet | Status |
|---|---:|---:|---|
| silver | 1541 | 1541 | sama |
| gold_panel_provinsi | 1448 | 1448 | sama |
| gold_nasional_periode_seri | 96 | 96 | sama |
| rekonsiliasi_nasional | 76 | 76 | sama |
