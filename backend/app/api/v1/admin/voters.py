import csv
import io
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_password_hash
from app.dependencies.auth import get_current_admin
from app.models.student import StudentDPT
from app.schemas.student import (
    StudentImportResult,
    StudentImportError,
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/admin/voters", tags=["Admin - Voters"])


@router.post(
    "/import",
    response_model=SuccessResponse[StudentImportResult],
    status_code=status.HTTP_200_OK,
)
async def import_voters(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: StudentDPT = Depends(get_current_admin),
):
    """Import DPT from CSV/Excel file."""
    # Validate file type
    allowed_types = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload CSV or Excel file.",
        )

    # Read file content
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 10MB.",
        )

    # Parse CSV
    try:
        text_content = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text_content))
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding must be UTF-8.",
        )

    # Validate required columns
    required_columns = {"nim", "full_name", "study_program", "email"}
    if not required_columns.issubset(set(reader.fieldnames or [])):
        missing = required_columns - set(reader.fieldnames or [])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing)}",
        )

    total_rows = 0
    imported = 0
    skipped = 0
    errors: List[StudentImportError] = []

    for row_num, row in enumerate(reader, start=1):
        total_rows += 1
        try:
            # Validate row data
            nim = row.get("nim", "").strip()
            full_name = row.get("full_name", "").strip()
            study_program = row.get("study_program", "").strip()
            email = row.get("email", "").strip().lower()

            if not all([nim, full_name, study_program, email]):
                errors.append(StudentImportError(
                    row=row_num,
                    code="MISSING_DATA",
                    message="Missing required field(s)",
                ))
                skipped += 1
                continue

            # Check if already exists
            existing = await db.execute(
                select(StudentDPT).where(StudentDPT.nim == nim)
            )
            if existing.scalar_one_or_none():
                errors.append(StudentImportError(
                    row=row_num,
                    code="DUPLICATE_NIM",
                    message="NIM sudah terdaftar.",
                ))
                skipped += 1
                continue

            existing_email = await db.execute(
                select(StudentDPT).where(StudentDPT.email == email)
            )
            if existing_email.scalar_one_or_none():
                errors.append(StudentImportError(
                    row=row_num,
                    code="DUPLICATE_EMAIL",
                    message="Email sudah terdaftar.",
                ))
                skipped += 1
                continue

            # Create student with default password (nim + "123" or random)
            # In production, generate secure random password and send via email
            default_password = f"{nim}123"
            password_hash = get_password_hash(default_password)

            student = StudentDPT(
                nim=nim,
                full_name=full_name,
                study_program=study_program,
                email=email,
                password_hash=password_hash,
                is_registered=False,
            )
            db.add(student)

            # Create voting status
            voting_status = StudentDPT.__table__.metadata.tables.get("voting_status")
            # We'll create it after flush to get the student

            try:
                await db.flush()
            except IntegrityError:
                await db.rollback()
                errors.append(StudentImportError(
                    row=row_num,
                    code="DATABASE_ERROR",
                    message="Failed to save student",
                ))
                skipped += 1
                continue

            imported += 1

        except Exception as e:
            errors.append(StudentImportError(
                row=row_num,
                code="PARSE_ERROR",
                message=str(e),
            ))
            skipped += 1

    await db.commit()

    result = StudentImportResult(
        total_rows=total_rows,
        imported=imported,
        skipped=skipped,
        errors=errors,
    )

    return SuccessResponse(
        success=True,
        message=f"Import selesai: {imported} berhasil, {skipped} dilewati.",
        data=result,
        meta={"request_id": f"req_{uuid.uuid4().hex[:8]}"},
    )


import uuid