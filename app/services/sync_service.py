"""Synchronization service for fetching and updating match data."""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import SyncRun, Sport
from app.services.dedup_service import DeduplicationService
from app.services.providers import get_provider_registry
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SyncService:
    """Service for synchronizing sports data from external sources."""
    
    def __init__(self, db: Session):
        self.db = db
        self.dedup = DeduplicationService(db)
        self.provider_registry = get_provider_registry()
    
    def run_sync(self, force: bool = False, source: Optional[str] = None) -> SyncRun:
        """
        Run synchronization job to fetch and update match data.
        
        Args:
            force: Force sync even if recently synced
            source: Specific provider to use (if None, uses all)
            
        Returns:
            SyncRun record with execution details
        """
        sync_run = SyncRun(
            started_at=datetime.utcnow(),
            status="running",
            source=source,
            matches_created=0,
            matches_updated=0
        )
        self.db.add(sync_run)
        self.db.commit()
        
        try:
            # Determine date range
            now = datetime.utcnow()
            start_date = now - timedelta(days=settings.HISTORY_DAYS_PAST)
            end_date = now + timedelta(days=settings.HISTORY_DAYS_FUTURE)
            
            logger.info(f"Starting sync from {start_date} to {end_date}")
            
            # Get providers to use
            providers = []
            if source:
                provider = self.provider_registry.get_provider(source)
                if provider:
                    providers.append(provider)
                else:
                    raise ValueError(f"Provider '{source}' not found")
            else:
                providers = self.provider_registry.get_all_providers()
            
            if not providers:
                raise ValueError("No providers available for sync")
            
            # Sync each provider
            for provider in providers:
                logger.info(f"Syncing with provider: {provider.name}")
                
                for sport_key in provider.supported_sports:
                    # Ensure sport exists
                    sport = self.dedup.get_or_create_sport(
                        sport_key=sport_key,
                        sport_name=sport_key.capitalize()
                    )
                    
                    # Get available leagues
                    leagues = provider.get_available_leagues(sport_key)
                    logger.info(f"Found {len(leagues)} leagues for {sport_key}")
                    
                    # Sync matches for each league
                    for league_info in leagues:
                        try:
                            self._sync_league(
                                provider=provider,
                                sport=sport,
                                league_info=league_info,
                                start_date=start_date,
                                end_date=end_date,
                                sync_run=sync_run
                            )
                        except Exception as e:
                            logger.error(f"Error syncing league {league_info.get('name')}: {e}")
                            continue
            
            # Mark sync as completed
            sync_run.status = "completed"
            sync_run.finished_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(
                f"Sync completed: {sync_run.matches_created} created, "
                f"{sync_run.matches_updated} updated"
            )
            
        except Exception as e:
            logger.error(f"Sync failed: {e}", exc_info=True)
            sync_run.status = "failed"
            sync_run.error_message = str(e)
            sync_run.finished_at = datetime.utcnow()
            self.db.commit()
        
        return sync_run
    
    def _sync_league(
        self,
        provider,
        sport: Sport,
        league_info: dict,
        start_date: datetime,
        end_date: datetime,
        sync_run: SyncRun
    ):
        """Sync matches for a specific league."""
        league_name = league_info.get("name", "")
        
        try:
            # Fetch matches from provider
            matches = provider.get_matches(
                sport=sport.key,
                league=league_name,
                start_date=start_date,
                end_date=end_date
            )
            
            logger.info(f"Processing {len(matches)} matches for {league_name}")
            
            for match_data in matches:
                try:
                    self._process_match(sport, match_data, sync_run)
                except Exception as e:
                    logger.error(f"Error processing match: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error fetching matches for {league_name}: {e}")
            raise
    
    def _process_match(self, sport: Sport, match_data: dict, sync_run: SyncRun):
        """Process and store a single match."""
        # Get or create league
        league = self.dedup.get_or_create_league(
            sport_id=sport.id,
            league_name=match_data["league_name"],
            country=match_data.get("league_country"),
            source=match_data["source"],
            external_id=match_data.get("league_external_id")
        )
        
        # Get or create teams
        home_team = self.dedup.get_or_create_team(
            sport_id=sport.id,
            team_name=match_data["home_team_name"],
            source=match_data["source"],
            external_id=match_data.get("home_team_external_id")
        )
        
        away_team = self.dedup.get_or_create_team(
            sport_id=sport.id,
            team_name=match_data["away_team_name"],
            source=match_data["source"],
            external_id=match_data.get("away_team_external_id")
        )
        
        # Find or create match
        match, created = self.dedup.find_or_create_match(
            sport_id=sport.id,
            league_id=league.id,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_datetime=match_data["match_datetime_utc"],
            status=match_data["status"],
            source=match_data["source"],
            external_id=match_data.get("external_id"),
            season=match_data.get("season"),
            home_score=match_data.get("home_score"),
            away_score=match_data.get("away_score")
        )
        
        if created:
            sync_run.matches_created += 1
        else:
            # Update existing match
            match.status = match_data["status"]
            match.home_score = match_data.get("home_score")
            match.away_score = match_data.get("away_score")
            match.last_synced_at = datetime.utcnow()
            sync_run.matches_updated += 1
        
        self.db.commit()
    
    def get_last_sync(self) -> Optional[SyncRun]:
        """Get the most recent sync run."""
        return self.db.query(SyncRun).order_by(SyncRun.started_at.desc()).first()
    
    def is_sync_running(self) -> bool:
        """Check if a sync is currently running."""
        running_sync = self.db.query(SyncRun).filter(
            SyncRun.status == "running"
        ).first()
        return running_sync is not None
