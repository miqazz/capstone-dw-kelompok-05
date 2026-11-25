# Profil Seri Pembanding WHO

## 1. Tujuan

Analisis ini dilakukan untuk mengidentifikasi karakteristik empat seri indikator WHO yang berpotensi digunakan sebagai data pembanding terhadap indikator BPS pada kasus 05, yaitu akses layanan dan tenaga kesehatan.

Profil yang dianalisis meliputi periode ketersediaan data, jumlah observasi, tingkat wilayah, satuan, dimensi atau breakdown, serta irisan tahun dengan data BPS.

## 2. Hasil Profil Seri WHO

| Seri WHO | Periode | Jumlah Observasi | Satuan | Tingkat Wilayah |
|---|---|---:|---|---|
| UHC_INDEX_REPORTED | 2000–2023 | 24 | Indeks (maksimum 100) | Nasional |
| FINPROTECTION_CATA_TOT_10_POP | 1999–2021 | 201 | Persentase populasi | Nasional |
| HWF_0001 | 1993–2023 | 13 | Dokter per 10.000 penduduk | Nasional |
| HWF_0006 | 1992–2023 | 13 | Perawat dan bidan per 10.000 penduduk | Nasional |

Seluruh seri WHO yang diperiksa hanya menyediakan data pada tingkat nasional Indonesia. Tidak ditemukan rincian data berdasarkan provinsi.

## 3. Dimensi dan Breakdown

Tiga seri, yaitu UHC_INDEX_REPORTED, HWF_0001, dan HWF_0006, tidak memiliki breakdown tambahan pada data yang diperoleh.

Seri FINPROTECTION_CATA_TOT_10_POP memiliki lima dimensi:

| Dimensi | Kategori | Jumlah Observasi per Kategori |
|---|---|---:|
| Komposisi rumah tangga | 6 kategori komposisi rumah tangga | 15 |
| Wilayah tempat tinggal | TOTAL | 20 |
| Wilayah tempat tinggal | RURAL | 16 |
| Wilayah tempat tinggal | URBAN | 16 |
| Jenis kelamin | FEMALE, MALE | 15 per kategori |
| Tipe populasi | POP_TYPE_HOUSEHOLD_HEAD | 60 |
| Kelompok umur | AGE60+, AGELT60 | 15 per kategori |

Rincian kategori lengkap disimpan dalam `reports/breakdown_finprotection.csv`.

## 4. Perbandingan Periode dengan Data BPS

Irisan tahun dihitung berdasarkan tahun observasi yang benar-benar tersedia pada kedua dataset, bukan hanya berdasarkan rentang tahun.

| Seri WHO | Seri BPS Pembanding | Tahun Irisan | Jumlah |
|---|---|---|---:|
| UHC_INDEX_REPORTED | var1402 | 2015–2023 | 9 |
| FINPROTECTION_CATA_TOT_10_POP | var2279 | Tidak ada | 0 |
| HWF_0001 | var1477 | 2017–2018 | 2 |
| HWF_0006 | var1477 | 2016–2018 | 3 |

## 5. Penilaian Kelayakan Pembanding

Status pemetaan dibedakan menjadi informasi yang telah terverifikasi berdasarkan metadata atau tabel resmi BPS dan kesesuaian definisi yang masih perlu dikonfirmasi. Kesamaan tema atau nama file tidak cukup untuk menyatakan dua indikator memiliki definisi yang identik.

### UHC_INDEX_REPORTED dan var1402

**Status: Pembanding kontekstual - kesetaraan definisi belum terverifikasi.**

**Informasi BPS yang terverifikasi:**
- Nama indikator: Persentase Unmet Need Pelayanan Kesehatan Menurut Provinsi.
- Satuan: persen.
- Periode: tahunan.
- Metadata SIRUSA menjelaskan unmet need sebagai penduduk yang mengalami keluhan kesehatan dan terganggu aktivitasnya, tetapi tidak berobat jalan.
- Sumber: https://sirusa.bps.go.id/metadata/indikator/1bd82d5c-6161-7de8-6dd0-152d7c8c448d

