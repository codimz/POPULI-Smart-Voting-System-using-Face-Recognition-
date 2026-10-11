from app.dependencies.auth import (
    get_current_student,
    get_current_admin,
    get_optional_student,
    require_roles,
)
from app.dependencies.rate_limit import (
    rate_limit_login,
    rate_limit_biometric,
    rate_limit_voting,
    RateLimiter,
)
from app.dependencies.database import get_db

__all__ = [
    "get_current_student",
    "get_current_admin",
    "get_optional_student",
    "require_roles",
    "rate_limit_login",
    "rate_limit_biometric",
    "rate_limit_voting",
    "RateLimiter",
    "get_db",
]