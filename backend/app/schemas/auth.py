from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "Bearer",
            "expires_in": 900
        }
    })


class TokenPayload(BaseModel):
    sub: str  # NIM
    type: str  # access, refresh, voting
    exp: int
    iat: Optional[int] = None


class LoginRequest(BaseModel):
    nim: str = Field(..., min_length=1, max_length=20, description="Nomor Induk Mahasiswa")
    password: str = Field(..., min_length=1, description="Password mahasiswa")

    model_config = ConfigDict(json_schema_extra={
        "example": {"nim": "2310112345", "password": "password123"}
    })


class StudentInfo(BaseModel):
    nim: str
    full_name: str
    study_program: str
    is_registered: bool
    has_voted: bool


class LoginResponse(BaseModel):
    success: bool = True
    message: str = "Login berhasil."
    data: Token
    meta: dict = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Login berhasil.",
            "data": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 900
            },
            "meta": {"request_id": "req_7f82a1"}
        }
    })


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    success: bool = True
    message: str = "Token berhasil diperbarui."
    data: Token
    meta: dict = Field(default_factory=dict)