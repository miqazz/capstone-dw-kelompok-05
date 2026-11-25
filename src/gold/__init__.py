"""Tahap Gold — Pembentukan panel provinsi dari data Silver."""

from pathlib import Path
import re
import unicodedata

import pandas as pd


JALUR_GOLD = Path("data/gold/panel_provinsi.parquet")

SERI_UTAMA = ["var1402", "var2279", "var1477"]

# Empat provinsi hasil pemekaran Papua.
PROVINSI_BARU = {9200, 9500, 9600, 9700}


def _slug(teks):
    """Mengubah nama profesi menjadi kode indikator."""
    teks = unicodedata.normalize("NFKD", str(teks))
    teks = teks.encode("ascii", "ignore").decode("ascii")
    teks = re.sub(r"[^a-zA-Z0-9]+", "_", teks.lower())
    return teks.strip("_")


def _status_kosong(seri, kode, periode, rincian, kategori_periode):
    """Menentukan status sel kosong berdasarkan keputusan wrangling."""

    tahun = int(periode)

    if seri == "var1402":
        if kode in PROVINSI_BARU and tahun <= 2021:
            return "struktural"
        if kode in PROVINSI_BARU and tahun in (2022, 2023):
            return "missing"

    elif seri == "var2279":
        if kode in PROVINSI_BARU and tahun == 2022:
            return "missing"

    elif seri == "var1477":
        if kode in PROVINSI_BARU:
            return "struktural"

        if rincian not in kategori_periode.get(periode, set()):
            return "kategori_tidak_tersedia"

    return "missing"


def jalankan(silver):
    """Membentuk panel provinsi dari Silver dan menyimpannya sebagai Parquet."""

    df = silver.copy()

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input Gold harus berupa DataFrame Silver.")

    wajib = {
        "seri_kode", "wilayah_kode", "nama_wilayah",
        "periode", "rincian", "nilai", "satuan",
        "_berkas_raw", "_sha256_raw"
    }

    kolom_hilang = wajib - set(df.columns)
    if kolom_hilang:
        raise ValueError(f"Kolom Silver tidak ditemukan: {sorted(kolom_hilang)}")

    df = df[df["seri_kode"].isin(SERI_UTAMA)].copy()
    df = df[df["wilayah_kode"] != 9999].copy()

    # Daftar wilayah diambil langsung dari Silver.
    wilayah = (
        df[["wilayah_kode", "nama_wilayah"]]
        .drop_duplicates()
        .sort_values("wilayah_kode")
    )

    if wilayah["wilayah_kode"].duplicated().any():
        raise ValueError("Satu kode wilayah memiliki lebih dari satu nama.")

    if len(wilayah) != 38:
        raise ValueError(
            f"Jumlah provinsi Silver seharusnya 38, ditemukan {len(wilayah)}."
        )

    hasil = []

    for seri in SERI_UTAMA:
        sumber = df[df["seri_kode"] == seri].copy()

        periode_list = sorted(sumber["periode"].astype(str).unique())

        if seri == "var1477":
            rincian_list = sorted(sumber["rincian"].unique())
            kategori_periode = {
                periode: set(
                    sumber.loc[
                        sumber["periode"].astype(str) == periode, "rincian"
                    ].unique()
                )
                for periode in periode_list
            }
        else:
            rincian_list = ["Tidak ada"]
            kategori_periode = {}

        # Memastikan tidak ada observasi Silver dengan kunci ganda.
        kunci_sumber = ["wilayah_kode", "periode", "rincian"]
        if sumber.duplicated(subset=kunci_sumber).any():
            raise ValueError(f"Ditemukan kunci Silver ganda pada {seri}.")

        lookup = {
            (int(row["wilayah_kode"]), str(row["periode"]), row["rincian"]): row
            for row in sumber.to_dict("records")
        }

        for provinsi in wilayah.itertuples(index=False):
            kode = int(provinsi.wilayah_kode)
            nama = provinsi.nama_wilayah

            for periode in periode_list:
                for rincian in rincian_list:
                    observasi = lookup.get((kode, periode, rincian))

                    if observasi is not None:
                        nilai_asli = float(observasi["nilai"])
                        satuan_asli = observasi["satuan"]

                        # Konversi kepadatan dari per 100.000 menjadi per 10.000.
                        if seri == "var1477":
                            nilai = nilai_asli / 10
                            satuan = "per_10000_penduduk"
                        else:
                            nilai = nilai_asli
                            satuan = satuan_asli

                        status = "terisi"
                        berkas_raw = observasi["_berkas_raw"]
                        sha256_raw = observasi["_sha256_raw"]

                    else:
                        nilai_asli = float("nan")
                        satuan_asli = (
                            "per_100000_penduduk"
                            if seri == "var1477"
                            else "persen"
                        )
                        nilai = float("nan")
                        satuan = (
                            "per_10000_penduduk"
                            if seri == "var1477"
                            else satuan_asli
                        )

                        status = _status_kosong(
                            seri, kode, periode, rincian, kategori_periode
                        )
                        berkas_raw = None
                        sha256_raw = None

                    indikator = (
                        f"var1477_{_slug(rincian)}"
                        if seri == "var1477"
                        else seri
                    )

                    hasil.append({
                        "wilayah_kode": kode,
                        "nama_wilayah": nama,
                        "periode": periode,
                        "indikator": indikator,
                        "seri_kode": seri,
                        "rincian": rincian,
                        "nilai_asli": nilai_asli,
                        "satuan_asli": satuan_asli,
                        "nilai": nilai,
                        "satuan": satuan,
                        "status": status,
                        "_berkas_raw": berkas_raw,
                        "_sha256_raw": sha256_raw,
                    })

    panel = pd.DataFrame(hasil)

    kunci_panel = ["wilayah_kode", "periode", "indikator"]

    if panel.duplicated(subset=kunci_panel).any():
        raise ValueError("Ditemukan kunci panel Gold yang duplikat.")

    # Memastikan semua nilai terisi memiliki lineage.
    terisi = panel["status"] == "terisi"
    if panel.loc[terisi, ["_berkas_raw", "_sha256_raw"]].isna().any().any():
        raise ValueError("Ada nilai Gold terisi tanpa lineage Silver.")

    # Memastikan sel kosong tidak diberi nilai buatan.
    kosong = ~terisi
    if panel.loc[kosong, "nilai"].notna().any():
        raise ValueError("Sel kosong memiliki nilai yang tidak semestinya.")

    panel = panel.sort_values(
        ["seri_kode", "wilayah_kode", "periode", "indikator"]
    ).reset_index(drop=True)

    JALUR_GOLD.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(JALUR_GOLD, index=False)

    print(f"Gold panel berhasil disimpan: {JALUR_GOLD}")
    print(f"Jumlah baris Gold: {len(panel)}")
    print(f"Jumlah indikator panel: {panel['indikator'].nunique()}")
    print("\nRingkasan status:")
    print(panel["status"].value_counts().to_string())

    return {"panel_provinsi": panel}
