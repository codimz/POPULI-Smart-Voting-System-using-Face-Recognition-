import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_token,
)
from app.dependencies.auth import get_current_student
from app.dependencies.rate_limit import rate_limit_login
from app.models.student import StudentDPT
from app.models.voting_status import VotingStatus
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    Token,
)
from app.schemas.student import StudentResponse
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit_login)],
)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate student with NIM and password."""
    # Find student
    result = await db.execute(
        select(StudentDPT).where(StudentDPT.nim == login_data.nim)
    )
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid NIM or password",
        )

    # Verify password
    if not verify_password(login_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid NIM or password",
        )

    # Check voting status
    voting_result = await db.execute(
        select(VotingStatus).where(VotingStatus.nim == student.nim)
    )
    voting_status = voting_result.scalar_one_or_none()
    has_voted = voting_status.has_voted if voting_status else False

    # Create tokens
    access_token = create_access_token(
        data={"sub": student.nim, "name": student.full_name}
    )
    refresh_token = create_refresh_token(data={"sub": student.nim})

    # TODO: Store refresh token in Redis with expiry

    token_data = Token(
        access_token=access_token,
        token_type="Bearer",
        expires_in=15 * 60,  # 15 minutes
    )

    return LoginResponse(
        success=True,
        message="Login berhasil.",
        data=token_data,
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        nim = payload.get("sub")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    # Verify student still exists
    result = await db.execute(select(StudentDPT).where(StudentDPT.nim == nim))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found",
        )

    access_token = create_access_token(data={"sub": student.nim})
    new_refresh_token = create_refresh_token(data={"sub": student.nim})

    token_data = Token(
        access_token=access_token,
        token_type="Bearer",
        expires_in=15 * 60,
    )

    return RefreshTokenResponse(
        success=True,
        message="Token berhasil diperbarui.",
        data=token_data,
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


@router.get("/me", response_model=SuccessResponse[StudentResponse])
async def get_current_user(
    student: StudentDPT = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated student info."""
    voting_result = await db.execute(
        select(VotingStatus).where(VotingStatus.nim == student.nim)
    )
    voting_status = voting_result.scalar_one_or_none()

    student_data = StudentResponse(
        nim=student.nim,
        full_name=student.full_name,
        study_program=student.study_program,
        email=student.email,
        is_registered=student.is_registered,
        has_voted=voting_status.has_voted if voting_status else False,
        created_at=student.created_at.isoformat() if student.created_at else "",
        updated_at=student.updated_at.isoformat() if student.updated_at else "",
    )

    return SuccessResponse(
        success=True,
        message="Data mahasiswa berhasil diambil.",
        data=student_data,
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )