"""Health check endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db, check_db_connection
from app.core.config import settings
from app.schemas import HealthCheckResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify service status.
    
    Returns service status, database connection status, and current timestamp.
    """
    db_status = "healthy" if check_db_connection() else "unhealthy"
    overall_status = "healthy" if db_status == "healthy" else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        database=db_status,
        version=settings.APP_VERSION
    )
