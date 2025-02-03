import bcrypt
import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlmodel import Session, select
from ..utils.jwt_utils import create_access_token
from ..schemas.auth_schemas import EmailAuthRequest, EmailRegisterRequest, AuthResponse
from cou_user.models.user import User
from cou_user.models.loginhistory import LoginHistory

logger = logging.getLogger(__name__)

class CredentialsAuthService:
    def __init__(self, db: Session):
        self.db = db

    async def register(self, request: EmailRegisterRequest) -> AuthResponse:
        """Handle user registration with email and password"""
        try:
            logger.info(f"Registration attempt for email: {request.email}")
            
            # Check if email already exists
            if self._get_user_by_email(request.email):
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )

            # Hash password
            hashed_password = self._hash_password(request.password)
            
            # Create new user
            user = self._create_user(request, hashed_password)
            
            # Create login history
            await self._create_login_history(user.id, user.role_id)
            
            # Generate access token
            access_token = create_access_token(user.id)
            
            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user_id=user.id,
                display_name=user.display_name,
                email=user.personal_email,
                expires_in=86400
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Registration failed: {str(e)}"
            )

    async def login(self, request: EmailAuthRequest) -> AuthResponse:
        """Handle user login with email and password"""
        try:
            logger.info(f"Login attempt for email: {request.email}")
            
            # Find user by email
            user = self._get_user_by_email(request.email)
            
            if not user:
                # Auto-register user if not found
                # Extract display name from email (part before @)
                display_name = request.email.split('@')[0]
                
                # Hash password
                hashed_password = self._hash_password(request.password)
                
                # Create new user with default role (2 for regular user)
                current_time = datetime.now(timezone.utc)
                user = User(
                    display_name=display_name,
                    personal_email=request.email,
                    key=hashed_password,
                    login_type_id=6,  # Email login type
                    role_id=2,  # Regular user role
                    created_by=0,
                    updated_by=0,
                    active=True,
                    created_at=current_time,
                    updated_at=current_time
                )
                
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                logger.info(f"Auto-registered new user with email: {request.email}")
            else:
                # Verify password for existing user
                if not self._verify_password(request.password, user.key):
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid email or password"
                    )

            # Create login history
            await self._create_login_history(user.id, user.role_id)

            # Generate access token
            access_token = create_access_token(user.id)
            
            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user_id=user.id,
                display_name=user.display_name,
                email=user.personal_email,
                expires_in=86400  # 1 day in seconds
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Login failed"
            )

    def _get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        return self.db.exec(
            select(User).where(User.personal_email == email)
        ).first()

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing password"
            )

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if not hashed:
            return False
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

    async def _create_login_history(self, user_id: int, role_id: int) -> None:
        """Create a login history record"""
        try:
            current_time = datetime.now(timezone.utc)
            login_history = LoginHistory(
                user_id=user_id,
                login_type_id=6,  # Email login type
                role_id=role_id,
                login_at=current_time,
                login_success=True,
                created_at=current_time,
                created_by=user_id,
                updated_at=current_time,
                updated_by=user_id,
                is_mobile=False
            )
            
            self.db.add(login_history)
            self.db.commit()
            logger.info(f"Created login history record for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating login history: {str(e)}")
            # Don't raise the exception as login history is not critical

    def _create_user(self, request: EmailRegisterRequest, hashed_password: str) -> User:
        """Create new user in database"""
        try:
            current_time = datetime.now(timezone.utc)
            user = User(
                display_name=request.display_name,
                personal_email=request.email,
                key=hashed_password,
                login_type_id=6,  # Email login type
                role_id=2,  # Regular user role
                created_by=0,
                updated_by=0,
                active=True,
                created_at=current_time,
                updated_at=current_time
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error creating user: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            ) 