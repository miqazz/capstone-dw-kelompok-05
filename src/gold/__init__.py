"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
GOLD_DIR = ROOT / "data" / "gold"
GOLD_DB = GOLD_DIR / "gold.sqlite"
GOLD_DDL = ROOT / "sql" / "gold.sql"
NASIONAL_CSV = GOLD_DIR / "nasional_periode_seri.csv"
PANEL_CSV = GOLD_DIR / "panel_provinsi.csv"
REKON_CSV = GOLD_DIR / "rekonsiliasi_nasional.csv"
KATEGORI_REKONSILIASI = (
    "definisi berbeda", "metode berbeda", "vintage berbeda", "cakupan berbeda", "belum terjelaskan",
)


def _ringkas_periode(nilai) -> str:
    tahun = sorted({int(str(p).strip()) for p in nilai if str(p).strip().isdigit()})
    if not tahun:
        return "tidak ada"
    if len(tahun) <= 8:
        return ", ".join(str(t) for t in tahun) + f" (n={len(tahun)})"
    return f"{tahun[0]}, {tahun[1]}, ..., {tahun[-2]}, {tahun[-1]} (n={len(tahun)})"


def _berkas_seri(df: pd.DataFrame) -> str:
    return ", ".join(sorted(set(df["_berkas_raw"].dropna().astype(str)))) or "berkas tidak tercatat"


def _bukti_csv_mentah(df: pd.DataFrame, label: str) -> str:
    berkas = _berkas_seri(df).split(", ")[0]
    path = RAW_DIR / berkas
    if not path.exists():
        return f"CSV mentah {label}: {berkas} tidak ditemukan di data/raw (belum terverifikasi)"
    mentah = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    kolom = next((k for k in ("tahun", "DIM_TIME") if k in mentah.columns), None)
    if kolom is None:
        return f"CSV mentah {berkas}: {len(mentah)} baris; kolom tahun tidak ditemukan"
    return f"CSV mentah {berkas}: {len(mentah)} baris, {kolom}={_ringkas_periode(mentah[kolom])}"


def _bukti_gold_seri(df: pd.DataFrame, label: str) -> str:
    return f"Gold nasional {label}: {_ringkas_periode(df['periode'])}; berkas {_berkas_seri(df)}"


def _bukti_bps_v1477() -> str:
    path = next(RAW_DIR.glob("bps/*/json/*v1477.json"), None)
    if path is None:
        return "metadata BPS var1477 tidak ditemukan di data/raw (belum terverifikasi)"
    isi = json.loads(path.read_text(encoding="utf-8-sig"))
    rekam = isi[0] if isinstance(isi, list) and isi else {}
    var = (rekam.get("var") or [{}])[0]
    catatan = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(var.get("note", "")))).strip()
    tahun = ", ".join(str(t.get("label")) for t in (rekam.get("tahun") or []) if t.get("label"))
    return (f"metadata {path.relative_to(ROOT).as_posix()}: var.note='{catatan}', "
            f"tahun={tahun or 'tidak tercatat'}, last_update={rekam.get('last_update', 'tidak tercatat')}")


def _bukti_who(df: pd.DataFrame, seri: str) -> str:
    berkas = _berkas_seri(df).split(", ")[0]
    kode = Path(berkas).name.split("_")[0]
    path = next(RAW_DIR.glob("who_gho/*/datadot/ddiindicators*.json"), None)
    if path is None:
        return f"metadata WHO {seri} ({kode}) tidak ditemukan di data/raw (belum terverifikasi)"
    isi = json.loads(path.read_text(encoding="utf-8-sig"))
    rekam = next(
        (r for r in isi.get("value", [])
         if str(r.get("UniqueIdentifier", "")).startswith(kode) or str(r.get("UrlName", "")).startswith(kode)),
        None,
    )
    if rekam is None:
        return f"metadata WHO {seri} (ID {kode}) tidak ditemukan (belum terverifikasi)"
    visual = str(rekam.get("DataVisualizationConfiguration", ""))
    try:
        label = json.loads(visual).get("label", "")
    except (ValueError, AttributeError):
        label = ""
    rentang = str(rekam.get("TimeIntervals", ""))
    if len(rentang) > 90:
        rentang = rentang[:87] + "..."
    return (f"metadata {path.relative_to(ROOT).as_posix()} ID {kode}: "
            f"label='{label}', ValueDisplayLabel='{rekam.get('ValueDisplayLabel', '')}', "
            f"DataUpdateLast={rekam.get('DataUpdateLast', 'tidak tercatat')}, "
            f"LastModified={rekam.get('LastModified', 'tidak tercatat')}, "
            f"TimeIntervals='{rentang}'")


