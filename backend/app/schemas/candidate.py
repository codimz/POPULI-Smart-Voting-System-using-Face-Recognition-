from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, HttpUrl


class CandidateBase(BaseModel):
    election_type: str = Field(..., min_length=1, max_length=50)
    candidate_name: str = Field(..., min_length=1, max_length=100)
    vision_mission: Optional[str] = Field(None, max_length=5000)
    photo_url: Optional[HttpUrl] = Field(None, max_length=255)


class CandidateCreate(CandidateBase):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "election_type": "HIMA",
            "candidate_name": "Kandidat A",
            "vision_mission": "Visi dan misi kandidat...",
            "photo_url": "https://example.com/photo.jpg"
        }
    })


class CandidateUpdate(BaseModel):
    candidate_name: Optional[str] = Field(None, min_length=1, max_length=100)
    vision_mission: Optional[str] = Field(None, max_length=5000)
    photo_url: Optional[HttpUrl] = Field(None, max_length=255)


class CandidateResponse(CandidateBase):
    candidate_id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "candidate_id": 1,
                "election_type": "HIMA",
                "candidate_name": "Kandidat A",
                "vision_mission": "Visi dan misi kandidat...",
                "photo_url": "https://example.com/photo.jpg",
                "created_at": "2026-10-01T00:00:00Z",
                "updated_at": "2026-10-01T00:00:00Z"
            }
        }
    )