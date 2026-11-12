# Data dictionary — Data Alchemist (Kelompok 5)

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

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
| nilai | float64 | numerik | tidak | 0–100 (persen), atau > 0 (kepadatan/indeks) | kolom nilai mentah | Nilai indikator (baris missing/kosong dari mentah tidak dimasukkan ke Silver) |
| satuan | string | - | tidak | persen, per_10000_penduduk, indeks | manifest_asal.json / log keputusan | Satuan ukur baku dari pengamatan |
| _berkas_raw | string | jalur relatif | tidak | jalur di dalam data/raw/ | src.common.manifest | Untuk penelusuran berkas mentah asli |
| _sha256_raw | string | hex 64 karakter | tidak | hash SHA-256 (64 karakter) | src.common.manifest | Hash menjamin keaslian data dari snapshot |

## data/gold/<tabel>.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|

## Contoh Ketertelusuran (Lineage) Baris Silver ke Berkas Mentah

Contoh untuk baris data persentase *Unmet Need* (var1402) di Aceh pada tahun 2023:

* **Kolom Pencarian di Silver:**
  * `seri_kode`: "var1402"
  * `wilayah_kode`: 1100
  * `periode`: "2023"
  * `rincian`: "total"
  * `_berkas_raw`: "bps/2026-10-20/sdg3_3_8_1_a_v1402.csv"
  * `_sha256_raw`: 28ffd7f28e35a54da609618ee3fd164c20cd39e248ab69aa2cda94c90e50b15d

* **Cara Verifikasi:**
  1. Pipeline mengecek `_sha256_raw` di atas apakah sama persis dengan hash file CSV tersebut di `data/raw/MANIFEST.csv`. Jika beda, pipeline gagal.
  2. Buka berkas `data/raw/bps/2026-10-20/sdg3_3_8_1_a_v1402.csv`.
  3. Cari baris dengan wilayah "Aceh" (kode `1100`) dan kolom tahun `2023`. Nilai di sel tersebut akan sama persis dengan kolom `nilai` di baris Silver kita, membuktikan tidak ada data yang dikarang.