import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_student, validate_voting_token
from app.dependencies.rate_limit import rate_limit_voting
from app.models.student import StudentDPT
from app.models.biometric_verification import BiometricVerification, VerificationStatus
from app.models.voting_token import VotingToken, TokenStatus
from app.models.election import Election, ElectionStatus
from app.services.vote_engine import get_vote_engine
from app.schemas.voting import (
    VotingTokenRequest,
    VotingTokenResponse,
    VotingTokenData,
    CastVoteRequest,
    CastVoteResponse,
    CastVoteData,
    ReceiptResponse,
    ReceiptData,
)

router = APIRouter(prefix="/voting", tags=["Voting"])


@router.post(
    "/token",
    response_model=VotingTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_voting_token(
    token_request: VotingTokenRequest,
    student: StudentDPT = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Issue a one-time voting token after successful biometric verification."""
    # Verify the biometric verification
    verification_result = await db.execute(
        select(BiometricVerification).where(
            BiometricVerification.verification_id == token_request.verification_id,
            BiometricVerification.student_nim == student.nim,
        )
    )
    verification = verification_result.scalar_one_or_none()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verifikasi tidak ditemukan",
        )

    if verification.status != VerificationStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verifikasi belum berhasil (status: {verification.status.value})",
        )

    # Check if verification is expired (1 hour)
    if verification.verified_at:
        from datetime import datetime, timezone, timedelta
        age = datetime.now(timezone.utc) - verification.verified_at
        if age > timedelta(hours=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verifikasi biometrik sudah kedaluwarsa. Silakan verifikasi ulang.",
            )

    # Get active election (for now, assume one active election)
    election_result = await db.execute(
        select(Election).where(Election.status == ElectionStatus.ACTIVE)
    )
    election = election_result.scalar_one_or_none()
    if not election:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tidak ada pemilihan aktif saat ini",
        )

    # Check eligibility using vote engine
    vote_engine = get_vote_engine(db)
    eligible, message = await vote_engine.check_eligibility(student.nim, election.election_id)
    if not eligible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )

    # Check if voting token already issued for this verification
    existing_token = await db.execute(
        select(VotingToken).where(
            VotingToken.verification_id == token_request.verification_id,
            VotingToken.status == TokenStatus.ISSUED,
        )
    )
    if existing_token.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Voting token sudah diterbitkan untuk verifikasi ini",
        )

    # Issue voting token
    token_record = await vote_engine.issue_voting_token(
        student_nim=student.nim,
        election_id=election.election_id,
        verification_id=token_request.verification_id,
    )

    # Get the actual token (we need to recreate it since we only stored hash)
    # In practice, we'd return the token generated in issue_voting_token
    # For now, we'll generate a new one (this is a simplification)
    token_payload = {
        "sub": student.nim,
        "election_id": election.election_id,
        "verification_id": token_request.verification_id,
        "jti": token_record.token_id,
    }
    from app.core.security import create_voting_token
    voting_token = create_voting_token(token_payload)

    return VotingTokenResponse(
        success=True,
        message="Voting token berhasil diterbitkan.",
        data=VotingTokenData(
            voting_token=voting_token,
            token_type="Bearer",
            expires_in=300,
            election_id=election.election_id,
        ),
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


@router.post(
    "/cast",
    response_model=CastVoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def cast_vote(
    request: Request,
    vote_request: CastVoteRequest,
    token: VotingToken = Depends(validate_voting_token),
    _rate_limit: None = Depends(rate_limit_voting),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
):
    """Cast vote using voting token (anonymous ballot)."""
    # Verify idempotency key matches
    if idempotency_key != vote_request.idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency key mismatch",
        )

    # Verify token belongs to the election
    if token.election_id != vote_request.election_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token tidak valid untuk pemilihan ini",
        )

    # Cast vote using vote engine
    vote_engine = get_vote_engine(db)
    try:
        ballot, receipt_id, vote_hash = await vote_engine.cast_vote(
            token=token,
            candidate_id=vote_request.candidate_id,
            election_id=vote_request.election_id,
            idempotency_key=idempotency_key,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return CastVoteResponse(
        success=True,
        message="Suara berhasil diterima.",
        data=CastVoteData(
            receipt_id=receipt_id,
            receipt_hash=vote_hash,
            status="accepted",
            message="Suara berhasil dihitung.",
        ),
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


@router.get(
    "/receipt/{receipt_id}",
    response_model=ReceiptResponse,
    status_code=status.HTTP_200_OK,
)
async def get_receipt(
    receipt_id: str,
    student: StudentDPT = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get vote receipt (verification of participation without revealing choice)."""
    vote_engine = get_vote_engine(db)
    receipt = await vote_engine.get_receipt(receipt_id)

    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt tidak ditemukan",
        )

    # Verify receipt belongs to this student
    if receipt.get("student_nim") != student.nim:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tidak memiliki akses ke receipt ini",
        )

    return ReceiptResponse(
        success=True,
        message="Status receipt berhasil diambil.",
        data=ReceiptData(
            receipt_id=receipt["receipt_id"],
            receipt_hash=receipt["vote_hash"],
            status="accepted",
            election_id=receipt.get("election_id", ""),
        ),
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )