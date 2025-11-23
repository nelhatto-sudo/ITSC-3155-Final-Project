from typing import Optional
from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    display_name: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None


class Tag(TagBase):
    id: int

    class ConfigDict:
        from_attributes = True