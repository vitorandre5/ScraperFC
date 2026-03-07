"""League endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import League, Sport
from app.schemas import LeagueResponse, LeagueWithSport

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.get("", response_model=List[LeagueWithSport])
def list_leagues(
    sport: Optional[str] = Query(None, description="Filter by sport key"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db)
):
    """
    Get list of leagues with optional filters.
    
    Args:
        sport: Filter by sport key (e.g., 'football')
        country: Filter by country name
        
    Returns:
        List of leagues with sport information
    """
    query = db.query(League)
    
    if sport:
        query = query.join(Sport).filter(Sport.key == sport)
    
    if country:
        query = query.filter(League.country.ilike(f"%{country}%"))
    
    leagues = query.order_by(League.name).all()
    return leagues


@router.get("/{league_id}", response_model=LeagueWithSport)
def get_league(league_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific league by ID.
    
    Args:
        league_id: League ID
        
    Returns:
        League details with sport information
        
    Raises:
        404: League not found
    """
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league
