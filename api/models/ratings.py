from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sandwich_id = Column(Integer, ForeignKey("sandwiches.id"))
    stars = Column(Integer, nullable=False)  # 1-5
    reason = Column(String(300))
    created_at = Column(DATETIME, default=datetime.utcnow)

    sandwich = relationship("Sandwich")