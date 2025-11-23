from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Sandwich(Base):
    __tablename__ = "sandwiches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sandwich_name = Column(String(100), unique=True, nullable=True)
    price = Column(DECIMAL(4, 2), nullable=False, server_default='0.0')

    recipes = relationship("Recipe", back_populates="sandwich")
    order_details = relationship("OrderDetail", back_populates="sandwich")

    # many-to-many relation to Tag via SandwichTag
    sandwich_tags = relationship(
        "SandwichTag",
        back_populates="sandwich",
        cascade="all, delete-orphan",
    )

    @property
    def tag_ids(self) -> list[int]:
        # sandwich.sandwich_tags is a list of SandwichTag objects
        return [st.tag_id for st in self.sandwich_tags]