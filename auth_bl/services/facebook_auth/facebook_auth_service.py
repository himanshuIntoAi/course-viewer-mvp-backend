import httpx
import os
import json
import urllib.parse
import logging
from fastapi import HTTPException, Request
from sqlmodel import Session, select
from typing import Optional
from ...utils.jwt_utils import create_access_token
from ...schemas.auth_schemas import StateData
from cou_user.models.user import User
from cou_user.models.logintype import LoginType
from cou_user.models.role import Role
from cou_user.models.loginhistory import LoginHistory
from datetime import datetime, timezone
import base64

logger = logging.getLogger(__name__)

class FacebookAuthService:
    def __init__(self, db: Session, request: Request = None):
        self.db = db
        self.request = request
        self.client_id = os.getenv("FACEBOOK_CLIENT_ID")
        self.client_secret = os.getenv("FACEBOOK_CLIENT_SECRET")

    def _validate_state(self, state: Optional[str]) -> Optional[StateData]:
        """Validate the state parameter"""
        if not state:
            return None
            
        try:
            # First URL decode if needed
            decoded_url = urllib.parse.unquote(state)
            # Then parse JSON
            decoded_state = json.loads(decoded_url)
            state_data = StateData(**decoded_state)
            
            # Check if state is not too old (e.g., 1 hour)
            state_age = (datetime.now().timestamp() - state_data.timestamp) / 3600
            if state_age > 1:
                raise HTTPException(
                    status_code=400,
                    detail="State parameter has expired"
                )
                
            return state_data
        except Exception as e:
            print(f"Error validating state: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        """Exchange Facebook OAuth code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.facebook.com/v12.0/oauth/access_token",
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri
                }
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get Facebook access token")
            return response.json()

    async def get_user_info(self, access_token: str) -> dict:
        """Get Facebook user information using access token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,first_name,last_name,picture,link",
                    "access_token": access_token
                }
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get Facebook user info")
            return response.json()

    async def _get_or_create_login_type(self) -> LoginType:
        """Get or create Facebook login type"""
        statement = select(LoginType).where(LoginType.name == "FACEBOOK")
        login_type = self.db.exec(statement).first()
        
        if not login_type:
            login_type = LoginType(
                name="FACEBOOK",
                created_by=0,
                updated_by=0
            )
            self.db.add(login_type)
            self.db.commit()
            self.db.refresh(login_type)
        
        return login_type

    async def _get_or_create_default_role(self) -> Role:
        """Get or create default user role"""
        statement = select(Role).where(Role.name == "USER")
        role = self.db.exec(statement).first()
        
        if not role:
            role = Role(
                name="USER",
                description="Default role for Facebook auth users",
                created_by=0,
                updated_by=0
            )
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
        
        return role

    async def _create_login_history(self, user_id: int, role_id: Optional[int] = None) -> None:
        """Create a login history record"""
        try:
            # Get user agent info
            user_agent = self.request.headers.get("user-agent", "") if self.request else ""
            
            # Determine device type
            device_type = "mobile" if "mobile" in user_agent.lower() else "web"
            if "tablet" in user_agent.lower():
                device_type = "tablet"
            
            # Get IP and try to determine location
            ip = None
            location = None
            if self.request:
                ip = str(self.request.client.host)
                # Get real IP if behind proxy
                forwarded_for = self.request.headers.get("x-forwarded-for")
                if forwarded_for:
                    ip = forwarded_for.split(",")[0].strip()
                
                # Check if it's a proxy
                is_proxy = bool(forwarded_for or self.request.headers.get("x-real-ip"))
                
                # Get location from headers if available
                location = self.request.headers.get("x-location")
            
            login_history = LoginHistory(
                user_id=user_id,
                login_type_id=2,  # Facebook login type
                role_id=role_id,
                login_at=datetime.now(timezone.utc),
                login_success=True,
                ip=ip,
                location=location,
                device_type=device_type,
                device_name=user_agent[:255] if user_agent else None,  # Truncate to max length
                is_proxy=bool(forwarded_for) if self.request else False,
                is_duplicate_login=False,  # Could be implemented with session tracking
                created_at=datetime.now(timezone.utc),
                created_by=user_id,  # Set created_by as the logged-in user
                is_mobile=device_type == "mobile"
            )
            
            self.db.add(login_history)
            self.db.commit()
            logger.info(f"Created login history record for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating login history: {str(e)}")
            # Don't raise the exception as login history is not critical

    async def authenticate(self, code: str, redirect_uri: str, state: Optional[str] = None) -> dict:
        """Complete Facebook authentication flow"""
        try:
            # Validate state if provided
            state_data = self._validate_state(state)
            
            # Exchange code for token
            token_response = await self.exchange_code_for_token(code, redirect_uri)
            
            # Get user info
            fb_user = await self.get_user_info(token_response["access_token"])
            
            # Get or create login type and role
            login_type = await self._get_or_create_login_type()
            role = await self._get_or_create_default_role()
            
            # Find or create user
            user = await self._get_or_create_user(
                fb_user,
                login_type.id,
                role.id
            )
            
            # Create login history record
            await self._create_login_history(user.id, role.id)
            
            # Generate JWT token
            access_token = create_access_token(user.id)
            
            # Convert image to base64 if it exists
            profile_image = None
            if user.image:
                try:
                    profile_image = f"data:image/png;base64,{base64.b64encode(user.image).decode('utf-8')}"
                except Exception as e:
                    logger.error(f"Error encoding profile image: {str(e)}")
            
            response = {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user.id,
                "display_name": user.display_name,
                "email": user.personal_email,
                "profile_image": profile_image,
                "expires_in": 86400  # 1 day in seconds
            }

            # Add redirect path from state if available
            if state_data:
                response["redirect_path"] = state_data.redirectPath

            return response
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    async def _get_or_create_user(
        self,
        fb_user: dict,
        login_type_id: int,
        role_id: int
    ) -> User:
        """Get or create user from Facebook data"""
        email = fb_user.get("email")
        if email:
            # Try to find user by email
            statement = select(User).where(
                (User.work_email == email) | (User.personal_email == email)
            )
            user = self.db.exec(statement).first()
            
            if user:
                # Update existing user
                user.display_name = fb_user["name"]
                user.first_name = fb_user.get("first_name")
                user.last_name = fb_user.get("last_name")
                user.login_type_id = login_type_id
                user.role_id = role_id
                user.key = fb_user.get("link")
                user.updated_at = datetime.now(timezone.utc)
                user.updated_by = 0
                
                # Update profile image
                if fb_user.get("picture", {}).get("data", {}).get("url"):
                    await self._update_user_image(user, fb_user["picture"]["data"]["url"])
                
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                return user
        
        # Create new user
        user = User(
            display_name=fb_user["name"],
            first_name=fb_user.get("first_name"),
            last_name=fb_user.get("last_name"),
            personal_email=email,
            login_type_id=login_type_id,
            role_id=role_id,
            created_by=0,
            updated_by=0,
            active=True,
            key=fb_user.get("link"),
            currency_id=None,
            country_id=None,
            affiliate_id=None
        )
        
        # Set profile image
        if fb_user.get("picture", {}).get("data", {}).get("url"):
            await self._update_user_image(user, fb_user["picture"]["data"]["url"])
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def _update_user_image(self, user: User, image_url: str):
        """Download and update user's profile image"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    user.image = response.content
                else:
                    print(f"Failed to download profile image from {image_url}: Status {response.status_code}")
        except Exception as e:
            print(f"Error downloading profile image from {image_url}: {str(e)}") 