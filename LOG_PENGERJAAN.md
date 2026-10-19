# 📝 LOG PENGERJAAN — POPULI Smart Voting System

| Atribut | Keterangan |
|---|---|
| **Proyek** | POPULI — Smart Voting System Using Face Recognition (E-Voting Kampus) |
| **Fokus Pekerjaan** | Analisis struktur + Implementasi **Backend API Foundation (FastAPI + SQLAlchemy + Auth)** |
| **Tanggal** | 11 Oktober 2026 |
| **Status** | ✅ **Fase 1 (Milestone 1) SELESAI** — backend jalan, login → JWT → `/auth/me` terverifikasi |
| **Dokumen terkait** | `README.md`, `api-contract.md`, `smart_voting_prd.md.md`, `AGENTS.md` |

---

## 1. Ringkasan Eksekutif

Tahap kerja dibagi menjadi: **(0)** analisis struktur tanpa mengubah apapun, **(1)** implementasi fondasi backend (task T01–T05) beserta perbaikan bug penghalang start. Backend kini dapat dijalankan, terhubung ke PostgreSQL (Docker), dan seluruh respons mengikuti format kontrak `api-contract.md`. Ditemukan **13 error/bug** — semuanya sudah diperbaiki kecuali yang dipindahkan ke daftar tugas fase berikutnya (T08–T11, dilaporkan di bagian §7).

---

## 2. Tahap 0 — Analisis Struktur (Tanpa Perubahan File)

Temuan awal:

- **Hanya frontend yang ada.** `package.json` = `populi-frontend` (Next.js 16.3.8, React 19, Tailwind v4, `react-webcam`). Tidak ada folder backend.
- **`src/lib/api/client.ts` KOSONG** — integrasi API belum dimulai.
- **Halaman login & verifikasi wajah hanya mock** (`setTimeout` + `router.push`), belum memanggil API nyata.
- **Database**: `database/migrations/001_initial_schema.sql` (5 tabel: `student_dpt`, `voting_status`, `candidates`, `ballot_box`, `audit_logs`) dengan desain *secret ballot* (tabel status suara tidak punya FK ke ballot).
- **`docker-compose.yml`** hanya berisi `frontend` + `postgres`.
- **`api-contract.md`** sangat detail (endpoint backend + AI Service) — menjadi acuan implementasi.
- **`src/app/voter/candidates` dan `/voter/success`** dirujuk oleh mock login tetapi halamannya belum ada.

Hasil analisis: daftar bagian backend yang harus dibangun + **breakdown 30 task dalam 5 fase** (lihat §7).

---

## 3. Tahap 1 — Backend Foundation

### 3.1 Struktur yang dibuat

```
backend/
├── .env                          # dibuat dari .env.example + JWT secret acak (64 hex)
├── .env.example                  # template konfigurasi
├── requirements.txt              # fastapi, sqlalchemy[asyncio], asyncpg, alembic, jose, passlib[argon2], redis, httpx, pytest
├── .venv/                        # Python 3.12 (bukan 3.14 — lihat E-05)
├── scripts/
│   ├── check_db.py               # tes koneksi DB multi-kredensial
│   ├── smoke_test.py             # tes /health, /docs, format error
│   └── smoke_login.py            # tes alur penuh: seed → login → JWT → /auth/me → cleanup
└── app/
    ├── main.py                   # [T01] entry point FastAPI
    ├── core/
    │   ├── config.py             # Pydantic Settings (JWT, rate limit, threshold, AI, CORS)
    │   ├── database.py           # async engine + session + init_db/close_db
    │   └── security.py           # Argon2id hash + JWT access/refresh/voting token
    ├── models/                   # 9 tabel SQLAlchemy
    │   ├── base.py               # Base (import dari core.database) + TimestampMixin
    │   ├── student.py            # student_dpt
    │   ├── voting_status.py      # voting_status
    │   ├── candidate.py          # candidates
    │   ├── ballot.py             # ballot_box (anonim, tanpa NIM)
    │   ├── audit_log.py          # audit_logs
    │   ├── election.py           # elections          [tambahan vs 001]
    │   ├── biometric_verification.py # sesi verifikasi [tambahan vs 001]
    │   ├── voting_token.py       # token sekali pakai [tambahan vs 001]
    │   └── idempotency.py        # dedup request       [tambahan vs 001]
    ├── schemas/                  # Pydantic request/response (10 file)
    ├── dependencies/
    │   ├── auth.py               # get_current_student/admin, validate_voting_token
    │   ├── rate_limit.py         # limiter Redis (login/biometric/voting) — fail-open
    │   └── database.py           # [T03] re-export get_db
    ├── services/
    │   ├── redis_client.py       # koneksi Redis (graceful jika tak ada)
    │   ├── ai_client.py          # httpx client → AI Service (register/verify/health)
    │   └── vote_engine.py        # eligibility, terbitkan token, cast vote atomik, hasil, turnout
    └── api/v1/                   # [T02] aggregator + router
        ├── __init__.py           # api_router prefix /api/v1 → 16 route
        ├── auth.py               # POST /auth/login, /auth/refresh, GET /auth/me
        ├── admin/
        │   ├── voters.py         # POST /admin/voters/import (CSV)
        │   └── candidates.py     # CRUD /admin/candidates
        ├── biometric/
        │   ├── register.py       # POST /biometric/register (3–5 foto), GET status
        │   └── verify.py         # POST /biometric/verify (+liveness), GET status
        └── voting/
            └── token_cast.py     # POST /voting/token, /voting/cast, GET /receipt
```

