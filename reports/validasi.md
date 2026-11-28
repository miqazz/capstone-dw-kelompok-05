# Validasi Pipeline & Hasil Rekonsiliasi (Sprint 2)

## Ringkasan Eksekusi

- **Total aturan validasi:** 10
- **Aturan lolos:** 10/10
- **Silver (`silver`):** 1541 baris
- **Gold (`panel_provinsi`):** 1448 baris
- **Gold (`nasional_periode_seri`):** 96 baris
- **Rekonsiliasi (`rekonsiliasi_nasional`):** 76 baris

## Hasil Lengkap Tiap Aturan Validasi

| No | Tahap | Aturan Validasi | Status | Detail Hasil |
|---:|---|---|---|---|
| 1 | Silver | Skema minimal Silver | **LOLOS** | 1541 baris lolos skema |
| 2 | Silver | Rentang nilai persen (0-100) | **LOLOS** | 545 baris dicek, 0 pelanggaran |
| 3 | Silver | Satuan var1477 baku | **LOLOS** | 926 baris dicek, 0 pelanggaran |
| 4 | Gold | Seluruh tabel Gold tidak kosong | **LOLOS** | panel=1448, nasional=96, rekon=76 |
| 5 | Gold | Kunci panel_provinsi unik (seri_kode, wilayah_kode, periode, rincian) | **LOLOS** | 1448 baris dicek, 0 duplikat |
| 6 | Gold | Satuan tunggal per indikator (seri_kode) | **LOLOS** | 7 indikator dicek, 0 bersatuan ganda |
| 7 | Gold | Setiap kunci Gold memiliki pasangan di Silver | **LOLOS** | 386 kunci dicek, 0 tanpa pasangan |
| 8 | Rekonsiliasi | Kategori selisih sesuai taksonomi baku (V4) | **LOLOS** | 76 baris valid |
| 9 | Rekonsiliasi | Kelengkapan penjelasan & bukti_dicari untuk 'belum terjelaskan' | **LOLOS** | 65 baris lengkap |
| 10 | Penyimpanan | Konsistensi jumlah baris SQL vs Parquet | **LOLOS** | 4/4 tabel sama |

## Hasil Rekonsiliasi Nasional

### Distribusi Kategori Selisih (V4)

| Kategori Selisih | Jumlah Baris | Proporsi |
|---|---:|---:|
| belum terjelaskan | 65 | 85.5% |
| definisi berbeda | 9 | 11.8% |
| cakupan berbeda | 2 | 2.6% |

## Konsistensi SQL vs Parquet

| Tabel | SQL | Parquet | Status |
|---|---:|---:|---|
| silver | 1541 | 1541 | sama |
| gold_panel_provinsi | 1448 | 1448 | sama |
| gold_nasional_periode_seri | 96 | 96 | sama |
| rekonsiliasi_nasional | 76 | 76 | sama |
