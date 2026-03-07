"""Match endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.core.database import get_db
from app.models import Match, League, Sport, Team
from app.schemas import MatchDetail, MatchResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/today", response_model=List[MatchDetail])
def get_today_matches(
    sport: Optional[str] = Query(None, description="Filter by sport key"),
    league: Optional[str] = Query(None, description="Filter by league name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get all matches scheduled for today.
    
    Args:
        sport: Optional sport key filter
        league: Optional league name filter  
        status: Optional status filter
        
    Returns:
        List of today's matches ordered by time
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    query = db.query(Match).filter(
        and_(
            Match.match_datetime_utc >= today,
            Match.match_datetime_utc < tomorrow
        )
    )
    
    query = _apply_filters(query, sport=sport, league=league, status=status)
    
    matches = query.order_by(Match.match_datetime_utc).all()
    return matches


@router.get("/date/{date_str}", response_model=List[MatchDetail])
def get_matches_by_date(
    date_str: str,
    sport: Optional[str] = Query(None, description="Filter by sport key"),
    league: Optional[str] = Query(None, description="Filter by league name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get all matches for a specific date.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        sport: Optional sport key filter
        league: Optional league name filter
        status: Optional status filter
        
    Returns:
        List of matches for the date ordered by time
        
    Raises:
        400: Invalid date format
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    next_date = target_date + timedelta(days=1)
    
    query = db.query(Match).filter(
        and_(
            Match.match_datetime_utc >= target_date,
            Match.match_datetime_utc < next_date
        )
    )
    
    query = _apply_filters(query, sport=sport, league=league, status=status)
    
    matches = query.order_by(Match.match_datetime_utc).all()
    return matches


@router.get("/range", response_model=List[MatchDetail])
def get_matches_range(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
    sport: Optional[str] = Query(None, description="Filter by sport key"),
    league: Optional[str] = Query(None, description="Filter by league name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get matches within a date range.
    
    Args:
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        sport: Optional sport key filter
        league: Optional league name filter
        status: Optional status filter
        page: Page number
        page_size: Items per page (1-100)
        
    Returns:
        List of matches in the date range
        
    Raises:
        400: Invalid date format or range
    """
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    if (end_date - start_date).days > 90:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 90 days")
    
    query = db.query(Match).filter(
        and_(
            Match.match_datetime_utc >= start_date,
            Match.match_datetime_utc <= end_date
        )
    )
    
    query = _apply_filters(query, sport=sport, league=league, status=status)
    
    # Apply pagination
    offset = (page - 1) * page_size
    matches = query.order_by(Match.match_datetime_utc).offset(offset).limit(page_size).all()
    
    return matches


@router.get("/search", response_model=List[MatchDetail])
def search_matches(
    team: Optional[str] = Query(None, description="Team name to search"),
    league: Optional[str] = Query(None, description="League name to search"),
    sport: Optional[str] = Query(None, description="Sport key filter"),
    status: Optional[str] = Query(None, description="Status filter"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Search matches by team or league name.
    
    Args:
        team: Team name to search (partial match)
        league: League name to search (partial match)
        sport: Sport key filter
        status: Status filter
        limit: Maximum results (1-100)
        
    Returns:
        List of matching matches
    """
    query = db.query(Match)
    
    if team:
        query = query.join(Team, or_(
            Match.home_team_id == Team.id,
            Match.away_team_id == Team.id
        )).filter(Team.name.ilike(f"%{team}%"))
    
    query = _apply_filters(query, sport=sport, league=league, status=status)
    
    matches = query.order_by(Match.match_datetime_utc.desc()).limit(limit).all()
    return matches


@router.get("/{match_id}", response_model=MatchDetail)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific match by ID.
    
    Args:
        match_id: Match ID
        
    Returns:
        Match details with all related entities
        
    Raises:
        404: Match not found
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


def _apply_filters(query, sport: Optional[str], league: Optional[str], status: Optional[str]):
    """Apply common filters to match query."""
    if sport:
        query = query.join(Sport).filter(Sport.key == sport)
    
    if league:
        query = query.join(League).filter(League.name.ilike(f"%{league}%"))
    
    if status:
        query = query.filter(Match.status == status)
    
    return query
