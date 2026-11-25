"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "data" / "gold"
GOLD_DB = GOLD_DIR / "gold.sqlite"
GOLD_DDL = ROOT / "sql" / "gold.sql"
NASIONAL_CSV = GOLD_DIR / "nasional_periode_seri.csv"
PANEL_CSV = GOLD_DIR / "panel_provinsi.csv"
REKON_CSV = GOLD_DIR / "rekonsiliasi_nasional.csv"
KATEGORI_REKONSILIASI = (
    "definisi berbeda", "metode berbeda", "vintage berbeda", "cakupan berbeda", "belum terjelaskan",
)


def _buat_panel(silver: pd.DataFrame) -> pd.DataFrame:
    panel = silver[silver["wilayah_kode"].astype(int) != 9999].copy()
    panel = panel.sort_values(["seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]).reset_index(drop=True)
    return panel


def _buat_nasional(silver: pd.DataFrame) -> pd.DataFrame:
    nat = silver[silver["wilayah_kode"].astype(int) == 9999].copy()
    cols = ["sumber", "seri_kode", "periode", "jenis_periode", "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw"]
    nat = nat[cols].copy()

    # turunan var1477 untuk rekonsiliasi
    v1477 = nat[(nat["seri_kode"] == "var1477") & (nat["periode"].astype(str) == "2018")]
    berkas = "bps/2026-10-20/sdg3_3_c_1_v1477.csv"
    sha = v1477["_sha256_raw"].iloc[0] if not v1477.empty else nat[nat["seri_kode"] == "var1477"]["_sha256_raw"].iloc[0]

    def row(seri, rincian, nilai, satuan, catatan):
        return {
            "sumber": "bps", "seri_kode": seri, "periode": "2018", "jenis_periode": "tahun",
            "rincian": rincian, "nilai": float(nilai), "satuan": satuan,
            "_berkas_raw": berkas, "_sha256_raw": sha, "catatan": catatan, "asal_angka": "turunan dari baris Indonesia var1477 (wilayah_kode=9999)",
        }

    dokter = v1477[v1477["rincian"] == "Dokter Umum"]
    perawat = v1477[v1477["rincian"] == "Perawat"]
    bidan = v1477[v1477["rincian"] == "Bidan"]
    turunan = []
    if not dokter.empty:
        v = float(dokter["nilai"].iloc[0])
        turunan.append(row("var1477_dokter_umum_per10k", "Dokter Umum", v / 10, "per 10.000 penduduk",
                           "turunan konversi: kepadatan Dokter Umum per 100.000 / 10 untuk pembanding HWF_0001"))
    if not perawat.empty and not bidan.empty:
        vp = float(perawat["nilai"].iloc[0])
        vb = float(bidan["nilai"].iloc[0])
        total = vp + vb
        turunan.append(row("var1477_perawat_bidan_per100k", "Perawat + Bidan", total, "kepadatan per 100.000 penduduk",
                           "turunan: penjumlahan kepadatan Perawat dan Bidan (rincian nasional 2018)"))
        turunan.append(row("var1477_perawat_bidan_per10k", "Perawat + Bidan", total / 10, "per 10.000 penduduk",
                           "turunan konversi: (Perawat + Bidan) per 100.000 / 10 untuk pembanding HWF_0006"))

    nat["catatan"] = ""
    nat["asal_angka"] = nat["seri_kode"].apply(
    lambda x: (
        "baris Indonesia (wilayah_kode=9999)"
        if x in ["var1402", "var2279", "var1477"]
        else "pembanding nasional WHO (wilayah_kode=9999)"
        )
    )
    # catatan WHO FINPROTECTION
    mask_fin = nat["seri_kode"] == "FINPROTECTION_CATA_TOT_10_POP"
    nat.loc[mask_fin, "catatan"] = "disagregasi TOTAL (DIM_DEG_URB=TOTAL, dimensi lain kosong)"

    if turunan:
        nat = pd.concat([nat, pd.DataFrame(turunan)], ignore_index=True)

    nat["periode"] = nat["periode"].astype(str)
    nat = nat.sort_values(["sumber", "seri_kode", "periode", "rincian"]).reset_index(drop=True)
    return nat[
        [
            "sumber", "seri_kode", "periode", "jenis_periode",
            "rincian", "nilai", "satuan",
            "_berkas_raw", "_sha256_raw", "catatan", "asal_angka"
        ]
    ]


def _buat_rekonsiliasi(nasional: pd.DataFrame) -> pd.DataFrame:
    rows = []

    def add(pasangan_id, seri_utama, rincian_utama, seri_pembanding, rincian_pembanding,
            periode, jenis_periode, nilai_utama, satuan_utama, nilai_pembanding, satuan_pembanding,
            kategori, penjelasan, bukti=""):
        selisih = None
        if pd.notna(nilai_utama) and pd.notna(nilai_pembanding):
            try:
                selisih = float(nilai_utama) - float(nilai_pembanding)
            except Exception:
                selisih = None
        rows.append({
            "pasangan_id": pasangan_id,
            "seri_utama": seri_utama,
            "rincian_utama": rincian_utama,
            "seri_pembanding": seri_pembanding,
            "rincian_pembanding": rincian_pembanding,
            "periode": str(periode),
            "jenis_periode": jenis_periode,
            "nilai_utama": nilai_utama,
            "satuan_utama": satuan_utama,
            "nilai_pembanding": nilai_pembanding,
            "satuan_pembanding": satuan_pembanding,
            "selisih": selisih,
            "kategori_selisih": kategori,
            "penjelasan": penjelasan,
            "bukti_dicari": bukti,
        })

    # Pasangan 1: var1477 Dokter Umum per10k vs HWF_0001
    utama = nasional[nasional["seri_kode"] == "var1477_dokter_umum_per10k"]
    banding = nasional[nasional["seri_kode"] == "HWF_0001"]
    periode_all = sorted(set(utama["periode"].astype(str)) | set(banding["periode"].astype(str)), key=lambda x: int(x))
    for p in periode_all:
        u = utama[utama["periode"].astype(str) == p]
        b = banding[banding["periode"].astype(str) == p]
        vu = float(u["nilai"].iloc[0]) if not u.empty else None
        vb = float(b["nilai"].iloc[0]) if not b.empty else None
        if vu is None or vb is None:
            kat = "belum terjelaskan"
            pen = "Belum terjelaskan: periode tidak berpasangan pada snapshot saat ini. Dugaan: seri sumber memiliki cakupan tahun berbeda/vintage rilis tidak sama. Bukti dicari: cek ketersediaan periode di silver/gold dan metadata rilis WHO/BPS; tidak dipaksa sama." 
            bukti = "Dicek: data/silver/silver.csv, data/gold/nasional_periode_seri.csv; metadata rilis WHO/BPS belum menunjukkan periode padanan pada snapshot 2026-10-20."
        else:
            kat = "cakupan berbeda"
            pen = "Satuan disetarakan (per 100.000 ke per 10.000). HWF_0001 mencakup medical doctors; var1477 menggunakan rincian Dokter Umum saja, Dokter Gigi tidak digabung. Selisih dapat dipengaruhi cakupan profesi, sumber pendataan, dan vintage."
            bukti = "Metadata BPS var1477 (per 100.000 penduduk); definisi WHO HWF_0001 medical doctors per 10.000; K-002,K-003"
        add("P1_dokter_hwf0001", "var1477_dokter_umum_per10k", "Dokter Umum", "HWF_0001", "TOTAL",
            p, "tahun", vu, "per 10.000 penduduk", vb, "per 10.000 penduduk", kat, pen, bukti)

    # Pasangan 2: perawat+bidan per10k vs HWF_0006
    utama = nasional[nasional["seri_kode"] == "var1477_perawat_bidan_per10k"]
    banding = nasional[nasional["seri_kode"] == "HWF_0006"]
    periode_all = sorted(set(utama["periode"].astype(str)) | set(banding["periode"].astype(str)), key=lambda x: int(x))
    for p in periode_all:
        u = utama[utama["periode"].astype(str) == p]
        b = banding[banding["periode"].astype(str) == p]
        vu = float(u["nilai"].iloc[0]) if not u.empty else None
        vb = float(b["nilai"].iloc[0]) if not b.empty else None
        if vu is None or vb is None:
            kat = "belum terjelaskan"
            pen = "Belum terjelaskan: periode tidak berpasangan pada snapshot saat ini. Dugaan: seri sumber memiliki cakupan tahun berbeda/vintage rilis tidak sama. Bukti dicari: cek ketersediaan periode di silver/gold dan metadata rilis WHO/BPS; tidak dipaksa sama." 
            bukti = "Dicek: data/silver/silver.csv, data/gold/nasional_periode_seri.csv; metadata rilis WHO/BPS belum menunjukkan periode padanan pada snapshot 2026-10-20."
        else:
            kat = "cakupan berbeda"
            pen = "Satuan disetarakan (per 100.000 ke per 10.000) dan rincian Perawat+Bidan dijumlahkan setelah verifikasi definisi. HWF_0006 mencakup nursing and midwifery personnel; selisih dapat dipengaruhi cakupan kader, sumber, dan vintage."
            bukti = "Metadata BPS var1477; definisi WHO HWF_0006 nursing and midwifery personnel; K-002,K-003"
        add("P2_perawat_bidan_hwf0006", "var1477_perawat_bidan_per10k", "Perawat + Bidan", "HWF_0006", "TOTAL",
            p, "tahun", vu, "per 10.000 penduduk", vb, "per 10.000 penduduk", kat, pen, bukti)

    # Pasangan 3: var1402 vs UHC_INDEX_REPORTED (kontekstual)
    utama = nasional[(nasional["seri_kode"] == "var1402") & (nasional["rincian"] == "Tidak ada")]
    banding = nasional[nasional["seri_kode"] == "UHC_INDEX_REPORTED"]
    periode_all = sorted(set(utama["periode"].astype(str)) | set(banding["periode"].astype(str)), key=lambda x: int(x))
    for p in periode_all:
        u = utama[utama["periode"].astype(str) == p]
        b = banding[banding["periode"].astype(str) == p]
        vu = float(u["nilai"].iloc[0]) if not u.empty else None
        vb = float(b["nilai"].iloc[0]) if not b.empty else None
        if vu is None or vb is None:
            kat = "belum terjelaskan"
            pen = "Belum terjelaskan: periode tidak berpasangan. Dugaan: rentang tahun seri berbeda (BPS vs WHO) atau vintage pembaruan berbeda. Bukti dicari: cek periode tersedia di silver/gold; tidak dipaksa sama."
            add("P3_var1402_uhc", "var1402", "Tidak ada", "UHC_INDEX_REPORTED", "TOTAL",
                p, "tahun", vu, "Persen", vb, "indeks (skor cakupan layanan UHC, 0-100)", kat, pen, "K-004; metadata indikator BPS/WHO")
        else:
            kat = "definisi berbeda"
            pen = "Konsep terkait SDG 3.8.1 tetapi indikator berbeda: var1402 unmet need layanan kesehatan (%) vs UHC service coverage index (0-100). Skala/arah/metode berbeda; selisih numerik tidak dihitung karena satuan/konstruk tidak sebanding."
            rows.append({
                "pasangan_id": "P3_var1402_uhc", "seri_utama": "var1402", "rincian_utama": "Tidak ada",
                "seri_pembanding": "UHC_INDEX_REPORTED", "rincian_pembanding": "TOTAL", "periode": str(p),
                "jenis_periode": "tahun", "nilai_utama": vu, "satuan_utama": "Persen", "nilai_pembanding": vb,
                "satuan_pembanding": "indeks (skor cakupan layanan UHC, 0-100)", "selisih": None,
                "kategori_selisih": kat, "penjelasan": pen, "bukti_dicari": "K-004; metadata indikator BPS/WHO",
            })

    # Pasangan 4: var2279 vs FINPROTECTION (kontekstual)
    utama = nasional[(nasional["seri_kode"] == "var2279") & (nasional["rincian"] == "Tidak ada")]
    banding = nasional[nasional["seri_kode"] == "FINPROTECTION_CATA_TOT_10_POP"]
    periode_all = sorted(set(utama["periode"].astype(str)) | set(banding["periode"].astype(str)), key=lambda x: int(x))
    for p in periode_all:
        u = utama[utama["periode"].astype(str) == p]
        b = banding[banding["periode"].astype(str) == p]
        vu = float(u["nilai"].iloc[0]) if not u.empty else None
        vb = float(b["nilai"].iloc[0]) if not b.empty else None
        if vu is None or vb is None:
            kat = "belum terjelaskan"
            pen = "Belum terjelaskan: periode tidak berpasangan pada snapshot saat ini. Dugaan: beda rentang waktu/vintage antara seri BPS var2279 dan WHO FINPROTECTION. Bukti dicari: cek periode di silver/gold dan metadata WHO/BPS; tidak dipaksa sama."
            add("P4_var2279_finprot", "var2279", "Tidak ada", "FINPROTECTION_CATA_TOT_10_POP", "TOTAL",
                p, "tahun", vu, "Persen", vb, "persen populasi", kat, pen, "K-004; filter WHO DIM_DEG_URB=TOTAL")
        else:
            kat = "definisi berbeda"
            pen = "Konsep terkait SDG 3.8.2 tetapi indikator berbeda: var2279 kepemilikan JKN (%) vs FINPROTECTION_CATA_TOT_10_POP pengeluaran kesehatan katastropik >10% anggaran rumah tangga (% populasi, TOTAL). Arah dan konstruk berbeda; selisih numerik tidak dihitung."
            rows.append({
                "pasangan_id":"P4_var2279_finprot","seri_utama":"var2279","rincian_utama":"Tidak ada",
                "seri_pembanding":"FINPROTECTION_CATA_TOT_10_POP","rincian_pembanding":"TOTAL","periode":str(p),
                "jenis_periode":"tahun","nilai_utama":vu,"satuan_utama":"Persen","nilai_pembanding":vb,
                "satuan_pembanding":"persen populasi","selisih":None,"kategori_selisih":kat,
                "penjelasan":pen,"bukti_dicari":"K-004; filter WHO DIM_DEG_URB=TOTAL",
            })

    df = pd.DataFrame(rows)
    df = df.sort_values(["pasangan_id", "periode"]).reset_index(drop=True)
    buruk = df[~df["kategori_selisih"].isin(KATEGORI_REKONSILIASI)]
    if not buruk.empty:
        raise ValueError(f"Kategori rekonsiliasi tidak dikenal: {sorted(buruk['kategori_selisih'].unique())}")
    return df


def simpan_gold(tables: dict[str, pd.DataFrame]) -> dict[str, Path]:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    panel = tables["panel_provinsi"]
    nasional = tables["nasional_periode_seri"]
    rekon = tables["rekonsiliasi_nasional"]

    panel.to_csv(PANEL_CSV, index=False)
    panel.to_parquet(GOLD_DIR / "panel_provinsi.parquet", index=False)
    nasional.to_csv(NASIONAL_CSV, index=False)
    nasional.to_parquet(GOLD_DIR / "nasional_periode_seri.parquet", index=False)
    rekon.to_csv(REKON_CSV, index=False)
    rekon.to_parquet(GOLD_DIR / "rekonsiliasi_nasional.parquet", index=False)

    schema = GOLD_DDL.read_text(encoding="utf-8")
    if GOLD_DB.exists():
        GOLD_DB.unlink()
    con = sqlite3.connect(GOLD_DB)
    try:
        con.executescript(schema)
        panel.to_sql("gold_panel_provinsi", con, if_exists="append", index=False)
        nasional.to_sql("gold_nasional_periode_seri", con, if_exists="append", index=False)
        rekon.to_sql("rekonsiliasi_nasional", con, if_exists="append", index=False)
        con.commit()
        counts = {
            "gold_panel_provinsi": con.execute("SELECT COUNT(*) FROM gold_panel_provinsi").fetchone()[0],
            "gold_nasional_periode_seri": con.execute("SELECT COUNT(*) FROM gold_nasional_periode_seri").fetchone()[0],
            "rekonsiliasi_nasional": con.execute("SELECT COUNT(*) FROM rekonsiliasi_nasional").fetchone()[0],
        }
    finally:
        con.close()
    expected = {
        "gold_panel_provinsi": len(panel),
        "gold_nasional_periode_seri": len(nasional),
        "rekonsiliasi_nasional": len(rekon),
    }
    parquet_map = {
        "gold_panel_provinsi": GOLD_DIR / "panel_provinsi.parquet",
        "gold_nasional_periode_seri": GOLD_DIR / "nasional_periode_seri.parquet",
        "rekonsiliasi_nasional": GOLD_DIR / "rekonsiliasi_nasional.parquet",
    }
    for k, v in expected.items():
        if counts[k] != v:
            raise ValueError(f"Baris SQL {k} ({counts[k]}) != DataFrame ({v})")
        pq = pd.read_parquet(parquet_map[k])
        if len(pq) != counts[k]:
            raise ValueError(f"Baris Parquet {k} ({len(pq)}) != SQL ({counts[k]})")
    return {"db": GOLD_DB, "panel": PANEL_CSV, "nasional": NASIONAL_CSV, "rekon": REKON_CSV}


def jalankan(silver: pd.DataFrame) -> dict[str, pd.DataFrame]:
    panel = _buat_panel(silver)
    nasional = _buat_nasional(silver)
    rekon = _buat_rekonsiliasi(nasional)
    tables = {
        "panel_provinsi": panel,
        "nasional_periode_seri": nasional,
        "rekonsiliasi_nasional": rekon,
    }
    simpan_gold(tables)
    return tables
