from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class DashboardStats(BaseModel):
    total_voters: int
    voted_count: int
    turnout_percentage: float
    total_candidates: int
    active_elections: int
    pending_verifications: int

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_voters": 5000,
            "voted_count": 3250,
            "turnout_percentage": 65.0,
            "total_candidates": 6,
            "active_elections": 1,
            "pending_verifications": 12
        }
    })


class TurnoutByProgram(BaseModel):
    study_program: str
    total_voters: int
    voted_count: int
    turnout_percentage: float


class TurnoutStats(BaseModel):
    overall: DashboardStats
    by_program: List[TurnoutByProgram]
    by_election_type: List["TurnoutByElectionType"]
    timeline: List["TurnoutTimeline"]


class TurnoutByElectionType(BaseModel):
    election_type: str
    total_voters: int
    voted_count: int
    turnout_percentage: float


class TurnoutTimeline(BaseModel):
    timestamp: datetime
    cumulative_votes: int


class CandidateResult(BaseModel):
    candidate_id: int
    candidate_name: str
    vote_count: int
    percentage: float


class ElectionResult(BaseModel):
    election_id: str
    election_type: str
    total_votes: int
    candidates: List[CandidateResult]


class ResultsStats(BaseModel):
    elections: List[ElectionResult]
    generated_at: datetime


class AuditLogResponse(BaseModel):
    log_id: int
    event_type: str
    ip_address: Optional[str]
    timestamp: datetime
    description: Optional[str]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "log_id": 1,
                "event_type": "LOGIN_SUCCESS",
                "ip_address": "192.168.1.1",
                "timestamp": "2026-10-11T10:00:00Z",
                "description": "Mahasiswa 2310112345 berhasil login"
            }
        }
    )


class ExportRequest(BaseModel):
    election_id: Optional[str] = None
    format: str = Field(default="csv", pattern="^(csv|pdf)$")
    include_audit: bool = False

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "election_id": "el_2026_hima",
            "format": "csv",
            "include_audit": False
        }
    })