DROP TABLE IF EXISTS rekonsiliasi_nasional;
DROP TABLE IF EXISTS gold_nasional_periode_seri;
DROP TABLE IF EXISTS gold_panel_provinsi;

CREATE TABLE gold_panel_provinsi (
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
    CHECK (wilayah_kode >= 0 AND wilayah_kode != 9999),
    CHECK (length(_sha256_raw) = 64)
);

CREATE TABLE gold_nasional_periode_seri (
    sumber        TEXT    NOT NULL,
    seri_kode     TEXT    NOT NULL,
    periode       TEXT    NOT NULL,
    jenis_periode TEXT    NOT NULL CHECK (jenis_periode IN ('tahun','semester','triwulan','bulan')),
    rincian       TEXT    NOT NULL,
    nilai         REAL    NOT NULL,
    satuan        TEXT    NOT NULL,
    _berkas_raw   TEXT    NOT NULL,
    _sha256_raw   TEXT    NOT NULL,
    catatan       TEXT,
    asal_angka    TEXT,
    PRIMARY KEY (sumber, seri_kode, periode, rincian, _berkas_raw)
);

CREATE TABLE rekonsiliasi_nasional (
    pasangan_id           TEXT NOT NULL,
    seri_utama            TEXT NOT NULL,
    rincian_utama         TEXT NOT NULL,
    seri_pembanding       TEXT NOT NULL,
    rincian_pembanding    TEXT NOT NULL,
    periode               TEXT NOT NULL,
    jenis_periode         TEXT NOT NULL CHECK (jenis_periode IN ('tahun','semester','triwulan','bulan')),
    nilai_utama           REAL,
    satuan_utama          TEXT,
    nilai_pembanding      REAL,
    satuan_pembanding     TEXT,
    selisih               REAL,
    kategori_selisih      TEXT NOT NULL CHECK (kategori_selisih IN (
        'definisi berbeda','metode berbeda','vintage berbeda','cakupan berbeda','belum terjelaskan'
    )),
    penjelasan            TEXT NOT NULL,
    bukti_dicari          TEXT,
    PRIMARY KEY (pasangan_id, periode, rincian_utama, rincian_pembanding)
);

CREATE INDEX IF NOT EXISTS idx_gold_panel_seri ON gold_panel_provinsi (seri_kode, periode);
CREATE INDEX IF NOT EXISTS idx_gold_nasional_seri ON gold_nasional_periode_seri (seri_kode, periode);
CREATE INDEX IF NOT EXISTS idx_rekon_pasangan ON rekonsiliasi_nasional (pasangan_id, periode);
