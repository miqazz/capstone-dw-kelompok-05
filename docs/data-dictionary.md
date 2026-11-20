# Data dictionary — Data Alchemist (Kelompok 5)

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan: tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## data/silver/silver.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | bps, bnpb, wdi, who_gho, ilostat | nama folder data/raw | |
| seri_kode | string | - | tidak | var1402, var2279, var1477, UHC_INDEX_REPORTED, FINPROTECTION_CATA_TOT_10_POP, HWF_0001, HWF_0006 | nama seri BPS/WHO | Kode indikator pengamatan |
| wilayah_kode | int | kode BPS x 100 | tidak | 9999 atau 1100–9600 | log K-001 | Kode 38 provinsi tahun 2025 (provinsi x 100) dan 9999 untuk nasional |
| nama_wilayah | string | teks | tidak | Aceh, Sumatera Utara, ..., Indonesia | log K-001 | Nama resmi provinsi atau Indonesia |
| periode | string | YYYY | tidak | 1992–2025 | tahun pengamatan BPS/WHO | Tahun pengamatan data |
| jenis_periode | string | - | tidak | tahunan | turtahun BPS / frekuensi WHO | Frekuensi pengumpulan/rilis data |
| rincian | string | snake_case | tidak | total, dokter, perawat, bidan, tenaga_kefarmasian, dll (dan dimensi WHO) | turvar BPS / DIM WHO | Kategori disagregasi. Nilainya 'total' jika angka agregat |
| nilai | float64 | numerik | tidak | sesuai rentang indikator dan satuan sumber | kolom nilai mentah | Nilai indikator; baris kosong dari mentah tidak dimasukkan ke Silver |
| satuan | string | - | tidak | persen, persen_populasi, per_100000_penduduk, per_10000_penduduk, indeks_per_100 | metadata sumber / log keputusan | Satuan ukur baku dari pengamatan |
| _berkas_raw | string | jalur relatif | tidak | jalur di dalam data/raw/ | src.common.manifest | Untuk penelusuran berkas mentah asli |
| _sha256_raw | string | hex 64 karakter | tidak | hash SHA-256 (64 karakter) | src.common.manifest | Hash menjamin keaslian data dari snapshot |

## data/gold/<tabel>.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|

## Referensi Metadata dan Definisi Seri

Bagian ini mendokumentasikan sumber metadata dan definisi seri BPS dan WHO yang digunakan dalam kasus 05. Profil periode, jumlah observasi, dimensi, dan irisan tahun tersedia pada `reports/profil_seri_pembanding.md`.

### A. Seri BPS

