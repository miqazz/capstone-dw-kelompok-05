
"""Tahap 1 — Ekstraksi data BPS CSV dan JSON."""

import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw


KOLOM = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "jenis_periode",
    "rincian",
    "nilai",
    "satuan",
    "_berkas_raw",
    "_sha256_raw",
]


def _buat_baris(
    seri, wilayah, tahun, rincian, nilai, satuan, berkas
):
    """Membentuk satu observasi dengan skema Silver minimal."""
    return {
        "sumber": "bps",
        "seri_kode": int(seri),
        "wilayah_kode": int(wilayah[0]),
        "nama_wilayah": str(wilayah[1]),
        "periode": str(tahun),
        "jenis_periode": "tahun",
        "rincian": str(rincian),
        "nilai": pd.to_numeric(nilai, errors="coerce"),
        "satuan": str(satuan or ""),
        "_berkas_raw": berkas,
        "_sha256_raw": sha256_raw(berkas),
    }


def baca_csv(path):
    """Membaca satu berkas CSV BPS menjadi tabel panjang."""
    path = Path(path)
    berkas = path.relative_to(RAW).as_posix()

    df = pd.read_csv(path, encoding="utf-8-sig")

    hasil = []
    for row in df.to_dict("records"):
        wilayah = (row["wilayah_id"], row["wilayah"])
        hasil.append(
            _buat_baris(
                seri=row["var_id"],
                wilayah=wilayah,
                tahun=row["tahun"],
                rincian=row["turvar"],
                nilai=row["nilai"],
                satuan=row["satuan"],
                berkas=berkas,
            )
        )

    print(f"CSV  {path.name}: {len(hasil)} baris")
    return pd.DataFrame(hasil, columns=KOLOM)


def baca_json(path):
    """Membaca JSON WebAPI BPS dengan menguraikan kode datacontent."""
    path = Path(path)
    berkas = path.relative_to(RAW).as_posix()

    with open(path, encoding="utf-8") as f:
        item = json.load(f)[0]

    # Membuat peta kode gabungan ke metadata dimensinya.
    indeks = {}

    for wilayah in item["vervar"]:
        for seri in item["var"]:
            for rincian in item["turvar"]:
                for tahun in item["tahun"]:
                    for jenis in item["turtahun"]:
                        kode = (
                            str(wilayah["val"])
                            + str(seri["val"])
                            + str(rincian["val"])
                            + str(tahun["val"])
                            + str(jenis["val"])
                        )

                        indeks[kode] = (
                            wilayah,
                            seri,
                            rincian,
                            tahun,
                            jenis,
                        )

    hasil = []

    for kode, nilai in item["datacontent"].items():
        if kode not in indeks:
            raise ValueError(
                f"Kode datacontent tidak dikenali: {kode} pada {path.name}"
            )

        wilayah, seri, rincian, tahun, jenis = indeks[kode]

        hasil.append(
            _buat_baris(
                seri=seri["val"],
                wilayah=(wilayah["val"], wilayah["label"]),
                tahun=tahun["label"],
                rincian=rincian["label"],
                nilai=nilai,
                satuan=seri.get("unit", ""),
                berkas=berkas,
            )
        )

    print(f"JSON {path.name}: {len(hasil)} baris")
    return pd.DataFrame(hasil, columns=KOLOM)


def jalankan():
    """Kembalikan DataFrame hasil ekstraksi CSV dan JSON BPS."""
    folder_bps = RAW / "bps"

    berkas_csv = sorted(folder_bps.rglob("*_v*.csv"))
    berkas_json = sorted(folder_bps.rglob("*_v*.json"))

    if not berkas_csv or not berkas_json:
        raise FileNotFoundError("Berkas CSV atau JSON BPS tidak ditemukan.")

    hasil_csv = [baca_csv(p) for p in berkas_csv]
    hasil_json = [baca_json(p) for p in berkas_json]

    return {
        "bps_csv": pd.concat(hasil_csv, ignore_index=True),
        "bps_json": pd.concat(hasil_json, ignore_index=True),
    }
