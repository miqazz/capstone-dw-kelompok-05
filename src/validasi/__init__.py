"""Tahap 8 - Validasi dan dokumentasi (pertemuan XIV-XV). Milik tim."""

import os
import pandas as pd
import pandera.pandas as pa

# 1. Kamus 10 profesi resmi pada seri var1477 (sesuaikan juga di docs/data-dictionary.md)
PROFESI_VALID = [
    "Ahli Teknologi Laboratorium Medik",
    "Bidan",
    "Dokter Gigi",
    "Dokter Umum",
    "Farmasi",
    "Gizi",
    "Kesehatan Lingkungan",
    "Kesehatan Masyarakat",
    "Pekarya",
    "Perawat",
]

# Satuan kepadatan yang diakui (harus seragam satu satuan dalam seri kepadatan)
SATUAN_KEPADATAN_VALID = [
    "per_1000_penduduk",
    "per_10000_penduduk",
    "per_100000_penduduk",
]

KODE_VAR1477 = ["var1477", "1477"]


def _cek_rentang_persen(df: pd.DataFrame) -> bool:
    sub = df[df["satuan"].isin(["persen", "%"])]
    if sub.empty:
        return True
    return bool(sub["nilai"].dropna().between(0, 100).all())


def _cek_profesi_var1477(df: pd.DataFrame) -> bool:
    sub = df[df["seri_kode"].isin(KODE_VAR1477)]
    if sub.empty:
        return True
    return bool(sub["rincian"].isin(PROFESI_VALID).all())


def _cek_satuan_kepadatan_seragam(df: pd.DataFrame) -> bool:
    sub = df[df["seri_kode"].isin(KODE_VAR1477)]
    if sub.empty:
        return True
    # Semua baris harus memakai satuan kepadatan baku DAN hanya ada 1 satuan (seragam)
    return bool(
        sub["satuan"].isin(SATUAN_KEPADATAN_VALID).all()
        and sub["satuan"].nunique() == 1
    )


skema_silver = pa.DataFrameSchema(
    columns={
        "seri_kode": pa.Column(str),
        "nilai": pa.Column(float, nullable=True),
        "satuan": pa.Column(str),
        "rincian": pa.Column(str),
    },
    checks=[
        pa.Check(_cek_rentang_persen, name="Rentang Nilai Persen (0-100)"),
        pa.Check(_cek_profesi_var1477, name="Kesesuaian Kamus Profesi (var1477)"),
        pa.Check(_cek_satuan_kepadatan_seragam, name="Keseragaman Satuan Kepadatan"),
    ],
)


def jalankan(silver, gold):
    print("--- Memulai Validasi Lapis Silver ---")
    os.makedirs("reports", exist_ok=True)

    df_silver = pd.read_parquet(silver) if isinstance(silver, str) else silver
    if df_silver is None or df_silver.empty:
        print("⚠️ Data Silver kosong. Melewati validasi.")
        return pd.DataFrame()

    gagal_umum = pd.DataFrame()
    aturan_gagal = []

    try:
        skema_silver.validate(df_silver, lazy=True)
    except pa.errors.SchemaErrors as e:
        gagal_umum = e.failure_cases[["column", "check", "failure_case", "index"]]
        aturan_gagal = gagal_umum["check"].unique().tolist()

    hasil = []
    for cek in skema_silver.checks:
        nama_aturan = cek.name
        hasil.append({
            "Aturan": nama_aturan,
            "Jenis": "Keras (Umum)",
            "Hasil": "GAGAL" if nama_aturan in aturan_gagal else "LOLOS",
        })
    tabel_ringkasan = pd.DataFrame(hasil)

    laporan = [
        "# Hasil Validasi Silver (Kasus 05)",
        "Dihasilkan otomatis oleh `python pipeline.py`.\n",
        "## Ringkasan Aturan",
        tabel_ringkasan.to_markdown(index=False),
        "\n## Rincian Kegagalan",
    ]

    if not gagal_umum.empty:
        laporan.append(gagal_umum.head(50).to_markdown(index=False))
    else:
        laporan.append("✅ *Tidak ada. Semua aturan lolos.*")

    with open("reports/validasi.md", "w", encoding="utf-8") as f:
        f.write("\n\n".join(laporan))

    if not gagal_umum.empty:
        raise SystemExit(
            f"❌ Validasi GAGAL pada aturan: {', '.join(aturan_gagal)}. "
            "Rincian lihat di reports/validasi.md"
        )

    print("✅ Validasi Silver lolos 100%. Laporan dicetak ke reports/validasi.md")
    return tabel_ringkasan