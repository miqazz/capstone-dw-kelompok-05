# Laporan tim — <Nama tim>, kasus <NN> <judul kasus>

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan
Kasus, seri yang ditangani, dan satu kalimat temuan utama tentang kualitas datanya.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17–20 Oktober 2026.

## Masalah data dan penanganannya (draf Sprint 1, 124450019)

Seluruh angka pada bagian ini dihitung dari `data/silver/silver.csv` dengan skrip `sprint/sprint-1/capstone/audit_profil.py`. Jalankan dari root repository menggunakan `python sprint/sprint-1/capstone/audit_profil.py`; hasil rinci (termasuk daftar sel/tahun yang hilang) ditulis ke `sprint/sprint-1/capstone/audit_profil.txt`. Silver yang diaudit berisi 1.541 baris, 7 seri, 39 kode wilayah unik, dan 0 duplikat pada kunci Silver.

Perlu dibedakan bahwa profil_ringkasan.txt merupakan hasil profiling pada saat pemuatan Silver pertama, sedangkan audit_profil.txt merupakan hasil audit ulang terhadap file Silver yang sama, yaitu data/silver/silver.csv. Perbedaan jumlah baris per seri pada kedua ringkasan disebabkan oleh perbedaan cakupan penghitungan. Ringkasan awal mencakup data nasional dan provinsi, sedangkan perhitungan celah panel BPS pada audit hanya mencakup data provinsi dengan mengecualikan kode wilayah 9999 (INDONESIA). Dengan demikian, perbedaan angka tersebut tidak menunjukkan penggunaan sumber Silver yang berbeda, melainkan perbedaan cakupan observasi yang dihitung.

Berdasarkan hasil audit, data Silver yang digunakan terdiri atas 1.541 baris, 7 seri, 39 kode wilayah unik, dan tidak ditemukan duplikasi pada kunci Silver. Hasil ini menjadi dasar dalam penyusunan ringkasan kualitas data dan identifikasi permasalahan data pada laporan.

