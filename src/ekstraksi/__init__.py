"""Tahap 1 — Ekstraksi (pertemuan X)."""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw

ROOT = Path(__file__).resolve().parents[2]


def _rel(path: Path) -> str:
    return path.resolve().relative_to(RAW.resolve()).as_posix()


def _baca_bps_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["_berkas_raw"] = _rel(path)
    df["_sha256_raw"] = sha256_raw(df["_berkas_raw"].iloc[0])
    return df


def _baca_who_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["_berkas_raw"] = _rel(path)
    df["_sha256_raw"] = sha256_raw(df["_berkas_raw"].iloc[0])
    return df


def jalankan() -> dict[str, pd.DataFrame]:
    """Kembalikan {nama_sumber: DataFrame mentah}."""
    hasil = {}
    peta = {
        "bps_var1402": RAW / "bps/2026-10-20/sdg3_3_8_1_a_v1402.csv",
        "bps_var2279": RAW / "bps/2026-10-20/sdg3_3_8_2_a_v2279.csv",
        "bps_var1477": RAW / "bps/2026-10-20/sdg3_3_c_1_v1477.csv",
        "who_hwf_0001": RAW / "who_gho/2026-10-20/datadot/217795A_HWF_0001.csv",
        "who_hwf_0006": RAW / "who_gho/2026-10-20/datadot/5C8435F_HWF_0006.csv",
        "who_uhc": RAW / "who_gho/2026-10-20/datadot/9A706FD_UHC_INDEX_REPORTED.csv",
        "who_finprot": RAW / "who_gho/2026-10-20/datadot/A65146D_FINPROTECTION_CATA_TOT_10_POP.csv",
    }
    for nama, path in peta.items():
        if not path.exists():
            raise FileNotFoundError(f"Berkas mentah tidak ditemukan: {path}")
        df = _baca_bps_csv(path) if "bps_" in nama else _baca_who_csv(path)
        hasil[nama] = df
    return hasil
