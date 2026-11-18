#!/usr/bin/env python3
"""Muat Silver pertama (tahap 5) ke CSV dan SQLite.

Ekstraksi minimal dari berkas mentah BPS/WHO -> tabel Silver ber-skema minimal,
lalu simpan ke data/silver/silver.csv dan data/silver/silver.sqlite.
Jalankan dari root repo: python3 sprint/sprint-1/capstone/muat_silver_pertama.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"

KOLOM = [
    "sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode",
    "jenis_periode", "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw",
]
KUNCI = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def baca_manifest():
    with open(RAW / "MANIFEST.csv", encoding="utf-8") as f:
        return {r["berkas"]: r["sha256"] for r in csv.DictReader(f)}


def sha256_raw(berkas: str, manifest: dict) -> str:
    try:
        return manifest[berkas]
    except KeyError as e:
        raise KeyError(f"{berkas} tidak ada di MANIFEST.csv") from e


def fnum(x):
    # simpan sebagai string angka stabil; validasi tipe numerik sederhana
    if x is None or x == "":
        return None
    s = str(x).strip()
    float(s)
    if "." in s:
        s = s.rstrip("0").rstrip(".") or "0"
    return s


def baris(out, sumber, seri, wk, nw, periode, jp, rincian, nilai, satuan, berkas, manifest):
    out.append({
        "sumber": sumber,
        "seri_kode": seri,
        "wilayah_kode": str(int(wk)),
        "nama_wilayah": nw,
        "periode": str(periode),
        "jenis_periode": jp,
        "rincian": rincian if rincian not in (None, "") else "TOTAL",
        "nilai": fnum(nilai),
        "satuan": satuan or "",
        "_berkas_raw": berkas,
        "_sha256_raw": sha256_raw(berkas, manifest),
    })


def ekstrak_bps(manifest):
    out = []
    specs = [
        ("bps/2026-10-20/sdg3_3_8_1_a_v1402.csv", "bps", "var1402", None),
        ("bps/2026-10-20/sdg3_3_8_2_a_v2279.csv", "bps", "var2279", None),
        ("bps/2026-10-20/sdg3_3_c_1_v1477.csv", "bps", "var1477", "kepadatan per 100.000 penduduk"),
    ]
    for berkas, sumber, seri, satuan_override in specs:
        with open(RAW / berkas, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                satuan = satuan_override if satuan_override is not None else (r.get("satuan") or "")
                rinc = r.get("turvar") or "TOTAL"
                jp = "tahun"  # periode label 'Tahun'
                baris(out, sumber, seri, r["wilayah_id"], r["wilayah"], r["tahun"], jp,
                      rinc, r["nilai"], satuan, berkas, manifest)
    return out


def ekstrak_who(manifest):
    out = []
    # UHC
    berkas = "who_gho/2026-10-20/datadot/9A706FD_UHC_INDEX_REPORTED.csv"
    with open(RAW / berkas, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("DIM_GEO_CODE_M49") != "360":
                continue
            baris(out, "who_gho", "UHC_INDEX_REPORTED", 9999, "INDONESIA", r["DIM_TIME"], "tahun",
                  "TOTAL", r["INDEX_N"], "indeks (skor cakupan layanan UHC, 0-100)", berkas, manifest)
    # FINPROTECTION total only
    berkas = "who_gho/2026-10-20/datadot/A65146D_FINPROTECTION_CATA_TOT_10_POP.csv"
    with open(RAW / berkas, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("DIM_GEO_CODE_M49") != "360":
                continue
            if r.get("DIM_DEG_URB") != "TOTAL":
                continue
            if any(r.get(d) for d in ["DIM_SEX", "DIM_AGE", "DIM_HOUSEHOLD_COMP_BY_AGE", "DIM_POP_TYPE"]):
                continue
            baris(out, "who_gho", "FINPROTECTION_CATA_TOT_10_POP", 9999, "INDONESIA", r["DIM_TIME"], "tahun",
                  "TOTAL", r["PERCENT_POP_N"], "persen populasi", berkas, manifest)
    # HWF
    for berkas, seri in [
        ("who_gho/2026-10-20/datadot/217795A_HWF_0001.csv", "HWF_0001"),
        ("who_gho/2026-10-20/datadot/5C8435F_HWF_0006.csv", "HWF_0006"),
    ]:
        with open(RAW / berkas, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("DIM_GEO_CODE_M49") != "360":
                    continue
                baris(out, "who_gho", seri, 9999, "INDONESIA", r["DIM_TIME"], "tahun",
                      "TOTAL", r["RATE_PER_10000_N"], "per 10.000 penduduk", berkas, manifest)
    return out


def tulis_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=KOLOM)
        w.writeheader()
        w.writerows(rows)


def muat_sqlite(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript(open(ROOT / "sprint/sprint-1/capstone/silver_ddl.sql", encoding="utf-8").read())
    cur.executemany(
        "INSERT INTO silver (" + ",".join(KOLOM) + ") VALUES (" + ",".join(["?"] * len(KOLOM)) + ")",
        [tuple(r[k] for k in KOLOM) for r in rows],
    )
    con.commit()
    n = cur.execute("SELECT COUNT(*) FROM silver").fetchone()[0]
    con.close()
    return n


def profil(rows):
    by_seri = defaultdict(list)
    for r in rows:
        by_seri[(r["sumber"], r["seri_kode"])].append(r)
    lines = []
    lines.append(f"total_baris\t{len(rows)}")
    lines.append(f"jumlah_seri\t{len(by_seri)}")
    lines.append(f"jumlah_wilayah\t{len({r['wilayah_kode'] for r in rows})}")
    for (sumber, seri), rs in sorted(by_seri.items()):
        years = sorted({r["periode"] for r in rs})
        wils = sorted({r["wilayah_kode"] for r in rs})
        prov = [w for w in wils if w != "9999"]
        turvar = sorted({r["rincian"] for r in rs})
        vals = [float(r["nilai"]) for r in rs if r["nilai"] not in (None, "")]
        dup = len(rs) - len({tuple(r[k] for k in KUNCI) for r in rs})
        lines.append(
            f"{sumber}\t{seri}\tbaris={len(rs)}\tperiode={years[0]}..{years[-1]}(n={len(years)})\t"
            f"wilayah={len(wils)}(prov={len(prov)})\trincian={len(turvar)}\t"
            f"nilai_min={min(vals)}\tnilai_max={max(vals)}\tduplikat_kunci={dup}"
        )
    # panel gaps for BPS prov grid
    bps = [r for r in rows if r["sumber"] == "bps"]
    by = defaultdict(list)
    for r in bps:
        by[r["seri_kode"]].append(r)
    for seri, rs in sorted(by.items()):
        prov = sorted({r["wilayah_kode"] for r in rs if r["wilayah_kode"] != "9999"})
        years = sorted({r["periode"] for r in rs})
        turvar = sorted({r["rincian"] for r in rs})
        have = {(r["wilayah_kode"], r["periode"], r["rincian"]) for r in rs if r["wilayah_kode"] != "9999"}
        exp = {(w, y, t) for w in prov for y in years for t in turvar}
        miss = len(exp) - len(have)
        lines.append(f"panel_gap\t{seri}\tprov_teramati={len(prov)}\texpected={len(exp)}\tobserved={len(have)}\tmissing_sel={miss}")
    return "\n".join(lines)


def main():
    manifest = baca_manifest()
    # verifikasi cepat
    for berkas, h in manifest.items():
        p = RAW / berkas
        if not p.exists():
            raise SystemExit(f"hilang: {berkas}")
        hh = sha256_file(p)
        if hh != h:
            raise SystemExit(f"sha256 mismatch: {berkas}")

    rows = ekstrak_bps(manifest) + ekstrak_who(manifest)
    # validasi minimal
    assert rows, "kosong"
    for r in rows:
        for k in KOLOM:
            assert r.get(k) is not None, (k, r)
        float(r["nilai"])
        int(r["wilayah_kode"])
    dup = len(rows) - len({tuple(r[k] for k in KUNCI) for r in rows})
    assert dup == 0, f"duplikat kunci: {dup}"

    csv_path = ROOT / "data/silver/silver.csv"
    db_path = ROOT / "data/silver/silver.sqlite"
    tulis_csv(rows, csv_path)
    n = muat_sqlite(rows, db_path)
    report = profil(rows)
    prof_path = ROOT / "sprint/sprint-1/capstone/profil_ringkasan.txt"
    prof_path.write_text(report + "\n", encoding="utf-8")

    print(f"silver_csv\t{csv_path}\trows={len(rows)}")
    print(f"silver_sqlite\t{db_path}\trows={n}")
    print(report)


if __name__ == "__main__":
    main()
