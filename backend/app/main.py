"""
License Manager Backend - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select

from app.core.config import settings
from app.core.limiter import limiter
from app.api.v1.router import api_router
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.models.user import User
from app.core.security import get_password_hash

# Create FastAPI application
app = FastAPI(
    title="License Manager API",
    description="Professional License Management System for Python Applications",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Default admin credentials
DEFAULT_ADMIN_EMAIL = "admin@localhost.com"
DEFAULT_ADMIN_PASSWORD = "AdminPass123!"


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and create default admin on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create default admin if not exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == DEFAULT_ADMIN_EMAIL))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                email=DEFAULT_ADMIN_EMAIL,
                password_hash=get_password_hash(DEFAULT_ADMIN_PASSWORD),
                full_name="System Administrator",
                is_verified=True,
                is_admin=True,
                is_approved=True,
                is_active=True
            )
            db.add(admin)
            await db.commit()
            print(f"[INIT] Default admin created: {DEFAULT_ADMIN_EMAIL}")
        else:
            print(f"[INIT] Default admin already exists: {DEFAULT_ADMIN_EMAIL}")


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "status": "healthy",
        "message": "License Manager API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
