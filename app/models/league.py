"""League model for database."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class League(Base):
    """Leagues/competitions table."""
    
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=True)
    canonical_name = Column(String(200), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sport = relationship("Sport", back_populates="leagues")
    matches = relationship("Match", back_populates="league", cascade="all, delete-orphan")
    external_mappings = relationship("ExternalMapping", back_populates="league", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('sport_id', 'canonical_name', name='uq_league_sport_canonical'),
        Index('ix_leagues_sport_canonical', 'sport_id', 'canonical_name'),
        Index('ix_leagues_country', 'country'),
    )
    
    def __repr__(self) -> str:
        return f"<League(id={self.id}, name='{self.name}', country='{self.country}')>"
