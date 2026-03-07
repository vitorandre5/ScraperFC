"""External mapping model for tracking external IDs."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ExternalMapping(Base):
    """External IDs mapping to avoid duplicates across sources."""
    
    __tablename__ = "external_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # league, team, match
    entity_id = Column(Integer, nullable=False)  # Internal ID
    source = Column(String(50), nullable=False)  # sofascore, fbref, etc
    external_id = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Optional relationships for foreign keys
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    
    league = relationship("League", back_populates="external_mappings")
    team = relationship("Team", back_populates="external_mappings")
    
    __table_args__ = (
        UniqueConstraint('entity_type', 'source', 'external_id', name='uq_external_mapping'),
        Index('ix_external_entity', 'entity_type', 'entity_id'),
        Index('ix_external_source', 'source', 'external_id'),
    )
    
    def __repr__(self) -> str:
        return f"<ExternalMapping(type='{self.entity_type}', source='{self.source}', external_id='{self.external_id}')>"
