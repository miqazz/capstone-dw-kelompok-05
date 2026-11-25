 # Rekonsiliasi Nasional (Tahap 6, Sprint 2)

**NIM:** 124450019  
**Kasus:** 05 — Akses layanan dan tenaga kesehatan

## Keluaran
- Tabel nasional periode × seri: `data/gold/nasional_periode_seri.csv`
  - Baris nasional diambil dari data Silver dengan (`wilayah_id` 9999 / Indonesia) seri utama BPS dan seri pembanding WHO dari berkas mentah (`data/raw/`), dilengkapi kolom lineage `_berkas_raw` dan `_sha256_raw` (mengacu `data/raw/MANIFEST.csv`).
  - Mencakup seri utama: `var1402`, `var2279`, `var1477` (semua rincian profesi yang tersedia pada baris nasional), seri pembanding WHO: `UHC_INDEX_REPORTED`, `FINPROTECTION_CATA_TOT_10_POP` (dimensi `TOTAL`), `HWF_0001`, `HWF_0006`, serta seri turunan konversi/penjumlahan rincian untuk keperluan perbandingan.

## Penetapan satuan dan definisi profesi (var1477 vs WHO HWF)

**Satuan var1477 (ditetapkan sebelum rekonsiliasi):** kepadatan per 100.000 penduduk. Dasar: metadata BPS JSON (`var` label "Kepadatan Dan Distribusi Tenaga Kesehatan", catatan memuat "(per 100.000 penduduk)"); kolom `satuan` pada CSV mentah kosong sehingga satuan dikonfirmasi dari metadata, bukan diasumsikan sebagai jumlah orang absolut. Untuk perbandingan dengan WHO (per 10.000 penduduk) dibuat seri turunan konversi `nilai_per10k = nilai_per100k / 10`.

**Definisi profesi WHO (diperiksa sebelum menjumlahkan rincian):**
- `HWF_0001` — *Medical doctors* (density per 10.000 population, NHWA/WHO; ISCO-08 221). Dibandingkan dengan rincian BPS **Dokter Umum** (`turvar_id` 1173) saja. Rincian **Dokter Gigi** (`turvar_id` 1174, ISCO-08 2261) **tidak** digabung ke HWF_0001 karena klasifikasi berbeda.
- `HWF_0006` — *Nursing and midwifery personnel* (density per 10.000 population, NHWA/WHO; ISCO-08 2221, 2222, 3221, 3222). Dibandingkan dengan jumlah rincian BPS **Perawat** (`turvar_id` 1175) + **Bidan** (`turvar_id` 1176). Rincian lain var1477 (Farmasi, Kesehatan Masyarakat, Kesehatan Lingkungan, Gizi, dll.) tidak termasuk.

**Rincian nasional yang dipakai (BPS):** `wilayah_id` 9999 (INDONESIA), `periode` 2018, berkas `bps/2026-10-20/sdg3_3_c_1_v1477.csv`. Nilai: Dokter Umum = 21 (per 100.000) → 2,1 (per 10.000); Perawat = 175, Bidan = 213, Perawat+Bidan = 388 (per 100.000) → 38,8 (per 10.000). Baris nasional 2016–2017 untuk rincian tersebut tidak tersedia pada snapshot mentah ini. BPS hanya menggunakan rincian Dokter Umum, sedangkan WHO HWF_0001 mencakup dokter umum dan dokter spesialis serta dokter yang tidak dirinci lebih lanjut. Oleh karena itu, perbandingan digunakan sebagai pembanding kontekstual terbatas dan tidak dianggap sebagai kesetaraan penuh.

## Daftar pasangan rekonsiliasi

