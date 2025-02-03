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

class GitHubAuthService:
    def __init__(self, db: Session, request: Request = None):
        self.db = db
        self.request = request
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")

    def _validate_state(self, state: Optional[str]) -> Optional[StateData]:
        """Validate the state parameter"""
        if not state:
            logger.debug("No state parameter provided")
            return None
            
        try:
            logger.debug(f"Raw state received: {state}")
            # First URL decode if needed
            decoded_url = urllib.parse.unquote(state)
            logger.debug(f"URL decoded state: {decoded_url}")
            # Then parse JSON
            decoded_state = json.loads(decoded_url)
            logger.debug(f"JSON decoded state: {decoded_state}")
            state_data = StateData(**decoded_state)
            
            # Check if state is not too old (e.g., 1 hour)
            state_age = (datetime.now().timestamp() - state_data.timestamp) / 3600
            if state_age > 1:
                logger.warning(f"State expired. Age: {state_age} hours")
                raise HTTPException(
                    status_code=400,
                    detail="State parameter has expired"
                )
                
            return state_data
        except Exception as e:
            logger.error(f"Error validating state: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        """Exchange GitHub OAuth code for access token"""
        logger.info("Exchanging GitHub code for access token")
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            logger.debug(f"Sending token request to GitHub with code: {code}")
            logger.debug(f"Using redirect_uri: {redirect_uri}")
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data=data,
                headers={"Accept": "application/json"}
            )
            
            token_response = response.json()
            logger.debug(f"GitHub token response: {token_response}")
            
            if "error" in token_response:
                logger.error(f"GitHub token exchange failed: {token_response['error_description']}")
                raise HTTPException(
                    status_code=400,
                    detail=token_response.get('error_description', 'Failed to get GitHub access token')
                )
            
            if response.status_code != 200 or "access_token" not in token_response:
                logger.error(f"Unexpected response from GitHub: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to get GitHub access token")
            
            logger.info("Successfully received GitHub access token")
            return token_response

    async def get_user_info(self, access_token: str) -> dict:
        """Get GitHub user information using access token"""
        logger.info("Fetching GitHub user information")
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            logger.debug("Sending user info request to GitHub")
            response = await client.get("https://api.github.com/user", headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to get GitHub user info. Status: {response.status_code}")
                raise HTTPException(status_code=400, detail="Failed to get GitHub user info")
            
            user_info = response.json()
            logger.debug(f"GitHub user info response: {user_info}")
            
            # Get email if not public in profile
            if not user_info.get("email"):
                logger.info("Email not found in profile, fetching from email endpoint")
                email_response = await client.get("https://api.github.com/user/emails", headers=headers)
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next((email["email"] for email in emails if email["primary"]), None)
                    user_info["email"] = primary_email
                    logger.debug(f"Found primary email: {primary_email}")

            return user_info

    async def _get_or_create_login_type(self) -> LoginType:
        """Get or create GitHub login type"""
        statement = select(LoginType).where(LoginType.name == "GITHUB")
        login_type = self.db.exec(statement).first()
        
        if not login_type:
            login_type = LoginType(
                name="GITHUB",
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
                description="Default role for GitHub auth users",
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
                login_type_id=4,  # GitHub login type
                role_id=1,  # Set as admin
                login_at=datetime.now(timezone.utc),
                login_success=True,
                ip=ip,
                location=location,
                device_type=device_type,
                device_name=user_agent[:500] if user_agent else None,  # Truncate to max length
                is_proxy=bool(forwarded_for) if self.request else False,
                is_duplicate_login=False,  # Could be implemented with session tracking
                created_at=datetime.now(timezone.utc),
                created_by=user_id,
                updated_by=user_id,
                is_mobile=device_type == "mobile"
            )
            
            self.db.add(login_history)
            self.db.commit()
            logger.info(f"Created login history record for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating login history: {str(e)}")
            # Don't raise the exception as login history is not critical

    async def authenticate(self, code: str, redirect_uri: str, state: Optional[str] = None) -> dict:
        """Complete GitHub authentication flow"""
        try:
            # Validate state if provided
            state_data = self._validate_state(state)
            
            # Exchange code for token
            token_response = await self.exchange_code_for_token(code, redirect_uri)
            
            # Get user info
            github_user = await self.get_user_info(token_response["access_token"])
            
            # Get or create login type
            login_type = await self._get_or_create_login_type()
            
            # Use admin role (role_id = 1)
            role_id = 1
            
            # Find or create user
            user = await self._get_or_create_user(
                github_user,
                login_type.id,
                role_id
            )
            
            # Create login history record
            await self._create_login_history(user.id, role_id)
            
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
        github_user: dict,
        login_type_id: int,
        role_id: int
    ) -> User:
        """Get or create user from GitHub data"""
        email = github_user.get("email")
        if email:
            # Try to find user by email
            statement = select(User).where(
                (User.work_email == email) | (User.personal_email == email)
            )
            user = self.db.exec(statement).first()
            
            if user:
                # Update existing user
                user.display_name = github_user["login"]
                user.first_name = github_user.get("name")
                user.login_type_id = login_type_id
                user.role_id = 1  # Set as admin
                user.key = github_user["html_url"]
                user.updated_at = datetime.now(timezone.utc)
                user.updated_by = 0
                
                # Update profile image
                if github_user.get("avatar_url"):
                    await self._update_user_image(user, github_user["avatar_url"])
                
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                return user
        
        # Create new user
        user = User(
            display_name=github_user["login"],
            first_name=github_user.get("name"),
            personal_email=email,
            login_type_id=login_type_id,
            role_id=1,  # Set as admin
            created_by=0,
            updated_by=0,
            active=True,
            key=github_user["html_url"],
            currency_id=None,
            country_id=None,
            affiliate_id=None
        )
        
        # Set profile image
        if github_user.get("avatar_url"):
            await self._update_user_image(user, github_user["avatar_url"])
        
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