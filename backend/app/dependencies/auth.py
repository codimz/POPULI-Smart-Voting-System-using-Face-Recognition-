from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, verify_voting_token
from app.core.database import get_db
from app.models.student import StudentDPT
from app.models.voting_status import VotingStatus
from app.models.voting_token import VotingToken, TokenStatus


security = HTTPBearer(auto_error=False)


async def get_current_student(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> StudentDPT:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        nim: str = payload.get("sub")
        if not nim:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    result = await db.execute(select(StudentDPT).where(StudentDPT.nim == nim))
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found",
        )

    # Check voting status
    voting_result = await db.execute(
        select(VotingStatus).where(VotingStatus.nim == nim)
    )
    voting_status = voting_result.scalar_one_or_none()
    student.has_voted = voting_status.has_voted if voting_status else False

    # Attach to request for logging
    request.state.student = student
    request.state.nim = nim

    return student


async def get_optional_student(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[StudentDPT]:
    if not credentials:
        return None

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        nim: str = payload.get("sub")
        if not nim:
            return None
    except ValueError:
        return None

    result = await db.execute(select(StudentDPT).where(StudentDPT.nim == nim))
    return result.scalar_one_or_none()


async def get_current_admin(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> StudentDPT:
    student = await get_current_student(request, credentials, db)

    # In a real implementation, check for admin role
    # For now, we'll check if email is admin or use a separate admin table
    if not student.email.endswith("@admin.kampus.ac.id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    request.state.is_admin = True
    return student


def require_roles(*allowed_roles: str):
    async def role_checker(
        student: StudentDPT = Depends(get_current_student),
    ) -> StudentDPT:
        # In a real implementation, check student.role against allowed_roles
        # For MVP, we'll just pass through
        return student

    return role_checker


async def get_voting_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Voting token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_voting_token(credentials.credentials)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


async def validate_voting_token(
    payload: dict = Depends(get_voting_token_payload),
    db: AsyncSession = Depends(get_db),
) -> VotingToken:
    token_hash = payload.get("token_hash") or payload.get("jti")
    if not token_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid voting token",
        )

    result = await db.execute(
        select(VotingToken).where(VotingToken.token_hash == token_hash)
    )
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Voting token not found",
        )

    if not token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Voting token expired or already used",
        )

    return token