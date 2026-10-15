import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.security import create_voting_token, create_access_token
from app.models.student import StudentDPT
from app.models.voting_status import VotingStatus
from app.models.candidate import Candidate
from app.models.ballot import BallotBox
from app.models.election import Election, ElectionStatus
from app.models.biometric_verification import BiometricVerification, VerificationStatus
from app.models.voting_token import VotingToken, TokenStatus
from app.models.idempotency import IdempotencyRecord
from app.models.vote_receipt import VoteReceipt
from app.services.redis_client import get_redis


class VoteEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_eligibility(
        self,
        student_nim: str,
        election_id: str,
    ) -> tuple[bool, str]:
        """Check if student is eligible to vote."""
        # Check student exists and is registered
        student_result = await self.db.execute(
            select(StudentDPT).where(StudentDPT.nim == student_nim)
        )
        student = student_result.scalar_one_or_none()
        if not student:
            return False, "Student not found"

        if not student.is_registered:
            return False, "Face not registered"

        # Check election exists and is active
        election_result = await self.db.execute(
            select(Election).where(Election.election_id == election_id)
        )
        election = election_result.scalar_one_or_none()
        if not election:
            return False, "Election not found"

        if election.status != ElectionStatus.ACTIVE:
            return False, f"Election is not active (status: {election.status.value})"

        if not election.is_active:
            return False, "Election is not within voting period"

        # Check voting status
        voting_result = await self.db.execute(
            select(VotingStatus).where(VotingStatus.nim == student_nim)
        )
        voting_status = voting_result.scalar_one_or_none()
        if voting_status and voting_status.has_voted:
            return False, "Already voted"

        # Check biometric verification
        verification_result = await self.db.execute(
            select(BiometricVerification)
            .where(
                BiometricVerification.student_nim == student_nim,
                BiometricVerification.status == VerificationStatus.VERIFIED,
            )
            .order_by(BiometricVerification.verified_at.desc())
        )
        verification = verification_result.scalar_one_or_none()
        if not verification:
            return False, "Biometric verification required"

        # Check verification not expired (e.g., within 1 hour)
        if verification.verified_at:
            age = datetime.now(timezone.utc) - verification.verified_at
            if age > timedelta(hours=1):
                return False, "Biometric verification expired"

        return True, "Eligible"

    async def issue_voting_token(
        self,
        student_nim: str,
        election_id: str,
        verification_id: str,
    ) -> VotingToken:
        """Issue a one-time voting token."""
        # Generate secure token
        token_payload = {
            "sub": student_nim,
            "election_id": election_id,
            "verification_id": verification_id,
            "jti": uuid.uuid4().hex,
        }
        voting_token = create_voting_token(token_payload)
        token_hash = hashlib.sha256(voting_token.encode()).hexdigest()

        # Create token record
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.VOTING_TOKEN_EXPIRE_SECONDS
        )

        token_record = VotingToken(
            student_nim=student_nim,
            election_id=election_id,
            verification_id=verification_id,
            token_hash=token_hash,
            status=TokenStatus.ISSUED,
            expires_at=expires_at,
        )

        self.db.add(token_record)
        await self.db.flush()

        return token_record

    async def cast_vote(
        self,
        token: VotingToken,
        candidate_id: int,
        election_id: str,
        idempotency_key: str,
    ) -> tuple[BallotBox, str, str]:
        """Cast vote atomically with idempotency."""
        # Check idempotency
        existing = await self.db.execute(
            select(IdempotencyRecord).where(
                IdempotencyRecord.idempotency_key == idempotency_key
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Duplicate request (idempotency key already used)")

        # Validate candidate
        candidate_result = await self.db.execute(
            select(Candidate).where(
                Candidate.candidate_id == candidate_id,
                Candidate.election_type == election_id,  # election_type in candidate matches election_id
            )
        )
        candidate = candidate_result.scalar_one_or_none()
        if not candidate:
            raise ValueError("Invalid candidate for this election")

        # Generate vote hash for receipt
        vote_data = f"{token.token_hash}:{candidate_id}:{datetime.now(timezone.utc).isoformat()}"
        vote_hash = hashlib.sha256(vote_data.encode()).hexdigest()

        # Create ballot (anonymous - no NIM reference)
        ballot = BallotBox(
            candidate_id=candidate_id,
            election_type=election_id,
            vote_hash=vote_hash,
        )
        self.db.add(ballot)

        # Flush to get ballot_id for receipt
        await self.db.flush()

        # Create vote receipt
        receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
        receipt = VoteReceipt(
            receipt_id=receipt_id,
            student_nim=token.student_nim,
            election_id=election_id,
            vote_hash=vote_hash,
            ballot_id=ballot.ballot_id,
        )
        self.db.add(receipt)

        # Mark token as consumed
        token.status = TokenStatus.CONSUMED
        token.consumed_at = datetime.now(timezone.utc)
        token.idempotency_key = idempotency_key

        # Update voting status
        voting_result = await self.db.execute(
            select(VotingStatus).where(VotingStatus.nim == token.student_nim)
        )
        voting_status = voting_result.scalar_one_or_none()
        if not voting_status:
            voting_status = VotingStatus(
                nim=token.student_nim,
                has_voted=True,
                voted_at=datetime.now(timezone.utc),
                verification_method="face_biometric",
            )
            self.db.add(voting_status)
        else:
            voting_status.has_voted = True
            voting_status.voted_at = datetime.now(timezone.utc)
            voting_status.verification_method = "face_biometric"

        # Save idempotency record
        idempotency_record = IdempotencyRecord(
            idempotency_key=idempotency_key,
            request_hash=hashlib.sha256(
                f"{token.token_hash}:{candidate_id}".encode()
            ).hexdigest(),
            response_status=201,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.IDEMPOTENCY_KEY_EXPIRE_HOURS),
        )
        self.db.add(idempotency_record)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Vote already cast or database error")

        return ballot, receipt_id, vote_hash

    async def get_receipt(self, receipt_id: str) -> Optional[dict]:
        """Get vote receipt (without revealing candidate choice)."""
        result = await self.db.execute(
            select(VoteReceipt).where(VoteReceipt.receipt_id == receipt_id)
        )
        receipt = result.scalar_one_or_none()
        if not receipt:
            return None
        return {
            "receipt_id": receipt.receipt_id,
            "student_nim": receipt.student_nim,
            "election_id": receipt.election_id,
            "vote_hash": receipt.vote_hash,
            "created_at": receipt.created_at.isoformat() if receipt.created_at else None,
        }

    async def get_results(self, election_id: str) -> list[dict]:
        """Get election results."""
        result = await self.db.execute(
            select(
                Candidate.candidate_id,
                Candidate.candidate_name,
                func.count(BallotBox.ballot_id).label("vote_count"),
            )
            .join(BallotBox, BallotBox.candidate_id == Candidate.candidate_id)
            .where(
                Candidate.election_type == election_id,
                BallotBox.election_type == election_id,
            )
            .group_by(Candidate.candidate_id, Candidate.candidate_name)
        )
        rows = result.all()

        total_votes = sum(row.vote_count for row in rows)

        return [
            {
                "candidate_id": row.candidate_id,
                "candidate_name": row.candidate_name,
                "vote_count": row.vote_count,
                "percentage": round((row.vote_count / total_votes * 100) if total_votes > 0 else 0, 2),
            }
            for row in rows
        ]

    async def get_turnout_stats(self, election_id: Optional[str] = None) -> dict:
        """Get turnout statistics."""
        # Total registered voters
        total_voters_result = await self.db.execute(
            select(func.count(StudentDPT.nim)).where(StudentDPT.is_registered == True)
        )
        total_voters = total_voters_result.scalar() or 0

        # Voted count
        voted_query = select(func.count(VotingStatus.nim)).where(VotingStatus.has_voted == True)
        if election_id:
            # Need to join with voting_tokens to filter by election
            voted_query = voted_query.join(
                VotingToken, VotingToken.student_nim == VotingStatus.nim
            ).where(VotingToken.election_id == election_id)

        voted_result = await self.db.execute(voted_query)
        voted_count = voted_result.scalar() or 0

        return {
            "total_voters": total_voters,
            "voted_count": voted_count,
            "turnout_percentage": round(
                (voted_count / total_voters * 100) if total_voters > 0 else 0, 2
            ),
        }


_vote_engine: Optional[VoteEngine] = None


def get_vote_engine(db: AsyncSession) -> VoteEngine:
    return VoteEngine(db)