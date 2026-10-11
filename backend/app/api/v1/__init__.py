from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.admin import candidates_router, voters_router
from app.api.v1.biometric import register_router, verify_router
from app.api.v1.voting.token_cast import router as voting_router

# Base path semua endpoint backend: /api/v1
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)          # /api/v1/auth/*
api_router.include_router(voters_router)        # /api/v1/admin/voters/*
api_router.include_router(candidates_router)    # /api/v1/admin/candidates/*
api_router.include_router(register_router)      # /api/v1/biometric/register*
api_router.include_router(verify_router)        # /api/v1/biometric/verify*, /status/*
api_router.include_router(voting_router)        # /api/v1/voting/*

__all__ = ["api_router"]
