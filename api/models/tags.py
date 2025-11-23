from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=True)

    sandwich_tags = relationship("SandwichTag", back_populates="tag")


class SandwichTag(Base):
    __tablename__ = "sandwich_tags"

    sandwich_id = Column(Integer, ForeignKey("sandwiches.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

    sandwich = relationship("Sandwich", back_populates="sandwich_tags")
    tag = relationship("Tag", back_populates="sandwich_tags")
