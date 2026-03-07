"""Match model for database."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Match(Base):
    """Matches/games table."""
    
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    season = Column(String(50), nullable=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_datetime_utc = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)  # scheduled, live, finished, postponed, cancelled
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    source_primary = Column(String(50), nullable=False)  # sofascore, fbref, etc
    source_external_id = Column(String(100), nullable=True)
    last_synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    league = relationship("League", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    
    __table_args__ = (
        UniqueConstraint(
            'league_id', 'home_team_id', 'away_team_id', 'match_datetime_utc',
            name='uq_match_unique_game'
        ),
        Index('ix_matches_datetime', 'match_datetime_utc'),
        Index('ix_matches_status', 'status'),
        Index('ix_matches_league', 'league_id'),
        Index('ix_matches_home_team', 'home_team_id'),
        Index('ix_matches_away_team', 'away_team_id'),
        Index('ix_matches_source', 'source_primary', 'source_external_id'),
    )
    
    def __repr__(self) -> str:
        return (f"<Match(id={self.id}, home={self.home_team_id} vs away={self.away_team_id}, "
                f"datetime={self.match_datetime_utc}, status='{self.status}')>")
