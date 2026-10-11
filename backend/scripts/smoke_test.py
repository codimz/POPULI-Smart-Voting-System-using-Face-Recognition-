"""Smoke test Phase 1: health, docs, error format, login flow sederhana."""

import httpx

BASE = "http://127.0.0.1:8000"


def show(label: str, resp: httpx.Response) -> None:
    body = resp.text[:300].replace("\n", " ")
    print(f"[{resp.status_code}] {label}: {body}")


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=10) as c:
        show("health", c.get("/health"))
        show("docs", c.get("/docs"))

        # 401 + format error kontrak api-contract.md
        show(
            "login NIM tak dikenal",
            c.post("/api/v1/auth/login", json={"nim": "999999", "password": "salah"}),
        )

        # 400 VALIDATION_ERROR + details field
        show(
            "login body kosong",
            c.post("/api/v1/auth/login", json={}),
        )

        # 404 resource tidak ada
        show("receipt tak dikenal", c.get("/api/v1/voting/receipt/rcpt_tidakada"))

        # 401 tanpa token
        show("auth/me tanpa token", c.get("/api/v1/auth/me"))


if __name__ == "__main__":
    main()