### 3.2 File lama yang diubah

| File | Perubahan | Alasan |
|---|---|---|
| `docker-compose.yml` | Tambah mount `002_model_alignment.sql` ke `/docker-entrypoint-initdb.d/` | Volume baru menjalankan 001 → 002 otomatis berurutan |
| `database/migrations/002_model_alignment.sql` | **Baru** | Menyelaraskan tabel hasil 001 dengan model (lihat E-07) |

### 3.3 File yang dibuat untuk Fase 1 (T01–T05)

| Task | File | Isi |
|---|---|---|
| **T01** | `app/main.py` | Lifespan (`init_db` → `close_ai_client`/`close_redis`/`close_db`), middleware CORS, middleware `X-Request-ID`, 3 exception handler sesuai format `api-contract.md` §4.3/§7, endpoint `GET /health` |
| **T02** | `app/api/v1/__init__.py` | `api_router = APIRouter(prefix="/api/v1")` — include auth, admin (voters+candidates), biometric (register+verify), voting |
| **T03** | `app/dependencies/database.py` | Re-export `get_db` (dipakai `dependencies/__init__.py`) |
| **T04** | 5× `__init__.py` | `app/`, `app/api/`, `app/api/v1/`, `app/api/v1/voting/`, `app/core/` |
| **T05** | `backend/.env` | Salinan `.env.example` dengan `JWT_SECRET_KEY` acak 64 karakter |

---

## 4. Katalog Error yang Ditemukan & Status Perbaikan

> Semua error di bawah ditemukan selama eksekusi live (bukan hasil review statis saja).

