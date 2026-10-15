-- 003: Tambah kolom role ke student_dpt + tabel vote_receipts
-- Dijalankan setelah 002

-- ---------------------------------------------------------------------------
-- 1. Kolom role untuk student_dpt (enum)
-- ---------------------------------------------------------------------------
CREATE TYPE userrole AS ENUM ('student', 'admin', 'auditor');

ALTER TABLE student_dpt
    ADD COLUMN IF NOT EXISTS role userrole NOT NULL DEFAULT 'student';

-- Index untuk query role
CREATE INDEX IF NOT EXISTS ix_student_dpt_role ON student_dpt (role);

-- ---------------------------------------------------------------------------
-- 2. Tabel vote_receipts untuk menyimpan receipt voting (B-06/B-07)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vote_receipts (
    receipt_id       VARCHAR(50) PRIMARY KEY,
    student_nim      VARCHAR(20) NOT NULL REFERENCES student_dpt(nim) ON DELETE CASCADE,
    election_id      VARCHAR(50) NOT NULL REFERENCES elections(election_id) ON DELETE CASCADE,
    vote_hash        VARCHAR(64) NOT NULL,
    ballot_id        UUID NOT NULL REFERENCES ballot_box(ballot_id) ON DELETE CASCADE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index untuk lookup receipt
CREATE INDEX IF NOT EXISTS ix_vote_receipts_student ON vote_receipts (student_nim);
CREATE INDEX IF NOT EXISTS ix_vote_receipts_election ON vote_receipts (election_id);
CREATE INDEX IF NOT EXISTS ix_vote_receipts_vote_hash ON vote_receipts (vote_hash);