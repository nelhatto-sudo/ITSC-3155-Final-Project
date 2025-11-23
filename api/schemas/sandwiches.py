from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class SandwichBase(BaseModel):
    sandwich_name: str
    price: float
    tag_ids: list[int] = []


class SandwichCreate(SandwichBase):
    # optional list of tag IDs to attach to this sandwich
    tag_ids: List[int] = []


class SandwichUpdate(BaseModel):
    sandwich_name: Optional[str] = None
    price: Optional[float] = None
    # if provided, this replaces the sandwich's tag list
    tag_ids: Optional[list[int]] = None


class Sandwich(SandwichBase):
    id: int

    class ConfigDict:
        from_attributes = True