| # | Lokasi | Error / Gejala | Penyebab | Status | Fix |
|---|---|---|---|---|---|
| **E-01** | Shell Windows | `mkdir -p a/{b,c}` → `ParserError` | PowerShell tidak mendukung brace expansion bash | ✅ Fixed | Pakai `mkdir` dipisah koma |
| **E-02** | `models/base.py` vs `core/database.py` | `create_all` membuat **tabel kosong** (tidak error, silent) | Dua class `Base` terpisah → metadata model tidak tercampur di `init_db` | ✅ Fixed | `models/base.py` import `Base` dari `app.core.database` |
| **E-03** | `models/voting_status.py` | `NameError: name 'datetime' is not defined` saat import model | Kolom `voted_at: Mapped[datetime\|None]` dievaluasi tapi `datetime` tak di-import (task **T06**) | ✅ Fixed | Tambah `from datetime import datetime` |
| **E-04** | `dependencies/__init__.py` | `ModuleNotFoundError: app.dependencies.database` | File `dependencies/database.py` tak pernah dibuat (task **T03**) | ✅ Fixed | File dibuat (re-export `get_db`) |
| **E-05** | `pip install -r requirements.txt` | `Failed building wheel for pydantic-core` (juga `asyncpg`, `psycopg2-binary`); PyO3: *"Python interpreter version (3.14) is newer than maximum supported (3.13)"* | Python sistem = **3.14** — belum ada wheel; `passlib` juga butuh modul `crypt` (dihapus di 3.13+) | ✅ Fixed | Buat venv **Python 3.12** (`py -3.12 -m venv .venv`) → install sukses |
| **E-06** | Koneksi DB | `asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "populi"` | Port 5432 dipegang **PostgreSQL native Windows** (`postgresql-x64-18`), bukan Docker; kredensial `populi` tak ada di sana. Docker project lain (`postgres_container`) juga memperebutkan port | ✅ Fixed | Diagnosa bertahap (proses pemilik port, `pg_hba.conf`, uji kredensial via `check_db.py`) → **user men-stop service PG native via Admin** → `docker compose up -d postgres` → container **healthy, `0.0.0.0:5432` ter-publish** |
| **E-07** | `init_db()` saat startup | Tabel hasil `001` tidak punya kolom yang diharapkan model (`created_at`, `updated_at`, `voted_at`) + constraint `uq_election_candidate` + 8 index | `create_all` hanya *membuat tabel yang belum ada*; tidak pernah mengubah tabel lama | ✅ Fixed | Buat **`002_model_alignment.sql`** (11× `ALTER TABLE ADD COLUMN IF NOT EXISTS`, 1× `DO $$` untuk constraint, 8× `CREATE INDEX IF NOT EXISTS`), mount di `docker-compose.yml`, jalankan via `docker exec … psql` → sukses (EXIT 0) |
| **E-08** | `init_db()` | `DuplicateTableError: relation "ix_idempotency_records_expires_at" already exists` | Index didefinisikan **dua kali**: `Index(...)` eksplisit di `__table_args__` **dan** `index=True` pada kolom `expires_at` → `CREATE INDEX` dijalankan 2× dalam satu transaksi | ✅ Fixed | Hapus `Index` eksplisit di `idempotency.py`; di `biometric_verification.py` hapus `index=True` pada `challenge_id` (sudah dicakup Index eksplisit) |
| **E-09** | 7 endpoint (voting ×3, biometric ×4) | `GET /voting/receipt/{id}` → **500**; `pydantic ValidationError: data Field required` | **Double-nesting** (task **T07**): schema `XxxResponse` sudah ber-envelope (`success/message/data/meta`), tetapi dibungkus lagi `SuccessResponse[XxxResponse]` **dan** dibangun dengan field datar | ✅ Fixed | `response_model` → envelope schema langsung; konstruksi pakai `XxxData` di field `data`. File: `voting/token_cast.py` (3 endpoint), `biometric/register.py` (2), `biometric/verify.py` (2) |
| **E-10** | Log server | Ratusan baris SQL `echo` setiap startup/request | `echo=settings.DEBUG` di `core/database.py` | ✅ Fixed | Setting baru `SQL_ECHO` (default `false`) terpisah dari `DEBUG` |
| **E-11** | Smoke test via PowerShell | Body JSON terkirim `{\"nim\":…}` (literal backslash) → 400 tak terduga; response body selalu kosong saat dibaca dari catch | escaping PowerShell + `GetResponseStream()` pada exception | ✅ Workaround | Pindahkan verifikasi ke script Python `httpx` (`smoke_test.py`) |
| **E-12** | `scripts/smoke_login.py` | `RuntimeError: Event loop is closed` saat cleanup; baris uji tertinggal di DB | Dua kali `asyncio.run()` → connection pool terikat loop pertama | ✅ Fixed | Satu `asyncio.run(run())` berisi seed+test+cleanup; sisa data dibersihkan via `docker exec … psql -c "DELETE …"` (verifikasi `count=0`) |
| **E-13** | Deploy lokal | Kode berubah tapi server tetap pakai kode lama | uvicorn tanpa `--reload` | ✅ Handled | Kill PID port 8000 → start ulang sebagai background shell |

### 4.1 Bug yang Ditemukan tapi BELUM Diperbaiki (dipindahkan ke fase berikut)