| Kode Seri | Nama Indikator | Informasi Metadata | Satuan | Sumber Metadata dan Data |
|---|---|---|---|---|
| `var1402` | Persentase Unmet Need Pelayanan Kesehatan Menurut Provinsi | Penduduk yang mengalami keluhan kesehatan dan terganggu aktivitasnya, tetapi tidak melakukan rawat jalan, berdasarkan metadata SIRUSA. | Persen | [Metadata SIRUSA](https://sirusa.bps.go.id/metadata/indikator/1bd82d5c-6161-7de8-6dd0-152d7c8c448d). Data: `data/raw/bps/2026-10-20/sdg3_3_8_1_a_v1402.csv`. |
| `var2279` | Persentase Penduduk yang Memiliki Jaminan Kesehatan Nasional (JKN) Menurut Provinsi | Menggambarkan kepemilikan JKN. Indikator ini membahas kepemilikan jaminan kesehatan, bukan pengeluaran kesehatan katastropik. | Persen | [Tabel BPS](https://www.bps.go.id/id/statistics-table/2/MjI3OSMy/persentase-penduduk-yang-memiliki-jaminan-kesehatan-nasional--jkn--menurut-provinsi--persen-.html) dan [metadata umum SIRUSA](https://sirusa.bps.go.id/metadata/indikator/cc16cb10-8f4a-da86-ae10-a40060aa9ca9). Data: `data/raw/bps/2026-10-20/sdg3_3_8_2_a_v2279.csv`. |
| `var1477` | Kepadatan dan Distribusi Tenaga Kesehatan | Metadata JSON BPS mencantumkan sumber Informasi SDM Kesehatan Badan PPSDM Kesehatan, Kementerian Kesehatan RI, serta keterangan satuan per 100.000 penduduk. | Per 100.000 penduduk | Metadata: `data/raw/bps/2026-10-20/json/sdg3_3_c_1_v1477.json`. Data: `data/raw/bps/2026-10-20/sdg3_3_c_1_v1477.csv`. |

### B. Seri WHO

Metadata WHO diperoleh dari `data/raw/who_gho/2026-10-20/datadot/ddiindicators_skip0000.json`. Identifikasi dilakukan berdasarkan kode indikator dan ID metadata (`UrlName`).

| Kode Seri | ID Metadata WHO | Definisi dan Informasi Metadata | Satuan | Sumber Data |
|---|---|---|---|---|
| `UHC_INDEX_REPORTED` | `9A706FD` | Indeks cakupan layanan kesehatan esensial yang disusun dari 14 indikator pelacak. | Indeks (maksimum 100) | `data/raw/who_gho/2026-10-20/datadot/9A706FD_UHC_INDEX_REPORTED.csv` |
| `FINPROTECTION_CATA_TOT_10_POP` | `A65146D` | Persentase penduduk dalam rumah tangga dengan pengeluaran kesehatan melebihi 10% anggaran rumah tangga. | Persen populasi | `data/raw/who_gho/2026-10-20/datadot/A65146D_FINPROTECTION_CATA_TOT_10_POP.csv` |
| `HWF_0001` | `217795A` | Kepadatan dokter. Metadata menyebut pelaporan melalui National Health Workforce Accounts (NHWA) dan denominator populasi dari UN World Population Prospects. | Per 10.000 penduduk | `data/raw/who_gho/2026-10-20/datadot/217795A_HWF_0001.csv` |
| `HWF_0006` | `5C8435F` | Kepadatan perawat dan bidan. Metadata menyebut pelaporan melalui NHWA dan denominator populasi dari UN World Population Prospects. | Per 10.000 penduduk | `data/raw/who_gho/2026-10-20/datadot/5C8435F_HWF_0006.csv` |

### C. Batasan Penggunaan dan Pemetaan Antar Seri

Kesamaan tema kesehatan tidak secara otomatis menunjukkan kesetaraan definisi, metode penghitungan, satuan, maupun cakupan populasi. Oleh karena itu, pemetaan seri BPS dan WHO digunakan sebagai pembanding kontekstual dengan batasan berikut:

1. `var1402` dan `UHC_INDEX_REPORTED` tidak dinyatakan sebagai indikator identik. Unmet need dan indeks cakupan layanan kesehatan esensial mengukur aspek yang berbeda. Kesamaan periode tidak membuktikan kesetaraan definisi.
2. `var2279` dan `FINPROTECTION_CATA_TOT_10_POP` tidak dinyatakan setara. Kepemilikan JKN tidak sama dengan pengeluaran kesehatan katastropik. Kedua seri juga tidak memiliki tahun observasi yang beririsan pada data yang diperoleh.
3. `var1477` dan `HWF_0001` hanya menjadi pembanding kontekstual. WHO menggunakan kepadatan dokter per 10.000 penduduk, sedangkan BPS menggunakan per 100.000 penduduk dan memiliki beberapa kategori tenaga kesehatan.
4. `var1477` dan `HWF_0006` hanya menjadi pembanding kontekstual. WHO menggabungkan perawat dan bidan, sedangkan BPS menyimpan kategori tenaga kesehatan secara terpisah.

Selain perbedaan definisi dan satuan, data WHO yang diperoleh hanya tersedia pada tingkat nasional, sedangkan data BPS mencakup tingkat provinsi. Data WHO tidak digunakan untuk menyimpulkan kesetaraan atau perbedaan kondisi antarprovinsi.

Analisis perbandingan memperhatikan irisan tahun yang benar-benar tersedia, tingkat wilayah, definisi indikator, satuan, dan cakupan data. Tidak dilakukan penyetaraan angka atau penarikan kesimpulan langsung dari dua indikator yang belum terbukti mengukur konstruk yang sama.

## Contoh Ketertelusuran (Lineage) Baris Silver ke Berkas Mentah

Contoh untuk baris data persentase *Unmet Need* (`var1402`) di Aceh pada tahun 2023:

**Kolom Pencarian di Silver:**

- `seri_kode`: "var1402"
- `wilayah_kode`: 1100
- `periode`: "2023"
- `rincian`: "total"
- `_berkas_raw`: "bps/2026-10-20/sdg3_3_8_1_a_v1402.csv"
- `_sha256_raw`: 28ffd7f28e35a54da609618ee3fd164c20cd39e248ab69aa2cda94c90e50b15d

**Cara Verifikasi:**

1. Pipeline mengecek `_sha256_raw` di atas apakah sama persis dengan hash file CSV tersebut di `data/raw/MANIFEST.csv`. Jika berbeda, pipeline gagal.
2. Buka berkas `data/raw/bps/2026-10-20/sdg3_3_8_1_a_v1402.csv`.
3. Cari baris dengan wilayah "Aceh" (kode `1100`) dan kolom tahun `2023`. Nilai di sel tersebut akan sama persis dengan kolom `nilai` di baris Silver, sehingga kesesuaian nilai dengan berkas mentah dapat diverifikasi.
