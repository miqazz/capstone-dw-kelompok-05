
"""Tahap 2-4 - Profil, pembersihan, dan penyeragaman ke Silver."""

from pathlib import Path
import pandas as pd
from src.common.skema import KOLOM, KUNCI

JALUR_SILVER = Path("data/silver/silver.parquet")

SERI_BPS = ["var1402", "var1477", "var2279"]


def jalankan(mentah):
    """Mengolah data BPS hasil ekstraksi ke format Silver."""

    nama_berkas = [
        "bps_csv_sdg3_3_8_1_a_v1402",
        "bps_csv_sdg3_3_8_2_a_v2279",
        "bps_csv_sdg3_3_c_1_v1477",
    ]

    data = []

    for nama in nama_berkas:
        df = mentah.get(nama)

        if df is None:
            raise ValueError(
                f"Data hasil ekstraksi tidak ditemukan: {nama}"
            )

        data.append(df.copy())

    # Menggabungkan seluruh data BPS.
    df = pd.concat(data, ignore_index=True)

    # Menghapus kolom label periode.
    # Tahun observasi sudah tersedia pada kolom tahun.
    df = df.drop(columns=["periode"])

    # Memetakan kolom CSV BPS ke skema Silver.
    df = df.rename(columns={
        "var_id": "seri_kode",
        "wilayah_id": "wilayah_kode",
        "wilayah": "nama_wilayah",
        "turvar": "rincian",
        "tahun": "periode",
    })

    # Menyeragamkan kode seri.
    df["seri_kode"] = (
        "var" + df["seri_kode"].astype(str)
    )

    # Memilih tiga seri BPS yang digunakan.
    df = df[df["seri_kode"].isin(SERI_BPS)].copy()

    # Melengkapi informasi sumber dan jenis periode.
    df["sumber"] = "bps"
    df["jenis_periode"] = "tahun"

    # Menyeragamkan tipe data.
    df["wilayah_kode"] = pd.to_numeric(
        df["wilayah_kode"], errors="raise"
    ).astype("int64")

    df["periode"] = df["periode"].astype(str)

    df["nilai"] = pd.to_numeric(
        df["nilai"], errors="coerce"
    )

    if df["nilai"].isna().any():
        raise ValueError(
            "Terdapat nilai observasi yang kosong atau tidak numerik."
        )

    # Mempertahankan label rincian asli dari BPS.
    df["rincian"] = (
        df["rincian"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["nama_wilayah"] = (
        df["nama_wilayah"]
        .astype(str)
        .str.strip()
    )

    # Menyeragamkan satuan dari CSV BPS.
    df["satuan"] = (
        df["satuan"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Melengkapi satuan var1477 berdasarkan catatan metadata BPS.
    df.loc[
        df["seri_kode"] == "var1477",
        "satuan"
    ] = "per_100000_penduduk"

    # Mempertahankan informasi lineage.
    df["_berkas_raw"] = df["_berkas_raw"].astype(str)
    df["_sha256_raw"] = df["_sha256_raw"].astype(str)

    # Memilih kolom sesuai skema Silver.
    df = df[KOLOM].copy()

    # Memastikan tidak ada duplikasi kunci Silver.
    if df.duplicated(subset=KUNCI).any():
        raise ValueError(
            "Ditemukan duplikasi pada kunci Silver."
        )

    # Mengurutkan data agar hasil konsisten.
    df = df.sort_values(
        by=["seri_kode", "wilayah_kode", "periode", "rincian"]
    ).reset_index(drop=True)

    # Menyimpan hasil Silver.
    JALUR_SILVER.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(JALUR_SILVER, index=False)

    print(f"Silver berhasil disimpan: {JALUR_SILVER}")
    print(f"Jumlah baris Silver: {len(df)}")

    return df
