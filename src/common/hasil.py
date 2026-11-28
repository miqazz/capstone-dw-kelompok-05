"""Berkas hasil anggota untuk Workbench: results/<nim>/metrics.json.

    python -m src.common.hasil
    python -m src.common.hasil 124450019 pasangan_rekonsiliasi=4 selisih_median=2.9

Tanpa argumen, semua berkas hasil yang sudah ada ditulis ulang dari data Silver/Gold/rekonsiliasi
untuk metrik yang memang dapat dihitung ulang. Metrik Sprint 1 yang tidak memiliki sumber
perhitungan di repository dipertahankan apa adanya, bukan dihapus atau diubah.
"""
import hashlib
import json
import platform
import sys
from pathlib import Path

from src.common.manifest import RAW, baca

ROOT = Path(__file__).resolve().parents[2]
HASIL_DIR = ROOT / "results"


def data_hash(raw=RAW):
    """sha256 dari pasangan berkas:sha256 di MANIFEST.csv, terurut."""
    h = hashlib.sha256()
    for berkas, sha in sorted(baca(Path(raw)).items()):
        h.update(f"{berkas}:{sha}\n".encode())
    return h.hexdigest()


def _baca_isi(nim) -> dict:
    tujuan = HASIL_DIR / str(nim) / "metrics.json"
    if not tujuan.exists():
        return {}
    return json.loads(tujuan.read_text(encoding="utf-8"))


def baca_metrik(nim) -> dict:
    return _baca_isi(nim).get("metrik", {})


def tulis_hasil(nim, metrik, seed=0, durasi_detik=None, raw=RAW, gabung=True):
    if not metrik or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in metrik.values()):
        raise ValueError("metrik harus berisi minimal satu angka, dan semua nilainya angka")
    lama = _baca_isi(nim) if gabung else {}
    akhir = dict(lama.get("metrik", {})) if gabung else {}
    akhir.update(metrik)
    if not akhir or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in akhir.values()):
        raise ValueError("metrik gabungan harus berisi angka")
    isi = {"metrik": akhir, "seed": int(seed), "data_hash": data_hash(raw),
           "perangkat": f"{platform.system()} {platform.machine()} Python {platform.python_version()}"}
    if durasi_detik is not None:
        isi["durasi_detik"] = round(float(durasi_detik), 2)
    elif gabung and "durasi_detik" in lama:
        isi["durasi_detik"] = lama["durasi_detik"]
    tujuan = HASIL_DIR / str(nim) / "metrics.json"
    tujuan.parent.mkdir(parents=True, exist_ok=True)
    tujuan.write_text(json.dumps(isi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return tujuan


def metrik_dari_data() -> dict:
    """Metrik yang dihitung ulang dari Silver, Gold, dan tabel rekonsiliasi."""
    import pandas as pd

    silver = pd.read_parquet(ROOT / "data/silver/silver.parquet")
    panel = pd.read_parquet(ROOT / "data/gold/panel_provinsi.parquet")
    nasional = pd.read_parquet(ROOT / "data/gold/nasional_periode_seri.parquet")
    rekon = pd.read_parquet(ROOT / "data/gold/rekonsiliasi_nasional.parquet")
    selisih = pd.to_numeric(rekon["selisih"], errors="coerce").dropna()
    if selisih.empty:
        raise ValueError("Tidak ada selisih numerik pada tabel rekonsiliasi")
    return {
        "baris_silver": int(len(silver)),
        "baris_gold_panel": int(len(panel)),
        "baris_gold_nasional": int(len(nasional)),
        "pasangan_rekonsiliasi": int(rekon["pasangan_id"].nunique()),
        "periode_beririsan": int(
            (rekon["nilai_utama"].notna() & rekon["nilai_pembanding"].notna()).sum()
        ),
        "selisih_median": round(float(selisih.median()), 10),
    }


def _metrik_turunan() -> dict[str, dict]:
    """Turunan tambahan yang masih dapat ditarik dari artefak yang tersedia."""
    import pandas as pd

    hasil = {}
    silver = pd.read_parquet(ROOT / "data/silver/silver.parquet")
    bps = silver[silver["sumber"] == "bps"]
    hasil["124450085"] = {
        "seri_silver": int(bps["seri_kode"].nunique()),
        "rincian_dienkode": int(bps.loc[bps["seri_kode"] == "var1477", "rincian"].nunique()),
        "baris_silver": int(len(bps)),
    }
    hasil["124450092"] = {
        "baris_silver": int(len(silver)),
        "sel_kosong_grid": int(len(pd.read_csv(ROOT / "reports/individu/missing_panel_124450092.csv"))),
        "outlier_ditandai": int(len(pd.read_csv(ROOT / "reports/klasifikasi_anomali.csv"))),
    }
    manifest = baca()
    hasil["124450052"] = {
        "berkas_dibaca": int(len(manifest)),
        "format": int(len({Path(k).suffix.lstrip(".").lower() for k in manifest})),
    }
    try:
        from src.ekstraksi import jalankan as baca_mentah
        hasil.setdefault("124450019", {})["baris_masuk"] = int(
            sum(len(df) for df in baca_mentah().values())
        )
    except (FileNotFoundError, KeyError):
        pass
    return hasil


def tulis_semua():
    """Tulis ulang seluruh metrics.json yang sudah ada dengan metrik turunan data."""
    data = metrik_dari_data()
    turunan = _metrik_turunan()
    ditulis = []
    for tujuan in sorted(HASIL_DIR.glob("*/metrics.json")):
        nim = tujuan.parent.name
        lama = _baca_isi(nim)
        metrik = dict(lama.get("metrik", {}))
        metrik.update(turunan.get(nim, {}))
        if nim == "124450019":
            metrik.update(data)
        if not metrik:
            continue
        ditulis.append(tulis_hasil(nim, metrik, seed=lama.get("seed", 0)))
    return ditulis


if __name__ == "__main__":
    if len(sys.argv) == 1:
        for jalur in tulis_semua():
            isi = json.loads(jalur.read_text(encoding="utf-8"))
            print(f"{jalur.relative_to(ROOT).as_posix()}: {json.dumps(isi['metrik'], ensure_ascii=False)}")
    else:
        if len(sys.argv) < 3:
            sys.exit("pakai: python -m src.common.hasil [<nim> nama=angka ...]")
        nim, pasangan = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
        seed = int(pasangan.pop("seed", 0))
        print(tulis_hasil(nim, {k: float(v) if "." in v else int(v) for k, v in pasangan.items()}, seed=seed))
