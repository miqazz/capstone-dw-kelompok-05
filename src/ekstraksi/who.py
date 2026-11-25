
"""Pembaca data WHO GHO untuk Kasus 05."""

import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw


FOLDER_WHO = Path(RAW) / "who_gho"

NAMA_CSV = [
    "217795A_HWF_0001.csv",
    "5C8435F_HWF_0006.csv",
    "9A706FD_UHC_INDEX_REPORTED.csv",
    "A65146D_FINPROTECTION_CATA_TOT_10_POP.csv",
]

NAMA_JSON = [
    "ddiindicators_skip0000.json",
    "Indicator.json",
]


def _cari_berkas(nama):
    """Mencari berkas WHO berdasarkan nama."""
    hasil = list(FOLDER_WHO.rglob(nama))

    if len(hasil) != 1:
        raise FileNotFoundError(
            f"Berkas {nama} tidak ditemukan atau ditemukan lebih dari satu."
        )

    return hasil[0]


def _tempel_lineage(df, path):
    """Menambahkan nama berkas asal dan SHA256."""
    berkas = path.relative_to(Path(RAW)).as_posix()

    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas)

    return df


def baca_csv(path):
    """Membaca CSV WHO tanpa membersihkan nilai dimensinya."""
    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False
    )

    return _tempel_lineage(df, path)


def baca_json(path):
    """Membaca metadata indikator WHO dari bagian value JSON."""
    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "value" not in data:
        raise ValueError(f"Struktur JSON tidak sesuai: {path.name}")

    df = pd.DataFrame(data["value"])

    return _tempel_lineage(df, path)

def cetak_hasil_uji(nama, df):
    """Menampilkan jumlah baris dan pemeriksaan kolom lineage."""
    kolom_lineage = ["_berkas_raw", "_sha256_raw"]

    kolom_ada = [kolom for kolom in kolom_lineage if kolom in df.columns]

    print(f"\nBerkas: {nama}")
    print(f"Jumlah baris: {len(df)}")
    print(f"Jumlah kolom lineage: {len(kolom_ada)}/2")

    for kolom in kolom_lineage:
        if kolom in df.columns:
            kosong = (
                df[kolom].isna()
                | df[kolom].astype(str).str.strip().eq("")
            ).sum()

            print(f"{kolom}: ADA | Kosong: {kosong}")
        else:
            print(f"{kolom}: TIDAK ADA")

def jalankan():
    """Membaca seluruh empat CSV dan dua JSON WHO."""
    hasil = {}

    for nama in NAMA_CSV:
        path = _cari_berkas(nama)
        df = baca_csv(path)
        hasil[path.stem] = df

        cetak_hasil_uji(nama, df)

    for nama in NAMA_JSON:
        path = _cari_berkas(nama)
        df = baca_json(path)
        hasil[path.stem] = df

        cetak_hasil_uji(nama, df)

    print("\nRINGKASAN WHO")
    print("Total berkas:", len(hasil))
    print("Total baris:", sum(len(df) for df in hasil.values()))

    return hasil
