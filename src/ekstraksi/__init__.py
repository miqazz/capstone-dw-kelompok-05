"""Tahap 1 — Ekstraksi seluruh data mentah BPS dan WHO."""

import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, baca as baca_manifest, periksa, sha256_raw
from . import who


def _lineage(df, berkas):
    """Menambahkan informasi asal berkas dan SHA-256."""
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas)
    return df


def _baca_bps_csv(path):
    """Membaca CSV BPS dengan mempertahankan kolom aslinya."""
    path = Path(path)
    berkas = path.relative_to(RAW).as_posix()

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )

    return _lineage(df, berkas)


def _baca_bps_json(path):
    """Menguraikan JSON WebAPI BPS menjadi baris berdasarkan dimensinya."""
    path = Path(path)
    berkas = path.relative_to(RAW).as_posix()

    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        raise ValueError(f"Struktur JSON BPS tidak sesuai: {path.name}")

    item = data[0]
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
                            wilayah, seri, rincian, tahun, jenis
                        )

    hasil = []

    for kode, nilai in item["datacontent"].items():
        if kode not in indeks:
            raise ValueError(
                f"Kode datacontent tidak dikenali: {kode} "
                f"pada {path.name}"
            )

        wilayah, seri, rincian, tahun, jenis = indeks[kode]

        hasil.append({
            "vervar_val": wilayah["val"],
            "vervar_label": wilayah["label"],
            "var_val": seri["val"],
            "var_label": seri["label"],
            "var_unit": seri.get("unit", ""),
            "turvar_val": rincian["val"],
            "turvar_label": rincian["label"],
            "tahun_val": tahun["val"],
            "tahun_label": tahun["label"],
            "turtahun_val": jenis["val"],
            "turtahun_label": jenis["label"],
            "nilai": nilai,
            "status": item.get("status"),
            "data-availability": item.get("data-availability"),
            "last_update": item.get("last_update"),
            "subject": item.get("subject"),
        })

    df = pd.DataFrame(hasil)
    return _lineage(df, berkas)


def _baca_manifest_asal(path):
    """Membaca metadata asal unduhan BPS sebagai satu baris."""
    path = Path(path)
    berkas = path.relative_to(RAW).as_posix()

    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Struktur manifest_asal.json tidak sesuai.")

    return _lineage(pd.DataFrame([data]), berkas)


def jalankan():
    """Menggabungkan keluaran seluruh pembaca BPS dan WHO."""

    jumlah, salah = periksa()

    if salah:
        raise ValueError(
            f"Pemeriksaan SHA-256 gagal untuk berkas: {salah}"
        )

    manifest = baca_manifest()
    hasil = {}

    # Membaca seluruh berkas BPS yang tercatat di manifest.
    for berkas in sorted(manifest):
        if not berkas.startswith("bps/"):
            continue

        path = Path(RAW) / berkas

        if path.name == "manifest_asal.json":
            df = _baca_manifest_asal(path)
            nama = "bps_manifest_asal"

        elif path.suffix.lower() == ".csv":
            df = _baca_bps_csv(path)
            nama = f"bps_csv_{path.stem}"

        elif path.suffix.lower() == ".json":
            df = _baca_bps_json(path)
            nama = f"bps_json_{path.stem}"

        else:
            raise ValueError(f"Format BPS tidak didukung: {berkas}")

        hasil[nama] = df
        print(f"BPS  {path.name}: {len(df)} baris")

    # Membaca seluruh berkas WHO menggunakan pembaca yang sudah ada.
    hasil_who = who.jalankan()
    hasil.update({
        f"who_{nama}": df
        for nama, df in hasil_who.items()
    })

    # Memastikan semua berkas dalam manifest sudah dibaca.
    terbaca = set()

    for df in hasil.values():
        if "_berkas_raw" in df.columns:
            terbaca.update(df["_berkas_raw"].dropna().astype(str))

    terlewat = sorted(set(manifest) - terbaca)
    tambahan = sorted(terbaca - set(manifest))

    if terlewat or tambahan:
        raise ValueError(
            f"Cakupan ekstraksi tidak sesuai. "
            f"Terlewat: {terlewat}; tambahan: {tambahan}"
        )

    total_baris = sum(len(df) for df in hasil.values())

    print("\nRINGKASAN EKSTRAKSI")
    print("Berkas dalam manifest:", jumlah)
    print("Berkas berhasil dibaca:", len(terbaca))
    print("Total kelompok keluaran:", len(hasil))
    print("Total baris:", total_baris)
    print("Cakupan manifest: LOLOS")

    return hasil
