from app.api.v1.admin.voters import router as voters_router
from app.api.v1.admin.candidates import router as candidates_router

__all__ = ["voters_router", "candidates_router"]