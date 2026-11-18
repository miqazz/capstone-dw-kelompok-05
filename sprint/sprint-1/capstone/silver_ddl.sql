-- Skema Silver minimal (tahap 5) - SQLite
-- Muat dengan: python3 sprint/sprint-1/capstone/muat_silver_pertama.py

DROP TABLE IF EXISTS silver;

CREATE TABLE silver (
    sumber        TEXT    NOT NULL,  -- bps | who_gho | wdi | bnpb | ilostat
    seri_kode     TEXT    NOT NULL,  -- kode seri/indikator di sumber
    wilayah_kode  INTEGER NOT NULL,  -- 9999 = Indonesia, provinsi = kode BPS x 100
    nama_wilayah  TEXT    NOT NULL,
    periode       TEXT    NOT NULL,  -- format sesuai jenis_periode (mis. 2020)
    jenis_periode TEXT    NOT NULL CHECK (jenis_periode IN ('tahun','semester','triwulan','bulan')),
    rincian       TEXT    NOT NULL,  -- turunan/rincian; 'TOTAL' bila tidak ada
    nilai         REAL    NOT NULL,  -- nilai numerik observasi yang ada (tanpa baris kosong)
    satuan        TEXT    NOT NULL,  -- satuan/format nilai (dikonfirmasi dari metadata bila perlu)
    _berkas_raw   TEXT    NOT NULL,  -- jalur relatif terhadap data/raw/
    _sha256_raw   TEXT    NOT NULL,  -- sha256 berkas mentah (dari MANIFEST.csv)
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw),
    CHECK (wilayah_kode >= 0),
    CHECK (length(_sha256_raw) = 64)
);

CREATE INDEX idx_silver_seri_periode ON silver (seri_kode, periode);
CREATE INDEX idx_silver_wilayah ON silver (wilayah_kode);
CREATE INDEX idx_silver_berkas ON silver (_berkas_raw);