**Hal yang belum terverifikasi:**
- Kesetaraan definisi, komponen penyusun, dan metode penghitungan var1402 dengan UHC Service Coverage Index (UHC_INDEX_REPORTED) dari WHO.
- Oleh karena itu, keduanya tidak dinyatakan sebagai indikator yang identik dan tidak digunakan untuk perbandingan angka secara langsung.

Terdapat sembilan tahun irisan, yaitu 2015-2023. Irisan periode tersebut memungkinkan pembacaan secara berdampingan, tetapi tidak membuktikan kesetaraan indikator.

### FINPROTECTION_CATA_TOT_10_POP dan var2279

**Status: Pembanding kontekstual - kesetaraan definisi belum terverifikasi.**

**Informasi BPS yang terverifikasi:**
- Nama indikator: Persentase Penduduk yang Memiliki Jaminan Kesehatan Nasional (JKN) Menurut Provinsi.
- Satuan: persen.
- Periode: tahunan.
- Indikator membahas kepemilikan JKN, bukan pengeluaran kesehatan katastropik.
- Sumber tabel BPS: https://www.bps.go.id/id/statistics-table/2/MjI3OSMy/persentase-penduduk-yang-memiliki-jaminan-kesehatan-nasional--jkn--menurut-provinsi--persen-.html
- Referensi metadata umum kepemilikan jaminan kesehatan: https://sirusa.bps.go.id/metadata/indikator/cc16cb10-8f4a-da86-ae10-a40060aa9ca9

**Hal yang belum terverifikasi:**
- Kesetaraan definisi dan metode penghitungan var2279 dengan indikator WHO FINPROTECTION_CATA_TOT_10_POP.
- Kepemilikan JKN tidak dapat dianggap identik dengan pengeluaran kesehatan katastropik.

Tidak terdapat tahun irisan antara kedua seri. Oleh karena itu, keduanya belum dapat digunakan untuk perbandingan berdasarkan periode yang tersedia.

### HWF_0001 dan var1477

**Status: Pembanding kontekstual - definisi dan satuan berbeda.**

WHO menyediakan kepadatan dokter per 10.000 penduduk, sedangkan BPS memiliki kategori tenaga kesehatan termasuk dokter umum. Cakupan definisi tenaga dokter dan satuannya berbeda sehingga hanya dapat digunakan sebagai pembanding kontekstual.

### HWF_0006 dan var1477

**Status: Pembanding kontekstual - definisi dan satuan berbeda.**

WHO menyajikan kepadatan gabungan perawat dan bidan per 10.000 penduduk, sedangkan BPS menyediakan data jumlah tenaga kesehatan berdasarkan kategori. Perbedaan satuan dan cakupan perlu diperhatikan sehingga keduanya belum dapat dibandingkan secara langsung.

## 6. Kesimpulan

Hasil profiling menunjukkan bahwa keempat seri WHO memiliki karakteristik periode, satuan, dan dimensi yang berbeda. Hanya tiga seri yang memiliki irisan tahun dengan indikator BPS, sedangkan seri Financial Protection tidak memiliki tahun irisan dengan seri BPS yang dipasangkan.

Seluruh seri WHO yang diperiksa hanya tersedia pada tingkat nasional. Oleh karena itu, data tersebut tidak dapat langsung dibandingkan dengan data BPS pada tingkat provinsi. Seri WHO dapat digunakan sebagai referensi atau pembanding kontekstual dengan memperhatikan kesesuaian definisi, satuan, cakupan, dan periode.

## 7. File Keluaran

- `notebooks/profil_seri_pembanding.ipynb`
- `reports/profil_seri_pembanding.csv`
- `reports/breakdown_finprotection.csv`
- `reports/profil_seri_pembanding.md`