| No | Masalah | Bukti/angka dan cara penarikan ulang | Penanganan/keputusan | Status/ID log |
|---:|---|---|---|---|
| 1 | Agregat nasional tercampur dengan unit provinsi | Kolom `wilayah_kode` menggunakan `9999` untuk INDONESIA. Silver memiliki 39 kode wilayah unik; kode nasional dipisahkan sehingga unit provinsi dianalisis tersendiri. | Pisahkan `9999` sebagai agregat nasional; 38 provinsi menjadi unit analisis provinsi. | K-001 |
| 2 | Celah panel provinsi×periode — var1402 | Dari Silver: 38 provinsi × 11 tahun (2015–2025) × 1 rincian = 418 sel yang diharapkan. Observasi provinsi = 382; celah = 418 − 382 = **36 sel**. Audit mencantumkan kode wilayah dan tahun yang tidak ada: 9200, 9500, 9600, 9700 pada 2015–2023 (4 × 9). | Tidak diimputasi di Silver; kekosongan dicatat sebagai celah panel. | — |
| 3 | Celah panel — var2279 | Dari Silver: 38 provinsi × 4 tahun (2022–2025) × 1 rincian = 152 sel yang diharapkan. Observasi provinsi = 148; celah = 152 − 148 = **4 sel**, yaitu kode 9200, 9500, 9600, 9700 pada 2022. | Pertahankan observasi sumber; ketiadaan dicatat dan tidak diimputasi. | — |
| 4 | Celah panel dan rincian tidak penuh — var1477 | Dari Silver: 34 provinsi × 3 tahun (2016–2018) × 10 rincian = 1.020 sel yang diharapkan. Observasi = 918; celah = 1.020 − 918 = **102 sel**. Audit menghitung **68 kombinasi wilayah-tahun** tidak lengkap: 34 kombinasi memiliki 9 rincian pada 2017 dan 34 kombinasi memiliki 8 rincian pada 2018. Empat kode 9200, 9500, 9600, 9700 tidak muncul pada seri ini. | Pertahankan rincian dan observasi sumber; celah panel dicatat tanpa imputasi. Daftar rinci wilayah-tahun tersedia di `audit_profil.txt`. | — |
| 5 | Rincian nasional var1477 tidak lengkap | Silver memuat **8 baris nasional**, seluruhnya pada 2018. Dari 10 rincian yang ada pada seri provinsi, rincian nasional yang tidak tersedia adalah “Ahli Teknologi Laboratorium Medik” dan “Pekarya”. | Rekonsiliasi nasional dibatasi pada rincian dan periode yang tersedia; rincian yang tidak tersedia tidak diimputasi. | — |
| 6 | Satuan var1477 tidak eksplisit pada CSV mentah dan pemetaan katalog | Catatan K-002 menyatakan satuan ditetapkan sebagai kepadatan per 100.000 penduduk berdasarkan metadata BPS; nilai Silver menyimpan satuan `kepadatan per 100.000 penduduk`. Ini bukan jumlah orang absolut. | Gunakan satuan kepadatan secara konsisten; konversi ke per 10.000 hanya untuk pasangan yang memang definisinya sebanding. | K-002 |
| 7 | Celah dan perubahan pada seri pembanding WHO | Dari Silver nasional: FINPROTECTION 20 observasi (1999–2021), tahun hilang 2000, 2003, 2008; HWF_0001 13 observasi (1993–2023), 18 tahun hilang; HWF_0006 13 observasi (1992–2023), 19 tahun hilang; UHC 24 observasi (2000–2023), tanpa tahun hilang dalam rentang. HWF_0006 berubah dari 30,89 (2018) menjadi 37,81 (2019), selisih 6,92 atau 22,40%. Daftar tahun hilang tersedia di `audit_profil.txt`. | Pertahankan observasi yang tersedia. Perubahan HWF_0006 ditandai sebagai indikasi yang perlu diperiksa terhadap metadata, bukan otomatis kesalahan atau patahan definisi. | — |
| 8 | Disagregasi pembanding dan keterbandingan definisi | Silver nasional memuat 20 observasi FINPROTECTION setelah pemilihan dimensi TOTAL. Pasangan var1402–UHC dan var2279–FINPROTECTION berkaitan secara konteks, tetapi konstruk/definisinya berbeda. Jumlah baris mentah dan jumlah kombinasi dimensi sebelum filter tidak dihitung ulang dari Silver karena `data/raw/` dikecualikan oleh `.gitignore`. | Filter TOTAL sebagaimana dicatat dalam skrip pemuat; pasangan dengan konsep terkait tetapi definisi berbeda dilaporkan sebagai kontekstual, bukan disetarakan. | K-004 |
| 9 | Duplikat dan format periode | Pemeriksaan kunci Silver (`sumber`, `seri_kode`, `wilayah_kode`, `periode`, `rincian`, `_berkas_raw`) menghasilkan **0 duplikat** dari 1.541 baris. Seri yang dimuat menggunakan `jenis_periode=tahun`. | Pertahankan pemeriksaan kunci dan representasi periode tahun pada pemuatan. | — |
| 10 | Rentang nilai yang perlu ditinjau | Profil Silver: var1477 = 0–377 kepadatan per 100.000 penduduk; var1402 = 1,39–10,21 persen; var2279 = 53,49–98,18 persen. Rentang lebar merupakan sinyal untuk pemeriksaan substantif, bukan bukti tunggal bahwa nilai salah. | Nilai dipertahankan; pemeriksaan outlier dan kewajaran substantif dilakukan pada tahap validasi/analisis berikutnya. | — |

**Batas keterlacakan sumber mentah:** `data/raw/` dikecualikan oleh `.gitignore`. Karena itu, angka jumlah baris mentah FINPROTECTION dan jumlah kombinasi dimensinya sebelum filter tidak dicantumkan sebagai angka yang dapat ditarik ulang dari artefak commit. Bukti angka yang digunakan pada tabel di atas berasal dari Silver yang di-commit atau keputusan yang tercatat di `log-keputusan.csv`.

**Keterlacakan:** jalankan `python sprint/sprint-1/capstone/audit_profil.py`. Skrip membaca `data/silver/silver.csv` dan menghasilkan `sprint/sprint-1/capstone/audit_profil.txt`; skrip tidak bergantung pada data mentah yang diabaikan Git.

## Integrasi dan rekonsiliasi
Seri utama vs pembanding nasional: selisih, penjelasannya (definisi, metode, vintage, granularitas),
dan hasil analisis revisi dari arsip WDI.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
