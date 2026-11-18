# Laporan tim — <Nama tim>, kasus <NN> <judul kasus>

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan
Kasus, seri yang ditangani, dan satu kalimat temuan utama tentang kualitas datanya.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17–20 Oktober 2026.

## Masalah data dan penanganannya (draf Sprint 1, 124450019)

Sumber angka: profil Silver pertama (`sprint/sprint-1/capstone/profil_ringkasan.txt`, hasil `python3 sprint/sprint-1/capstone/muat_silver_pertama.py` atas `data/silver/silver.csv`/`data/silver/silver.sqlite`) dan keputusan di `log-keputusan.csv`. Manifest: 13 berkas mentah, 1.389.023 bait (`data/raw/MANIFEST.csv`). Silver pertama: 1.541 baris, 7 seri, 39 wilayah, duplikat kunci 0.

| No | Masalah | Bukti/angka (dapat ditarik ulang) | Penanganan/keputusan | Status/ID log |
|---:|---|---|---|---|
| 1 | Agregat nasional tercampur dengan unit provinsi | `wilayah_id` 9999 (INDONESIA) hadir di seri BPS; Silver memuat 39 wilayah (38 prov + 1 nasional) per seri BPS terkait. | Pisahkan 9999 sebagai agregat nasional; 38 provinsi sebagai unit analisis provinsi (kode BPS 4 digit). | K-001 |
| 2 | Celah panel provinsi×periode (pemekaran & cakupan tahun) — var1402 | 393 baris; periode 2015–2025 (n=11), 38 prov teramati, 1 rincian; grid prov teramati: expected 418, observed 382, **missing 36 sel** (4 prov pemekaran Papua: 9200,9500,9600,9700 tanpa observasi 2015–2023 = 4×9). | Belum diimputasi di Silver; kekosongan dicatat sebagai celah panel (baris kosong baru tampak saat grid lengkap dibentuk). | — |
| 3 | Celah panel — var2279 (seri baru) | 152 baris; periode 2022–2025 (n=4), 38 prov; expected 152, observed 148, **missing 4 sel** (9200,9500,9600,9700 pada 2022). | Sama: pertahankan observasi apa adanya, tangani ketiadaan pra-2022/pemekaran di tahap transformasi/analisis. | — |
| 4 | Celah panel & cakupan provinsi/rincian tidak penuh — var1477 | 926 baris; periode 2016–2018 (n=3), **35 wilayah (34 prov)**, 10 rincian; expected 1020, observed 918, **missing 102 sel**. Prov 9200,9500,9600,9700 tidak hadir; dari 34 prov teramati ada 68 kombinasi wilayah-tahun dengan rincian tak lengkap (102 sel). Nilai teramati 0,0–377,0 (kepadatan/100.000). | Pertahankan rincian & observasi sumber; celah panel didokumentasikan (termasuk provinsi/sel rincian yang hilang). | — |
| 5 | Rincian nasional var1477 tidak lengkap | Baris nasional (9999) = 8 (hanya 2018) dari 10 turvar; rincian nasional **tidak ada**: “Ahli Teknologi Laboratorium Medik”, “Pekarya”; tidak ada baris nasional 2016–2017. | Rekonsiliasi tenaga kesehatan dibatasi pada rincian & periode yang tersedia; rincian tak tersedia tidak diimputasi. | — |
| 6 | Satuan var1477 tidak eksplisit di CSV & koreksi pemetaan katalog | Kolom `satuan` CSV mentah var1477 kosong; metadata BPS JSON menyatakan kepadatan “(per 100.000 penduduk)”. KASUS.md: seri tenaga kesehatan belum terpetakan ke kode SDG di katalog. | Satuan ditetapkan sebagai kepadatan per 100.000 penduduk (bukan jumlah orang) sebelum konversi; pemetaan SDG (konteks 3.c.1) perlu ditetapkan tim (koreksi katalog). | K-002 |
| 7 | Ketidakteraturan/patahan deret waktu seri pembanding WHO (snapshot) | FINPROTECTION_CATA_TOT_10_POP (TOTAL, 20 obs, 1999–2021): **celah 2000,2003,2008**. HWF_0001 (13 obs, 1993–2023): 18 tahun hilang dalam rentang. HWF_0006 (13 obs, 1992–2023): 19 tahun hilang; lonjakan 2018→2019 (30,89→37,81 per 10.000) teramati di Silver — indikasi potensi patahan definisi/cakupan, perlu verifikasi metadata. UHC 24 obs (2000–2023) kontinu. | Simpan observasi tahun yang tersedia; celah/potensi patahan dilaporkan (bukan diisi/dihapus) untuk kehati-hatian interpretasi. | — |
| 8 | Disagregasi pembanding & keterbandingan definisi | FINPROTECTION mentah 201 baris, 14 kombinasi dimensi; untuk populasi nasional dipakai `DIM_DEG_URB=TOTAL` dengan dimensi lain kosong (20 baris). Pasangan var1402–UHC dan var2279–FINPROTECTION terkait konsep tapi definisi/konstruk berbeda. | Filter dimensi TOTAL untuk pembanding nasional; pasangan kontekstual dilaporkan dengan kategori **definisi berbeda** (tidak disetarakan). | K-004 |
| 9 | Duplikat & format periode | Duplikat kunci Silver = 0 untuk semua seri (7 seri). Periode BPS/WHO yang dimuat bertipe tahun (`jenis_periode=tahun`). | Kunci unik ditegakkan di skema/pemuat; format periode distandardisasi ke representasi tahun. | — |
| 10 | Anomali rentang nilai (perlu perhatian, bukan penghapusan) | var1477 rentang 0,0–377,0 (kepadatan/100.000) — sebaran lebar antar provinsi/rincian; var1402 1,39–10,21%; var2279 53,49–98,18%. | Nilai dipertahankan (profil/validasi lanjut & deteksi outlier formal di tahap berikutnya). | — |

**Keterlacakan:** hitung ulang profil/celah via `python3 sprint/sprint-1/capstone/muat_silver_pertama.py` (menghasilkan `profil_ringkasan.txt`, `data/silver/silver.csv`, `data/silver/silver.sqlite`); rincian keputusan di `log-keputusan.csv`.

## Integrasi dan rekonsiliasi
Seri utama vs pembanding nasional: selisih, penjelasannya (definisi, metode, vintage, granularitas),
dan hasil analisis revisi dari arsip WDI.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
