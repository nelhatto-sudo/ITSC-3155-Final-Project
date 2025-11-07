from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PromotionBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str  # 'percent' or 'amount'
    discount_value: float
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = True

class PromotionCreate(PromotionBase):
    pass

class PromotionUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class Promotion(PromotionBase):
    id: int
    class ConfigDict:
        from_attributes = True