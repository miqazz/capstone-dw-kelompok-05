"""Tahap 8 — Validasi ringan untuk Sprint 2."""
from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

from src.common.skema import periksa_silver
from src.common.manifest import baca
from src.gold import KATEGORI_REKONSILIASI

ROOT = Path(__file__).resolve().parents[2]
VALIDASI_BARIS_CSV = ROOT / "reports" / "validasi_jumlah_baris.csv"
KOLOM_VALIDASI_BARIS = [
    "nama_tabel", "jumlah_baris_parquet", "jumlah_baris_sql", "selisih", "status",
]


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


def _validasi_baris() -> list[dict[str, object]]:
    sql_counts = _hitung_sql()
    parquet_counts = {
        "silver": len(pd.read_parquet(ROOT / "data/silver/silver.parquet")),
        "gold_panel_provinsi": len(pd.read_parquet(ROOT / "data/gold/panel_provinsi.parquet")),
        "gold_nasional_periode_seri": len(pd.read_parquet(ROOT / "data/gold/nasional_periode_seri.parquet")),
        "rekonsiliasi_nasional": len(pd.read_parquet(ROOT / "data/gold/rekonsiliasi_nasional.parquet")),
    }
    baris = []
    for nama in [
        "silver", "gold_panel_provinsi", "gold_nasional_periode_seri", "rekonsiliasi_nasional",
    ]:
        n_sql = int(sql_counts[nama])
        n_parquet = int(parquet_counts[nama])
        selisih = n_sql - n_parquet
        baris.append({
            "nama_tabel": nama,
            "jumlah_baris_parquet": n_parquet,
            "jumlah_baris_sql": n_sql,
            "selisih": selisih,
            "status": "sesuai" if selisih == 0 else "tidak sesuai",
        })
    return baris


def _tulis_dan_tampilkan_validasi_baris(baris: list[dict[str, object]]) -> None:
    VALIDASI_BARIS_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(baris, columns=KOLOM_VALIDASI_BARIS).to_csv(
        VALIDASI_BARIS_CSV, index=False, lineterminator="\n"
    )

    lebar = [max(len(str(kolom)), *(len(str(b[kolom])) for b in baris)) for kolom in KOLOM_VALIDASI_BARIS]
    print("\nValidasi jumlah baris Parquet vs SQL")
    print(" | ".join(str(kolom).ljust(lebar[i]) for i, kolom in enumerate(KOLOM_VALIDASI_BARIS)))
    print("-+-".join("-" * lebar[i] for i in range(len(KOLOM_VALIDASI_BARIS))))
    for b in baris:
        print(" | ".join(str(b[kolom]).ljust(lebar[i]) for i, kolom in enumerate(KOLOM_VALIDASI_BARIS)))
    sesuai = sum(b["status"] == "sesuai" for b in baris)
    print(f"Hasil: {sesuai}/{len(baris)} tabel sesuai. "
          f"Detail: {VALIDASI_BARIS_CSV.relative_to(ROOT).as_posix()}\n")


def jalankan(silver: pd.DataFrame, gold: dict[str, pd.DataFrame]):
    manifest = baca()
    salah = periksa_silver(silver, manifest)
    if salah:
        raise ValueError("Validasi Silver gagal: " + "; ".join(salah))

    baris_validasi = _validasi_baris()
    _tulis_dan_tampilkan_validasi_baris(baris_validasi)
    masalah = [
        f"Baris SQL vs Parquet tidak sama untuk {b['nama_tabel']}: "
        f"SQL={b['jumlah_baris_sql']}, Parquet={b['jumlah_baris_parquet']}"
        for b in baris_validasi if b["status"] != "sesuai"
    ]

    panel = gold["panel_provinsi"]
    nasional = gold["nasional_periode_seri"]
    rekon = gold["rekonsiliasi_nasional"]

    for nama, df in {"panel_provinsi": panel, "nasional_periode_seri": nasional, "rekonsiliasi_nasional": rekon}.items():
        if df.empty:
            masalah.append(f"Tabel gold kosong: {nama}")

    if rekon["kategori_selisih"].isna().any() or (rekon["kategori_selisih"] == "").any():
        masalah.append("Ada baris rekonsiliasi tanpa kategori_selisih")
    boleh = set(KATEGORI_REKONSILIASI)
    asing = set(rekon["kategori_selisih"].dropna().astype(str)) - boleh
    if asing:
        masalah.append(f"Kategori rekonsiliasi tidak dikenal: {sorted(asing)}")
    belum = rekon[rekon["kategori_selisih"] == "belum terjelaskan"]
    for kolom in ["penjelasan", "bukti_dicari"]:
        kosong = belum[kolom].isna() | belum[kolom].astype(str).str.strip().eq("")
        if kosong.any():
            masalah.append(f"Kategori 'belum terjelaskan' wajib punya {kolom}: {int(kosong.sum())} baris kosong")
    _ = rekon["selisih"]

    sesuai = sum(b["status"] == "sesuai" for b in baris_validasi)
    status_baris = "SESUAI" if not masalah and sesuai == len(baris_validasi) else "TIDAK SESUAI"
    lines = [
        "# Validasi", "",
        f"- Silver lolos skema minimal: {len(silver)} baris",
        f"- Gold panel_provinsi: {len(panel)} baris",
        f"- Gold nasional_periode_seri: {len(nasional)} baris",
        f"- Rekonsiliasi_nasional: {len(rekon)} baris",
        "- Semua baris rekonsiliasi memiliki kategori.",
        f"- Baris 'belum terjelaskan' memiliki penjelasan dan bukti_dicari: {len(belum)} baris",
        f"- Validasi jumlah baris: {status_baris} ({sesuai}/{len(baris_validasi)} tabel sesuai).",
        f"- Detail CSV: `reports/{VALIDASI_BARIS_CSV.name}`",
        "", "## SQL vs Parquet", "",
        "| nama_tabel | jumlah_baris_parquet | jumlah_baris_sql | selisih | status |",
        "|---|---:|---:|---:|---|",
    ]
    for b in baris_validasi:
        lines.append(
            f"| {b['nama_tabel']} | {b['jumlah_baris_parquet']} | {b['jumlah_baris_sql']} "
            f"| {b['selisih']} | {b['status']} |"
        )
    (ROOT / "reports" / "validasi.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )

    if masalah:
        raise ValueError("Validasi gagal: " + "; ".join(masalah))
    return {"silver_ok": True, "rows": {k: len(v) for k, v in gold.items()}}
