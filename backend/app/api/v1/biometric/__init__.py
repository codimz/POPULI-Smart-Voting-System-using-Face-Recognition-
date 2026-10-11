from app.api.v1.biometric.register import router as register_router
from app.api.v1.biometric.verify import router as verify_router

__all__ = ["register_router", "verify_router"]