from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base
import enum
import uuid

def generate_tracking_number() -> str:
    # Example: TRK-3F9A1C2D
    return f"TRK-{uuid.uuid4().hex[:8].upper()}"

class OrderStatus(enum.Enum):
    placed = "placed"
    preparing = "preparing"
    ready = "ready"
    out_for_delivery = "out_for_delivery"
    completed = "completed"
    canceled = "canceled"

class OrderType(enum.Enum):
    takeout = "takeout"
    delivery = "delivery"

class PaymentStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (UniqueConstraint('tracking_number', name='uq_orders_tracking'),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tracking_number = Column(
        String(50),
        nullable=False,
        unique=True,
        default=generate_tracking_number,  # auto-assign on insert
    )
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    delivery_address = Column(String(255), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False, default=OrderType.takeout)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.placed)
    order_date = Column(DATETIME, nullable=False, default=datetime.utcnow)
    subtotal = Column(DECIMAL(10, 2), nullable=False, default=0)
    discount = Column(DECIMAL(10, 2), nullable=False, default=0)
    tax = Column(DECIMAL(10, 2), nullable=False, default=0)
    total = Column(DECIMAL(10, 2), nullable=False, default=0)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)

    promo_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)

    # relationships
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")
    promotion = relationship("Promotion", back_populates="orders")



