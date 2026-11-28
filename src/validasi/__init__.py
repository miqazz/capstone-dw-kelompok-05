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
    """Menghitung jumlah baris pada database SQLite."""
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


def _catat(tahap: str, nama: str, lolos: bool, detail: str) -> dict:
    return {
        "tahap": tahap,
        "aturan": nama,
        "status": "LOLOS" if lolos else "GAGAL",
        "detail": detail,
    }


def jalankan(silver: pd.DataFrame, gold: dict[str, pd.DataFrame]):
    hasil_aturan: list[dict] = []

    # 1. Validasi Skema Minimal Silver
    manifest = baca()
    salah = periksa_silver(silver, manifest)
    hasil_aturan.append(_catat("Silver", "Skema minimal Silver", not salah, f"{len(silver)} baris lolos skema" if not salah else "; ".join(salah)))
    if salah:
        raise ValueError("Validasi Silver gagal: " + "; ".join(salah))

    # 2. Aturan Silver Sprint 1
    persen = silver.loc[silver["satuan"].astype(str).str.lower() == "persen", "nilai"].dropna()
    gagal_persen = int((~persen.between(0, 100)).sum())
    hasil_aturan.append(_catat("Silver", "Rentang nilai persen (0-100)", gagal_persen == 0, f"{len(persen)} baris dicek, {gagal_persen} pelanggaran"))

    v1477 = silver.loc[silver["seri_kode"] == "var1477"]
    if not v1477.empty:
        gagal_satuan = int((v1477["satuan"] != "kepadatan per 100.000 penduduk").sum())
        hasil_aturan.append(_catat("Silver", "Satuan var1477 baku", gagal_satuan == 0, f"{len(v1477)} baris dicek, {gagal_satuan} pelanggaran"))

    # 3. Ambil Tabel Gold & Cek Tidak Kosong
    panel = gold["panel_provinsi"]
    nasional = gold["nasional_periode_seri"]
    rekon = gold["rekonsiliasi_nasional"]

    tabel_gold = {
        "panel_provinsi": panel,
        "nasional_periode_seri": nasional,
        "rekonsiliasi_nasional": rekon,
    }
    tabel_kosong = [nama for nama, df in tabel_gold.items() if df.empty]
    hasil_aturan.append(_catat(
        "Gold",
        "Seluruh tabel Gold tidak kosong",
        len(tabel_kosong) == 0,
        f"panel={len(panel)}, nasional={len(nasional)}, rekon={len(rekon)}" if not tabel_kosong else f"Kosong: {tabel_kosong}",
    ))
    if tabel_kosong:
        raise ValueError(f"Tabel gold kosong: {', '.join(tabel_kosong)}")

    # 4. Aturan Gold Sprint 2 (#25)
    # 4a. Kunci panel provinsi unik
    dup_panel = int(panel.duplicated(subset=["seri_kode", "wilayah_kode", "periode", "rincian"]).sum())
    hasil_aturan.append(_catat("Gold", "Kunci panel_provinsi unik (seri_kode, wilayah_kode, periode, rincian)", dup_panel == 0, f"{len(panel)} baris dicek, {dup_panel} duplikat"))

    # 4b. Satuan satu per indikator
    satuan_ganda = silver.groupby("seri_kode")["satuan"].nunique()
    jml_ganda = int((satuan_ganda > 1).sum())
    hasil_aturan.append(_catat("Gold", "Satuan tunggal per indikator (seri_kode)", jml_ganda == 0, f"{len(satuan_ganda)} indikator dicek, {jml_ganda} bersatuan ganda"))

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
        "Gold",
        "Setiap sel Gold yang terisi memiliki pasangan di Silver",
        tanpa_pasangan == 0,
        f"{len(kunci_panel)} kunci dicek, {tanpa_pasangan} tanpa pasangan",
    ))

    # 5. Aturan Rekonsiliasi V4 & Kelengkapan Penjelasan
    kat_kosong = rekon["kategori_selisih"].isna() | rekon["kategori_selisih"].astype(str).str.strip().eq("")
    asing = set(rekon["kategori_selisih"].dropna().astype(str)) - KATEGORI_BAKU
    rekon_ok = (not kat_kosong.any()) and (len(asing) == 0)
    hasil_aturan.append(_catat(
        "Rekonsiliasi",
        "Kategori selisih sesuai taksonomi baku (V4)",
        rekon_ok,
        f"{len(rekon)} baris valid" if rekon_ok else f"Kosong: {int(kat_kosong.sum())}, Asing: {sorted(asing)}",
    ))
    if kat_kosong.any():
        raise ValueError("Ada baris rekonsiliasi tanpa kategori_selisih")
    if asing:
        raise ValueError(f"Kategori rekonsiliasi tidak dikenal: {sorted(asing)}")

    belum = rekon[rekon["kategori_selisih"] == "belum terjelaskan"]
    kosong_detail = {}
    for kolom in ["penjelasan", "bukti_dicari"]:
        kosong = belum[kolom].isna() | belum[kolom].astype(str).str.strip().eq("")
        if kosong.any():
            kosong_detail[kolom] = int(kosong.sum())
    hasil_aturan.append(_catat(
        "Rekonsiliasi",
        "Kelengkapan penjelasan & bukti_dicari untuk 'belum terjelaskan'",
        len(kosong_detail) == 0,
        f"{len(belum)} baris lengkap" if not kosong_detail else f"Kolom kosong: {kosong_detail}",
    ))
    for kolom, jml in kosong_detail.items():
        raise ValueError(f"Kategori 'belum terjelaskan' wajib punya {kolom}: {jml} baris kosong")

    # 6. Cek Konsistensi Baris SQL vs Parquet
    sql_counts = _hitung_sql()
    parquet_counts = {
        "silver": len(pd.read_parquet(ROOT / "data/silver/silver.parquet")),
        "gold_panel_provinsi": len(pd.read_parquet(ROOT / "data/gold/panel_provinsi.parquet")),
        "gold_nasional_periode_seri": len(pd.read_parquet(ROOT / "data/gold/nasional_periode_seri.parquet")),
        "rekonsiliasi_nasional": len(pd.read_parquet(ROOT / "data/gold/rekonsiliasi_nasional.parquet")),
    }
    sql_ok = all(sql_counts[k] == parquet_counts[k] for k in sql_counts)
    hasil_aturan.append(_catat("Penyimpanan", "Konsistensi jumlah baris SQL vs Parquet", sql_ok, "4/4 tabel sama" if sql_ok else "Ada selisih baris"))
    for k, sql_n in sql_counts.items():
        pq_n = parquet_counts[k]
        if sql_n != pq_n:
            raise ValueError(f"Baris SQL vs Parquet tidak sama untuk {k}: SQL={sql_n}, Parquet={pq_n}")

    # 7. Hitung Ringkasan & Rincian Rekonsiliasi
    total_aturan = len(hasil_aturan)
    aturan_lolos = sum(1 for h in hasil_aturan if h["status"] == "LOLOS")

    dist_kat = rekon["kategori_selisih"].astype(str).value_counts()

    # 8. Simpan Laporan Lengkap ke reports/validasi.md
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    lines = [
        "# Validasi Pipeline & Hasil Rekonsiliasi (Sprint 2)",
        "",
        "## Ringkasan Eksekusi",
        "",
        f"- **Total aturan validasi:** {total_aturan}",
        f"- **Aturan lolos:** {aturan_lolos}/{total_aturan}",
        f"- **Silver (`silver`):** {len(silver)} baris",
        f"- **Gold (`panel_provinsi`):** {len(panel)} baris",
        f"- **Gold (`nasional_periode_seri`):** {len(nasional)} baris",
        f"- **Rekonsiliasi (`rekonsiliasi_nasional`):** {len(rekon)} baris",
        "",
        "## Hasil Lengkap Tiap Aturan Validasi",
        "",
        "| No | Tahap | Aturan Validasi | Status | Detail Hasil |",
        "|---:|---|---|---|---|",
    ]
    for i, h in enumerate(hasil_aturan, start=1):
        lines.append(f"| {i} | {h['tahap']} | {h['aturan']} | **{h['status']}** | {h['detail']} |")

    lines += [
        "",
        "## Hasil Rekonsiliasi Nasional",
        "",
        "### Distribusi Kategori Selisih (V4)",
        "",
        "| Kategori Selisih | Jumlah Baris | Proporsi |",
        "|---|---:|---:|",
    ]
    for kat, jml in dist_kat.items():
        pct = (jml / len(rekon)) * 100
        lines.append(f"| {kat} | {int(jml)} | {pct:.1f}% |")

    if "seri_kode" in rekon.columns:
        lines += [
            "",
            "### Ringkasan Rekonsiliasi per Indikator (`seri_kode`)",
            "",
            "| Seri Kode | Jumlah Baris | Kategori Selisih | Rentang Selisih |",
            "|---|---:|---|---|",
        ]
        for seri, grp in rekon.groupby("seri_kode"):
            kat_str = ", ".join(f"{k} ({int(v)})" for k, v in grp["kategori_selisih"].value_counts().items())
            if "selisih" in grp.columns:
                num_sel = pd.to_numeric(grp["selisih"], errors="coerce").dropna()
                rentang = f"{num_sel.min():.2f} s.d. {num_sel.max():.2f}" if not num_sel.empty else "N/A"
            else:
                rentang = "N/A"
            lines.append(f"| {seri} | {len(grp)} | {kat_str} | {rentang} |")

    lines += [
        "",
        "## Konsistensi SQL vs Parquet",
        "",
        "| Tabel | SQL | Parquet | Status |",
        "|---|---:|---:|---|",
    ]
    for k in ["silver", "gold_panel_provinsi", "gold_nasional_periode_seri", "rekonsiliasi_nasional"]:
        status = "sama" if sql_counts[k] == parquet_counts[k] else "beda"
        lines.append(f"| {k} | {sql_counts[k]} | {parquet_counts[k]} | {status} |")

    (reports / "validasi.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 9. Cetak Hasil Lengkap Tiap Aturan & Rekonsiliasi di Terminal
    print(f"[VALIDASI] {aturan_lolos}/{total_aturan} aturan LOLOS:")
    for i, h in enumerate(hasil_aturan, start=1):
        print(f"  {i:02d}. [{h['status']}] ({h['tahap']}) {h['aturan']} -> {h['detail']}")
    print("[REKONSILIASI] Distribusi kategori_selisih:")
    for kat, jml in dist_kat.items():
        print(f"  - {kat}: {int(jml)} baris")
    print("[VALIDASI] Laporan lengkap disimpan di reports/validasi.md")

    return {
        "silver_ok": True,
        "rows": {k: len(v) for k, v in gold.items()},
        "aturan_validasi": total_aturan,
        "aturan_lolos": aturan_lolos,
    }