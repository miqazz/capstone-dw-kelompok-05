"""Tahap 8 — Validasi ringan untuk Sprint 2."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.common.skema import periksa_silver
from src.common.manifest import baca

ROOT = Path(__file__).resolve().parents[2]


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

    # rekonsiliasi harus punya kategori
    if rekon["kategori_selisih"].isna().any() or (rekon["kategori_selisih"] == "").any():
        raise ValueError("Ada baris rekonsiliasi tanpa kategori_selisih")
    # selisih tidak dipaksa sama - hanya cek kolom ada
    _ = rekon["selisih"]

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "validasi.md").write_text(
        "# Validasi\n\n"
        f"- Silver lolos skema minimal: {len(silver)} baris\n"
        f"- Gold panel_provinsi: {len(panel)} baris\n"
        f"- Gold nasional_periode_seri: {len(nasional)} baris\n"
        f"- Rekonsiliasi_nasional: {len(rekon)} baris\n"
        "- Semua baris rekonsiliasi memiliki kategori.\n",
        encoding="utf-8",
    )
    return {"silver_ok": True, "rows": {k: len(v) for k, v in gold.items()}}
