import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import get_current_student
from app.dependencies.rate_limit import (
    rate_limit_biometric,
    check_biometric_attempts,
    increment_biometric_attempts,
    reset_biometric_attempts,
)
from app.models.student import StudentDPT
from app.models.biometric_verification import (
    BiometricVerification,
    VerificationStatus,
    LivenessMethod,
)
from app.models.voting_status import VotingStatus
from app.services.ai_client import get_ai_client
from app.services.vote_engine import get_vote_engine
from app.schemas.biometric import (
    BiometricVerifyResponse,
    BiometricVerificationData,
    BiometricVerificationStatusResponse,
    BiometricVerificationStatusData,
    FaceMatchResult,
    LivenessResult,
)

router = APIRouter(prefix="/biometric", tags=["Biometric"])


# Challenge types for liveness detection
CHALLENGE_TYPES = [LivenessMethod.BLINK, LivenessMethod.SMILE, LivenessMethod.HEAD_TURN]


@router.post(
    "/verify",
    response_model=BiometricVerifyResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def verify_face(
    frames: List[UploadFile] = File(..., description="Video frames for face verification"),
    student: StudentDPT = Depends(get_current_student),
    _rate_limit: None = Depends(rate_limit_biometric),
    db: AsyncSession = Depends(get_db),
):
    """Start face verification with liveness detection."""
    # Check if student is registered
    if not student.is_registered or not student.face_embedding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wajah belum terdaftar. Silakan lakukan registrasi terlebih dahulu.",
        )

    # Check if already voted
    voting_result = await db.execute(
        select(VotingStatus).where(VotingStatus.nim == student.nim)
    )
    voting_status = voting_result.scalar_one_or_none()
    if voting_status and voting_status.has_voted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Anda sudah menggunakan hak suara.",
        )

    # Check biometric attempts
    attempts_remaining = await check_biometric_attempts(student.nim)
    if attempts_remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Batas percobaan verifikasi terlampaui. Silakan hubungi panitia.",
        )

    # Validate frames
    if len(frames) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimal 3 frame diperlukan untuk verifikasi",
        )

    frame_bytes = []
    for frame in frames:
        if frame.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipe file tidak didukung: {frame.content_type}",
            )
        content = await frame.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File terlalu besar. Maksimal {settings.MAX_UPLOAD_SIZE_MB}MB per file.",
            )
        frame_bytes.append(content)

    # Generate challenge
    challenge_id = f"ch_{uuid.uuid4().hex[:12]}"
    challenge_type = random.choice(CHALLENGE_TYPES)
    challenge_nonce = uuid.uuid4().hex
    challenge_expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.BIOMETRIC_CHALLENGE_EXPIRE_SECONDS
    )

    # Create verification session
    verification_id = f"ver_{uuid.uuid4().hex[:12]}"
    verification = BiometricVerification(
        verification_id=verification_id,
        student_nim=student.nim,
        status=VerificationStatus.PROCESSING,
        challenge_id=challenge_id,
        challenge_type=challenge_type,
        challenge_nonce=challenge_nonce,
        challenge_expires_at=challenge_expires_at,
        attempts=0,
        max_attempts=settings.MAX_BIOMETRIC_ATTEMPTS,
    )
    db.add(verification)
    await db.flush()

    try:
        # Parse face embedding from student record
        import ast
        try:
            reference_embedding = ast.literal_eval(student.face_embedding)
        except (ValueError, SyntaxError):
            reference_embedding = []

        # Call AI service for verification
        ai_client = get_ai_client()
        challenge = {
            "challenge_id": challenge_id,
            "type": challenge_type.value,
            "nonce": challenge_nonce,
            "issued_at": datetime.now(timezone.utc).isoformat(),
        }

        result = await ai_client.verify_face(
            verification_id=verification_id,
            reference_embedding=reference_embedding,
            model_version="face-model-v1",
            challenge=challenge,
            frames=frame_bytes,
        )

        # Process AI result
        ai_data = result.get("data", {})
        face_match = ai_data.get("face_match", {})
        liveness = ai_data.get("liveness", {})

        face_verified = face_match.get("verified", False)
        similarity = face_match.get("similarity", 0.0)
        liveness_verified = liveness.get("verified", False)
        challenge_passed = liveness.get("challenge_passed", False)

        verification.attempts += 1
        verification.face_match_verified = face_verified
        verification.face_similarity = similarity
        verification.liveness_verified = liveness_verified
        verification.liveness_method = challenge_type
        verification.ai_model_version = ai_data.get("model_version")
        verification.ai_processed_at = datetime.now(timezone.utc)

        # Determine overall status
        if face_verified and liveness_verified and challenge_passed:
            verification.status = VerificationStatus.VERIFIED
            verification.verified_at = datetime.now(timezone.utc)
            await reset_biometric_attempts(student.nim)
        else:
            verification.status = VerificationStatus.REJECTED
            await increment_biometric_attempts(student.nim)

            if face_verified is False:
                verification.error_message = "Wajah tidak cocok dengan data terdaftar"
            elif not liveness_verified:
                verification.error_message = "Liveness detection gagal. Pastikan Anda manusia asli."
            elif not challenge_passed:
                verification.error_message = "Tantangan liveness tidak terpenuhi"

        await db.commit()

        return BiometricVerifyResponse(
            success=True,
            message="Verifikasi wajah sedang diproses.",
            data=BiometricVerificationData(
                verification_id=verification_id,
                status=verification.status.value,
                expires_in=settings.BIOMETRIC_CHALLENGE_EXPIRE_SECONDS,
            ),
            meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
        )

    except Exception as e:
        await db.rollback()
        # Create a NEW record for failure status since the original is detached after rollback
        failed_verification = BiometricVerification(
            verification_id=f"ver_{uuid.uuid4().hex[:12]}",
            student_nim=student.nim,
            status=VerificationStatus.FAILED,
            error_message=str(e),
            attempts=1,
            max_attempts=settings.MAX_BIOMETRIC_ATTEMPTS,
        )
        db.add(failed_verification)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Service error: {str(e)}",
        )


@router.get(
    "/status/{verification_id}",
    response_model=BiometricVerificationStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_verification_status(
    verification_id: str,
    student: StudentDPT = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get biometric verification status."""
    result = await db.execute(
        select(BiometricVerification).where(
            BiometricVerification.verification_id == verification_id,
            BiometricVerification.student_nim == student.nim,
        )
    )
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verifikasi tidak ditemukan",
        )

    # Build response data
    face_match = None
    if verification.face_match_verified is not None:
        face_match = FaceMatchResult(
            verified=verification.face_match_verified,
            similarity=verification.face_similarity or 0.0,
            threshold_version="threshold-v1",
        )

    liveness = None
    if verification.liveness_verified is not None:
        liveness = LivenessResult(
            verified=verification.liveness_verified,
            method=verification.liveness_method.value if verification.liveness_method else "unknown",
            challenge_passed=verification.liveness_verified,
        )

    return BiometricVerificationStatusResponse(
        success=True,
        message="Status verifikasi berhasil diambil.",
        data=BiometricVerificationStatusData(
            verification_id=verification.verification_id,
            status=verification.status.value,
            verified_at=verification.verified_at.isoformat() if verification.verified_at else None,
            attempts_remaining=verification.attempts_remaining,
            face_match=face_match,
            liveness=liveness,
        ),
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )