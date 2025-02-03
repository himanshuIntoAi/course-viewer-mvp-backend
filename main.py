import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from common.database import engine, create_db_and_tables
from cou_admin.api.country_routes import router as country_router
from cou_admin.api.currency_routes import router as currency_router
from cou_user.api.user_routes import router as user_router
from cou_course.api.course_routes import router as course_router
from cou_course.api.coursecategory_routes import router as coursecategory_router
from fastapi.middleware.cors import CORSMiddleware
from auth_bl import auth_router
import logging
from cou_mentor.api.mentor_routes import router as mentor_router
from fastapi import FastAPI

#from cou_admin.api.state_routes import router as state_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Actions to run at startup
    from cou_admin.models.country import Country
    from cou_user.models.user import User
    from cou_user.models.role import Role
    from cou_user.models.logintype import LoginType
    from cou_user.models.loginhistory import LoginHistory
    
    SQLModel.metadata.create_all(engine)
    
    yield  # Allows FastAPI to proceed after startup
    # Add any shutdown actions here if needed

# Create FastAPI app with the lifespan context
app = FastAPI(
    lifespan=lifespan,
    debug=True,
    title="Your API",
    description="Your API Description",
    version="1.0.0",
    # Remove the /api/v1 prefix from OpenAPI URLs to keep them at root level
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create database tables on startup
@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with explicit prefixes
app.include_router(country_router, prefix="/api/v1")
app.include_router(currency_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(course_router, prefix="/api/v1")
app.include_router(coursecategory_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(mentor_router, prefix="/api/v1")

# Debug print routes
print("\nRegistered routes:")
[print(f"{route.path} [{', '.join(route.methods)}]") for route in app.routes]

# Debug: Print all routes
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)