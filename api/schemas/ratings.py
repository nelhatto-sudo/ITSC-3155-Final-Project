from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class RatingBase(BaseModel):
    sandwich_id: int
    stars: int
    reason: Optional[str] = None

class RatingCreate(RatingBase):
    pass

class RatingUpdate(BaseModel):
    sandwich_id: Optional[int] = None
    stars: Optional[int] = None
    reason: Optional[str] = None

class Rating(RatingBase):
    id: int
    created_at: Optional[datetime] = None
    class ConfigDict:
        from_attributes = True