from fastapi import APIRouter
from .routes.auth.auth_routes import router as auth_router
from .services.github_auth.github_auth_service import GitHubAuthService
from .services.facebook_auth.facebook_auth_service import FacebookAuthService
from .schemas.auth_schemas import AuthRequest, AuthResponse

__all__ = [
    'auth_router',
    'GitHubAuthService',
    'FacebookAuthService',
    'AuthRequest',
    'AuthResponse'
]

router = APIRouter()
router.include_router(auth_router) 