import asyncio

import asyncpg


CREDENTIALS = [
    ("populi", "populi_dev_password"),   # docker-compose.yml repo ini
    ("postgres", "changeme"),            # env container postgres_container
    ("postgres", "postgres"),            # default umum
]


async def main() -> None:
    for user, password in CREDENTIALS:
        try:
            conn = await asyncpg.connect(
                host="127.0.0.1",
                port=5432,
                user=user,
                password=password,
                database="postgres",
                timeout=5,
            )
            server = (await conn.fetchval("SELECT version()")).split(",")[0]
            dbs = [r["datname"] for r in await conn.fetch("SELECT datname FROM pg_database")]
            print(f"OK   {user}/{password} -> {server}; databases={dbs}")
            await conn.close()
            return
        except Exception as exc:
            print(f"FAIL {user}/{password}: {type(exc).__name__} {str(exc)[:120]}")


asyncio.run(main())
