from sqlalchemy import Column, Integer, String, DECIMAL, DATETIME, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from ..dependencies.database import Base

class Promotion(Base):
    __tablename__ = "promotions"
    __table_args__ = (UniqueConstraint('code', name='uq_promotions_code'),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(40), nullable=False)
    description = Column(String(200))
    discount_type = Column(String(10))  # 'percent' or 'amount'
    discount_value = Column(DECIMAL(10,2), nullable=False)
    expires_at = Column(DATETIME)
    is_active = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="promotion")