import uuid
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import get_current_student
from app.dependencies.rate_limit import rate_limit_biometric
from app.models.student import StudentDPT
from app.models.biometric_verification import BiometricVerification, VerificationStatus
from app.services.ai_client import get_ai_client
from app.schemas.biometric import (
    BiometricRegisterResponse,
    BiometricRegistrationData,
    BiometricStatusResponse,
    BiometricRegistrationStatusData,
)

router = APIRouter(prefix="/biometric", tags=["Biometric"])


@router.post(
    "/register",
    response_model=BiometricRegisterResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limit_biometric)],
)
async def register_face(
    images: List[UploadFile] = File(..., description="3-5 face images"),
    student: StudentDPT = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Register face embedding for student (3-5 images)."""
    # Validate number of images
    if len(images) < 3 or len(images) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Harus mengunggah 3-5 foto wajah",
        )

    # Validate file types and sizes
    image_bytes = []
    for img in images:
        if img.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipe file tidak didukung: {img.content_type}. Gunakan JPEG, PNG, atau WebP.",
            )
        content = await img.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File terlalu besar. Maksimal {settings.MAX_UPLOAD_SIZE_MB}MB per file.",
            )
        image_bytes.append(content)

    # Check if already registered
    if student.is_registered:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wajah sudah terdaftar. Hubungi admin untuk registrasi ulang.",
        )

    # Create registration record
    registration_id = f"reg_{uuid.uuid4().hex[:12]}"
    verification = BiometricVerification(
        verification_id=registration_id,
        student_nim=student.nim,
        status=VerificationStatus.PROCESSING,
        max_attempts=1,  # Registration is single attempt
    )
    db.add(verification)
    await db.flush()

    try:
        # Call AI service to extract embedding
        ai_client = get_ai_client()
        result = await ai_client.register_face(
            registration_id=registration_id,
            images=image_bytes,
        )

        # Update student with embedding
        if result.get("success") and result.get("data", {}).get("embedding"):
            embedding = result["data"]["embedding"]
            student.face_embedding = str(embedding.get("vector"))
            student.is_registered = True

            verification.status = VerificationStatus.COMPLETED
            verification.face_match_verified = True
            verification.ai_model_version = embedding.get("model")
        else:
            verification.status = VerificationStatus.FAILED
            verification.error_message = result.get("message", "Registration failed")

        await db.commit()

        return BiometricRegisterResponse(
            success=True,
            message="Registrasi wajah berhasil diproses.",
            data=BiometricRegistrationData(
                registration_id=registration_id,
                status=verification.status.value,
                message="Registrasi wajah berhasil." if student.is_registered else "Registrasi gagal.",
            ),
            meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
        )

    except Exception as e:
        await db.rollback()
        verification.status = VerificationStatus.FAILED
        verification.error_message = str(e)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Service error: {str(e)}",
        )


@router.get(
    "/register/{registration_id}",
    response_model=BiometricStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_registration_status(
    registration_id: str,
    student: StudentDPT = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get face registration status."""
    result = await db.execute(
        select(BiometricVerification).where(
            BiometricVerification.verification_id == registration_id,
            BiometricVerification.student_nim == student.nim,
        )
    )
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registrasi tidak ditemukan",
        )

    return BiometricStatusResponse(
        success=True,
        message="Status registrasi berhasil diambil.",
        data=BiometricRegistrationStatusData(
            registration_id=verification.verification_id,
            status=verification.status.value,
            is_registered=student.is_registered,
        ),
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )