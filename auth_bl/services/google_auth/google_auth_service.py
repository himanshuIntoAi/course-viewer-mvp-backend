import httpx
import logging
from fastapi import HTTPException, Request
from sqlmodel import Session, select
from typing import Optional, Dict, Any
from ...utils.jwt_utils import create_access_token
from ...utils.config import get_settings
from cou_user.models.user import User
from cou_user.models.logintype import LoginType
from cou_user.models.loginhistory import LoginHistory
from datetime import datetime, timezone
import base64

logger = logging.getLogger(__name__)
settings = get_settings()

class GoogleAuthService:
    def __init__(self, db: Session, request: Request = None):
        self.db = db
        self.request = request
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.token_endpoint = "https://oauth2.googleapis.com/token"
        self.user_info_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        logger.info("Exchanging Google code for access token")
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_endpoint, data=data)
            if response.status_code != 200:
                logger.error(f"Failed to get Google access token: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to get access token")
            
            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information using access token"""
        logger.info("Fetching Google user information")
        async with httpx.AsyncClient() as client:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = await client.get(self.user_info_endpoint, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get Google user info: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            user_info = response.json()
            return {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'email_verified': user_info.get('email_verified', False)
            }

    async def _get_or_create_login_type(self) -> LoginType:
        """Get or create Google login type"""
        statement = select(LoginType).where(LoginType.name == "GOOGLE")
        login_type = self.db.exec(statement).first()
        
        if not login_type:
            login_type = LoginType(
                name="GOOGLE",
                created_by=0,
                updated_by=0
            )
            self.db.add(login_type)
            self.db.commit()
            self.db.refresh(login_type)
        
        return login_type

    async def _create_login_history(self, user_id: int, role_id: Optional[int] = None) -> None:
        """Create a login history record"""
        try:
            # Get user agent and device type
            user_agent = self.request.headers.get("user-agent", "") if self.request else ""
            device_type = "mobile" if "mobile" in user_agent.lower() else "web"
            if "tablet" in user_agent.lower():
                device_type = "tablet"
            
            # Get IP and location
            ip = None
            location = None
            forwarded_for = None
            if self.request:
                ip = str(self.request.client.host)
                forwarded_for = self.request.headers.get("x-forwarded-for")
                if forwarded_for:
                    ip = forwarded_for.split(",")[0].strip()
                location = self.request.headers.get("x-location")
            
            logger.info(f"Creating login history for user_id={user_id}, ip={ip}, device_type={device_type}")
            
            # Create login history record
            login_history = LoginHistory(
                user_id=user_id,
                login_type_id=1,  # Google login type
                role_id=role_id if role_id else 1,  # Use provided role_id or default to admin
                login_at=datetime.now(timezone.utc),
                login_success=True,
                ip=ip,
                location=location,
                device_type=device_type,
                device_name=user_agent[:500] if user_agent else None,
                is_proxy=bool(forwarded_for) if self.request else False,
                is_duplicate_login=False,
                created_at=datetime.now(timezone.utc),
                created_by=user_id,
                updated_at=datetime.now(timezone.utc),
                updated_by=user_id,
                is_mobile=device_type == "mobile"
            )
            
            # Add and commit with error handling
            try:
                self.db.add(login_history)
                self.db.commit()
                self.db.refresh(login_history)
                logger.info(f"Successfully created login history record id={login_history.id} for user {user_id}")
            except Exception as commit_error:
                self.db.rollback()
                logger.error(f"Database error creating login history: {str(commit_error)}")
                raise
            
        except Exception as e:
            logger.error(f"Error creating login history for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create login history: {str(e)}"
            )

    async def _get_or_create_user(self, user_info: dict, login_type_id: int, role_id: int) -> User:
        """Get existing user or create new one"""
        try:
            if not user_info.get('email'):
                logger.error("Email not provided by Google")
                raise HTTPException(status_code=400, detail="Email not provided by Google")
            
            logger.info(f"Looking up user with email: {user_info['email']}")
            user_query = select(User).where(User.personal_email == user_info['email'])
            user = self.db.exec(user_query).first()
            
            try:
                if not user:
                    logger.info(f"Creating new user for email: {user_info['email']}")
                    name_parts = user_info['name'].split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    user = User(
                        personal_email=user_info['email'],
                        first_name=first_name,
                        last_name=last_name,
                        display_name=user_info['name'],
                        auth_provider="google",
                        role_id=role_id,
                        login_type_id=login_type_id,
                        created_by=0,
                        updated_by=0,
                        active=True
                    )
                    
                    if user_info.get('picture'):
                        await self._update_user_image(user, user_info['picture'])
                    
                    self.db.add(user)
                    self.db.commit()
                    self.db.refresh(user)
                    logger.info(f"Successfully created new user with id: {user.id}")
                else:
                    logger.info(f"Updating existing user with id: {user.id}")
                    # Update existing user's display name and other details
                    user.display_name = user_info['name']
                    user.first_name = user_info['name'].split(' ', 1)[0]
                    user.last_name = user_info['name'].split(' ', 1)[1] if len(user_info['name'].split(' ', 1)) > 1 else ""
                    user.login_type_id = login_type_id
                    user.role_id = role_id
                    user.updated_at = datetime.now(timezone.utc)
                    user.updated_by = user.id
                    user.active = True
                    
                    if user_info.get('picture'):
                        await self._update_user_image(user, user_info['picture'])
                    
                    self.db.add(user)
                    self.db.commit()
                    self.db.refresh(user)
                    logger.info(f"Successfully updated user with id: {user.id}")
                
            except Exception as db_error:
                self.db.rollback()
                logger.error(f"Database error in user operation: {str(db_error)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error in user operation: {str(db_error)}"
                )
            
            logger.info(f"User info from Google: {user_info}")
            logger.info(f"User details after update/create: id={user.id}, display_name={user.display_name}, email={user.personal_email}")
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in user operation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error in user operation: {str(e)}"
            )

    async def _update_user_image(self, user: User, image_url: str):
        """Update user's profile image"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    user.image = response.content
        except Exception as e:
            logger.error(f"Failed to download profile picture: {str(e)}")

    async def authenticate(self, code: str, redirect_uri: str, state: Optional[str] = None) -> dict:
        """Complete Google authentication flow"""
        try:
            # Exchange code for token
            token_response = await self.exchange_code_for_token(code, redirect_uri)
            access_token = token_response.get('access_token')
            
            # Get user info
            user_info = await self.get_user_info(access_token)
            
            if not user_info.get('email_verified'):
                raise HTTPException(status_code=400, detail="Email not verified")
            
            # Get or create login type
            login_type = await self._get_or_create_login_type()
            
            # Use admin role (role_id = 1)
            role_id = 1
            
            # Find or create user
            user = await self._get_or_create_user(user_info, login_type.id, role_id)
            
            # Create login history record
            await self._create_login_history(user.id, role_id)
            
            # Generate JWT token
            jwt_token = create_access_token(user.id)
            
            # Convert image to base64 if it exists
            profile_image = None
            if user.image:
                try:
                    profile_image = f"data:image/png;base64,{base64.b64encode(user.image).decode('utf-8')}"
                except Exception as e:
                    logger.error(f"Error encoding profile image: {str(e)}")
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user_id": user.id,
                "display_name": user.display_name,
                "email": user.personal_email,
                "profile_image": profile_image,
                "expires_in": 86400  # 1 day in seconds
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Google auth error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=str(e),
                headers={"error_uri": "/"}
            ) 