"""Background scheduler for automatic synchronization."""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.services.sync_service import SyncService

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


async def run_scheduled_sync():
    """Run scheduled synchronization job."""
    logger.info("Starting scheduled sync job")
    
    db = SessionLocal()
    try:
        sync_service = SyncService(db)
        
        # Check if already running
        if sync_service.is_sync_running():
            logger.warning("Sync already running, skipping scheduled run")
            return
        
        # Run sync
        sync_run = sync_service.run_sync(force=False)
        
        if sync_run.status == "completed":
            logger.info(
                f"Scheduled sync completed: {sync_run.matches_created} created, "
                f"{sync_run.matches_updated} updated"
            )
        else:
            logger.error(f"Scheduled sync failed: {sync_run.error_message}")
            
    except Exception as e:
        logger.error(f"Error in scheduled sync: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler."""
    logger.info(f"Starting scheduler with interval: {settings.SYNC_INTERVAL_MINUTES} minutes")
    
    # Add sync job
    scheduler.add_job(
        run_scheduled_sync,
        trigger=IntervalTrigger(minutes=settings.SYNC_INTERVAL_MINUTES),
        id="sync_matches",
        name="Sync matches from providers",
        replace_existing=True,
        max_instances=1  # Only one sync at a time
    )
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started successfully")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
