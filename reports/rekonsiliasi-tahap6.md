# Rekonsiliasi Nasional (Tahap 6, Sprint 2)

**NIM:** 124450019  
**Kasus:** 05 — Akses layanan dan tenaga kesehatan

## Keluaran

- Tabel nasional periode × seri: `data/gold/nasional_periode_seri.csv` (96 baris).
- Tabel rekonsiliasi final: `data/gold/rekonsiliasi_nasional.csv` / `.parquet` / tabel `rekonsiliasi_nasional` di `data/gold/gold.sqlite` (76 baris).
- Baris nasional diambil dari Silver dengan `wilayah_kode = 9999` (INDONESIA). Setiap baris memuat lineage `_berkas_raw` dan `_sha256_raw` yang berasal dari `data/raw/MANIFEST.csv`.
- Tabel nasional memuat seri utama BPS (`var1402`, `var2279`, `var1477`), seri pembanding WHO (`UHC_INDEX_REPORTED`, `FINPROTECTION_CATA_TOT_10_POP` dengan `DIM_DEG_URB=TOTAL`, `HWF_0001`, `HWF_0006`), serta seri turunan konversi/penjumlahan rincian untuk perbandingan.

## Penetapan satuan dan definisi profesi (var1477 vs WHO HWF)

**Satuan var1477 diperiksa sebelum rekonsiliasi:** kepadatan per 100.000 penduduk, bukan jumlah orang absolut. `data/raw/bps/2026-10-20/json/sdg3_3_c_1_v1477.json` mencantumkan `var.label = "Kepadatan Dan Distribusi Tenaga Kesehatan"` dan `var.note = "... (per 100.000 penduduk)"`; kolom `satuan` pada CSV mentah kosong. Konversi ke skala WHO dilakukan dengan `nilai_per10k = nilai_per100k / 10` (K-004, K-009).

**Definisi profesi WHO diperiksa sebelum penjumlahan rincian:**

- `HWF_0001` — *Density of doctors* (per 10.000 penduduk; metadata WHO ID `217795A`). Dibandingkan dengan rincian BPS **Dokter Umum** (`turvar_id` 1173) saja. **Dokter Gigi** (`turvar_id` 1174) tidak digabung (K-007, K-010).
- `HWF_0006` — *Density of nurses and midwives* / *nursing and midwifery personnel* (per 10.000 penduduk; metadata WHO ID `5C8435F`). Dibandingkan dengan **Perawat** (`turvar_id` 1175) + **Bidan** (`turvar_id` 1176). Rincian var1477 lainnya tidak dimasukkan (K-008, K-010).

Rincian nasional var1477 yang tersedia hanya 8 baris pada 2018: Dokter Umum 21, Dokter Gigi 4, Perawat 175, Bidan 213, Farmasi 20, Kesehatan Masyarakat 33, Kesehatan Lingkungan 20, Gizi 11 (semua per 100.000). Turunan yang dipakai: Dokter Umum 2,1 per 10.000 dan Perawat+Bidan 38,8 per 10.000. Data provinsi var1477 mencakup 2016–2018, tetapi baris nasional hanya 2018.

## Daftar pasangan dan hasil

| ID pasangan | Seri utama (BPS) | Pembanding (WHO) | Baris | Berpasangan | Kategori konsep | Kategori baris berpasangan | Selisih numerik |
|---|---|---|---:|---:|---|---|---|
| P1_dokter_hwf0001 | `var1477_dokter_umum_per10k` | `HWF_0001` | 13 | 1 (2018) | cakupan berbeda | cakupan berbeda | 2018: 2,10 − 4,21 = **−2,11** |
| P2_perawat_bidan_hwf0006 | `var1477_perawat_bidan_per10k` | `HWF_0006` | 13 | 1 (2018) | cakupan berbeda | cakupan berbeda | 2018: 38,80 − 30,89 = **+7,91** |
| P3_var1402_uhc | `var1402` | `UHC_INDEX_REPORTED` | 26 | 9 (2015–2023) | definisi berbeda | definisi berbeda | tidak dihitung (satuan/konstruk berbeda) |
| P4_var2279_finprot | `var2279` | `FINPROTECTION_CATA_TOT_10_POP` | 24 | 0 | definisi berbeda | tidak ada baris berpasangan | tidak dihitung |

`pasangan_rekonsiliasi = 4`, `periode_beririsan = 11` (baris dengan nilai di kedua sisi), `selisih_median = 2,9` (median dari dua selisih numerik: −2,11 dan +7,91). Seluruh 65 baris tanpa pasangan tetap tercatat dengan kategori `belum terjelaskan`, dugaan, dan bukti.

P3 dan P4 tetap diperlakukan sebagai pasangan kontekstual dengan `kategori_konsep = "definisi berbeda"`: var1402 adalah *unmet need* (%) sedangkan UHC_INDEX_REPORTED adalah indeks cakupan layanan (0–100); var2279 adalah kepemilikan JKN (%) sedangkan FINPROTECTION_CATA_TOT_10_POP adalah insiden pengeluaran kesehatan rumah tangga di atas 10% anggaran (% populasi). Keduanya berkaitan dengan SDG 3.8 tetapi tidak identik (K-002, K-003, K-005, K-006, K-011).

## Pemeriksaan periode yang belum berpasangan

