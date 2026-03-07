"""Base provider interface for sports data sources."""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class BaseProvider(ABC):
    """Abstract base class for sports data providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass
    
    @property
    @abstractmethod
    def supported_sports(self) -> List[str]:
        """List of supported sport keys."""
        pass
    
    @abstractmethod
    def get_matches(
        self,
        sport: str,
        league: str,
        start_date: datetime,
        end_date: datetime,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Fetch matches from provider.
        
        Args:
            sport: Sport key (e.g., 'football')
            league: League name/identifier
            start_date: Start of date range
            end_date: End of date range
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of match dictionaries with standardized structure
        """
        pass
    
    @abstractmethod
    def get_available_leagues(self, sport: str) -> List[Dict[str, Any]]:
        """
        Get list of available leagues for a sport.
        
        Args:
            sport: Sport key
            
        Returns:
            List of league information dictionaries
        """
        pass
    
    def normalize_status(self, raw_status: Any) -> str:
        """
        Normalize match status to standard values.
        
        Standard statuses:
        - scheduled: Match not yet started
        - live: Match in progress
        - finished: Match completed
        - postponed: Match postponed
        - cancelled: Match cancelled
        
        Args:
            raw_status: Provider-specific status value
            
        Returns:
            Normalized status string
        """
        return "scheduled"  # Default implementation
