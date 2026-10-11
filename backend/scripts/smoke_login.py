"""Smoke test Milestone 1: login penuh dengan data sungguhan di DB.

Membuat mahasiswa uji → login → akses /auth/me → bersih-bersih.
"""

import asyncio
import uuid

import httpx

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.student import StudentDPT

BASE = "http://127.0.0.1:8000"
NIM = "2310119999"
PASSWORD = "Testing123!"


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        existing = await db.get(StudentDPT, NIM)
        if existing:
            await db.delete(existing)
            await db.commit()
        db.add(
            StudentDPT(
                nim=NIM,
                full_name="Mahasiswa Uji Smoke Test",
                study_program="Teknik Informatika",
                email=f"uji.{uuid.uuid4().hex[:6]}@student.kampus.ac.id",
                password_hash=get_password_hash(PASSWORD),
                is_registered=False,
            )
        )
        await db.commit()
    print(f"[seed] mahasiswa {NIM} dibuat")


async def cleanup() -> None:
    async with AsyncSessionLocal() as db:
        student = await db.get(StudentDPT, NIM)
        if student:
            await db.delete(student)
            await db.commit()
    print(f"[cleanup] mahasiswa {NIM} dihapus")


async def run() -> None:
    await seed()
    try:
        with httpx.Client(base_url=BASE, timeout=15) as c:
            # 1. Login dengan password salah -> 401
            r = c.post(
                "/api/v1/auth/login",
                json={"nim": NIM, "password": "salah"},
            )
            print(f"[{r.status_code}] login password salah (harus 401): {r.json()['error']['code']}")

            # 2. Login benar -> 200 + access_token
            r = c.post(
                "/api/v1/auth/login",
                json={"nim": NIM, "password": PASSWORD},
            )
            body = r.json()
            print(f"[{r.status_code}] login benar: token={body['data']['access_token'][:25]}...")
            assert r.status_code == 200, body
            assert body["data"]["token_type"] == "Bearer"
            token = body["data"]["access_token"]

            # 3. /auth/me dengan token -> 200 + data mahasiswa
            r = c.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            me = r.json()
            print(f"[{r.status_code}] /auth/me: {me['data']['full_name']} | has_voted={me['data']['has_voted']}")
            assert r.status_code == 200 and me["data"]["nim"] == NIM

            # 4. Token palsu -> 401
            r = c.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer tokengalat"},
            )
            print(f"[{r.status_code}] token palsu (harus 401): {r.json()['error']['code']}")

        print("\nMILESTONE 1 LOLOS: login -> JWT -> /auth/me berfungsi")
    finally:
        # Cleanup di event loop yang sama dengan seed (pool terikat loop)
        await cleanup()


if __name__ == "__main__":
    asyncio.run(run())
