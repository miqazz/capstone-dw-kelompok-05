#!/usr/bin/env python3
"""Audit keterlacakan temuan Sprint 1 dari data/silver/silver.csv.

Jalankan dari root repository:
    python sprint/sprint-1/capstone/audit_profil.py

Skrip hanya menggunakan artefak Silver yang di-commit. Data mentah yang
berada di data/raw/ tidak diperlukan untuk menjalankan audit ini.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SILVER = ROOT / "data" / "silver" / "silver.csv"
OUTPUT = ROOT / "sprint" / "sprint-1" / "capstone" / "audit_profil.txt"
KEY = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]


def fmt_list(values):
    return ", ".join(str(v) for v in values) if values else "(tidak ada)"


def main():
    df = pd.read_csv(SILVER, dtype={"wilayah_kode": str, "periode": str})
    required = set(KEY + ["nilai", "satuan", "nama_wilayah", "jenis_periode"])
    missing_cols = sorted(required - set(df.columns))
    if missing_cols:
        raise SystemExit(f"Kolom Silver tidak lengkap: {missing_cols}")
    df["nilai"] = pd.to_numeric(df["nilai"], errors="raise")
    lines = [
        "AUDIT PROFIL SPRINT 1",
        "Sumber: data/silver/silver.csv (artefak Silver yang di-commit)",
        "Cara menjalankan: python sprint/sprint-1/capstone/audit_profil.py",
        "",
        "A. RINGKASAN SILVER",
        f"total_baris={len(df)}",
        f"jumlah_seri={df['seri_kode'].nunique()}",
        f"jumlah_wilayah_unik={df['wilayah_kode'].nunique()} (termasuk kode nasional 9999 bila ada)",
        f"duplikat_kunci={int(df.duplicated(KEY).sum())}",
        "",
        "B. PANEL BPS (hanya provinsi; kode 9999/INDONESIA dikecualikan)",
    ]

    for seri in ["var1402", "var1477", "var2279"]:
        x = df[(df["sumber"] == "bps") & (df["seri_kode"] == seri) & (df["wilayah_kode"] != "9999")].copy()
        years = sorted(x["periode"].unique(), key=int)
        provinces = sorted(x["wilayah_kode"].unique(), key=int)
        details = sorted(x["rincian"].dropna().unique())
        expected = len(provinces) * len(years) * len(details)
        observed = x[["wilayah_kode", "periode", "rincian"]].drop_duplicates().shape[0]
        gaps = []
        present = set(map(tuple, x[["wilayah_kode", "periode", "rincian"]].itertuples(index=False, name=None)))
        for w in provinces:
            for y in years:
                for d in details:
                    if (w, y, d) not in present:
                        gaps.append((w, y, d))
        lines += [
            f"\n[{seri}]",
            f"baris_provinsi={len(x)}",
            f"rentang_periode={years[0]}..{years[-1]} (jumlah_tahun={len(years)})" if years else "rentang_periode=(kosong)",
            f"jumlah_provinsi_teramati={len(provinces)}",
            f"rincian={len(details)}: {fmt_list(details)}",
            f"expected={expected} = {len(provinces)} x {len(years)} x {len(details)}",
            f"observed={observed}",
            f"missing_sel={expected-observed}",
        ]
        if seri in ("var1402", "var2279"):
            pairs = sorted({(w, y) for w, y, _ in gaps}, key=lambda z: (int(z[0]), int(z[1])))
            lines.append("daftar_wilayah_periode_tidak_ada=" + fmt_list([f"{w}:{y}" for w, y in pairs]))
        if seri == "var1477":
            counts = x.groupby(["wilayah_kode", "periode"])["rincian"].nunique()
            incomplete = counts[counts < len(details)]
            lines.append(f"kombinasi_wilayah_tahun_tidak_lengkap={len(incomplete)}")
            lines.append("distribusi_jumlah_rincian=" + fmt_list([f"{n} rincian: {int(c)} kombinasi" for n, c in sorted(counts.value_counts().items())]))
            lines.append("rincian_kurang_per_wilayah_tahun=" + fmt_list([f"{w}:{y}={int(n)}" for (w, y), n in incomplete.items()]))
            missing_prov = sorted(set(["9200", "9500", "9600", "9700"]) - set(provinces))
            lines.append("kode_pemekaran_tidak_muncul_dalam_seri=" + fmt_list(missing_prov))
            nat = df[(df["sumber"] == "bps") & (df["seri_kode"] == seri) & (df["wilayah_kode"] == "9999")]
            lines.append(f"baris_nasional={len(nat)}; periode_nasional={fmt_list(sorted(nat['periode'].unique(), key=int))}")
            national_details = sorted(nat["rincian"].unique())
            lines.append("rincian_nasional_tersedia=" + fmt_list(national_details))
            all_detail = sorted(x["rincian"].unique())
            lines.append("rincian_nasional_tidak_tersedia=" + fmt_list(sorted(set(all_detail) - set(national_details))))
            lines.append("catatan: daftar rincian nasional dibandingkan dengan daftar rincian seri provinsi; ketidaktersediaan nasional bukan bukti bahwa profesi tidak ada.")
        vals = x["nilai"]
        if len(vals):
            lines.append(f"nilai_min={vals.min():g}; nilai_max={vals.max():g}; satuan_tercantum={fmt_list(sorted(x['satuan'].dropna().unique()))}")

    lines += ["", "C. SERI WHO NASIONAL (kode wilayah 9999)"]
    who_series = ["FINPROTECTION_CATA_TOT_10_POP", "HWF_0001", "HWF_0006", "UHC_INDEX_REPORTED"]
    for seri in who_series:
        x = df[(df["sumber"] == "who_gho") & (df["seri_kode"] == seri) & (df["wilayah_kode"] == "9999")]
        years = sorted({int(y) for y in x["periode"]})
        if not years:
            continue
        missing_years = sorted(set(range(years[0], years[-1] + 1)) - set(years))
        lines += [
            f"\n[{seri}]",
            f"jumlah_observasi={len(x)}",
            f"rentang_periode={years[0]}..{years[-1]} (jumlah_tahun_dalam_rentang={years[-1]-years[0]+1})",
            f"tahun_hilang={len(missing_years)}: {fmt_list(missing_years)}",
            f"nilai_min={x['nilai'].min():g}; nilai_max={x['nilai'].max():g}; satuan={fmt_list(sorted(x['satuan'].dropna().unique()))}",
        ]
        if seri == "HWF_0006":
            by_year = x.assign(tahun=x["periode"].astype(int)).set_index("tahun")["nilai"].sort_index()
            if 2018 in by_year.index and 2019 in by_year.index:
                delta = by_year.loc[2019] - by_year.loc[2018]
                pct = (by_year.loc[2019] / by_year.loc[2018] - 1) * 100
                lines.append(f"perubahan_2018_ke_2019={by_year.loc[2018]:g} -> {by_year.loc[2019]:g}; selisih={delta:.2f}; perubahan_persen={pct:.2f}%")
                lines.append("interpretasi=indikasi perubahan tajam yang perlu verifikasi metadata; bukan otomatis kesalahan data atau bukti patahan definisi.")

    lines += [
        "",
        "D. BATASAN KETERLACAKAN",
        "Audit ini menghitung ulang angka dari Silver yang di-commit. Data mentah di data/raw/ dikecualikan oleh .gitignore.",
        "Karena itu, jumlah baris mentah FINPROTECTION dan jumlah kombinasi dimensi sebelum filter tidak dihitung ulang oleh skrip ini.",
        "Angka tersebut hanya boleh dicantumkan sebagai informasi snapshot jika manifest/metadata sumber yang mendukung ikut disimpan sebagai artefak yang dapat diperiksa.",
        "Metadata definisi profesi WHO dan satuan var1477 perlu dirujuk ke dokumentasi/metadata sumber; audit numerik Silver tidak membuktikan kesetaraan definisi profesi.",
    ]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nTERSIMPAN: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
