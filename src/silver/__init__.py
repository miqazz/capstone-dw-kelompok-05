
"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver."""

from pathlib import Path
import pandas as pd
from src.common.skema import KOLOM, KUNCI

JALUR_SILVER = Path("data/silver/silver.parquet")
SERI_BPS = [1402, 1477, 2279]


def jalankan(mentah):
    if "bps_csv" not in mentah:
        raise ValueError("Data hasil ekstraksi BPS CSV tidak ditemukan.")

    df = mentah["bps_csv"].copy()

    # Mengambil tiga seri BPS yang digunakan.
    df = df[df["seri_kode"].isin(SERI_BPS)].copy()

    # Penyeragaman tipe data.
    df["sumber"] = df["sumber"].astype(str)
    df["seri_kode"] = df["seri_kode"].astype(str)
    df["wilayah_kode"] = pd.to_numeric(
        df["wilayah_kode"], errors="raise"
    ).astype("int64")
    df["nama_wilayah"] = df["nama_wilayah"].astype(str)
    df["periode"] = df["periode"].astype(str)
    df["jenis_periode"] = "tahun"
    df["rincian"] = df["rincian"].astype(str)
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")

    # Membersihkan satuan tanpa mengarang nilai yang tidak tersedia.
    df["satuan"] = (
        df["satuan"]
        .replace(["nan", "NaN", "None"], "")
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["_berkas_raw"] = df["_berkas_raw"].astype(str)
    df["_sha256_raw"] = df["_sha256_raw"].astype(str)

    # Menyesuaikan urutan kolom dengan skema baku.
    df = df[KOLOM].copy()

    # Memastikan tidak ada nilai numerik yang gagal dikonversi.
    if df["nilai"].isna().any():
        raise ValueError("Terdapat nilai observasi yang kosong atau tidak numerik.")

    # Memastikan kunci Silver unik.
    if df.duplicated(subset=KUNCI).any():
        raise ValueError("Ditemukan duplikasi pada kunci Silver.")

    # Mengurutkan data agar konsisten.
    df = df.sort_values(
        by=["seri_kode", "wilayah_kode", "periode", "rincian"]
    ).reset_index(drop=True)

    # Menyimpan hasil Silver.
    JALUR_SILVER.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(JALUR_SILVER, index=False)

    print(f"Silver berhasil disimpan: {JALUR_SILVER}")
    print(f"Jumlah baris Silver: {len(df)}")

    return df
