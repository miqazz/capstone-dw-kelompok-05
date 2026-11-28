"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.common.manifest import sha256_raw

ROOT = Path(__file__).resolve().parents[2]
SILVER_DIR = ROOT / "data" / "silver"
SILVER_CSV = SILVER_DIR / "silver.csv"
SILVER_PARQUET = SILVER_DIR / "silver.parquet"
SILVER_DB = SILVER_DIR / "silver.sqlite"
SILVER_DDL = ROOT / "sql" / "silver.sql"

KOLOM = [
    "sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode",
    "jenis_periode", "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw",
]
KUNCI = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]


def _num(s):
    n = pd.to_numeric(s, errors="coerce")
    return n


def _bersihkan_bps(df: pd.DataFrame, seri_kode: str, satuan_override: str | None = None) -> pd.DataFrame:
    out = pd.DataFrame()
    out["sumber"] = ["bps"] * len(df)
    out["seri_kode"] = seri_kode
    out["wilayah_kode"] = pd.to_numeric(df["wilayah_id"], errors="raise").astype(int)
    out["nama_wilayah"] = df["wilayah"].astype(str).str.strip()
    out["periode"] = df["tahun"].astype(str).str.strip()
    out["jenis_periode"] = df["periode"].astype(str).str.strip().str.lower().map({"tahun": "tahun"}).fillna("tahun")
    rincian = df["turvar"].astype(str).str.strip()
    out["rincian"] = rincian.where(rincian.ne("") & rincian.ne("nan"), "TOTAL")
    out["nilai"] = _num(df["nilai"])
    if satuan_override is not None:
        out["satuan"] = satuan_override
    else:
        satuan = df["satuan"].fillna("").astype(str).str.strip()
        out["satuan"] = satuan.replace({"nan": ""})
    out["_berkas_raw"] = df["_berkas_raw"].astype(str)
    out["_sha256_raw"] = df["_sha256_raw"].astype(str)
    out = out.dropna(subset=["nilai"]).copy()
    out["nilai"] = out["nilai"].astype(float)
    return out[KOLOM]


def _bersihkan_who_hwf(df: pd.DataFrame, seri_kode: str) -> pd.DataFrame:
    d = df[df["DIM_GEO_CODE_M49"].astype(str) == "360"].copy().reset_index(drop=True)
    out = pd.DataFrame({
        "sumber": "who_gho",
        "seri_kode": seri_kode,
        "wilayah_kode": 9999,
        "nama_wilayah": "INDONESIA",
        "periode": d["DIM_TIME"].astype(str).str.strip(),
        "jenis_periode": "tahun",
        "rincian": "TOTAL",
        "nilai": _num(d["RATE_PER_10000_N"]),
        "satuan": "per 10.000 penduduk",
        "_berkas_raw": d["_berkas_raw"].astype(str),
        "_sha256_raw": d["_sha256_raw"].astype(str),
    })
    out = out.dropna(subset=["nilai"]).copy()
    out["nilai"] = out["nilai"].astype(float)
    return out[KOLOM]


def _bersihkan_who_uhc(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["DIM_GEO_CODE_M49"].astype(str) == "360"].copy().reset_index(drop=True)
    out = pd.DataFrame({
        "sumber": "who_gho",
        "seri_kode": "UHC_INDEX_REPORTED",
        "wilayah_kode": 9999,
        "nama_wilayah": "INDONESIA",
        "periode": d["DIM_TIME"].astype(str).str.strip(),
        "jenis_periode": "tahun",
        "rincian": "TOTAL",
        "nilai": _num(d["INDEX_N"]),
        "satuan": "indeks (skor cakupan layanan UHC, 0-100)",
        "_berkas_raw": d["_berkas_raw"].astype(str),
        "_sha256_raw": d["_sha256_raw"].astype(str),
    })
    out = out.dropna(subset=["nilai"]).copy()
    out["nilai"] = out["nilai"].astype(float)
    return out[KOLOM]


def _bersihkan_who_finprot(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["DIM_GEO_CODE_M49"].astype(str) == "360"].copy()
    for col in ["DIM_SEX", "DIM_AGE", "DIM_HOUSEHOLD_COMP_BY_AGE", "DIM_POP_TYPE"]:
        if col in d.columns:
            d = d[d[col].fillna("").astype(str).str.strip().isin(["", "nan"])]
    if "DIM_DEG_URB" in d.columns:
        d = d[d["DIM_DEG_URB"].astype(str).str.strip() == "TOTAL"]
    d = d.reset_index(drop=True)
    out = pd.DataFrame({
        "sumber": "who_gho",
        "seri_kode": "FINPROTECTION_CATA_TOT_10_POP",
        "wilayah_kode": 9999,
        "nama_wilayah": "INDONESIA",
        "periode": d["DIM_TIME"].astype(str).str.strip(),
        "jenis_periode": "tahun",
        "rincian": "TOTAL",
        "nilai": _num(d["PERCENT_POP_N"]),
        "satuan": "persen populasi",
        "_berkas_raw": d["_berkas_raw"].astype(str),
        "_sha256_raw": d["_sha256_raw"].astype(str),
    })
    out = out.dropna(subset=["nilai"]).copy()
    out["nilai"] = out["nilai"].astype(float)
    return out[KOLOM]


def bangun_silver(mentah: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frames = [
        _bersihkan_bps(mentah["bps_var1402"], "var1402"),
        _bersihkan_bps(mentah["bps_var2279"], "var2279"),
        _bersihkan_bps(mentah["bps_var1477"], "var1477", "kepadatan per 100.000 penduduk"),
        _bersihkan_who_hwf(mentah["who_hwf_0001"], "HWF_0001"),
        _bersihkan_who_hwf(mentah["who_hwf_0006"], "HWF_0006"),
        _bersihkan_who_uhc(mentah["who_uhc"]),
        _bersihkan_who_finprot(mentah["who_finprot"]),
    ]
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(KUNCI).reset_index(drop=True)
    # validasi kunci
    dup = df.duplicated(KUNCI).sum()
    if dup:
        raise ValueError(f"Duplikat kunci Silver: {dup}")
    return df[KOLOM]


def simpan_silver(df: pd.DataFrame) -> dict[str, Path]:
    import sqlite3

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SILVER_CSV, index=False, lineterminator="\n")
    df.to_parquet(SILVER_PARQUET, index=False)

    schema = SILVER_DDL.read_text(encoding="utf-8") if SILVER_DDL.exists() else _ddl_default()
    if SILVER_DB.exists():
        SILVER_DB.unlink()
    con = sqlite3.connect(SILVER_DB)
    try:
        con.executescript(schema)
        df.to_sql("silver", con, if_exists="append", index=False)
        con.commit()
        n = con.execute("SELECT COUNT(*) FROM silver").fetchone()[0]
    finally:
        con.close()
    if n != len(df):
        raise ValueError(f"Baris SQLite ({n}) != DataFrame ({len(df)})")
    pq = pd.read_parquet(SILVER_PARQUET)
    if len(pq) != n:
        raise ValueError(f"Baris Parquet silver ({len(pq)}) != SQL ({n})")
    return {"csv": SILVER_CSV, "parquet": SILVER_PARQUET, "sqlite": SILVER_DB}


def _ddl_default() -> str:
    return (ROOT / "sql" / "silver.sql").read_text(encoding="utf-8")


def jalankan(mentah):
    df = bangun_silver(mentah)
    simpan_silver(df)
    return df