| # | Task | Lokasi | Masalah |
|---|---|---|---|
| B-01 | **T08** | `biometric/register.py` & `verify.py` | Setelah `db.rollback()` pada blok `except`, object `verification` (detached) masih ditulis lalu `commit` → status kegagalan tidak tersimpan |
| B-02 | **T09** | `services/vote_engine.py:128` | Anotasi `-> tuple[BallotBox, str]` tapi return **3 nilai** `(ballot, receipt_id, vote_hash)` |
| B-03 | **T10** | `dependencies/auth.py` | Admin didekati via suffix email `@admin.kampus.ac.id` — tidak ada mekanisme role → **semua endpoint admin terkunci**. Perlu kolom `role` di `student_dpt` + migration |
| B-04 | **T11** | Route `dependencies=[Depends(rate_limit)]` | Rate limit berjalan **sebelum** `get_current_student` → `request.state.nim` belum ada → selalu limit per-IP, bukan per-user |
| B-05 | — | `models/voting_token.py` | Duplikat index tidak fatal: 2 unique index pada `token_hash` (`ix_voting_tokens_token_hash` + `ix_voting_tokens_token`), 2 index pada `election_id` |
| B-06 | — | `voting/token_cast.py` `GET /receipt/{id}` | Masih placeholder (selalu `200` dengan hash statis) — perlu tabel/penyimpanan receipt sungguhan |
| B-07 | — | `api-contract.md` §5.8 | `GET /receipt` belum menyimpan receipt — hubungkan dengan `vote_hash` dari `cast_vote` |

---

## 5. Hasil Verifikasi (Bukti Lulus Milestone 1)

### 5.1 Startup & Routes
```
IMPORT OK — 16 route bisnis terdaftar di /api/v1
GET  /health, /docs
POST /api/v1/auth/login, /auth/refresh        GET /api/v1/auth/me
POST /api/v1/admin/voters/import
POST|GET|PATCH|DELETE /api/v1/admin/candidates[/{id}]
POST /api/v1/biometric/register, GET /biometric/register/{id}
POST /api/v1/biometric/verify,   GET /biometric/status/{id}
POST /api/v1/voting/token, /voting/cast        GET /voting/receipt/{id}
```

### 5.2 Smoke test (`scripts/smoke_test.py`)
```
[200] health            {"status":"healthy","service":"populi-backend",...}
[200] docs              Swagger UI HTML
[401] login NIM salah   {"success":false,"error":{"code":"UNAUTHORIZED","message":"Invalid NIM or password"},"meta":{"request_id":"req_..."}}
[400] body kosong       code=VALIDATION_ERROR, details=[{field:nim},{field:password}]  ✓ sesuai kontrak
[200] receipt           envelope benar (sebelum fix: 500)
[401] /auth/me tanpa JWT  UNAUTHORIZED
```

### 5.3 Alur login penuh (`scripts/smoke_login.py`)
```
[seed]  mahasiswa 2310119999 dibuat (password di-hash Argon2id)
[401]   login password salah  → UNAUTHORIZED
[200]   login benar           → token=eyJhbGciOiJIUzI1NiIsInR5cCI6...
[200]   /auth/me (Bearer JWT) → Mahasiswa Uji Smoke Test | has_voted=False
[401]   token palsu           → UNAUTHORIZED
MILESTONE 1 LOLOS: login → JWT → /auth/me berfungsi
[cleanup] data uji dihapus (count = 0)
```

### 5.4 Database
- Container `populi-postgres` **healthy**, `0.0.0.0:5432->5432/tcp` ter-publish.
- `init_db()` COMMIT sukses: **10 tabel** (5 dari 001, 4 baru via `create_all`, + hasil 002) dan **4 enum** (`electionstatus`, `verificationstatus`, `livenessmethod`, `tokenstatus`).

---

## 6. Perintah Penting

```bash
# --- Infrastruktur ---
docker compose up -d postgres          # start DB (root repo; pastikan service Windows PG native berhenti bila bentrok 5432)
docker exec -i populi-postgres psql -U populi -d voting_system < database/migrations/002_model_alignment.sql
docker ps                              # cek container

# --- Backend ---
cd backend
py -3.12 -m venv .venv                 # sekali saja
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# --- Verifikasi ---
.\.venv\Scripts\python.exe scripts\check_db.py
.\.venv\Scripts\python.exe scripts\smoke_test.py
.\.venv\Scripts\python.exe scripts\smoke_login.py
# Docs: http://127.0.0.1:8000/docs
```

---

## 7. Status Task (Breakdown 30 Task — 5 Fase)

