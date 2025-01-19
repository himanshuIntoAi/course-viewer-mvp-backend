import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from common.database import engine
from cou_admin.api.country_routes import router as country_router
from fastapi import FastAPI
#from cou_admin.api.state_routes import router as state_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Actions to run at startup
    from cou_admin.models.country import Country
    SQLModel.metadata.create_all(engine)
    
    yield  # Allows FastAPI to proceed after startup
    # Add any shutdown actions here if needed

# Create FastAPI app with the lifespan context
app = FastAPI(lifespan=lifespan, debug=True)

# Include the router for country-related API endpoints
app.include_router(country_router, prefix="/api/v1")
#app.include_router(state_router, prefix="/api/v1")

# Debug: Print all routes
if __name__ == "__main__":
    for route in app.routes:
        print(route.path, route.name)