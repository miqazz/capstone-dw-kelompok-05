# Alasan Pilihan Basis Data untuk Silver (Tahap 5, draf laporan tim)

**Konteks:** Silver pertama dimuat dari 13 berkas mentah (BPS & WHO, kasus 05) menjadi 1.541 baris ber-skema minimal (`sumber, seri_kode, wilayah_kode, nama_wilayah, periode, jenis_periode, rincian, nilai, satuan, _berkas_raw, _sha256_raw`) dengan kunci unik `(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)`.

## Pilihan: SQLite (`data/silver/silver.sqlite`)

- **Tanpa konfigurasi & portabel:** berbasis satu berkas, tidak memerlukan server; mudah direproduksi dan dibagikan dalam repo (ukuran Silver pertama ~568 KB) serta dijalankan di lingkungan Windows/Linux/WSL.
- **Skema & integritas eksplisit:** mendukung tipe kolom, `PRIMARY KEY`, `CHECK` (mis. `jenis_periode`, panjang `_sha256_raw`), dan indeks; sesuai kebutuhan Silver yang tabular dan ter-standar.
- **Reproducible & tanpa dependensi tambahan:** pemuatan memakai modul standar Python `sqlite3` (`sprint/sprint-1/capstone/muat_silver_pertama.py` + `sprint/sprint-1/capstone/silver_ddl.sql`), sehingga tidak bergantung paket eksternal di tahap awal.
- **Kueri analitis langsung:** memudahkan agregasi, filter, join lintas seri, dan audit lineage (`_berkas_raw`, `_sha256_raw`) untuk profil/validasi.
- **Kecukupan skala:** volume Silver kasus ini kecil (ribuan baris); SQLite memadai. Bila skala/konkurensi meningkat, skema dapat dipindahkan ke PostgreSQL/DuckDB dengan perubahan minimal.

## Perbandingan singkat: SQLite (tabel relasional) vs respons JSON mentah sebagai dokumen

| Aspek | Respons JSON mentah sebagai dokumen (arsip/bronze) | Silver di SQLite (tabel relasional) |
|---|---|---|
| Bentuk & kelengkapan | Mempertahankan struktur asli/bersarang dan metadata sumber (mis. WebAPI BPS: `var/turvar/vervar/tahun/datacontent`, definisi/katalog WHO) — baik untuk provenance & audit. | Bentuk tabular ter-normalisasi ke skema seragam; field konteks diringkas ke kolom baku. |
| Fleksibilitas skema | Fleksibel/schema-on-read; mudah menyimpan variasi respons apa adanya. | Schema-on-write; memaksa konsistensi tipe, domain, dan kunci unik. |
| Kueri & integrasi | Perlu parsing/ekstraksi per struktur; agregasi/join lintas berkas lebih rumit. | SQL standar untuk filter, join, agregasi, dan pemeriksaan integritas. |
| Validasi & kualitas | Sulit menegakkan constraint (unik, tipe, domain) secara deklaratif. | PK/CHECK/tipe menahan duplikat dan nilai tak sah sejak muat. |
| Skalabilitas | Dokumen besar/bersarang bisa boros diproses berulang; baik sebagai penyimpanan mentah. | Efisien untuk data terstruktur berukuran kecil–menengah; indeks mempercepat akses. |
| Peran dalam pipeline | **Bronze/dokumen mentah** (`data/raw/`, tidak diubah) sebagai rujukan asal. | **Silver** terstruktur siap profil, pembersihan, dan integrasi ke Gold. |

**Kesimpulan:** JSON mentah disimpan sebagai dokumen untuk menjaga kesetiaan dan keterlacakan sumber, sedangkan SQLite dipilih untuk Silver agar data rapi, tervalidasi secara skema, dan mudah diolah/diulang. Keduanya saling melengkapi dalam arsitektur bronze–silver.
