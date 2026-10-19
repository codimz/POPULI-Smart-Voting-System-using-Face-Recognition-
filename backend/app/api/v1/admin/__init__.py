from app.api.v1.admin.voters import router as voters_router
from app.api.v1.admin.candidates import router as candidates_router
from app.api.v1.admin.dashboard import router as dashboard_router
from app.api.v1.admin.analytics.turnout import router as turnout_router
from app.api.v1.admin.analytics.results import router as results_router
from app.api.v1.admin.elections import router as elections_router
# from app.api.v1.admin.audit_logs import router as audit_router
# from app.api.v1.admin.reports import router as reports_router

__all__ = ["voters_router", "candidates_router", "dashboard_router", "turnout_router", "results_router", "elections_router", "audit_router", "reports_router"]