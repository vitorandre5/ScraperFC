"""Sport model for database."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Sport(Base):
    """Sports/modalities table."""
    
    __tablename__ = "sports"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    leagues = relationship("League", back_populates="sport", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="sport", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_sports_key', 'key'),
    )
    
    def __repr__(self) -> str:
        return f"<Sport(id={self.id}, key='{self.key}', name='{self.name}')>"