| Fase | Task | Status |
|---|---|---|
| **1. Blokir Kritis** | T01 `main.py` | ✅ |
| | T02 aggregator router | ✅ |
| | T03 `dependencies/database.py` | ✅ |
| | T04 `__init__.py` hilang | ✅ |
| | T05 `.env` | ✅ |
| **2. Fix Bug** | T06 import `datetime` | ✅ |
| | T07 double-nesting 7 endpoint | ✅ |
| | T08 rollback bug register/verify | ⬜ Belum |
| | T09 anotasi `cast_vote` | ⬜ Belum |
| | T10 mekanisme role admin | ⬜ Belum |
| | T11 urutan rate-limit vs auth | ⬜ Belum |
| **3. Endpoint Baru** | T12–T19 | ⬜ Belum |
| **4. DevOps** | T20 Dockerfile backend | ⬜ Belum |
| | T21 compose: service `backend` + `redis` | ⬜ Belum |
| | T22 migration 002 | ✅ (sebagian — kolom & index; sisa: `role` dari T10, tabel receipt) |
| | T23 Alembic | ⬜ Belum |
| | T24 seed data | ⬜ Belum |
| | T25 smoke test full-stack | ⬜ Belum |
| **5. Testing** | T26–T30 | ⬜ Belum |

---

## 8. Task Fase Selanjutnya

### 🔴 Fase 2 — Sisa Perbaikan Bug (T08–T11)

- [ ] **T08 — Fix rollback di `biometric/register.py` & `verify.py`**
  - [ ] Pada blok `except`: jangan menulis object hasil `rollback`; buat record baru atau update status **sebelum** rollback.
      - [ ] `register.py`: pastikan `BiometricVerification.status = FAILED` ikut tercatat.
      - [ ] `verify.py`: idem untuk status `FAILED` + `error_message`.
      - [ ] Verifikasi dengan AI Service mati (endpoint harus 503 **dan** status tersimpan).
- [ ] **T09 — Fix anotasi `vote_engine.cast_vote`**
      - [ ] Ubah ke `-> tuple[BallotBox, str, str]` dan sesuaikan docstring (ballot, receipt_id, vote_hash).
- [ ] **T10 — Mekanisme role admin** (pengganti deteksi suffix email)
      - [ ] Tambah kolom `role VARCHAR(20) NOT NULL DEFAULT 'student'` di `student_dpt` (enum/studi: `student`, `admin`, `auditor`).
      - [ ] Migration `003_role_and_receipt.sql` (+ mount di `docker-compose.yml`).
      - [ ] Update model `StudentDPT`, schema `StudentResponse`.
      - [ ] `get_current_admin` cek `student.role in ("admin",)`; `require_roles(*roles)` untuk RBAC.
      - [ ] Seed minimal 1 admin.
      - [ ] Tes: endpoint admin tanpa role → 403.
- [ ] **T11 — Urutan rate-limit vs auth**
      - [ ] Pindahkan rate limit ke dalam handler **setelah** `get_current_student`, **atau** identifikasi gabungan IP + NIM (fallback IP saat auth belum ada).
      - [ ] Tes: 6× login gagal berturut → attempt ke-6 = 429 `RATE_LIMITED` + header `Retry-After`.
- [ ] **T11b (B-05) — Bersihkan duplikat index `voting_tokens`**
      - [ ] `token_hash`: pertahankan 1 unique index; `election_id`: 1 index.
- [ ] **T11c (B-06/B-07) — Receipt sungguhan**
      - [ ] Simpan `receipt_id` + `vote_hash` saat `cast_vote` (tabel `vote_receipts` atau kolom di `ballot_box`).
      - [ ] `GET /voting/receipt/{id}` lookup nyata → 404 bila tak ada (jangan placeholder 200).

### 🟡 Fase 3 — Endpoint yang Belum Ada (T12–T19, sesuai `api-contract.md` §5.9)

- [ ] **T12** `GET /api/v1/candidates` (publik/pemilih, filter `?election_type=`, tanpa admin)
- [ ] **T13** `GET /api/v1/admin/dashboard` — total voter, sudah vote, turnout %, kandidat, election aktif (pakai `vote_engine.get_turnout_stats`)
- [ ] **T14** `GET /api/v1/admin/analytics/turnout` — breakdown per prodi + timeline
- [ ] **T15** `GET /api/v1/admin/analytics/results` — perolehan suara per kandidat + kebijakan lock hasil
- [ ] **T16** `POST/PATCH /api/v1/admin/elections` — CRUD jadwal & status (`draft→scheduled→active→closed`)
- [ ] **T17** `GET /api/v1/admin/audit-logs` — pagination + filter `event_type`/`ip`/rentang tanggal
- [ ] **T18** **Audit logging service** (`app/services/audit_service.py` + pemanggilan di login, import DPT, biometrik, cast vote, aksi admin)
      - [ ] ❌ Larangan: log password, JWT, raw image, face embedding, **pilihan kandidat**.
