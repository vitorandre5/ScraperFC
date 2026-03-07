"""Deduplication service for managing entity uniqueness."""
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Sport, League, Team, Match, ExternalMapping
from app.services.normalization import normalize_name, normalize_league_name, normalize_team_name
from app.core.logging import get_logger

logger = get_logger(__name__)


class DeduplicationService:
    """Service for preventing duplicate entities across sources."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_sport(self, sport_key: str, sport_name: str) -> Sport:
        """Get existing sport or create new one."""
        sport = self.db.query(Sport).filter(Sport.key == sport_key).first()
        
        if not sport:
            sport = Sport(key=sport_key, name=sport_name)
            self.db.add(sport)
            self.db.commit()
            self.db.refresh(sport)
            logger.info(f"Created new sport: {sport_name} ({sport_key})")
        
        return sport
    
    def get_or_create_league(
        self,
        sport_id: int,
        league_name: str,
        country: Optional[str] = None,
        source: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> League:
        """Get existing league or create new one with deduplication."""
        canonical = normalize_league_name(league_name, country)
        
        # Check if league exists by canonical name
        league = self.db.query(League).filter(
            League.sport_id == sport_id,
            League.canonical_name == canonical
        ).first()
        
        if not league and source and external_id:
            # Check by external mapping
            mapping = self.db.query(ExternalMapping).filter(
                ExternalMapping.entity_type == "league",
                ExternalMapping.source == source,
                ExternalMapping.external_id == str(external_id)
            ).first()
            
            if mapping:
                league = self.db.query(League).filter(League.id == mapping.entity_id).first()
        
        if not league:
            # Create new league
            league = League(
                sport_id=sport_id,
                name=league_name,
                country=country,
                canonical_name=canonical
            )
            self.db.add(league)
            self.db.commit()
            self.db.refresh(league)
            logger.info(f"Created new league: {league_name} (canonical: {canonical})")
            
            # Create external mapping if provided
            if source and external_id:
                self._create_external_mapping("league", league.id, source, external_id, league_id=league.id)
        
        return league
    
    def get_or_create_team(
        self,
        sport_id: int,
        team_name: str,
        country: Optional[str] = None,
        source: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Team:
        """Get existing team or create new one with deduplication."""
        canonical = normalize_team_name(team_name)
        
        # Check if team exists by canonical name
        team = self.db.query(Team).filter(
            Team.sport_id == sport_id,
            Team.canonical_name == canonical
        ).first()
        
        if not team and source and external_id:
            # Check by external mapping
            mapping = self.db.query(ExternalMapping).filter(
                ExternalMapping.entity_type == "team",
                ExternalMapping.source == source,
                ExternalMapping.external_id == str(external_id)
            ).first()
            
            if mapping:
                team = self.db.query(Team).filter(Team.id == mapping.entity_id).first()
        
        if not team:
            # Create new team
            team = Team(
                sport_id=sport_id,
                name=team_name,
                canonical_name=canonical,
                country=country
            )
            self.db.add(team)
            self.db.commit()
            self.db.refresh(team)
            logger.info(f"Created new team: {team_name} (canonical: {canonical})")
            
            # Create external mapping if provided
            if source and external_id:
                self._create_external_mapping("team", team.id, source, external_id, team_id=team.id)
        
        return team
    
    def find_or_create_match(
        self,
        sport_id: int,
        league_id: int,
        home_team_id: int,
        away_team_id: int,
        match_datetime: datetime,
        status: str,
        source: str,
        external_id: Optional[str] = None,
        season: Optional[str] = None,
        home_score: Optional[int] = None,
        away_score: Optional[int] = None
    ) -> tuple[Match, bool]:
        """
        Find existing match or create new one.
        
        Returns:
            Tuple of (match, created) where created is True if new match was created
        """
        # Try to find by source external ID first
        if external_id:
            mapping = self.db.query(ExternalMapping).filter(
                ExternalMapping.entity_type == "match",
                ExternalMapping.source == source,
                ExternalMapping.external_id == str(external_id)
            ).first()
            
            if mapping:
                match = self.db.query(Match).filter(Match.id == mapping.entity_id).first()
                if match:
                    return match, False
        
        # Try to find by unique match characteristics (within time window)
        time_window = timedelta(hours=2)  # Matches within 2 hours are considered same
        
        match = self.db.query(Match).filter(
            Match.league_id == league_id,
            Match.home_team_id == home_team_id,
            Match.away_team_id == away_team_id,
            Match.match_datetime_utc >= match_datetime - time_window,
            Match.match_datetime_utc <= match_datetime + time_window
        ).first()
        
        if match:
            # Update existing match
            return match, False
        
        # Create new match
        match = Match(
            sport_id=sport_id,
            league_id=league_id,
            season=season,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_datetime_utc=match_datetime,
            status=status,
            home_score=home_score,
            away_score=away_score,
            source_primary=source,
            source_external_id=external_id
        )
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        
        # Create external mapping
        if external_id:
            self._create_external_mapping("match", match.id, source, external_id)
        
        logger.debug(f"Created new match: {match.id}")
        return match, True
    
    def _create_external_mapping(
        self,
        entity_type: str,
        entity_id: int,
        source: str,
        external_id: str,
        league_id: Optional[int] = None,
        team_id: Optional[int] = None
    ):
        """Create external ID mapping."""
        existing = self.db.query(ExternalMapping).filter(
            ExternalMapping.entity_type == entity_type,
            ExternalMapping.source == source,
            ExternalMapping.external_id == str(external_id)
        ).first()
        
        if not existing:
            mapping = ExternalMapping(
                entity_type=entity_type,
                entity_id=entity_id,
                source=source,
                external_id=str(external_id),
                league_id=league_id,
                team_id=team_id
            )
            self.db.add(mapping)
            self.db.commit()
