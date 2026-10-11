CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE student_dpt (
    nim VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    study_program VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    face_embedding TEXT,
    is_registered BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE voting_status (
    nim VARCHAR(20) PRIMARY KEY,
    has_voted BOOLEAN NOT NULL DEFAULT FALSE,
    verification_method VARCHAR(50),

    CONSTRAINT fk_voting_status_student
        FOREIGN KEY (nim)
        REFERENCES student_dpt(nim)
);

CREATE TABLE candidates (
    candidate_id SERIAL PRIMARY KEY,
    election_type VARCHAR(50) NOT NULL,
    candidate_name VARCHAR(100) NOT NULL,
    vision_mission TEXT,
    photo_url VARCHAR(255)
);

CREATE TABLE ballot_box (
    ballot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id INTEGER NOT NULL,
    election_type VARCHAR(50) NOT NULL,
    casted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    vote_hash VARCHAR(255) UNIQUE,

    CONSTRAINT fk_ballot_candidate
        FOREIGN KEY (candidate_id)
        REFERENCES candidates(candidate_id)
);

CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);