| No | Seri utama (BPS) | Rincian utama yang dipakai | Seri pembanding (WHO) | Kategori keterbandingan | Catatan keterbandingan | Periode beririsan |
|---:|---|---|---|---|---|---|
| 1 | `var1477` (turunan: `var1477_dokter_umum_per10k`) | Dokter Umum (1173), nasional 2018, dikonversi ke per 10.000 | `HWF_0001` (Density of medical doctors, per 10.000) | Dapat dibandingkan secara terbatas dengan penyesuaian satuan, tetapi cakupan profesi tidak sepenuhya setara. | Satuan disetarakan (÷10). Definisi dibatasi ke dokter umum vs medical doctors; Dokter Gigi dikeluarkan. Cakupan/sumber pendataan dan tahun referensi dapat berbeda meski periode sama. | 2018 (n=1) |
| 2 | `var1477` (turunan: `var1477_perawat_bidan_per10k`) | Perawat (1175) + Bidan (1176), nasional 2018, dijumlahkan lalu dikonversi ke per 10.000 | `HWF_0006` (Density of nursing and midwifery personnel, per 10.000) | Dapat dibandingkan dengan penyesuaian satuan & agregasi rincian | Penjumlahan dilakukan setelah pemeriksaan definisi: WHO HWF_0006 mencakup nursing and midwifery personnel (selaras dengan Perawat+Bidan). Satuan disetarakan (÷10). Perbedaan cakupan kader (mis. asisten keperawatan) tetap mungkin. | 2018 (n=1) |
| 3 | `var1402` (Persentase unmet need pelayanan kesehatan, %) | Tidak ada (turvar 0), nasional | `UHC_INDEX_REPORTED` (UHC service coverage index, skor 0–100) | Kontekstual — **definisi berbeda** | Keduanya terkait SDG 3.8.1/cakupan layanan, tetapi konstruk berbeda: unmet need (proporsi kebutuhan tidak terpenuhi) vs indeks cakupan layanan esensial komposit. Skala, arah interpretasi, metode, dan komponen berbeda; tidak disetarakan/dijumlahkan, hanya dibaca berdampingan. | 2015–2023 (n=9) |
| 4 | `var2279` (Persentase penduduk memiliki JKN, %) | Tidak ada (turvar 0), nasional | `FINPROTECTION_CATA_TOT_10_POP` (% populasi dengan pengeluaran kesehatan >10% anggaran rumah tangga, dimensi `TOTAL`) | Kontekstual — **definisi berbeda**; baris periode tidak berpasangan: `belum terjelaskan` | Terkait perlindungan finansial kesehatan (3.8.2) namun indikator berbeda arah/konsep: kepemilikan jaminan (JKN: BPJS PBI/Non PBI/Jamkesda) vs insiden pengeluaran kesehatan katastropik `FINPROTECTION_CATA_TOT_10_POP`. Sumber/metode survei dan cakupan berbeda. Pembanding WHO difilter ke `DIM_DEG_URB=TOTAL` dengan dimensi lain kosong agar mewakili populasi total. Periode snapshot tidak beririsan. | — (n=0) |

**Ringkasan:** `pasangan_rekonsiliasi = 4`, `periode_beririsan = 11` (jumlah baris pasangan dengan nilai utama dan pembanding terisi; selisih numerik dihitung hanya untuk pasangan sebanding: P1 2018 = -2.11, P2 2018 = +7.91; P3 memiliki 9 baris beririsan tetapi `selisih` dikosongkan karena definisi/konstruk berbeda; P4 tidak beririsan).

## Tabel keluaran

- `data/gold/rekonsiliasi_nasional.csv` / `.parquet` / tabel `rekonsiliasi_nasional` di `data/gold/gold.sqlite`
- Kolom: `pasangan_id, seri_utama, rincian_utama, seri_pembanding, rincian_pembanding, periode, jenis_periode, nilai_utama, satuan_utama, nilai_pembanding, satuan_pembanding, selisih, kategori_selisih, penjelasan, bukti_dicari`
- 76 baris total; semua baris memiliki kategori; baris `belum terjelaskan` memuat dugaan dan bukti yang dicari. Validasi memeriksa kelengkapan `penjelasan` dan `bukti_dicari` untuk kategori tersebut.

## Keterbatasan
- Baris nasional var1477 pada snapshot hanya tersedia tahun 2018 (8 rincian), sehingga rekonsiliasi tenaga kesehatan terbatas pada satu periode.
- Selisih nilai pada periode beririsan (jika ada) tidak dihapus; perbedaan definisi, satuan, cakupan, dan metode harus dibaca dari kolom `catatan`/tabel ini.
- Rekonsiliasi numerik tingkat provinsi dan integrasi ke Gold panel penuh merupakan pekerjaan tahap lanjutan tim.