def _bukti_pasangan(utama: pd.DataFrame, banding: pd.DataFrame, label_utama: str,
                    label_banding: str, meta_utama: str) -> str:
    return "; ".join([
        _bukti_csv_mentah(utama, label_utama),
        _bukti_gold_seri(utama, label_utama),
        meta_utama,
        _bukti_csv_mentah(banding, label_banding),
        _bukti_gold_seri(banding, label_banding),
        _bukti_who(banding, label_banding),
    ])


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
            "_berkas_raw": berkas, "_sha256_raw": sha, "catatan": catatan,
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
    # catatan WHO FINPROTECTION
    mask_fin = nat["seri_kode"] == "FINPROTECTION_CATA_TOT_10_POP"
    nat.loc[mask_fin, "catatan"] = "disagregasi TOTAL (DIM_DEG_URB=TOTAL, dimensi lain kosong)"

    if turunan:
        nat = pd.concat([nat, pd.DataFrame(turunan)], ignore_index=True)

    nat["periode"] = nat["periode"].astype(str)
    nat = nat.sort_values(["sumber", "seri_kode", "periode", "rincian"]).reset_index(drop=True)
    return nat[["sumber", "seri_kode", "periode", "jenis_periode", "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw", "catatan"]]


def _buat_rekonsiliasi(nasional: pd.DataFrame) -> pd.DataFrame:
    rows = []
    bukti_v1477 = _bukti_bps_v1477()

    def status_pasangan(vu, vb) -> str:
        if vu is not None and vb is not None:
            return "berpasangan"
        return "hanya_pembanding" if vu is None else "hanya_utama"

    def tambah(pasangan_id, seri_utama, rincian_utama, seri_pembanding, rincian_pembanding,
               satuan_utama, satuan_pembanding, periode, vu, vb, status, kategori_konsep,
               kategori_selisih, penjelasan, bukti, rentang_utama, rentang_pembanding,
               hitung_selisih):
        selisih = None
        if hitung_selisih and vu is not None and vb is not None:
            selisih = round(float(vu) - float(vb), 10)
        rows.append({
            "pasangan_id": pasangan_id,
            "seri_utama": seri_utama,
            "rincian_utama": rincian_utama,
            "seri_pembanding": seri_pembanding,
            "rincian_pembanding": rincian_pembanding,
            "periode": str(periode),
            "jenis_periode": "tahun",
            "nilai_utama": vu,
            "satuan_utama": satuan_utama,
            "nilai_pembanding": vb,
            "satuan_pembanding": satuan_pembanding,
            "selisih": selisih,
            "status_pasangan": status,
            "kategori_konsep": kategori_konsep,
            "kategori_selisih": kategori_selisih,
            "penjelasan": penjelasan,
            "bukti_dicari": bukti,
            "rentang_utama": rentang_utama,
            "rentang_pembanding": rentang_pembanding,
        })

    def pasangan(pasangan_id, seri_utama, rincian_utama, seri_pembanding, rincian_pembanding,
                 satuan_utama, satuan_pembanding, kategori_konsep, meta_utama,
                 penjelasan_berpasangan, dugaan_saat_utama_saja, dugaan_saat_pembanding_saja,
                 hitung_selisih, catatan_log):
        utama = nasional[(nasional["seri_kode"] == seri_utama) & (nasional["rincian"] == rincian_utama)]
        banding = nasional[(nasional["seri_kode"] == seri_pembanding) & (nasional["rincian"] == rincian_pembanding)]
        bukti = _bukti_pasangan(utama, banding, seri_utama, seri_pembanding, meta_utama)
        bukti += f"; keputusan {catatan_log} di log-keputusan.csv"
        rentang_u = _ringkas_periode(utama["periode"])
        rentang_b = _ringkas_periode(banding["periode"])
        untuk_semua = sorted(
            {int(p) for p in set(utama["periode"].astype(str)) | set(banding["periode"].astype(str)) if p.isdigit()}
        )
        for p in untuk_semua:
            u = utama[utama["periode"].astype(str) == str(p)]
            b = banding[banding["periode"].astype(str) == str(p)]
            vu = float(u["nilai"].iloc[0]) if not u.empty else None
            vb = float(b["nilai"].iloc[0]) if not b.empty else None
            status = status_pasangan(vu, vb)
            if status == "berpasangan":
                kategori = kategori_konsep
                penjelasan = penjelasan_berpasangan
            else:
                kategori = "belum terjelaskan"
                dugaan = dugaan_saat_utama_saja if status == "hanya_utama" else dugaan_saat_pembanding_saja
                penjelasan = (f"Belum terjelaskan: periode {p} tidak memiliki pasangan pada snapshot ini. {dugaan} "
                              "Penyebab akhirnya belum terverifikasi; periode dipertahankan dan nilai tidak dipaksa sama.")
            tambah(pasangan_id, seri_utama, rincian_utama, seri_pembanding, rincian_pembanding,
                   satuan_utama, satuan_pembanding, p, vu, vb, status, kategori_konsep,
                   kategori, penjelasan, bukti, rentang_u, rentang_b, hitung_selisih)

    pasangan(
        "P1_dokter_hwf0001", "var1477_dokter_umum_per10k", "Dokter Umum", "HWF_0001", "TOTAL",
        "per 10.000 penduduk", "per 10.000 penduduk", "cakupan berbeda",
        bukti_v1477 + "; keputusan K-004,K-007,K-009,K-010 di log-keputusan.csv",
        "Satuan disetarakan dari per 100.000 ke per 10.000. HWF_0001 adalah density of doctors; "
        "rincian BPS yang dipakai hanya Dokter Umum, Dokter Gigi tidak digabung. Selisih tercatat apa adanya.",
        "Dugaan: WHO HWF_0001 tidak melaporkan nilai Indonesia pada tahun ini dalam snapshot; "
        "observasi WHO tidak tersedia setiap tahun. Perlu cek rilis WHO terbaru; belum terverifikasi.",
        "Dugaan: agregat nasional var1477 tidak tersedia pada tahun ini dalam snapshot; metadata BPS mencatat "
        "tahun 2016-2018, tetapi baris nasional hanya 2018. Perlu cek rilis BPS lain; belum terverifikasi.",
        True, "K-004,K-007,K-009,K-010",
    )

    pasangan(
        "P2_perawat_bidan_hwf0006", "var1477_perawat_bidan_per10k", "Perawat + Bidan", "HWF_0006", "TOTAL",
        "per 10.000 penduduk", "per 10.000 penduduk", "cakupan berbeda",
        bukti_v1477 + "; keputusan K-004,K-008,K-009,K-010 di log-keputusan.csv",
        "Satuan disetarakan dari per 100.000 ke per 10.000. Perawat dan Bidan dijumlahkan setelah "
        "pemeriksaan definisi WHO nursing and midwifery personnel; selisih tercatat apa adanya.",
        "Dugaan: WHO HWF_0006 tidak melaporkan nilai Indonesia pada tahun ini dalam snapshot; "
        "observasi WHO tidak tersedia setiap tahun. Perlu cek rilis WHO terbaru; belum terverifikasi.",
        "Dugaan: agregat nasional var1477 tidak tersedia pada tahun ini dalam snapshot; metadata BPS mencatat "
        "tahun 2016-2018, tetapi baris nasional hanya 2018. Perlu cek rilis BPS lain; belum terverifikasi.",
        True, "K-004,K-008,K-009,K-010",
    )

    pasangan(
        "P3_var1402_uhc", "var1402", "Tidak ada", "UHC_INDEX_REPORTED", "TOTAL",
        "Persen", "indeks (skor cakupan layanan UHC, 0-100)", "definisi berbeda",
        "log-keputusan.csv K-002: var1402 adalah unmet need layanan kesehatan (%), metadata SIRUSA; "
        "file metadata BPS tidak disimpan di repository",
        "Konteks SDG 3.8.1 serupa, tetapi var1402 mengukur unmet need (%) dan UHC_INDEX_REPORTED "
        "adalah indeks cakupan layanan (0-100). Konstruk dan satuan berbeda; selisih numerik tidak dihitung.",
        "Dugaan: WHO UHC_INDEX_REPORTED pada snapshot berhenti di 2023 meskipun metadata DataUpdateLast "
        "2024-01-08; BPS var1402 berlanjut sampai 2025. Perlu cek rilis WHO terbaru; belum terverifikasi.",
        "Dugaan: tahun ini berada sebelum cakupan BPS var1402 yang dimulai 2015 (K-019), "
        "sedangkan WHO UHC_INDEX_REPORTED tersedia sejak 2000 pada snapshot ini. Bukan missing pada grid BPS.",
        False, "K-002,K-005,K-011,K-019",
    )

    pasangan(
        "P4_var2279_finprot", "var2279", "Tidak ada", "FINPROTECTION_CATA_TOT_10_POP", "TOTAL",
        "Persen", "persen populasi", "definisi berbeda",
        "log-keputusan.csv K-003: var2279 adalah kepemilikan JKN (%), metadata BPS; "
        "file metadata BPS tidak disimpan di repository",
        "Konteks SDG 3.8.2 serupa, tetapi var2279 mengukur kepemilikan JKN (%) sedangkan "
        "FINPROTECTION_CATA_TOT_10_POP mengukur pengeluaran kesehatan rumah tangga di atas 10% "
        "anggaran (% populasi, TOTAL). Arah/konstruk berbeda; selisih numerik tidak dihitung.",
        "Dugaan: WHO FINPROTECTION pada snapshot berhenti di 2021 (CSV setelah filter TOTAL) "
        "sementara BPS var2279 mulai 2022; metadata mencatat TimeIntervals hingga 2020 dan "
        "DataUpdateLast 2023-06-20. Perlu cek rilis WHO terbaru; belum terverifikasi.",
        "Dugaan: BPS var2279 baru tersedia sejak 2022 (K-013/K-021), sehingga tahun ini berada di luar "
        "rentang seri BPS, bukan missing pada grid BPS.",
        False, "K-003,K-006,K-011,K-013,K-021",
    )

    df = pd.DataFrame(rows)
    df = df.sort_values(["pasangan_id", "periode", "rincian_utama", "rincian_pembanding"]).reset_index(drop=True)
    for kolom in ["kategori_selisih", "kategori_konsep"]:
        buruk = df[~df[kolom].isin(KATEGORI_REKONSILIASI)]
        if not buruk.empty:
            raise ValueError(f"Kategori rekonsiliasi tidak dikenal pada {kolom}: {sorted(buruk[kolom].unique())}")
    return df


def simpan_gold(tables: dict[str, pd.DataFrame]) -> dict[str, Path]:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    panel = tables["panel_provinsi"]
    nasional = tables["nasional_periode_seri"]
    rekon = tables["rekonsiliasi_nasional"]

    panel.to_csv(PANEL_CSV, index=False, lineterminator="\n")
    panel.to_parquet(GOLD_DIR / "panel_provinsi.parquet", index=False)
    nasional.to_csv(NASIONAL_CSV, index=False, lineterminator="\n")
    nasional.to_parquet(GOLD_DIR / "nasional_periode_seri.parquet", index=False)
    rekon.to_csv(REKON_CSV, index=False, lineterminator="\n")
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
