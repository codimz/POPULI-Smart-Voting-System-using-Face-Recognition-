from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class StudentBase(BaseModel):
    nim: str = Field(..., min_length=1, max_length=20, pattern=r"^\d+$")
    full_name: str = Field(..., min_length=1, max_length=100)
    study_program: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=255)


class StudentCreate(StudentBase):
    password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "nim": "2310112345",
            "full_name": "Budi Santoso",
            "study_program": "Teknik Informatika",
            "email": "budi.santoso@student.kampus.ac.id",
            "password": "securePassword123"
        }
    })


class StudentUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    study_program: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    face_embedding: Optional[str] = None
    is_registered: Optional[bool] = None


class StudentResponse(StudentBase):
    is_registered: bool
    has_voted: bool
    created_at: str
    updated_at: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "nim": "2310112345",
                "full_name": "Budi Santoso",
                "study_program": "Teknik Informatika",
                "email": "budi.santoso@student.kampus.ac.id",
                "is_registered": True,
                "has_voted": False,
                "created_at": "2026-10-01T00:00:00Z",
                "updated_at": "2026-10-01T00:00:00Z"
            }
        }
    )


class StudentImportError(BaseModel):
    row: int
    code: str
    message: str

    model_config = ConfigDict(json_schema_extra={
        "example": {"row": 12, "code": "DUPLICATE_NIM", "message": "NIM sudah terdaftar."}
    })


class StudentImportResult(BaseModel):
    total_rows: int
    imported: int
    skipped: int
    errors: list[StudentImportError]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_rows": 500,
            "imported": 490,
            "skipped": 10,
            "errors": [
                {"row": 12, "code": "DUPLICATE_NIM", "message": "NIM sudah terdaftar."}
            ]
        }
    })