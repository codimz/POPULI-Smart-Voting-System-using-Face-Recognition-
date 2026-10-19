# T24: Seed data for development / smoke test
import asyncio
import sys, os
sys.path.insert(0, "/app")

from datetime import datetime, timedelta
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.election import Election, ElectionStatus
from app.models.student import StudentDPT, UserRole
from app.models.candidate import Candidate
from sqlalchemy import select

async def seed():
    async with AsyncSessionLocal() as db:
        # 1 election active
        election = Election(
            election_id="E-2026-001",
            name="Pemilihan Ketua BEM 2026",
            election_type="bem",
            status=ElectionStatus.ACTIVE,
            starts_at=datetime.now() - timedelta(days=1),
            ends_at=datetime.now() + timedelta(days=7),
        )
        db.add(election)
        await db.commit()
        await db.refresh(election)

        # 1 admin
        admin = StudentDPT(
            nim="2310123456",
            name="Admin Kampus",
            email="admin@admin.kampus.ac.id",
            role=UserRole.admin,
            password_hash=get_password_hash("admin123"),
            department="TI",
            has_voted=False,
        )
        db.add(admin)
        await db.commit()

        # ~10 students
        for i in range(10):
            nim = f"231011{900+i:03d}"
            s = StudentDPT(
                nim=nim,
                name=f"Mahasiswa Uji {i+1}",
                email=f"mahasiswa{i+1}@kampus.ac.id",
                role=UserRole.student,
                password_hash=get_password_hash("password"),
                department="TI" if i % 2 == 0 else "SI",
                has_voted=False,
            )
            db.add(s)
        await db.commit()

        # 4-6 candidates
        for j in range(4):
            c = Candidate(
                candidate_id=f"C-{j+1:02d}",
                election_id=election.election_id,
                nim=f"231011{900+j:03d}",
                name=f"Kandidat {chr(65+j)}",
                vision="Visi perubahan",
            )
            db.add(c)
        await db.commit()
        print("[seed] 1 election + 1 admin + 10 students + 4 candidates inserted.")

if __name__ == "__main__":
    asyncio.run(seed())
