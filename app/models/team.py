"""Team model for database."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Team(Base):
    """Teams/clubs table."""
    
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    name = Column(String(200), nullable=False)
    canonical_name = Column(String(200), nullable=False, index=True)
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sport = relationship("Sport", back_populates="teams")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    external_mappings = relationship("ExternalMapping", back_populates="team", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('sport_id', 'canonical_name', name='uq_team_sport_canonical'),
        Index('ix_teams_sport_canonical', 'sport_id', 'canonical_name'),
    )
    
    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}')>"
