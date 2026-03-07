"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# Sport schemas
class SportBase(BaseModel):
    """Base sport schema."""
    key: str = Field(..., description="Unique key for the sport")
    name: str = Field(..., description="Display name of the sport")


class SportCreate(SportBase):
    """Schema for creating a sport."""
    pass


class SportResponse(SportBase):
    """Schema for sport response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# League schemas
class LeagueBase(BaseModel):
    """Base league schema."""
    name: str = Field(..., description="League name")
    country: Optional[str] = Field(None, description="Country of the league")
    canonical_name: str = Field(..., description="Normalized league name")


class LeagueCreate(LeagueBase):
    """Schema for creating a league."""
    sport_id: int


class LeagueResponse(LeagueBase):
    """Schema for league response."""
    id: int
    sport_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LeagueWithSport(LeagueResponse):
    """League response with sport information."""
    sport: SportResponse
    
    model_config = ConfigDict(from_attributes=True)


# Team schemas
class TeamBase(BaseModel):
    """Base team schema."""
    name: str = Field(..., description="Team name")
    canonical_name: str = Field(..., description="Normalized team name")
    country: Optional[str] = Field(None, description="Team's country")


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    sport_id: int


class TeamResponse(TeamBase):
    """Schema for team response."""
    id: int
    sport_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Match schemas
class MatchBase(BaseModel):
    """Base match schema."""
    season: Optional[str] = Field(None, description="Season identifier")
    match_datetime_utc: datetime = Field(..., description="Match datetime in UTC")
    status: str = Field(..., description="Match status")
    home_score: Optional[int] = Field(None, description="Home team score")
    away_score: Optional[int] = Field(None, description="Away team score")


class MatchCreate(MatchBase):
    """Schema for creating a match."""
    sport_id: int
    league_id: int
    home_team_id: int
    away_team_id: int
    source_primary: str
    source_external_id: Optional[str] = None


class MatchResponse(MatchBase):
    """Schema for match response."""
    id: int
    sport_id: int
    league_id: int
    home_team_id: int
    away_team_id: int
    source_primary: str
    source_external_id: Optional[str]
    last_synced_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MatchDetail(MatchResponse):
    """Detailed match response with related entities."""
    league: LeagueResponse
    home_team: TeamResponse
    away_team: TeamResponse
    
    model_config = ConfigDict(from_attributes=True)


# Sync schemas
class SyncRunResponse(BaseModel):
    """Schema for sync run response."""
    id: int
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    source: Optional[str]
    matches_created: int
    matches_updated: int
    error_message: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SyncTriggerRequest(BaseModel):
    """Schema for triggering a sync."""
    force: bool = Field(False, description="Force sync even if recently synced")
    source: Optional[str] = Field(None, description="Specific source to sync")


class SyncStatusResponse(BaseModel):
    """Schema for sync status response."""
    is_running: bool
    last_sync: Optional[SyncRunResponse]
    next_scheduled: Optional[datetime]


# Pagination
class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = ConfigDict(from_attributes=True)


# Health check
class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current server time")
    database: str = Field(..., description="Database connection status")
    version: str = Field(..., description="API version")
