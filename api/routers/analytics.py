from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies.database import get_db
from ..controllers import analytics as controller

router = APIRouter(
    tags=["Staff Analytics"],
    prefix="/staff",
)


@router.get("/least-popular-dishes")
def least_popular_dishes(limit: int = 5, db: Session = Depends(get_db)):
    """
    Identify dishes that are less popular (ordered least often).
    Example: /staff/least-popular-dishes?limit=5
    """
    return controller.get_least_popular_dishes(db, limit)


@router.get("/complaints")
def complaints(max_stars: int = 2, db: Session = Depends(get_db)):
    """
    View low-star reviews (<= max_stars) and their reasons.
    Example: /staff/complaints?max_stars=2
    """
    return controller.get_complaints(db, max_stars)
