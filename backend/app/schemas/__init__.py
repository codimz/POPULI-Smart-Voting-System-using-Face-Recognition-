from app.schemas.auth import (
    Token,
    TokenPayload,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentImportResult,
    StudentImportError,
)
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
)
from app.schemas.biometric import (
    BiometricRegisterRequest,
    BiometricRegisterResponse,
    BiometricStatusResponse,
    BiometricVerifyRequest,
    BiometricVerifyResponse,
    FaceMatchResult,
    LivenessResult,
)
from app.schemas.voting import (
    VotingTokenRequest,
    VotingTokenResponse,
    CastVoteRequest,
    CastVoteResponse,
    ReceiptResponse,
)
from app.schemas.election import (
    ElectionCreate,
    ElectionUpdate,
    ElectionResponse,
)
from app.schemas.admin import (
    DashboardStats,
    TurnoutStats,
    ResultsStats,
    AuditLogResponse,
    ExportRequest,
)
from app.schemas.common import (
    SuccessResponse,
    ErrorResponse,
    ErrorDetail,
    PaginatedResponse,
    MessageResponse,
)

__all__ = [
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    # Student
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentImportResult",
    "StudentImportError",
    # Candidate
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    # Biometric
    "BiometricRegisterRequest",
    "BiometricRegisterResponse",
    "BiometricStatusResponse",
    "BiometricVerifyRequest",
    "BiometricVerifyResponse",
    "FaceMatchResult",
    "LivenessResult",
    # Voting
    "VotingTokenRequest",
    "VotingTokenResponse",
    "CastVoteRequest",
    "CastVoteResponse",
    "ReceiptResponse",
    # Election
    "ElectionCreate",
    "ElectionUpdate",
    "ElectionResponse",
    # Admin
    "DashboardStats",
    "TurnoutStats",
    "ResultsStats",
    "AuditLogResponse",
    "ExportRequest",
    # Common
    "SuccessResponse",
    "ErrorResponse",
    "ErrorDetail",
    "PaginatedResponse",
    "MessageResponse",
]