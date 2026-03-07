"""Team endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import Team
from app.schemas import TeamResponse

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/search", response_model=List[TeamResponse])
def search_teams(
    q: str = Query(..., min_length=2, description="Search query"),
    sport: Optional[str] = Query(None, description="Filter by sport key"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Search teams by name.
    
    Args:
        q: Search query (minimum 2 characters)
        sport: Optional sport key filter
        limit: Maximum number of results (1-100)
        
    Returns:
        List of matching teams
    """
    query = db.query(Team).filter(
        Team.name.ilike(f"%{q}%") | Team.canonical_name.ilike(f"%{q}%")
    )
    
    if sport:
        from app.models import Sport
        query = query.join(Sport).filter(Sport.key == sport)
    
    teams = query.limit(limit).all()
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific team by ID.
    
    Args:
        team_id: Team ID
        
    Returns:
        Team details
        
    Raises:
        404: Team not found
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
