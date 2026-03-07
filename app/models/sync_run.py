"""Sync run model for tracking synchronization jobs."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from app.core.database import Base


class SyncRun(Base):
    """Sync runs tracking table."""
    
    __tablename__ = "sync_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, nullable=False, index=True)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)  # running, completed, failed, partial
    source = Column(String(50), nullable=True)  # which provider was used
    matches_created = Column(Integer, default=0)
    matches_updated = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('ix_sync_runs_started', 'started_at'),
        Index('ix_sync_runs_status', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<SyncRun(id={self.id}, status='{self.status}', started_at={self.started_at})>"
