# Data dictionary — Kasus 05 Akses layanan dan tenaga kesehatan (Data Alchemist / Kelompok 5)

Diisi dari data nyata. Angka dihitung dari berkas `data/silver` dan `data/gold` yang di-commit.

## data/silver/silver.(csv|parquet|sqlite:table silver)

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | ['bps', 'who_gho'] | nama folder/format sumber | Sumber data |
| seri_kode | string | kode seri | tidak | ['FINPROTECTION_CATA_TOT_10_POP', 'HWF_0001', 'HWF_0006', 'UHC_INDEX_REPORTED', 'var1402', 'var1477', 'var2279'] | BPS/WHO raw | Kode seri indikator |
| wilayah_kode | int | kode BPS x 100 / 9999 | tidak | 1100–9999 | K-001 | 9999=Indonesia, provinsi=kode BPS x 100 |
| nama_wilayah | string | — | tidak | 39 nilai unik | raw BPS/WHO | Nama wilayah |
| periode | string/int | YYYY | tidak | 1992–2025 | raw | Periode observasi |
| jenis_periode | string | enum | tidak | ['tahun'] | normalisasi | Tipe periode |
| rincian | string | — | tidak | 12 nilai unik | turvar BPS / TOTAL WHO | Rincian/turunan |
| nilai | float | lihat satuan | tidak | 0.0–377.0 | raw | Nilai observasi |
| satuan | string | — | tidak | ['Persen', 'indeks (skor cakupan layanan UHC, 0-100)', 'kepadatan per 100.000 penduduk', 'per 10.000 penduduk', 'persen populasi'] | raw/metadata K-002 | Satuan nilai |
| _berkas_raw | string | path relatif data/raw | tidak | 7 berkas | MANIFEST | Lineage berkas |
| _sha256_raw | string | sha256 hex | tidak | 64 char | MANIFEST.csv | Lineage hash |

Ringkasan: 1541 baris, 7 seri, 39 wilayah, duplikat kunci 0.

## data/gold/panel_provinsi.(csv|parquet|sqlite:gold_panel_provinsi)

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | ['bps'] | Silver | Sumber |
| seri_kode | string | — | tidak | ['var1402', 'var1477', 'var2279'] | Silver | Seri BPS provinsi |
| wilayah_kode | int | kode BPS x 100 | tidak | 1100–9700, !=9999 | Silver | Provinsi saja |
| nama_wilayah | string | — | tidak | 38 nilai | Silver | Nama provinsi |
| periode | string | YYYY | tidak | 2015–2025 | Silver | Tahun |
| jenis_periode | string | enum | tidak | tahun | Silver | Tahunan |
| rincian | string | — | tidak | 11 nilai | Silver | Rincian/turvar |
| nilai | float | lihat satuan | tidak | 0.0–377.0 | Silver | Nilai |
| satuan | string | — | tidak | ['Persen', 'kepadatan per 100.000 penduduk'] | Silver/K-002 | Satuan |
| _berkas_raw | string | path | tidak | 3 berkas | MANIFEST | Lineage |
| _sha256_raw | string | sha256 | tidak | 64 char | MANIFEST | Lineage |

Ringkasan: 1448 baris (nasional 9999 dikeluarkan).

## data/gold/nasional_periode_seri.(csv|parquet|sqlite:gold_nasional_periode_seri)

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | ['bps', 'who_gho'] | Silver/turunan | bps/who_gho |
| seri_kode | string | — | tidak | ['FINPROTECTION_CATA_TOT_10_POP', 'HWF_0001', 'HWF_0006', 'UHC_INDEX_REPORTED', 'var1402', 'var1477', 'var1477_dokter_umum_per10k', 'var1477_perawat_bidan_per100k', 'var1477_perawat_bidan_per10k', 'var2279'] | Silver/turunan | Termasuk seri turunan per10k |
| periode | string | YYYY | tidak | 1992–2025 | Silver | Tahun |
| jenis_periode | string | enum | tidak | tahun | Silver | Tahunan |
| rincian | string | — | tidak | ['Bidan', 'Dokter Gigi', 'Dokter Umum', 'Farmasi', 'Gizi', 'Kesehatan Lingkungan', 'Kesehatan Masyarakat', 'Perawat', 'Perawat + Bidan', 'TOTAL', 'Tidak ada'] | Silver/turunan | Rincian/TOTAL |
| nilai | float | lihat satuan | tidak | 0.57–388.0 | Silver/turunan | Nilai |
| satuan | string | — | tidak | ['Persen', 'indeks (skor cakupan layanan UHC, 0-100)', 'kepadatan per 100.000 penduduk', 'per 10.000 penduduk', 'persen populasi'] | Silver/K-002/K-003 | Satuan |
| _berkas_raw | string | path | tidak | 7 berkas | MANIFEST | Lineage |
| _sha256_raw | string | sha256 | tidak | 64 char | MANIFEST | Lineage |
| catatan | string | — | ya | teks/kosong | aturan rekonsiliasi | Catatan turunan/filter |

Ringkasan: 96 baris.

## data/gold/rekonsiliasi_nasional.(csv|parquet|sqlite:rekonsiliasi_nasional)

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal | Keterangan |
|---|---|---|---|---|---|---|
| pasangan_id | string | ID | tidak | ['P1_dokter_hwf0001', 'P2_perawat_bidan_hwf0006', 'P3_var1402_uhc', 'P4_var2279_finprot'] | aturan kasus 05 | ID pasangan |
| seri_utama | string | — | tidak | ['var1402', 'var1477_dokter_umum_per10k', 'var1477_perawat_bidan_per10k', 'var2279'] | BPS/turunan | Seri utama |
| rincian_utama | string | — | tidak | ['Dokter Umum', 'Perawat + Bidan', 'Tidak ada'] | BPS | Rincian utama |
| seri_pembanding | string | — | tidak | ['FINPROTECTION_CATA_TOT_10_POP', 'HWF_0001', 'HWF_0006', 'UHC_INDEX_REPORTED'] | WHO | Seri pembanding |
| rincian_pembanding | string | — | tidak | TOTAL | WHO | Rincian pembanding |
| periode | string | YYYY | tidak | 1992–2025 | Silver/Gold | Tahun |
| jenis_periode | string | enum | tidak | tahun | aturan | Tahunan |
| nilai_utama | float | sesuai satuan_utama | ya | 2.1–75.49 atau kosong | Gold nasional | Nilai utama |
| satuan_utama | string | — | ya | ['Persen', 'per 10.000 penduduk'] | Gold | Satuan utama |
| nilai_pembanding | float | sesuai satuan_pembanding | ya | 0.57–68.0 atau kosong | Gold nasional | Nilai pembanding |
| satuan_pembanding | string | — | ya | ['indeks (skor cakupan layanan UHC, 0-100)', 'per 10.000 penduduk', 'persen populasi'] | Gold | Satuan pembanding |
| selisih | float | utama-pembanding | ya | numerik/kosong | hitung | Kosong bila tidak berpasangan/definisi berbeda |
| kategori_selisih | string | enum | tidak | definisi berbeda, metode berbeda, vintage berbeda, cakupan berbeda, belum terjelaskan | K-003/K-004/aturan | Kategori; `belum terjelaskan` wajib punya penjelasan & bukti_dicari |
| penjelasan | string | teks | tidak | teks | log/analisis | Alasan kategori |
| bukti_dicari | string | teks | ya | teks | log/analisis | Bukti/rujukan yang diperiksa |

Ringkasan: 76 baris; 4 pasangan; periode beririsan terisi 11.

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
