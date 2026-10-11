from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ElectionBase(BaseModel):
    election_type: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    starts_at: datetime
    ends_at: datetime
    registration_starts_at: Optional[datetime] = None
    registration_ends_at: Optional[datetime] = None


class ElectionCreate(ElectionBase):
    election_id: str = Field(..., min_length=1, max_length=50)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "election_id": "el_2026_hima",
            "election_type": "HIMA",
            "name": "Pemilihan Ketua HIMATI 2026",
            "description": "Pemilihan Ketua Himpunan Mahasiswa Teknik Informatika Periode 2026/2027",
            "starts_at": "2026-10-12T08:00:00Z",
            "ends_at": "2026-10-14T20:00:00Z",
            "registration_starts_at": "2026-10-01T00:00:00Z",
            "registration_ends_at": "2026-10-10T23:59:59Z"
        }
    })


class ElectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    registration_starts_at: Optional[datetime] = None
    registration_ends_at: Optional[datetime] = None
    status: Optional[str] = None  # draft, scheduled, active, closed, archived


class ElectionResponse(ElectionBase):
    election_id: str
    status: str
    created_at: str
    updated_at: str
    is_active: bool
    is_registration_open: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "election_id": "el_2026_hima",
                "election_type": "HIMA",
                "name": "Pemilihan Ketua HIMATI 2026",
                "description": "Pemilihan Ketua Himpunan Mahasiswa Teknik Informatika Periode 2026/2027",
                "starts_at": "2026-10-12T08:00:00Z",
                "ends_at": "2026-10-14T20:00:00Z",
                "registration_starts_at": "2026-10-01T00:00:00Z",
                "registration_ends_at": "2026-10-10T23:59:59Z",
                "status": "active",
                "created_at": "2026-10-01T00:00:00Z",
                "updated_at": "2026-10-01T00:00:00Z",
                "is_active": True,
                "is_registration_open": False
            }
        }
    )