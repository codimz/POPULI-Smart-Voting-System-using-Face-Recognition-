from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class VotingTokenRequest(BaseModel):
    verification_id: str = Field(..., min_length=1, max_length=50)

    model_config = ConfigDict(json_schema_extra={
        "example": {"verification_id": "ver_8f12ab"}
    })


class VotingTokenResponse(BaseModel):
    success: bool = True
    message: str = "Voting token berhasil diterbitkan."
    data: "VotingTokenData"
    meta: dict = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Voting token berhasil diterbitkan.",
            "data": {
                "voting_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 300,
                "election_id": "el_2026_hima"
            },
            "meta": {"request_id": "req_7f82a1"}
        }
    })


class VotingTokenData(BaseModel):
    voting_token: str
    token_type: str = "Bearer"
    expires_in: int
    election_id: str


class CastVoteRequest(BaseModel):
    candidate_id: int = Field(..., gt=0)
    election_id: str = Field(..., min_length=1, max_length=50)
    idempotency_key: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "candidate_id": 1,
            "election_id": "el_2026_hima",
            "idempotency_key": "idem_72ab91"
        }
    })


class CastVoteResponse(BaseModel):
    success: bool = True
    message: str = "Suara berhasil diterima."
    data: "CastVoteData"
    meta: dict = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Suara berhasil diterima.",
            "data": {
                "receipt_id": "rcpt_8f12ab",
                "receipt_hash": "sha256_hash_here",
                "status": "accepted",
                "message": "Suara berhasil diterima."
            },
            "meta": {"request_id": "req_7f82a1"}
        }
    })


class CastVoteData(BaseModel):
    receipt_id: str
    receipt_hash: str
    status: str
    message: str


class ReceiptResponse(BaseModel):
    success: bool = True
    message: str = "Status receipt berhasil diambil."
    data: "ReceiptData"
    meta: dict = Field(default_factory=dict)


class ReceiptData(BaseModel):
    receipt_id: str
    receipt_hash: str
    status: str
    election_id: str