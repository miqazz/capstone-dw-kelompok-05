"""Tahap 8 — Validasi ringan untuk Sprint 2."""
from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

from src.common.skema import periksa_silver
from src.common.manifest import baca

ROOT = Path(__file__).resolve().parents[2]


def _hitung_sql() -> dict[str, int]:
    con_s = sqlite3.connect(ROOT / "data/silver/silver.sqlite")
    con_g = sqlite3.connect(ROOT / "data/gold/gold.sqlite")
    try:
        return {
            "silver": con_s.execute("SELECT COUNT(*) FROM silver").fetchone()[0],
            "gold_panel_provinsi": con_g.execute("SELECT COUNT(*) FROM gold_panel_provinsi").fetchone()[0],
            "gold_nasional_periode_seri": con_g.execute("SELECT COUNT(*) FROM gold_nasional_periode_seri").fetchone()[0],
            "rekonsiliasi_nasional": con_g.execute("SELECT COUNT(*) FROM rekonsiliasi_nasional").fetchone()[0],
        }
    finally:
        con_s.close()
        con_g.close()


def jalankan(silver: pd.DataFrame, gold: dict[str, pd.DataFrame]):
    manifest = baca()
    salah = periksa_silver(silver, manifest)
    if salah:
        raise ValueError("Validasi Silver gagal: " + "; ".join(salah))

    panel = gold["panel_provinsi"]
    nasional = gold["nasional_periode_seri"]
    rekon = gold["rekonsiliasi_nasional"]

    # cek baris SQL vs output parquet/csv dilakukan saat simpan; ini cek konsistensi dasar
    for nama, df in {"panel_provinsi": panel, "nasional_periode_seri": nasional, "rekonsiliasi_nasional": rekon}.items():
        if df.empty:
            raise ValueError(f"Tabel gold kosong: {nama}")

    if rekon["kategori_selisih"].isna().any() or (rekon["kategori_selisih"] == "").any():
        raise ValueError("Ada baris rekonsiliasi tanpa kategori_selisih")
    boleh = {"definisi berbeda", "metode berbeda", "vintage berbeda", "cakupan berbeda", "belum terjelaskan"}
    asing = set(rekon["kategori_selisih"].dropna().astype(str)) - boleh
    if asing:
        raise ValueError(f"Kategori rekonsiliasi tidak dikenal: {sorted(asing)}")
    belum = rekon[rekon["kategori_selisih"] == "belum terjelaskan"]
    for kolom in ["penjelasan", "bukti_dicari"]:
        kosong = belum[kolom].isna() | belum[kolom].astype(str).str.strip().eq("")
        if kosong.any():
            raise ValueError(f"Kategori 'belum terjelaskan' wajib punya {kolom}: {int(kosong.sum())} baris kosong")
    _ = rekon["selisih"]

    sql_counts = _hitung_sql()
    parquet_counts = {
        "silver": len(pd.read_parquet(ROOT / "data/silver/silver.parquet")),
        "gold_panel_provinsi": len(pd.read_parquet(ROOT / "data/gold/panel_provinsi.parquet")),
        "gold_nasional_periode_seri": len(pd.read_parquet(ROOT / "data/gold/nasional_periode_seri.parquet")),
        "rekonsiliasi_nasional": len(pd.read_parquet(ROOT / "data/gold/rekonsiliasi_nasional.parquet")),
    }
    for k, sql_n in sql_counts.items():
        pq_n = parquet_counts[k]
        if sql_n != pq_n:
            raise ValueError(f"Baris SQL vs Parquet tidak sama untuk {k}: SQL={sql_n}, Parquet={pq_n}")

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    lines = [
        "# Validasi", "",
        f"- Silver lolos skema minimal: {len(silver)} baris",
        f"- Gold panel_provinsi: {len(panel)} baris",
        f"- Gold nasional_periode_seri: {len(nasional)} baris",
        f"- Rekonsiliasi_nasional: {len(rekon)} baris",
        "- Semua baris rekonsiliasi memiliki kategori.",
        f"- Baris 'belum terjelaskan' memiliki penjelasan dan bukti_dicari: {len(belum)} baris",
        "", "## SQL vs Parquet", "",
        "| Tabel | SQL | Parquet | Status |", "|---|---:|---:|---|",
    ]
    for k in ["silver", "gold_panel_provinsi", "gold_nasional_periode_seri", "rekonsiliasi_nasional"]:
        lines.append(f"| {k} | {sql_counts[k]} | {parquet_counts[k]} | {'sama' if sql_counts[k] == parquet_counts[k] else 'beda'} |")
    (reports / "validasi.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"silver_ok": True, "rows": {k: len(v) for k, v in gold.items()}}
