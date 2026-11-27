# AI_LOG — <Nama tim>

Satu baris per pemakaian AI yang bermakna (ChatGPT, Claude, Copilot, Bravais, dan sejenisnya).
Ringkas dan jujur; transkrip penuh tidak diminta. Yang dinilai bukan "pakai AI atau tidak",
melainkan "mengerti atau tidak" — isi kolom terakhir dengan apa yang Anda ubah dari keluarannya.

| Tanggal | Siapa (NIM) | Alat | Untuk apa | Apa yang diubah dari keluarannya |
|---|---|---|---|---|
| 2026-11-16 | 124450011 | Gemini | Merancang penyatuan ekstraksi data mentah BPS dan WHO GHO (Sprint 1 - PR #5) | Menyesuaikan pemetaan kode wilayah dan penggabungan kolom dimensi WHO (`DIM_*`) agar selaras dengan `MANIFEST.csv` |
| 2026-11-18 | 124450011 | Gemini | Menyusun draf transformasi skema Silver dan kerangka `docs/data-dictionary.md` (Sprint 1 - PR #6 & #7) | Memperbaiki daftar nilai unik `rincian`, tipe data kolom, dan pembacaan satuan dari metadata JSON agar lolos `src.common.skema` |
| 2026-11-21 | 124450011 | Gemini | Merancang aturan validasi dasar Silver di `src/validasi/` untuk rentang persen dan satuan `var1477` (Sprint 1) | Menambahkan validasi kamus 10 profesi pada `var1477` dan menyesuaikan argumen `results/124450011/metrics.json` |
| 2026-11-24 | 124450011 | Gemini | Mengintegrasikan aturan validasi Gold & kategori rekonsiliasi V4 dengan kode tim di `src/validasi/__init__.py` (Sprint 2 - #25) | Mempertahankan cek SQL vs Parquet serta aturan `kategori_selisih` dan `belum terjelaskan` dari rekan tim lalu menggabungkannya dengan aturan #25 |
| 2026-11-25 | 124450011 | Gemini | *Debugging* kegagalan aturan satuan `var1477` dan duplikasi kunci `panel_provinsi` pada data terbaru (Sprint 2 - #25) | Mengubah target satuan `var1477` menjadi `'kepadatan per 100.000 penduduk'` dan memperluas kunci unik `panel_provinsi` menjadi `['seri_kode', 'wilayah_kode', 'periode', 'rincian']` |
