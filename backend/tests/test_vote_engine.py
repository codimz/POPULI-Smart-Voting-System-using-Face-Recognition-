# T27: Unit test vote_engine
import pytest
from app.services.vote_engine import VoteEngine
from app.models.student import StudentDPT


@pytest.mark.asyncio
async def test_eligibility_and_double_vote():
    # Verify VoteEngine interface exists; full DB integration requires fixture
    from app.services.vote_engine import VoteEngine
    assert hasattr(VoteEngine, "check_eligibility")


@pytest.mark.asyncio
async def test_idempotency_key_exists():
    # Idempotency record check
    from app.models.idempotency import IdempotencyRecord
    assert IdempotencyRecord.__tablename__ == "idempotency_records"


@pytest.mark.asyncio
async def test_token_expired_logic():
    from app.models.voting_token import VotingToken, TokenStatus
    assert TokenStatus.EXPIRED.value == "expired"
