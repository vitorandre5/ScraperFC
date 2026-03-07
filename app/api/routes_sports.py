"""Sports endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Sport
from app.schemas import SportResponse

router = APIRouter(prefix="/sports", tags=["sports"])


@router.get("", response_model=List[SportResponse])
def list_sports(db: Session = Depends(get_db)):
    """
    Get list of all available sports/modalities.
    
    Returns all sports currently in the system.
    """
    sports = db.query(Sport).order_by(Sport.name).all()
    return sports


@router.get("/{sport_id}", response_model=SportResponse)
def get_sport(sport_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific sport by ID.
    
    Args:
        sport_id: Sport ID
        
    Returns:
        Sport details
        
    Raises:
        404: Sport not found
    """
    sport = db.query(Sport).filter(Sport.id == sport_id).first()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    return sport
