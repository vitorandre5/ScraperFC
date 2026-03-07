"""Sofascore provider for fetching match data."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path to import ScraperFC
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from ScraperFC import Sofascore
from app.services.providers.base_provider import BaseProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


# Sofascore status code mappings
SOFASCORE_STATUS_MAP = {
    0: "scheduled",     # Not started
    6: "live",          # 1st half
    7: "live",          # 2nd half
    31: "live",         # Extra time
    100: "finished",    # Ended
    110: "finished",    # AET (After Extra Time)
    120: "finished",    # AP (After Penalties)
    60: "postponed",    # Postponed
    70: "cancelled",    # Canceled
    90: "cancelled",    # Abandoned
    93: "finished",     # Removed
}


class SofascoreProvider(BaseProvider):
    """Provider for Sofascore sports data."""
    
    def __init__(self):
        self.scraper = Sofascore()
        self._sport_key = "football"
    
    @property
    def name(self) -> str:
        return "sofascore"
    
    @property
    def supported_sports(self) -> List[str]:
        # Sofascore tem múltiplos esportes, mas focamos em futebol por enquanto
        return ["football"]
    
    def get_available_leagues(self, sport: str = "football") -> List[Dict[str, Any]]:
        """Get available leagues from Sofascore."""
        # Import comps from ScraperFC
        from ScraperFC.utils import get_module_comps
        comps = get_module_comps("SOFASCORE")
        
        leagues = []
        for league_name, league_data in comps.items():
            if isinstance(league_data, dict) and "SOFASCORE" in league_data:
                leagues.append({
                    "name": league_name,
                    "external_id": str(league_data["SOFASCORE"]),
                    "sport": sport
                })
        
        return leagues
    
    def get_matches(
        self,
        sport: str,
        league: str,
        start_date: datetime,
        end_date: datetime,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Fetch matches from Sofascore.
        
        For Sofascore, we fetch by season/year since that's how their API works.
        """
        matches = []
        
        try:
            # Determine season/year to fetch
            # Sofascore uses format like "2023/2024" or "2024"
            year = self._determine_season(start_date, end_date)
            
            logger.info(f"Fetching Sofascore matches for {league}, season {year}")
            
            # Get match dictionaries from Sofascore
            match_dicts = self.scraper.get_match_dicts(year=year, league=league)
            
            # Filter matches by date range and normalize
            for match_dict in match_dicts:
                match_data = self._normalize_match(match_dict, league, sport)
                
                # Filter by date range
                match_dt = match_data["match_datetime_utc"]
                if start_date <= match_dt <= end_date:
                    matches.append(match_data)
            
            logger.info(f"Fetched {len(matches)} matches from Sofascore for {league}")
            
        except Exception as e:
            logger.error(f"Error fetching Sofascore matches for {league}: {e}")
        
        return matches
    
    def _determine_season(self, start_date: datetime, end_date: datetime) -> str:
        """Determine season string from date range."""
        # Most European leagues run Aug-May, so season crosses years
        # Use the year of the start_date as reference
        year = start_date.year
        
        # Check if this might be a cross-year season
        if start_date.month >= 8:  # Aug onwards
            return f"{year}/{year + 1}"
        else:
            return f"{year - 1}/{year}"
    
    def _normalize_match(self, match_dict: Dict[str, Any], league: str, sport: str) -> Dict[str, Any]:
        """Normalize Sofascore match data to standard format."""
        # Extract tournament info
        tournament = match_dict.get("tournament", {})
        season_info = match_dict.get("season", {})
        
        # Extract team info
        home_team = match_dict.get("homeTeam", {})
        away_team = match_dict.get("awayTeam", {})
        
        # Extract status
        status_dict = match_dict.get("status", {})
        status_code = status_dict.get("code", 0)
        status = self.normalize_status(status_code)
        
        # Extract scores
        home_score = match_dict.get("homeScore", {}).get("current")
        away_score = match_dict.get("awayScore", {}).get("current")
        
        # Extract datetime (Sofascore uses Unix timestamp)
        timestamp = match_dict.get("startTimestamp", 0)
        match_datetime = datetime.fromtimestamp(timestamp) if timestamp else datetime.utcnow()
        
        return {
            "sport": sport,
            "league_name": tournament.get("name", league),
            "league_country": tournament.get("category", {}).get("name"),
            "league_external_id": str(tournament.get("uniqueTournament", {}).get("id", "")),
            "season": season_info.get("name") or season_info.get("year"),
            "home_team_name": home_team.get("name", ""),
            "home_team_external_id": str(home_team.get("id", "")),
            "away_team_name": away_team.get("name", ""),
            "away_team_external_id": str(away_team.get("id", "")),
            "match_datetime_utc": match_datetime,
            "status": status,
            "home_score": home_score,
            "away_score": away_score,
            "external_id": str(match_dict.get("id", "")),
            "source": self.name
        }
    
    def normalize_status(self, raw_status: Any) -> str:
        """Normalize Sofascore status codes to standard format."""
        if isinstance(raw_status, int):
            return SOFASCORE_STATUS_MAP.get(raw_status, "scheduled")
        return "scheduled"
    
    def get_today_matches(self, sport: str = "football") -> List[Dict[str, Any]]:
        """Get today's matches across all available leagues."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        all_matches = []
        leagues = self.get_available_leagues(sport)
        
        # Focus on major leagues for "today" queries
        priority_leagues = [
            "England Premier League",
            "Spain La Liga",
            "Germany Bundesliga",
            "Italy Serie A",
            "France Ligue 1",
            "UEFA Champions League",
        ]
        
        for league_info in leagues:
            if league_info["name"] in priority_leagues:
                try:
                    matches = self.get_matches(
                        sport=sport,
                        league=league_info["name"],
                        start_date=today,
                        end_date=tomorrow
                    )
                    all_matches.extend(matches)
                except Exception as e:
                    logger.warning(f"Could not fetch matches for {league_info['name']}: {e}")
        
        return all_matches
