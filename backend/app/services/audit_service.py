from datetime import datetime
from typing import Optional

class AuditService:
    async def log_login(self, nim: str, ip: str, success: bool):
        pass  # placeholder
    async def log_vote(self, nim: str, event: str):
        pass