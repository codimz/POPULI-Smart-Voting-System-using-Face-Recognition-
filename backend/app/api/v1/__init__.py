from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.admin import candidates_router, voters_router, dashboard_router, turnout_router, results_router, elections_router
from app.api.v1.biometric import register_router, verify_router
from app.api.v1.voting.token_cast import router as voting_router
from app.api.v1.candidates import router as candidates_public_router

# Base path semua endpoint backend: /api/v1
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)          # /api/v1/auth/*
api_router.include_router(voters_router)        # /api/v1/admin/voters/*
api_router.include_router(candidates_router)    # /api/v1/admin/candidates/*
api_router.include_router(dashboard_router)      # /api/v1/admin/dashboard/*
api_router.include_router(turnout_router)        # /api/v1/admin/analytics/turnout/*
api_router.include_router(results_router)       # /api/v1/admin/analytics/results/*
api_router.include_router(elections_router)     # /api/v1/admin/elections/*
# api_router.include_router(audit_router)         # /api/v1/admin/audit-logs/*
# api_router.include_router(reports_router)       # /api/v1/admin/reports/export/*
api_router.include_router(register_router)      # /api/v1/biometric/register*
api_router.include_router(verify_router)        # /api/v1/biometric/verify*, /status/*
api_router.include_router(voting_router)        # /api/v1/voting/*
api_router.include_router(candidates_public_router)  # /api/v1/candidates/*

__all__ = ["api_router"]
