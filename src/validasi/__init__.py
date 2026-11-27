"""Tahap 8: Validasi Silver, Gold, Rekonsiliasi, dan Konsistensi SQL vs Parquet."""
from __future__ import annotations
from pathlib import Path
import sqlite3
import pandas as pd
from src.common.skema import periksa_silver
from src.common.manifest import baca

ROOT = Path(__file__).resolve().parents[2]

KATEGORI_BAKU = {
    "definisi berbeda",
    "metode berbeda",
    "vintage berbeda",
    "cakupan berbeda",
    "belum terjelaskan",
    "tanpa pasangan",
}


def _hitung_sql() -> dict[str, int]:
    """Menghitung jumlah baris pada database SQLite (bagian Allisha)."""
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


def _catat(nama: str, lolos: bool, detail: str) -> dict:
    return {"aturan": nama, "status": "LOLOS" if lolos else "GAGAL", "detail": detail}


def jalankan(silver: pd.DataFrame, gold: dict[str, pd.DataFrame]):
    hasil_aturan: list[dict] = []

    # 1. Validasi Skema Minimal Silver (Allisha)
    manifest = baca()
    salah = periksa_silver(silver, manifest)
    hasil_aturan.append(_catat("Silver: Skema minimal", not salah, "Lolos" if not salah else "; ".join(salah)))
    if salah:
        raise ValueError("Validasi Silver gagal: " + "; ".join(salah))

    # 2. Aturan Silver Sprint 1 (Mufti)
    persen = silver.loc[silver["satuan"].astype(str).str.lower() == "persen", "nilai"].dropna()
    gagal_persen = int((~persen.between(0, 100)).sum())
    hasil_aturan.append(_catat("Silver: Rentang persen (0-100)", gagal_persen == 0, f"{gagal_persen} pelanggaran"))

    v1477 = silver.loc[silver["seri_kode"] == "var1477"]
    if not v1477.empty:
        gagal_satuan = int((v1477["satuan"] != "kepadatan per 100.000 penduduk").sum())
        hasil_aturan.append(_catat("Silver: Satuan var1477 baku", gagal_satuan == 0, f"{gagal_satuan} pelanggaran"))


    # 3. Ambil Tabel Gold & Cek Tidak Kosong (Allisha)
    panel = gold["panel_provinsi"]
    nasional = gold["nasional_periode_seri"]
    rekon = gold["rekonsiliasi_nasional"]

    for nama, df in {"panel_provinsi": panel, "nasional_periode_seri": nasional, "rekonsiliasi_nasional": rekon}.items():
        if df.empty:
            raise ValueError(f"Tabel gold kosong: {nama}")

    # 4. Aturan Gold Sprint 2 (#25 - Mufti)
    # 4a. Kunci panel provinsi unik
    dup_panel = int(panel.duplicated(subset=["seri_kode", "wilayah_kode", "periode", "rincian"]).sum())
    hasil_aturan.append(_catat("Gold: Kunci panel_provinsi unik", dup_panel == 0, f"{dup_panel} baris duplikat"))

    # 4b. Satuan satu per indikator (cek dari Silver berdasarkan seri_kode)
    satuan_ganda = silver.groupby("seri_kode")["satuan"].nunique()
    jml_ganda = int((satuan_ganda > 1).sum())
    hasil_aturan.append(_catat("Gold: Satuan satu per indikator", jml_ganda == 0, f"{jml_ganda} indikator bersatuan ganda"))

        # 4c. Setiap observasi Gold yang terisi punya pasangan di Silver
    panel_terisi = panel.loc[panel["status"] == "terisi"]

    kunci_silver = set(zip(
        silver["wilayah_kode"].astype(int),
        silver["periode"].astype(str),
        silver["seri_kode"].astype(str),
    ))

    kunci_panel = set(zip(
        panel_terisi["wilayah_kode"].astype(int),
        panel_terisi["periode"].astype(str),
        panel_terisi["seri_kode"].astype(str),
    ))

    tanpa_pasangan = len(kunci_panel - kunci_silver)

    hasil_aturan.append(_catat(
        "Gold: Sel Gold punya pasangan di Silver",
        tanpa_pasangan == 0,
        f"{tanpa_pasangan} kunci tidak ada di Silver",
    ))

    # 5. Aturan Rekonsiliasi V4 & Kelengkapan Penjelasan (Gabungan Allisha & Mufti)
    kat_kosong = rekon["kategori_selisih"].isna() | rekon["kategori_selisih"].astype(str).str.strip().eq("")
    asing = set(rekon["kategori_selisih"].dropna().astype(str)) - KATEGORI_BAKU
    rekon_ok = (not kat_kosong.any()) and (len(asing) == 0)
    hasil_aturan.append(_catat(
        "Rekonsiliasi: Kategori baku (V4)",
        rekon_ok,
        "Semua kategori valid" if rekon_ok else f"Kosong: {int(kat_kosong.sum())}, Asing: {sorted(asing)}",
    ))
    if kat_kosong.any():
        raise ValueError("Ada baris rekonsiliasi tanpa kategori_selisih")
    if asing:
        raise ValueError(f"Kategori rekonsiliasi tidak dikenal: {sorted(asing)}")

    belum = rekon[rekon["kategori_selisih"] == "belum terjelaskan"]
    for kolom in ["penjelasan", "bukti_dicari"]:
        kosong = belum[kolom].isna() | belum[kolom].astype(str).str.strip().eq("")
        if kosong.any():
            raise ValueError(f"Kategori 'belum terjelaskan' wajib punya {kolom}: {int(kosong.sum())} baris kosong")

    # 6. Cek Konsistensi Baris SQL vs Parquet (Allisha)
    sql_counts = _hitung_sql()
    parquet_counts = {
        "silver": len(pd.read_parquet(ROOT / "data/silver/silver.parquet")),
        "gold_panel_provinsi": len(pd.read_parquet(ROOT / "data/gold/panel_provinsi.parquet")),
        "gold_nasional_periode_seri": len(pd.read_parquet(ROOT / "data/gold/nasional_periode_seri.parquet")),
        "rekonsiliasi_nasional": len(pd.read_parquet(ROOT / "data/gold/rekonsiliasi_nasional.parquet")),
    }
    sql_ok = all(sql_counts[k] == parquet_counts[k] for k in sql_counts)
    hasil_aturan.append(_catat("Penyimpanan: Baris SQL sama dengan Parquet", sql_ok, "Semua tabel sama" if sql_ok else "Ada selisih baris"))
    for k, sql_n in sql_counts.items():
        pq_n = parquet_counts[k]
        if sql_n != pq_n:
            raise ValueError(f"Baris SQL vs Parquet tidak sama untuk {k}: SQL={sql_n}, Parquet={pq_n}")

    # 7. Simpan Laporan ke reports/validasi.md
    total_aturan = len(hasil_aturan)
    aturan_lolos = sum(1 for h in hasil_aturan if h["status"] == "LOLOS")

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    lines = [
        "# Validasi Pipeline (Sprint 2)",
        "",
        f"- **Total aturan validasi:** {total_aturan}",
        f"- **Aturan lolos:** {aturan_lolos}",
        f"- Silver lolos skema minimal: {len(silver)} baris",
        f"- Gold panel_provinsi: {len(panel)} baris",
        f"- Gold nasional_periode_seri: {len(nasional)} baris",
        f"- Rekonsiliasi_nasional: {len(rekon)} baris",
        f"- Baris 'belum terjelaskan' lengkap (penjelasan & bukti_dicari): {len(belum)} baris",
        "",
        "## Ringkasan Aturan Validasi",
        "",
        "| Aturan | Status | Detail |",
        "| :--- | :--- | :--- |",
    ]
    for h in hasil_aturan:
        lines.append(f"| {h['aturan']} | **{h['status']}** | {h['detail']} |")

    lines += [
        "",
        "## SQL vs Parquet",
        "",
        "| Tabel | SQL | Parquet | Status |",
        "|---|---:|---:|---|",
    ]
    for k in ["silver", "gold_panel_provinsi", "gold_nasional_periode_seri", "rekonsiliasi_nasional"]:
        status = "sama" if sql_counts[k] == parquet_counts[k] else "beda"
        lines.append(f"| {k} | {sql_counts[k]} | {parquet_counts[k]} | {status} |")

    (reports / "validasi.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[VALIDASI] {aturan_lolos}/{total_aturan} aturan LOLOS. Laporan disimpan di reports/validasi.md")

    return {
        "silver_ok": True,
        "rows": {k: len(v) for k, v in gold.items()},
        "aturan_validasi": total_aturan,
        "aturan_lolos": aturan_lolos,
    }