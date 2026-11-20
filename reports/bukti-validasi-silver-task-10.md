# Bukti Validasi Artefak Silver — Task #10

## 1. Identitas Pemeriksaan

- Artefak: `data/silver/silver.parquet`
- Seri yang diperiksa: `var1477`
- Commit transformasi: `7f677b1`
- File transformasi: `src/silver/__init__.py`
- Metadata acuan: `data/raw/bps/2026-10-20/json/sdg3_3_c_1_v1477.json`

## 2. Hasil Uji Skema

Perintah validasi:

```bash
python -m src.common.skema data/silver/silver.parquet
```

Hasil:

```text
LOLOS  1,471 baris, 3 seri, 39 wilayah, 3 berkas sumber
```

## 3. Sampel Baris Artefak Silver

Sampel observasi `var1477` untuk wilayah Aceh tahun 2016:

| Wilayah | Periode | Rincian tenaga kesehatan | Nilai | Satuan |
|---|---:|---|---:|---|
| Aceh | 2016 | Ahli Teknologi Laboratorium Medik | 13.0 | per_100000_penduduk |
| Aceh | 2016 | Bidan | 124.0 | per_100000_penduduk |
| Aceh | 2016 | Dokter Gigi | 6.0 | per_100000_penduduk |
| Aceh | 2016 | Dokter Umum | 31.0 | per_100000_penduduk |
| Aceh | 2016 | Farmasi | 23.0 | per_100000_penduduk |
| Aceh | 2016 | Gizi | 15.0 | per_100000_penduduk |
| Aceh | 2016 | Kesehatan Lingkungan | 17.0 | per_100000_penduduk |
| Aceh | 2016 | Kesehatan Masyarakat | 63.0 | per_100000_penduduk |
| Aceh | 2016 | Pekarya | 0.0 | per_100000_penduduk |
| Aceh | 2016 | Perawat | 168.0 | per_100000_penduduk |

Jumlah observasi `var1477`: **926 baris**.

## 4. Rekap Kategori Tenaga Kesehatan

| Kategori | Jumlah baris |
|---|---:|
| Ahli Teknologi Laboratorium Medik | 68 |
| Bidan | 103 |
| Dokter Gigi | 103 |
| Dokter Umum | 103 |
| Farmasi | 103 |
| Gizi | 103 |
| Kesehatan Lingkungan | 103 |
| Kesehatan Masyarakat | 103 |
| Pekarya | 34 |
| Perawat | 103 |
| **Total** | **926** |

Kesepuluh nama kategori tersebut sesuai dengan label `turvar` pada metadata JSON BPS.

## 5. Dasar Penetapan Satuan

Metadata JSON BPS untuk variabel `1477` memuat:

- Nama variabel: `Kepadatan Dan Distribusi Tenaga Kesehatan`.
- Kolom `unit`: kosong.
- Kolom `note`: mencantumkan sumber Informasi SDM Kesehatan Badan PPSDM Kesehatan, Kementerian Kesehatan RI, serta keterangan `(per 100.000 penduduk)`.

Dengan demikian, satuan `per_100000_penduduk` pada artefak Silver ditetapkan berdasarkan keterangan pada `note` metadata BPS, bukan dari kolom `unit` yang kosong.

## 6. Kesimpulan

Hasil validasi menunjukkan artefak Silver memiliki 1.471 baris, 3 seri, 39 wilayah, dan 3 berkas sumber.

Pemeriksaan `var1477` menunjukkan 926 observasi dengan satuan `per_100000_penduduk`. Sepuluh kategori tenaga kesehatan yang tersimpan sesuai dengan label kategori pada metadata BPS.

Pemeriksaan ini mendokumentasikan kesesuaian struktur, satuan, dan rincian kategori terhadap metadata yang tersedia. Dasar penetapan satuan secara eksplisit adalah keterangan pada `note`.
