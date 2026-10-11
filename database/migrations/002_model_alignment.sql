-- 002: Penyelarasan tabel hasil 001_initial_schema.sql dengan model SQLAlchemy.
-- Alasan: tabel dari 001 dibuat tanpa kolom TimestampMixin (created_at/updated_at),
-- tanpa voting_status.voted_at, serta tanpa constraint/index yang didefinisikan
-- di model (create_all hanya melewati tabel yang sudah ada).
-- Dijalankan berurutan setelah 001 di docker-entrypoint-initdb.d (volume baru)
-- atau via: docker exec -i populi-postgres psql -U populi -d voting_system < 002_...

-- ---------------------------------------------------------------------------
-- 1. Kolom TimestampMixin (created_at/updated_at) untuk tabel lama
-- ---------------------------------------------------------------------------
ALTER TABLE student_dpt   ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE student_dpt   ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

ALTER TABLE voting_status ADD COLUMN IF NOT EXISTS voted_at    TIMESTAMPTZ;
ALTER TABLE voting_status ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE voting_status ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

ALTER TABLE candidates    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE candidates    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

ALTER TABLE ballot_box    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE ballot_box    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

ALTER TABLE audit_logs    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE audit_logs    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

-- ---------------------------------------------------------------------------
-- 2. Constraint unik dari model (tidak ikut dibuat karena tabel sudah ada)
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_election_candidate'
    ) THEN
        ALTER TABLE candidates
            ADD CONSTRAINT uq_election_candidate UNIQUE (election_type, candidate_name);
    END IF;
END $$;

-- ---------------------------------------------------------------------------
-- 3. Index dari model
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS ix_student_dpt_full_name        ON student_dpt (full_name);
CREATE INDEX IF NOT EXISTS ix_student_dpt_study_program    ON student_dpt (study_program);

CREATE INDEX IF NOT EXISTS ix_candidates_election_type     ON candidates (election_type);

CREATE INDEX IF NOT EXISTS ix_ballot_box_election_type     ON ballot_box (election_type);

CREATE INDEX IF NOT EXISTS ix_audit_logs_event_type        ON audit_logs (event_type);
CREATE INDEX IF NOT EXISTS ix_audit_logs_event_type_timestamp
    ON audit_logs (event_type, "timestamp");
CREATE INDEX IF NOT EXISTS ix_audit_logs_ip_address        ON audit_logs (ip_address);
