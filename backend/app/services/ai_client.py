from typing import Optional
import httpx
from app.core.config import settings


class AIServiceClient:
    def __init__(self):
        self.base_url = settings.AI_SERVICE_URL.rstrip("/")
        self.timeout = settings.AI_SERVICE_TIMEOUT
        self.api_key = settings.AI_SERVICE_API_KEY
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def register_face(
        self,
        registration_id: str,
        images: list[bytes],
        model_version: str = "face-model-v1",
    ) -> dict:
        """Register face embedding from multiple images."""
        files = [
            ("images", (f"face_{i}.jpg", img, "image/jpeg"))
            for i, img in enumerate(images)
        ]
        data = {
            "registration_id": registration_id,
            "model_version": model_version,
        }

        response = await self.client.post(
            "/internal/v1/face/register",
            files=files,
            data=data,
        )
        response.raise_for_status()
        return response.json()

    async def verify_face(
        self,
        verification_id: str,
        reference_embedding: list[float],
        model_version: str,
        challenge: dict,
        frames: list[bytes],
    ) -> dict:
        """Verify face with liveness detection."""
        files = [
            ("frames", (f"frame_{i}.jpg", frame, "image/jpeg"))
            for i, frame in enumerate(frames)
        ]
        data = {
            "verification_id": verification_id,
            "reference_embedding": str(reference_embedding),  # Will be JSON encoded
            "model_version": model_version,
            "challenge": str(challenge),  # Will be JSON encoded
        }

        response = await self.client.post(
            "/internal/v1/face/verify",
            files=files,
            data=data,
        )
        response.raise_for_status()
        return response.json()

    async def check_liveness(
        self,
        verification_id: str,
        challenge: dict,
        frames: list[bytes],
    ) -> dict:
        """Check liveness only (separate endpoint if needed)."""
        files = [
            ("frames", (f"frame_{i}.jpg", frame, "image/jpeg"))
            for i, frame in enumerate(frames)
        ]
        data = {
            "verification_id": verification_id,
            "challenge": str(challenge),
        }

        response = await self.client.post(
            "/internal/v1/liveness/check",
            files=files,
            data=data,
        )
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict:
        """Check AI service health."""
        response = await self.client.get("/internal/v1/health")
        response.raise_for_status()
        return response.json()


_ai_client: Optional[AIServiceClient] = None


def get_ai_client() -> AIServiceClient:
    global _ai_client
    if _ai_client is None:
        _ai_client = AIServiceClient()
    return _ai_client


async def close_ai_client() -> None:
    global _ai_client
    if _ai_client:
        await _ai_client.close()
        _ai_client = None