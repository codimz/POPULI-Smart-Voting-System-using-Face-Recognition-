from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class BiometricRegisterRequest(BaseModel):
    # Images will be sent as multipart/form-data
    pass


class BiometricRegisterResponse(BaseModel):
    success: bool = True
    message: str = "Registrasi wajah sedang diproses."
    data: "BiometricRegistrationData"
    meta: dict = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Registrasi wajah sedang diproses.",
            "data": {
                "registration_id": "reg_123abc",
                "status": "processing",
                "message": "Registrasi wajah sedang diproses."
            },
            "meta": {"request_id": "req_7f82a1"}
        }
    })


class BiometricRegistrationData(BaseModel):
    registration_id: str
    status: str  # pending, processing, completed, failed
    message: str


class BiometricStatusResponse(BaseModel):
    success: bool = True
    message: str = "Status registrasi berhasil diambil."
    data: "BiometricRegistrationStatusData"
    meta: dict = Field(default_factory=dict)


class BiometricRegistrationStatusData(BaseModel):
    registration_id: str
    status: str
    is_registered: bool


class FaceMatchResult(BaseModel):
    verified: bool
    similarity: float
    threshold_version: str


class LivenessResult(BaseModel):
    verified: bool
    method: str
    challenge_passed: bool


class BiometricVerifyRequest(BaseModel):
    # Frames and challenge_id sent as multipart/form-data
    pass


class BiometricVerifyResponse(BaseModel):
    success: bool = True
    message: str = "Verifikasi wajah sedang diproses."
    data: "BiometricVerificationData"
    meta: dict = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "message": "Verifikasi wajah sedang diproses.",
            "data": {
                "verification_id": "ver_8f12ab",
                "status": "processing",
                "expires_in": 120
            },
            "meta": {"request_id": "req_7f82a1"}
        }
    })


class BiometricVerificationData(BaseModel):
    verification_id: str
    status: str  # pending, processing, verified, rejected, expired, failed
    expires_in: int


class BiometricVerificationStatusResponse(BaseModel):
    success: bool = True
    message: str = "Status verifikasi berhasil diambil."
    data: "BiometricVerificationStatusData"
    meta: dict = Field(default_factory=dict)


class BiometricVerificationStatusData(BaseModel):
    verification_id: str
    status: str
    verified_at: Optional[str] = None
    attempts_remaining: int
    face_match: Optional[FaceMatchResult] = None
    liveness: Optional[LivenessResult] = None