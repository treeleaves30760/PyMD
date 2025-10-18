"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from pymd.backend.app.core.database import get_db
from pymd.backend.app.core.redis import get_redis

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "pymd-backend",
    }


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check - verifies database and redis connectivity"""
    try:
        # Check database
        await db.execute(text("SELECT 1"))

        # Check Redis
        redis = get_redis()
        await redis.ping()

        return {
            "status": "ready",
            "database": "connected",
            "redis": "connected",
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
        }


@router.get("/health/live")
async def liveness_check():
    """Liveness check - verifies service is running"""
    return {
        "status": "alive",
    }
