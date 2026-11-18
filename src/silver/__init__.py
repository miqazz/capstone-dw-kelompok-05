"""Tahap 2-4 - Profil, pembersihan, dan penyeragaman ke Silver."""

from pathlib import Path
import pandas as pd
from src.common.skema import KOLOM, KUNCI

JALUR_SILVER = Path("data/silver/silver.parquet")
SERI_BPS = ["var1402", "var1477", "var2279"]

def jalankan(mentah):
    # 1. Mengambil data JSON BPS (strukturnya sudah pasti dan rapi dari tahap ekstraksi)
    df1 = mentah.get("bps_json_sdg3_3_8_1_a_v1402")
    df2 = mentah.get("bps_json_sdg3_3_8_2_a_v2279")
    df3 = mentah.get("bps_json_sdg3_3_c_1_v1477")
    
    if df1 is None or df2 is None or df3 is None:
        raise ValueError("Data hasil ekstraksi BPS JSON tidak ditemukan. Ekstraksi gagal.")
    
    df = pd.concat([df1, df2, df3], ignore_index=True)
    
    # 2. RENAME KOLOM BPS -> Silver (Ini solusi untuk mengatasi KeyError!)
    df = df.rename(columns={
        "var_val": "seri_kode",
        "vervar_val": "wilayah_kode",
        "turvar_val": "rincian",
        "tahun_val": "periode",
        "vervar_label": "nama_wilayah"
    })
# 3. Format dan lengkapi kolom wajib Silver
    df["sumber"] = "bps"
    df["jenis_periode"] = "tahunan"
    
    # Pastikan format seri_kode menjadi 'var1402', dst.
    df["seri_kode"] = df["seri_kode"].astype(str)
    df["seri_kode"] = "var" + df["seri_kode"].str.replace("var", "", regex=False)
    
    # Filter hanya seri BPS yang dibutuhkan
    df = df[df["seri_kode"].isin(SERI_BPS)].copy()
    
    # Menentukan satuan secara otomatis agar lolos validasi Pandera
    df["satuan"] = df["seri_kode"].apply(lambda x: "persen" if x in ["var1402", "var2279"] else "tidak_ada")
    
    # Penyeragaman tipe data
    df["wilayah_kode"] = pd.to_numeric(df["wilayah_kode"], errors="coerce").fillna(0).astype("int64")
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
    df["rincian"] = df["rincian"].astype(str).str.lower().str.replace(" ", "_")
    df["nama_wilayah"] = df["nama_wilayah"].astype(str)
    df["_berkas_raw"] = df["_berkas_raw"].astype(str)
    df["_sha256_raw"] = df["_sha256_raw"].astype(str)