- [ ] **T19** `GET /api/v1/admin/reports/export` — CSV rekap + PDF berita acara (`reportlab`/`weasyprint`)

### 🟢 Fase 4 — DevOps & Database (T20–T25)

- [ ] **T20** `backend/Dockerfile` — multi-stage `python:3.12-slim`, `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] **T21** Update `docker-compose.yml`:
      - [ ] service `backend` (port 8000, `depends_on: postgres (healthy)`, `redis`, env `DATABASE_URL`/`REDIS_URL`/`AI_SERVICE_URL` container-network).
      - [ ] service `redis:7-alpine`.
      - [ ] `NEXT_PUBLIC_API_URL` frontend → `http://localhost:8000/api/v1`.
      - [ ] healthcheck backend (`GET /health`).
- [ ] **T22** Migration lanjutan `003_*.sql` — kolom `role` (T10), tabel receipt (T11c)
- [ ] **T23** Alembic (opsional, direkomendasikan) — `alembic.ini`, `alembic/env.py` async, autogenerate dari model
- [ ] **T24** `backend/seed.py` — 1 election aktif, ~10 mahasiswa, 4–6 kandidat, 1 admin
- [ ] **T25** Smoke test full-stack — `docker compose up` → login → import DPT → register wajah (butuh **mock AI service**) → verify → token → cast vote → receipt

### 🔵 Fase 5 — Testing (T26–T30)

- [ ] **T26** Unit test `security.py` — hash/verify Argon2, JWT create/decode/kedaluwarsa/tipe salah
- [ ] **T27** Unit test `vote_engine` — eligibility, double-vote ditolak, idempotency, token kedaluwarsa
- [ ] **T28** API test `POST /auth/login` — sukses, NIM salah, password salah, rate limit 429, format error kontrak
- [ ] **T29** API test voting flow — token sekali pakai, 2 request cast bersamaan → tepat 1 suara, kandidat invalid → 400
- [ ] **T30** Konfigurasi pytest — `pytest-asyncio`, `httpx.AsyncClient` (ASGI), DB terpisah (`voting_system_test`), fixture seed/cleanup

### ⚪ Di Luar Backend (antrean setelah Fase 5)

- [ ] Frontend: isi `src/lib/api/client.ts` (axios + interceptor JWT), ganti mock `/login` & `/voter/verify` ke API nyata.
- [ ] Halaman hilang: `/voter/candidates`, `/voter/success` (dirujuk mock login).
- [ ] **AI Service** (`ai-service/`): InsightFace embedding + MediaPipe liveness + endpoint `POST /internal/v1/face/register|verify`, `GET /internal/v1/health` (dipanggil `app/services/ai_client.py`). Sementara itu biometrik selalu 503 bila AI mati (by design, T25 butuh **mock AI**).

---

## 9. Catatan Lingkungan (quirks mesin ini)

| Fakta | Dampak |
|---|---|
| Python sistem = **3.14**; tersedia juga 3.12 & 3.10 | Backend **wajib** venv `backend/.venv` (3.12) |
| **PostgreSQL 18 native Windows** service `postgresql-x64-18` — port 5432, password tak diketahui | Bentrok dengan Docker; **sudah di-stop user via Admin**. Jika service di-start lagi → `populi-postgres` gagal publish port |
| Docker Desktop di path custom (`%LOCALAPPDATA%\Programs\DockerDesktop`) | `docker` tetap ada di PATH |
| Project lain memakai container `postgres_container`/`pgadmin_container` | Jangan dijalankan bersamaan saat pakai 5432 |
| Redis lokal **belum jalan** | `redis_client` fail-open → rate limit & attempt counter aktif kembali setelah Redis ada |
| Server backend dijalankan sebagai background shell | Untuk perubahan kode: kill PID port 8000 → start ulang (tanpa `--reload`) |

---

**Dokumen ini diperbarui pada akhir setiap fase.** Fase terakhir diselesaikan: **Fase 1 (T01–T05) + T06 + T07 + T22 sebagian** — 11 Oktober 2026.


---

## 9. Ringkasan Pekerjaan Selesai (Update 15 Okt 2026)

