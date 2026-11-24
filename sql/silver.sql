DROP TABLE IF EXISTS silver;

CREATE TABLE silver (
    sumber        TEXT    NOT NULL,
    seri_kode     TEXT    NOT NULL,
    wilayah_kode  INTEGER NOT NULL,
    nama_wilayah  TEXT    NOT NULL,
    periode       TEXT    NOT NULL,
    jenis_periode TEXT    NOT NULL CHECK (jenis_periode IN ('tahun','semester','triwulan','bulan')),
    rincian       TEXT    NOT NULL,
    nilai         REAL    NOT NULL,
    satuan        TEXT    NOT NULL,
    _berkas_raw   TEXT    NOT NULL,
    _sha256_raw   TEXT    NOT NULL,
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw),
    CHECK (wilayah_kode >= 0),
    CHECK (length(_sha256_raw) = 64)
);

CREATE INDEX IF NOT EXISTS idx_silver_seri_periode ON silver (seri_kode, periode);
CREATE INDEX IF NOT EXISTS idx_silver_wilayah ON silver (wilayah_kode);
CREATE INDEX IF NOT EXISTS idx_silver_berkas ON silver (_berkas_raw);