| Pasangan | Sisi yang kosong | Periode yang tetap tercatat | Dugaan penyebab | Bukti yang diperiksa |
|---|---|---|---|---|
| P1 | Utama (BPS) | WHO 1993, 2003, 2009, 2010, 2012, 2015, 2017, 2019, 2020, 2021, 2022, 2023 (12 tahun) | Agregat nasional var1477 tidak tersedia pada tahun ini di snapshot. Metadata BPS mencatat tahun 2016–2018, tetapi baris nasional hanya 2018. Perlu cek rilis BPS lain; belum terverifikasi. | `data/raw/bps/2026-10-20/sdg3_3_c_1_v1477.csv` (926 baris; tahun 2016–2018), `.../json/sdg3_3_c_1_v1477.json` (`last_update=2021-11-08 09:53:25`), `data/raw/who_gho/2026-10-20/datadot/217795A_HWF_0001.csv` (13 baris; 1993–2023), `ddiindicators_skip0000.json` (`DataUpdateLast=2023-01-12T20:00:00Z`). |
| P2 | Utama (BPS) | WHO 1992, 2003, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023 (12 tahun) | Sama seperti P1: agregat nasional var1477 hanya 2018 pada snapshot. Belum terverifikasi untuk rilis lain. | `data/raw/bps/2026-10-20/sdg3_3_c_1_v1477.csv`, metadata BPS var1477, `5C8435F_HWF_0006.csv` (13 baris; 1992–2023), `ddiindicators_skip0000.json` (`DataUpdateLast=2023-01-12T20:00:00Z`). |
| P3 | Pembanding (WHO) | BPS 2000–2014 (15 tahun) | Tahun-tahun ini berada sebelum cakupan BPS var1402 yang mulai 2015 (K-019), bukan missing pada grid BPS. | `sdg3_3_8_1_a_v1402.csv` (393 baris; 2015–2025), `9A706FD_UHC_INDEX_REPORTED.csv` (24 baris; 2000–2023). |
| P3 | Utama (BPS) | WHO 2024, 2025 (2 tahun) | WHO UHC_INDEX_REPORTED berhenti di 2023 pada snapshot meskipun metadata mencatat `DataUpdateLast=2024-01-08T20:00:00Z`; BPS berlanjut sampai 2025. Perlu cek rilis WHO terbaru. | `sdg3_3_8_1_a_v1402.csv` (2015–2025), `9A706FD_UHC_INDEX_REPORTED.csv` (2000–2023), `ddiindicators_skip0000.json` ID `9A706FD`. |
| P4 | Utama (BPS) | WHO 1999, 2001, 2002, 2004, 2005, 2006, 2007, 2009–2021 (20 tahun) | BPS var2279 baru tersedia sejak 2022 (K-013, K-021); tahun ini di luar rentang seri BPS, bukan missing pada grid BPS. | `sdg3_3_8_2_a_v2279.csv` (152 baris; 2022–2025), `A65146D_FINPROTECTION_CATA_TOT_10_POP.csv` (201 baris mentah; 20 tahun setelah filter `DIM_DEG_URB=TOTAL`). |
| P4 | Pembanding (WHO) | BPS 2022, 2023, 2024, 2025 (4 tahun) | WHO FINPROTECTION berhenti di 2021 pada snapshot; metadata mencatat `TimeIntervals` hingga 2020 dan `DataUpdateLast=2023-06-20T19:00:00Z`. Perlu cek rilis WHO terbaru. | `sdg3_3_8_2_a_v2279.csv` (2022–2025), `A65146D_FINPROTECTION_CATA_TOT_10_POP.csv` (1999–2021 setelah filter TOTAL), `ddiindicators_skip0000.json` ID `A65146D`. |

Kesimpulan pemeriksaan: untuk semua periode tanpa pasangan, sudah diperiksa rentang tahun pada CSV mentah, ketersediaan baris pada Gold nasional, definisi indikator di metadata/local `log-keputusan.csv`, dan cakupan sumber (nasional WHO versus BPS nasional/provinsi). Tidak ada bukti di repository yang memastikan ketersediaan nilai pada rilis lain, sehingga penyebab akhirnya dinyatakan **belum terverifikasi** dan tidak disimpulkan sebagai "data tidak tersedia" secara global.

## Kolom tabel rekonsiliasi

`pasangan_id, seri_utama, rincian_utama, seri_pembanding, rincian_pembanding, periode, jenis_periode, nilai_utama, satuan_utama, nilai_pembanding, satuan_pembanding, selisih, status_pasangan, kategori_konsep, kategori_selisih, penjelasan, bukti_dicari, rentang_utama, rentang_pembanding`.

## Keterbatasan

- Baris nasional var1477 hanya tersedia pada 2018 (8 rincian), sehingga rekonsiliasi tenaga kesehatan terbatas pada satu periode beririsan.
- Selisih P1/P2 dipertahankan apa adanya; tidak ada nilai yang dihapus atau dipaksa sama.
- Selisih numerik P3/P4 sengaja dikosongkan karena konstruk dan satuannya tidak sebanding; nilainya tetap ditampilkan di `nilai_utama`/`nilai_pembanding`.
- Rekonsiliasi numerik tingkat provinsi dan integrasi penuh ke panel Gold merupakan pekerjaan tahap lanjutan.