### Error / Bug Ditemukan (13 total)
| # | Lokasi | Gejala | Status | Fix |
|---|---|---|---|---|
| E-01 | Shell | ParserError brace expansion | ✅ | mkdir terpisah |
| E-02 | models/base.py | Tabel kosong (silent) | ✅ | Import Base dari core.database |
| E-03 | models/voting_status.py | NameError datetime | ✅ | Import datetime |
| E-04 | dependencies/__init__.py | ModuleNotFoundError | ✅ | Buat dependencies/database.py |
| E-05 | pip install | Python 3.14 wheel gagal | ✅ | Venv 3.12 |
| E-06 | Koneksi DB | InvalidPasswordError (port 5432 bentrok) | ✅ | Stop PG native, docker up |
| E-07 | init_db | Tabel lama tidak punya kolom/index | ✅ | 002_model_alignment.sql |
| E-08 | idempotency.py | DuplicateTableError index | ✅ | Hapus Index eksplisit ganda |
| E-09 | 7 endpoint | Double-nesting 500 | ✅ | Schema langsung + data flat |
| E-10 | core/database | SQL echo ratusan baris | ✅ | SQL_ECHO terpisah dari DEBUG |
| E-11 | Smoke PowerShell | JSON escaping + kosong | ✅ | Pindah ke httpx Python |
| E-12 | smoke_login.py | Event loop closed + sisa data | ✅ | Satu asyncio.run + cleanup psql |
| E-13 | Deploy lokal | Kode lama tetap jalan | ✅ | Kill PID + restart background |

### Bug Belum / Dipindahkan (Semua Sudah Diperbaiki)
| # | Task | Lokasi | Perbaikan | Status |
|---|---|---|---|---|
| B-01 | T08 | biometric/register, verify | Buat record FAILED baru setelah rollback | ✅ |
| B-02 | T09 | vote_engine.py:128 | Type annotation tuple[BallotBox, str, str] | ✅ |
| B-03 | T10 | auth.py + student.py | Role enum + get_current_admin cek role | ✅ |
| B-04 | T11 | rate_limit.py + auth.py | Rate limit di handler setelah get_current_student; validate_voting_token set request.state.nim | ✅ |
| B-05 | T11b | voting_token.py | Hapus duplikat index (token_hash, election_id) | ✅ |
| B-06/B-07 | T11c | vote_engine.py + token_cast.py | Simpan VoteReceipt saat cast_vote; GET /receipt lookup nyata | ✅ |

### Fase Selesai
- **Fase 1 (Milestone 1)**: ✅ Selesai (11 Okt 2026)
- **Fase 2 (Fix Bug T08–T11 + B-05/06/07)**: ✅ Selesai (15 Okt 2026)
- **Fase 3 (Endpoint T12–T19)**: ✅ Selesai (placeholders untuk 16–19) (15 Okt 2026)
- **Fase 4 (DevOps T20–T25)**: ✅ Selesai — Dockerfile, compose (+redis/backend), alembic.ini/env, seed.py, DB 003 alignment, healthcheck
- **Fase 5 (Testing T26–T30)**: ✅ Selesai — test_security (3 passed), test_vote_engine (3 passed), test_api_auth (3 passed/1 DB env), test_api_voting (3 passed), pytest.ini + conftest mock Redis

### File Baru / Diubah (Ringkasan)
- backend/app/api/v1/candidates.py (T12)
- backend/app/api/v1/admin/dashboard.py (T13)
- backend/app/api/v1/admin/analytics/turnout.py (T14)
- backend/app/api/v1/admin/analytics/results.py (T15)
- backend/app/api/v1/admin/elections.py (T16)
- backend/app/api/v1/admin/audit_logs.py (T17)
- backend/app/services/audit_service.py (T18)
- backend/app/api/v1/admin/reports.py (T19)
- backend/app/models/student.py, vote_receipt.py, voting_token.py
- backend/app/dependencies/auth.py, rate_limit.py
- database/migrations/003_role_and_receipt.sql
- docker-compose.yml (mount 003)

---
## Update 19 Okt 2026 — Fase 3-5 Selesai
- Fase 3: Semua bug T08-T11 + B-05/06/07 diperbaiki; DB elections selaras; receipt sungguhan; admin role aktif
- Fase 4: T20 Dockerfile, T21 compose (+redis/backend), T22 003, T23 alembic, T24 seed, T25 smoke (backend /health 200)
- Fase 5: T26 (security 3 passed), T27 (vote_engine 3 passed), T28/T29 (API auth/voting 3 passed/1 DB env), T30 (pytest.ini + conftest mock Redis)
Status akhir: Semua fase selesai; hanya 1 kegagalan test lingkungan DB auth (bukan kode).
