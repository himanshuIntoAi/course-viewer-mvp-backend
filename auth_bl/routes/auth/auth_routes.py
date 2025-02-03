from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session, select
from ...schemas.auth_schemas import AuthRequest, AuthResponse, EmailAuthRequest, EmailRegisterRequest, GoogleAuthRequest
from ...services.github_auth.github_auth_service import GitHubAuthService
from ...services.facebook_auth.facebook_auth_service import FacebookAuthService
from ...services.google_auth.google_auth_service import GoogleAuthService
from ...services.credentials_auth_service import CredentialsAuthService
from ...utils.oauth2 import get_current_user, oauth2_scheme
from ...utils.jwt_utils import create_access_token
from typing import Annotated
from common.database import get_session
from cou_user.models.user import User
from cou_user.models.logintype import LoginType
from cou_user.models.loginhistory import LoginHistory
import base64
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}}
)

@router.post(
    "/github/callback",
    response_model=AuthResponse,
    summary="GitHub OAuth Callback",
    description="Handle GitHub OAuth callback and return access token"
)
async def github_callback(
    request: Request,
    auth_request: AuthRequest,
    db: Annotated[Session, Depends(get_session)]
) -> AuthResponse:
    """
    Handle GitHub OAuth callback
    
    - **code**: The OAuth code received from GitHub
    - **redirect_uri**: The redirect URI used in the OAuth flow (Next.js frontend callback)
    - **state**: Optional state parameter for maintaining application state
    
    Returns a JWT token and user information with optional redirect path
    """
    try:
        # Validate redirect URI
        expected_redirect_uri = "http://localhost:3000/api/auth/callback/github"
        if auth_request.redirect_uri != expected_redirect_uri:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid redirect URI. Expected: {expected_redirect_uri}"
            )
        
        service = GitHubAuthService(db, request)
        return await service.authenticate(
            auth_request.code,
            auth_request.redirect_uri,
            auth_request.state
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions with error_uri field
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e.detail),
            headers={"error_uri": "/"}  # Redirect to home page
        )
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"error_uri": "/"}  # Redirect to home page
        )

@router.post(
    "/facebook/callback",
    response_model=AuthResponse,
    summary="Facebook OAuth Callback",
    description="Handle Facebook OAuth callback and return access token"
)
async def facebook_callback(
    request: Request,
    auth_request: AuthRequest,
    db: Annotated[Session, Depends(get_session)]
) -> AuthResponse:
    """
    Handle Facebook OAuth callback
    
    - **code**: The OAuth code received from Facebook
    - **redirect_uri**: The redirect URI used in the OAuth flow (Next.js frontend callback)
    - **state**: Optional state parameter for maintaining application state
    
    Returns a JWT token and user information with optional redirect path
    """
    # Validate redirect URI
    expected_redirect_uri = "http://localhost:3000/api/auth/callback/facebook"
    if auth_request.redirect_uri != expected_redirect_uri:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid redirect URI. Expected: {expected_redirect_uri}"
        )
    
    service = FacebookAuthService(db, request)
    return await service.authenticate(
        auth_request.code,
        auth_request.redirect_uri,
        auth_request.state
    )

@router.post(
    "/google/callback",
    response_model=AuthResponse,
    summary="Google OAuth Callback",
    description="Handle Google OAuth callback and return access token"
)
async def google_callback(
    request: Request,
    auth_request: GoogleAuthRequest,
    db: Annotated[Session, Depends(get_session)]
) -> AuthResponse:
    """
    Handle Google OAuth callback
    
    - **code**: The OAuth code received from Google
    - **redirect_uri**: The redirect URI used in the OAuth flow
    - **state**: Optional state parameter for maintaining application state
    
    Returns a JWT token and user information with optional redirect path
    """
    try:
        # Validate redirect URI
        expected_redirect_uri = "http://localhost:3000/api/auth/callback/google"
        if auth_request.redirect_uri != expected_redirect_uri:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid redirect URI. Expected: {expected_redirect_uri}"
            )
        
        service = GoogleAuthService(db, request)
        return await service.authenticate(
            auth_request.code,
            auth_request.redirect_uri,
            auth_request.state
        )
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
            headers={"error_uri": "/"}  # Redirect to home page
        )

@router.get(
    "/verify",
    summary="Verify Token",
    description="Verify if the provided token is valid"
)
async def verify_token(user_id: int = Depends(get_current_user)):
    """
    Verify if the provided token is valid
    Returns 200 if valid, 401 if invalid
    """
    return {"status": "valid", "user_id": user_id}

@router.get(
    "/user",
    summary="Get User Info",
    description="Get current user information"
)
async def get_user_info(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get current user information based on the provided token"""
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Convert image to base64 if it exists
    profile_image = None
    if user.image:
        try:
            profile_image = f"data:image/png;base64,{base64.b64encode(user.image).decode('utf-8')}"
        except Exception as e:
            logger.error(f"Error encoding profile image: {str(e)}")
    
    return {
        "id": user.id,
        "display_name": user.display_name,
        "email": user.personal_email,
        "profile_image": profile_image,
        "first_name": user.first_name,
        "last_name": user.last_name
    }

@router.post(
    "/logout",
    summary="Logout",
    description="Logout the current user",
    status_code=status.HTTP_200_OK
)
async def logout(
    response: Response,
    current_user: int = Depends(get_current_user)  # Verify token is valid
):
    """Logout the current user and clear the authentication token"""
    # Clear cookie if you're using cookie-based auth
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return {
        "status": "success",
        "message": "Successfully logged out",
        "user_id": current_user
    }

@router.post("/register")
async def register_with_email(
    request: EmailRegisterRequest,
    db: Annotated[Session, Depends(get_session)]
) -> AuthResponse:
    """Register a new user with email and password"""
    service = CredentialsAuthService(db)
    return await service.register(request)

@router.post("/login")
async def login_with_email(
    request: EmailAuthRequest,
    db: Annotated[Session, Depends(get_session)]
) -> AuthResponse:
    """Login with email and password"""
    service = CredentialsAuthService(db)
    return await service.login(request)