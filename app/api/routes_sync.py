"""Sync endpoints for manual synchronization control."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.services.sync_service import SyncService
from app.models import SyncRun
from app.schemas import SyncRunResponse, SyncTriggerRequest, SyncStatusResponse

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/run", response_model=SyncRunResponse)
def trigger_sync(
    request: SyncTriggerRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger a synchronization job.
    
    Args:
        request: Sync trigger configuration
        background_tasks: FastAPI background tasks
        
    Returns:
        Sync run information
        
    Raises:
        409: Sync already running
        400: Invalid source specified
    """
    sync_service = SyncService(db)
    
    # Check if sync is already running
    if sync_service.is_sync_running() and not request.force:
        raise HTTPException(
            status_code=409,
            detail="Sync is already running. Use force=true to override."
        )
    
    # Run sync in background
    def run_sync_task():
        # Create new DB session for background task
        from app.core.database import SessionLocal
        bg_db = SessionLocal()
        try:
            bg_sync_service = SyncService(bg_db)
            bg_sync_service.run_sync(force=request.force, source=request.source)
        finally:
            bg_db.close()
    
    background_tasks.add_task(run_sync_task)
    
    # Return immediately with pending status
    sync_run = SyncRun(
        started_at=datetime.utcnow(),
        status="running",
        source=request.source,
        matches_created=0,
        matches_updated=0
    )
    db.add(sync_run)
    db.commit()
    db.refresh(sync_run)
    
    return sync_run


@router.get("/status", response_model=SyncStatusResponse)
def get_sync_status(db: Session = Depends(get_db)):
    """
    Get current synchronization status.
    
    Returns:
        Sync status including last run and next scheduled time
    """
    sync_service = SyncService(db)
    
    is_running = sync_service.is_sync_running()
    last_sync = sync_service.get_last_sync()
    
    # Calculate next scheduled sync (every 5 minutes from last completed)
    next_scheduled = None
    if last_sync and last_sync.status == "completed" and last_sync.finished_at:
        from app.core.config import settings
        next_scheduled = last_sync.finished_at + timedelta(minutes=settings.SYNC_INTERVAL_MINUTES)
    
    return SyncStatusResponse(
        is_running=is_running,
        last_sync=last_sync,
        next_scheduled=next_scheduled
    )


@router.get("/history", response_model=list[SyncRunResponse])
def get_sync_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get synchronization history.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of recent sync runs
    """
    sync_runs = db.query(SyncRun).order_by(
        SyncRun.started_at.desc()
    ).limit(limit).all()
    
    return sync_runs
